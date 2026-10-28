"""Schemas Pydantic das fontes juridicas oficiais.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T019
    Contrato: contracts/sources-documents-api.yaml
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["SourceCreate", "SourceResponse"]


class SourceCreate(BaseModel):
    """Dados necessarios para cadastrar uma nova fonte oficial."""

    name: str = Field(..., max_length=255)
    short_name: str = Field(..., max_length=50)
    base_url: str = Field(..., max_length=500)
    description: str | None = None


class SourceResponse(BaseModel):
    """Fonte oficial emissora de uma norma, como o Planalto ou o TST."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_name: str
    base_url: str
    description: str | None = None
    created_at: datetime