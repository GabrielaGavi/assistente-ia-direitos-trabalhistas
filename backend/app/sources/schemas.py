"""Schemas Pydantic das fontes juridicas oficiais.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T019 (parcial -- `SourceResponse`, exigido pelo detalhe da citacao da US1)
    Contrato: contracts/sources-documents-api.yaml
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

__all__ = ["SourceResponse"]


class SourceResponse(BaseModel):
    """Fonte oficial emissora de uma norma, como o Planalto ou o TST."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    short_name: str
    base_url: str
    description: str | None = None
    created_at: datetime
