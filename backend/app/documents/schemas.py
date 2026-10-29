"""T020: contratos de cadastro, resposta e status de documentos normativos."""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, field_validator, model_validator

from app.documents.chunk_schemas import DocumentChunkResponse
from app.documents.models import DocumentStatus
from app.documents.service import validate_document_metadata

__all__ = [
    "DocumentChunkListResponse",
    "DocumentCreate",
    "DocumentListResponse",
    "DocumentResponse",
    "DocumentStatusUpdate",
]


class DocumentCreate(BaseModel):
    """Versao, checksum normalizado e estado inicial sao definidos pelo service."""

    source_id: UUID
    title: str
    logical_name: str
    checksum_sha256: str
    published_at: AwareDatetime | None = None

    @model_validator(mode="after")
    def validate_metadata(self) -> "DocumentCreate":
        # Compartilha as regras preexistentes com consumidores nao HTTP.
        validate_document_metadata(self.title, self.logical_name, self.checksum_sha256)
        return self

    @field_validator("published_at")
    @classmethod
    def publication_in_utc(cls, value: datetime | None) -> datetime | None:
        return value.astimezone(timezone.utc) if value is not None else None


class DocumentResponse(BaseModel):
    """Metadados publicos; nao carrega conteudo ou colecoes de chunks."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    title: str
    logical_name: str
    version: int
    checksum_sha256: str
    published_at: datetime | None = None
    is_active: bool
    status: DocumentStatus
    original_file_path: str | None = None
    created_at: datetime
    updated_at: datetime


class DocumentStatusUpdate(BaseModel):
    """Comando de ativacao/desativacao; nao permite saltar para READY."""

    is_active: bool


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int


class DocumentChunkListResponse(BaseModel):
    items: list[DocumentChunkResponse]
    total: int
