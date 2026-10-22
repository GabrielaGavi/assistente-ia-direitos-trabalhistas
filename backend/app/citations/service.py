"""T013: detalhe de citacoes e resolucao de links oficiais cadastrados.

Consulta historica independe da vigencia atual do documento. A validacao de
elegibilidade de NOVAS evidencias pertence ao fluxo de criacao de citacoes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol
from uuid import UUID

from pydantic import HttpUrl, TypeAdapter, ValidationError

from app.citations.schemas import CitationDetailResponse
from app.documents.chunk_schemas import DocumentChunkResponse
from app.sources.schemas import SourceResponse

if TYPE_CHECKING:
    from app.citations.repository import CitationEvidence

__all__ = [
    "CitationNotFoundError",
    "CitationReader",
    "CitationService",
    "InvalidCitationLinkError",
]

_HTTP_URL = TypeAdapter(HttpUrl)


class CitationReader(Protocol):
    """Porta de leitura implementada por CitationRepository."""

    async def get_by_id(self, citation_id: UUID) -> CitationEvidence | None: ...


class CitationNotFoundError(LookupError):
    """Ausencia de citacao; o router decide a representacao HTTP do erro."""

    def __init__(self, citation_id: UUID) -> None:
        self.citation_id = citation_id
        super().__init__(f"Citacao {citation_id} nao encontrada.")


class InvalidCitationLinkError(ValueError):
    """A evidencia armazenada nao possui um link HTTP(S) absoluto valido."""


class CitationService:
    """Monta o detalhe sem acessar rede, inventar links ou controlar transacoes."""

    def __init__(self, repository: CitationReader) -> None:
        self._repository = repository

    async def get_by_id(self, citation_id: UUID) -> CitationDetailResponse:
        """Resolve a citacao e sua fonte local, inclusive para normas inativas.

        A URL do chunk e a referencia especifica ja cadastrada. A URL raiz
        institucional continua em source.base_url; nao a usamos como fallback
        para um link ausente, pois ela nao identifica o trecho citado.
        """
        evidencia = await self._repository.get_by_id(citation_id)
        if evidencia is None:
            raise CitationNotFoundError(citation_id)

        chunk = DocumentChunkResponse.model_validate(evidencia.chunk)
        self._validar_link(chunk.official_url)
        return CitationDetailResponse(
            id=evidencia.citation.id,
            citation_number=evidencia.citation.citation_number,
            original_quote=evidencia.citation.original_quote,
            chunk=chunk,
            source=SourceResponse.model_validate(evidencia.source),
        )

    @staticmethod
    def _validar_link(url: str) -> None:
        # Valida sem substituir pela forma normalizada do Pydantic: ancora,
        # query e grafia da URL arquivada permanecem exatamente como gravadas.
        try:
            _HTTP_URL.validate_python(url)
        except ValidationError as erro:
            raise InvalidCitationLinkError(
                "A citacao nao possui um link oficial HTTP(S) absoluto valido."
            ) from erro
