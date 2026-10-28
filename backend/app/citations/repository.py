"""Consulta de evidencias persistidas para a US1 (T012).

O repositorio recebe a sessao do caso de uso e nao controla a transacao.
Validacao de elegibilidade para NOVAS citacoes pertence ao servico; consultar
uma citacao historica continua permitido quando a norma e desativada.
"""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.models import Citation
from app.documents.chunk_models import DocumentChunk
from app.sources.models import Source

__all__ = ["CitationEvidence", "CitationRepository"]


@dataclass(frozen=True)
class CitationEvidence:
    """Resultado de persistencia, independente dos schemas de resposta HTTP.

    As tres entidades sao carregadas na mesma consulta, sem depender de
    relacionamentos lazy durante a montagem da resposta pelo servico.
    """

    citation: Citation
    chunk: DocumentChunk
    source: Source


class CitationRepository:
    """Acesso de leitura a citacoes e suas evidencias oficiais."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, citation_id: UUID) -> CitationEvidence | None:
        """Retorna a evidencia completa ou None quando a citacao nao existe.

        Nao filtra status ou is_active: isso apagaria o acesso ao historico
        quando uma nova versao da norma substituisse a evidencia original.
        Nao faz commit nem traduz ausencia em erro HTTP.
        """
        consulta = (
            select(Citation, DocumentChunk, Source)
            .join(DocumentChunk, Citation.chunk_id == DocumentChunk.id)
            .join(Source, DocumentChunk.source_id == Source.id)
            .where(Citation.id == citation_id)
        )
        resultado = await self._session.execute(consulta)
        linha = resultado.one_or_none()
        if linha is None:
            return None

        citacao, chunk, fonte = linha
        return CitationEvidence(citation=citacao, chunk=chunk, source=fonte)
