"""Contratos de saida do pipeline minimo de RAG."""

from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

__all__ = ["RagAnswer", "RagAnswerStatus", "RetrievedChunk"]


class RagAnswerStatus(str, Enum):
    ANSWERED = "ANSWERED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class RetrievedChunk(BaseModel):
    """Evidencia usada para fundamentar a resposta, no formato que o frontend consome."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    content: str
    official_url: str
    article: str | None = None


class RagAnswer(BaseModel):
    status: RagAnswerStatus
    answer: str
    citations: list[RetrievedChunk]
