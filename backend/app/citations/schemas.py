"""Schemas Pydantic das citacoes rastreaveis.

A citacao e o contrato de confianca do produto: e o que permite ao trabalhador
conferir que a orientacao recebida vem da lei, e nao de invencao do modelo.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T011
    Requisitos: FR-006, FR-007
    Contrato: contracts/sources-documents-api.yaml
"""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.documents.chunk_schemas import DocumentChunkResponse
from app.sources.schemas import SourceResponse

__all__ = ["CitationDetailResponse", "CitationResponse"]


class CitationResponse(BaseModel):
    """Citacao em sua forma resumida, como aparece ao lado da resposta."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID

    # A numeracao segue a ordem de aparicao na resposta e comeca em [1].
    citation_number: int = Field(ge=1)

    # min_length=1 porque citacao sem evidencia textual nao prova nada.
    # Nenhum strip e aplicado: o texto precisa sair igual ao da norma.
    original_quote: str = Field(min_length=1)


class CitationDetailResponse(CitationResponse):
    """Citacao inspecionada pelo usuario.

    Traz o trecho e a fonte aninhados porque o Cenario 1 da US1 exige que uma
    unica consulta responda "de onde veio isso": norma, artigo, texto literal e
    link oficial, sem o usuario precisar juntar as pecas.

    Ambos sao obrigatorios: citacao sem chunk ou sem fonte e exatamente a
    alucinacao juridica que o Principio IV existe para impedir.
    """

    chunk: DocumentChunkResponse
    source: SourceResponse
