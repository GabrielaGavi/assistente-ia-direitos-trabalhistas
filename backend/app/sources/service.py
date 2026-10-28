"""Casos de uso minimos de fontes necessarios a integracao da T023."""

from contextlib import AbstractAsyncContextManager
from typing import Protocol
from uuid import UUID

from app.sources.models import Source
from app.sources.schemas import SourceCreate, SourceResponse


class SourceNotFoundError(LookupError):
    """Fonte solicitada nao existe."""

    def __init__(self, source_id: UUID) -> None:
        self.source_id = source_id
        super().__init__(f"Fonte {source_id} nao encontrada.")


class DuplicateSourceError(ValueError):
    """A sigla ja identifica outra fonte oficial."""


class SourceAlreadyExistsError(ValueError):
    def __init__(self, short_name: str) -> None:
        self.short_name = short_name
        super().__init__(f"Fonte com a sigla '{short_name}' ja esta cadastrada.")


class SourceStore(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]: ...
    async def add(self, source: Source) -> None: ...
    async def get_by_id(self, source_id: UUID) -> Source | None: ...
    async def list_sources(self, *, offset: int, limit: int) -> tuple[list[Source], int]: ...
    async def get_by_short_name(self, short_name: str) -> Source | None: ...
    async def list_all(self) -> list[Source]: ...
    async def create(self, source: Source) -> Source: ...


SourceRepositoryProtocol = SourceStore


class SourceService:
    def __init__(self, repository: SourceStore) -> None:
        self._repository = repository

    async def create_source(
        self,
        *,
        name: str,
        short_name: str,
        base_url: str,
        description: str | None = None,
    ) -> Source:
        source = Source(
            name=name, short_name=short_name, base_url=base_url, description=description
        )
        async with self._repository.transaction():
            await self._repository.add(source)
        return source

    async def get_source(self, source_id: UUID) -> Source:
        source = await self._repository.get_by_id(source_id)
        if source is None:
            raise SourceNotFoundError(source_id)
        return source

    async def list_sources(self, *, offset: int = 0, limit: int = 20) -> tuple[list[Source], int]:
        return await self._repository.list_sources(offset=offset, limit=limit)

    async def get_by_id(self, source_id: UUID) -> SourceResponse:
        return SourceResponse.model_validate(await self.get_source(source_id))

    async def list_all(self) -> list[SourceResponse]:
        return [
            SourceResponse.model_validate(source) for source in await self._repository.list_all()
        ]

    async def create(self, data: SourceCreate) -> SourceResponse:
        if await self._repository.get_by_short_name(data.short_name) is not None:
            raise SourceAlreadyExistsError(data.short_name)
        source = Source(**data.model_dump())
        return SourceResponse.model_validate(await self._repository.create(source))
