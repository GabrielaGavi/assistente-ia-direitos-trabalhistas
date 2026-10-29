"""Persistencia de fontes, necessaria aos endpoints da T023."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.sources.models import Source
from app.sources.service import DuplicateSourceError


class SourceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """A fronteira transacional e escolhida pelo service, como em documentos."""
        async with self._session.begin_nested():
            yield
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def add(self, source: Source) -> None:
        self._session.add(source)
        try:
            await self._session.flush()
        except IntegrityError as error:
            # Somente a constraint conhecida vira conflito de dominio; outros
            # erros continuam visiveis no servidor, sem detalhes no HTTP 500.
            cause = error.orig.__cause__
            if (
                getattr(error.orig, "sqlstate", None) == "23505"
                and getattr(cause, "constraint_name", None) == "sources_short_name_key"
            ):
                raise DuplicateSourceError("Ja existe uma fonte com esta sigla.") from error
            raise

    async def get_by_id(self, source_id: UUID) -> Source | None:
        return await self._session.scalar(select(Source).where(Source.id == source_id))

    async def list_sources(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Source], int]:
        if type(offset) is not int or type(limit) is not int or offset < 0 or limit < 1:
            raise ValueError("Offset deve ser inteiro nao negativo e limit inteiro positivo.")
        total = await self._session.scalar(select(func.count()).select_from(Source))
        items = await self._session.scalars(
            select(Source).order_by(Source.created_at, Source.id).offset(offset).limit(limit)
        )
        return list(items), total or 0
