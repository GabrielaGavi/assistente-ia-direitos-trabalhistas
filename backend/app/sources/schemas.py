"""Schemas Pydantic das fontes juridicas oficiais.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T019
    Contrato: contracts/sources-documents-api.yaml
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, TypeAdapter, field_validator

__all__ = ["SourceCreate", "SourceListResponse", "SourceResponse"]

_HTTP_URL = TypeAdapter(HttpUrl)


class SourceCreate(BaseModel):
    """Metadados de cadastro; identificador e data sao gerados pela persistencia."""

    name: str = Field(min_length=1, max_length=255)
    short_name: str = Field(min_length=1, max_length=50)
    base_url: str = Field(min_length=1, max_length=500)
    description: str | None = None

    @field_validator("name", "short_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Nome e sigla nao podem conter apenas espacos.")
        return value

    @field_validator("base_url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        # Como nas citacoes, valida HTTP(S) sem reescrever a URL arquivada.
        _HTTP_URL.validate_python(value)
        return value


class SourceResponse(BaseModel):
    """Fonte oficial emissora de uma norma, como o Planalto ou o TST."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_name: str
    base_url: str
    description: str | None = None
    created_at: datetime


class SourceListResponse(BaseModel):
    """Pagina e total de fontes, conforme o contrato HTTP."""

    items: list[SourceResponse]
    total: int
