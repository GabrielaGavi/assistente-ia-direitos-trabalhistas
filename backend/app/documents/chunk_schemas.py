"""Schemas Pydantic dos trechos normativos estruturados.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T026 (parcial -- exigido pelo detalhe da citacao da US1)
    Requisito: FR-005
    Contrato: contracts/sources-documents-api.yaml
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict

__all__ = ["DocumentChunkResponse"]


class DocumentChunkResponse(BaseModel):
    """Trecho literal de uma norma, com os metadados que permitem localiza-lo.

    `content` nao passa por nenhuma normalizacao. Aparar espacos ou colapsar
    quebras de linha produziria um texto que nao e mais o texto da lei, e a
    fidelidade do trecho e o que a citacao promete ao usuario (FR-007).
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    official_url: str

    # Opcionais porque nem todo trecho tem estrutura: preambulos e ementas
    # nao pertencem a artigo, secao ou paragrafo nenhum.
    article: str | None = None
    section: str | None = None
    paragraph: str | None = None
