"""Repositorio de persistencia para fontes juridicas oficiais (T021).

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T021
    Requisito: FR-001
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.sources.models import Source

__all__ = ["SourceRepository"]


class SourceRepository:
    """Acesso ao banco de dados para a entidade Source."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, source_id: UUID) -> Source | None:
        """Busca uma fonte pelo identificador unico."""
        consulta = select(Source).where(Source.id == source_id)
        resultado = await self._session.execute(consulta)
        return resultado.scalar_one_or_none()

    async def get_by_short_name(self, short_name: str) -> Source | None:
        """Busca uma fonte pela sigla unica."""
        consulta = select(Source).where(Source.short_name == short_name)
        resultado = await self._session.execute(consulta)
        return resultado.scalar_one_or_none()

    async def list_all(self) -> list[Source]:
        """Lista todas as fontes cadastradas ordenadas por nome."""
        consulta = select(Source).order_by(Source.name.asc())
        resultado = await self._session.execute(consulta)
        return list(resultado.scalars().all())

    async def create(self, source: Source) -> Source:
        """Persiste uma nova fonte na sessao ativa.
        
        Nao executa commit; a transacao e delimitada pelo caso de uso.
        """
        self._session.add(source)
        await self._session.flush()
        await self._session.refresh(source)
        return source