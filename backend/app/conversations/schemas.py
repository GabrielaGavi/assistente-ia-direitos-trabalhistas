"""Contratos de conversas, mensagens e do envio de pergunta (chat)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.citations.schemas import CitationResponse
from app.conversations.models import MessageRole, MessageStatus

__all__ = [
    "ConversationCreate",
    "ConversationDetailResponse",
    "ConversationListResponse",
    "ConversationResponse",
    "MessageCreate",
    "MessageResponse",
]


class ConversationCreate(BaseModel):
    # Titulo inicial pode ser ajustado depois pelo usuario; nao ha geracao
    # automatica via LLM nesta etapa (OVERVIEW TECNICO.md, secao 13, ja previa
    # que o titulo nasce deterministico, sem custo de IA).
    title: str = Field(default="Nova conversa", min_length=1, max_length=100)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    total: int


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: MessageRole
    status: MessageStatus
    content: str
    created_at: datetime
    citations: list[CitationResponse] = Field(default_factory=list)


class ConversationDetailResponse(ConversationResponse):
    messages: list[MessageResponse]
