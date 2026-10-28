"""Regras de negocio e gestao de fontes juridicas oficiais (T021).

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T021
    Requisito: FR-001
"""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.sources.models import Source
from app.sources.schemas import SourceCreate, SourceResponse

__all__ = [
    "SourceAlreadyExistsError",
    "SourceNotFoundError",
    "SourceRepositoryProtocol",
    "SourceService",
]


class SourceRepositoryProtocol(Protocol):
    """Porta de persistencia para a entidade Source."""

    async def get_by_id(self, source_id: UUID) -> Source | None: ...
    async def get_by_short_name(self, short_name: str) -> Source | None: ...
    async def list_all(self) -> list[Source]: ...
    async def create(self, source: Source) -> Source: ...


class SourceNotFoundError(LookupError):
    """Ausencia da fonte; o router traduz para HTTP 404."""

    def __init__(self, source_id: UUID) -> None:
        self.source_id = source_id
        super().__init__(f"Fonte {source_id} nao encontrada.")


class SourceAlreadyExistsError(ValueError):
    """Sigla duplicada; o router traduz para HTTP 409 ou 422."""

    def __init__(self, short_name: str) -> None:
        self.short_name = short_name
        super().__init__(f"Fonte com a sigla '{short_name}' ja esta cadastrada.")


class SourceService:
    """Orquestra validacoes de regras de negocio e montagem de schemas."""

    def __init__(self, repository: SourceRepositoryProtocol) -> None:
        self._repository = repository

    async def get_by_id(self, source_id: UUID) -> SourceResponse:
        """Recupera uma fonte pelo identificador unico."""
        fonte = await self._repository.get_by_id(source_id)
        if fonte is None:
            raise SourceNotFoundError(source_id)
        return SourceResponse.model_validate(fonte)

    async def list_all(self) -> list[SourceResponse]:
        """Lista todas as fontes cadastradas."""
        fontes = await self._repository.list_all()
        return [SourceResponse.model_validate(f) for f in fontes]

    async def create(self, data: SourceCreate) -> SourceResponse:
        """Cadastra uma nova fonte garantindo unicidade do short_name."""
        existente = await self._repository.get_by_short_name(data.short_name)
        if existente is not None:
            raise SourceAlreadyExistsError(data.short_name)

        nova_fonte = Source(
            name=data.name,
            short_name=data.short_name,
            base_url=str(data.base_url),
            description=data.description,
        )
        fonte_criada = await self._repository.create(nova_fonte)
        return SourceResponse.model_validate(fonte_criada)
        