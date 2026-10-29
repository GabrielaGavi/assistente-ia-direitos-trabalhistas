"""Orquestra conversas, mensagens e o fluxo de chat (RAG) sobre elas.

O `RagService` e chamado FORA de qualquer transacao de banco: e uma chamada
de rede lenta (embedding + busca vetorial + LLM), e manter uma transacao
aberta durante ela prenderia a conexao por tempo desproporcional. Cada
gravacao (mensagem do usuario, mensagem da IA, citacoes) e sua propria
transacao curta.
"""

from contextlib import AbstractAsyncContextManager
from typing import Protocol
from uuid import UUID

from app.citations.models import Citation
from app.citations.schemas import CitationResponse
from app.conversations.models import Conversation, Message, MessageRole, MessageStatus
from app.conversations.schemas import ConversationDetailResponse, MessageResponse
from app.rag.schemas import RagAnswer

__all__ = [
    "ChatGenerationError",
    "ConversationNotFoundError",
    "ConversationService",
    "ConversationStore",
]

_MENSAGEM_DE_FALHA = "Nao foi possivel gerar uma resposta agora. Tente novamente em instantes."


class ConversationNotFoundError(LookupError):
    """Conversa inexistente ou pertencente a outro usuario.

    Os dois casos usam o mesmo erro (e o router devolve o mesmo 404 para
    ambos): diferenciar "nao existe" de "nao e sua" revelaria a um usuario
    que determinado ID pertence a outra pessoa.
    """


class ChatGenerationError(RuntimeError):
    """O provider de IA (embedding ou LLM) falhou ao gerar a resposta."""


class RagAnswerer(Protocol):
    async def answer(self, question: str, *, source_id: UUID | None = None) -> RagAnswer: ...


class ConversationStore(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]: ...
    async def add_conversation(self, conversation: Conversation) -> None: ...
    async def get_conversation(self, conversation_id: UUID) -> Conversation | None: ...
    async def list_conversations(
        self, user_id: UUID, *, offset: int, limit: int
    ) -> tuple[list[Conversation], int]: ...
    async def add_message(self, message: Message) -> None: ...
    async def list_messages(self, conversation_id: UUID) -> list[Message]: ...
    async def add_citation(self, citation: Citation) -> None: ...
    async def list_citations_by_message_ids(self, message_ids: list[UUID]) -> list[Citation]: ...


class ConversationService:
    def __init__(self, repository: ConversationStore, rag_service: RagAnswerer) -> None:
        self._repository = repository
        self._rag_service = rag_service

    async def create(self, *, user_id: UUID, title: str) -> Conversation:
        conversation = Conversation(user_id=user_id, title=title)
        async with self._repository.transaction():
            await self._repository.add_conversation(conversation)
        return conversation

    async def list_for_user(
        self, user_id: UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[Conversation], int]:
        return await self._repository.list_conversations(user_id, offset=offset, limit=limit)

    async def get_detail(self, conversation_id: UUID, user_id: UUID) -> ConversationDetailResponse:
        conversation = await self._owned_conversation(conversation_id, user_id)
        mensagens = await self._repository.list_messages(conversation_id)
        citacoes_por_mensagem = await self._citacoes_por_mensagem(mensagens)
        return ConversationDetailResponse(
            id=conversation.id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[
                self._para_message_response(mensagem, citacoes_por_mensagem.get(mensagem.id, []))
                for mensagem in mensagens
            ],
        )

    async def send_message(
        self, conversation_id: UUID, user_id: UUID, content: str
    ) -> MessageResponse:
        await self._owned_conversation(conversation_id, user_id)

        async with self._repository.transaction():
            await self._repository.add_message(
                Message(
                    conversation_id=conversation_id,
                    role=MessageRole.USER,
                    status=MessageStatus.COMPLETED,
                    content=content,
                )
            )

        try:
            resposta = await self._rag_service.answer(content)
        except Exception as erro:
            async with self._repository.transaction():
                await self._repository.add_message(
                    Message(
                        conversation_id=conversation_id,
                        role=MessageRole.ASSISTANT,
                        status=MessageStatus.FAILED,
                        content=_MENSAGEM_DE_FALHA,
                    )
                )
            raise ChatGenerationError("Falha ao gerar resposta via RAG.") from erro

        async with self._repository.transaction():
            assistant_message = Message(
                conversation_id=conversation_id,
                role=MessageRole.ASSISTANT,
                status=MessageStatus.COMPLETED,
                content=resposta.answer,
            )
            await self._repository.add_message(assistant_message)
            citacoes = []
            for indice, chunk in enumerate(resposta.citations, start=1):
                citacao = Citation(
                    message_id=assistant_message.id,
                    chunk_id=chunk.id,
                    citation_number=indice,
                    original_quote=chunk.content,
                )
                await self._repository.add_citation(citacao)
                citacoes.append(citacao)

        return self._para_message_response(assistant_message, citacoes)

    async def _owned_conversation(self, conversation_id: UUID, user_id: UUID) -> Conversation:
        conversation = await self._repository.get_conversation(conversation_id)
        if conversation is None or conversation.user_id != user_id:
            raise ConversationNotFoundError(f"Conversa {conversation_id} nao encontrada.")
        return conversation

    async def _citacoes_por_mensagem(
        self, mensagens: list[Message]
    ) -> dict[UUID, list[Citation]]:
        todas = await self._repository.list_citations_by_message_ids(
            [mensagem.id for mensagem in mensagens]
        )
        agrupadas: dict[UUID, list[Citation]] = {}
        for citacao in todas:
            agrupadas.setdefault(citacao.message_id, []).append(citacao)
        return agrupadas

    @staticmethod
    def _para_message_response(mensagem: Message, citacoes: list[Citation]) -> MessageResponse:
        return MessageResponse(
            id=mensagem.id,
            role=mensagem.role,
            status=mensagem.status,
            content=mensagem.content,
            created_at=mensagem.created_at,
            citations=[CitationResponse.model_validate(citacao) for citacao in citacoes],
        )
