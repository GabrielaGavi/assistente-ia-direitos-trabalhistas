"""Endpoints de conversas e do envio de pergunta (chat/RAG)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.anonymous.repository import AnonymousRepository
from app.auth.dependencies import ChatActor, get_chat_actor
from app.conversations.repository import ConversationRepository
from app.conversations.schemas import (
    ConversationCreate,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.conversations.service import (
    ChatGenerationError,
    ConversationNotFoundError,
    ConversationService,
)
from app.rag.dependencies import get_rag_service
from app.rag.service import RagService
from app.shared.database import get_session

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def _service(session: AsyncSession, rag_service: RagService | None = None) -> ConversationService:
    return ConversationService(ConversationRepository(session), rag_service)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova conversa",
)
async def create_conversation(
    payload: ConversationCreate,
    actor: Annotated[ChatActor, Depends(get_chat_actor)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationResponse:
    conversation = await _service(session).create(
        user_id=actor.user_id, title=payload.title, anonymous_session_id=actor.anonymous_session_id
    )
    return ConversationResponse.model_validate(conversation)


@router.get("", response_model=ConversationListResponse, summary="Listar conversas do usuario")
async def list_conversations(
    actor: Annotated[ChatActor, Depends(get_chat_actor)],
    session: Annotated[AsyncSession, Depends(get_session)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ConversationListResponse:
    repository = ConversationRepository(session)
    if actor.user_id is not None:
        items, total = await repository.list_conversations(
            actor.user_id, offset=offset, limit=limit
        )
    else:
        items, total = await repository.list_anonymous_conversations(
            actor.anonymous_session_id, offset=offset, limit=limit
        )
    return ConversationListResponse(
        items=[ConversationResponse.model_validate(item) for item in items], total=total
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Historico de uma conversa",
    responses={404: {"description": "Conversa nao encontrada"}},
)
async def get_conversation(
    conversation_id: UUID,
    actor: Annotated[ChatActor, Depends(get_chat_actor)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationDetailResponse:
    try:
        return await _service(session).get_detail(
            conversation_id, actor.user_id, actor.anonymous_session_id
        )
    except ConversationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada."
        ) from error


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enviar pergunta (RAG) e receber a resposta fundamentada",
    responses={
        404: {"description": "Conversa nao encontrada"},
        429: {"description": "Limite de perguntas da sessao anonima atingido"},
        502: {"description": "Falha no provider de IA (embedding ou LLM)"},
    },
)
async def send_message(
    conversation_id: UUID,
    payload: MessageCreate,
    actor: Annotated[ChatActor, Depends(get_chat_actor)],
    session: Annotated[AsyncSession, Depends(get_session)],
    rag_service: Annotated[RagService, Depends(get_rag_service)],
) -> MessageResponse:
    service = _service(session, rag_service)
    quota = AnonymousRepository(session)
    reserved = False
    try:
        await service.ensure_owner(conversation_id, actor.user_id, actor.anonymous_session_id)
        if actor.anonymous_session_id is not None:
            reserved = await quota.reserve(actor.anonymous_session_id)
            if not reserved:
                raise HTTPException(
                    status_code=429,
                    detail="Voce usou as perguntas sem conta. Entre para continuar a conversa.",
                )
        return await service.send_message(
            conversation_id, actor.user_id, payload.content, actor.anonymous_session_id
        )
    except ConversationNotFoundError as error:
        if reserved:
            await quota.refund(actor.anonymous_session_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada."
        ) from error
    except ChatGenerationError as error:
        if reserved:
            await quota.refund(actor.anonymous_session_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nao foi possivel gerar uma resposta agora. Tente novamente.",
        ) from error
    except Exception:
        if reserved:
            await session.rollback()
            await quota.refund(actor.anonymous_session_id)
        raise
