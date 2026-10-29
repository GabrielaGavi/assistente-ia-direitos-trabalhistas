"""Endpoints de conversas e do envio de pergunta (chat/RAG)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User
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


def _service(session: AsyncSession, rag_service: RagService) -> ConversationService:
    return ConversationService(ConversationRepository(session), rag_service)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar nova conversa",
)
async def create_conversation(
    payload: ConversationCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    rag_service: Annotated[RagService, Depends(get_rag_service)],
) -> ConversationResponse:
    conversation = await _service(session, rag_service).create(
        user_id=current_user.id, title=payload.title
    )
    return ConversationResponse.model_validate(conversation)


@router.get("", response_model=ConversationListResponse, summary="Listar conversas do usuario")
async def list_conversations(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    rag_service: Annotated[RagService, Depends(get_rag_service)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1)] = 20,
) -> ConversationListResponse:
    items, total = await _service(session, rag_service).list_for_user(
        current_user.id, offset=offset, limit=limit
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
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    rag_service: Annotated[RagService, Depends(get_rag_service)],
) -> ConversationDetailResponse:
    try:
        return await _service(session, rag_service).get_detail(conversation_id, current_user.id)
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
        502: {"description": "Falha no provider de IA (embedding ou LLM)"},
    },
)
async def send_message(
    conversation_id: UUID,
    payload: MessageCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    rag_service: Annotated[RagService, Depends(get_rag_service)],
) -> MessageResponse:
    service = _service(session, rag_service)
    try:
        return await service.send_message(conversation_id, current_user.id, payload.content)
    except ConversationNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversa nao encontrada."
        ) from error
    except ChatGenerationError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Nao foi possivel gerar uma resposta agora. Tente novamente.",
        ) from error
