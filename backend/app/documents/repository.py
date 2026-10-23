"""T022: persistencia de documentos, lock e unidade de trabalho PostgreSQL."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document
from app.shared.audit.models import AuditLog
from app.sources.models import Source


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        """O service confirma documento e auditoria na mesma transacao.

        O savepoint reverte a operacao em caso de erro de dominio ou escrita.
        A sessao deve ser dedicada ao caso de uso, pois o sucesso faz commit.
        """
        async with self._session.begin_nested():
            yield
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def lock_source(self, source_id: UUID) -> None:
        # Uma linha estavel existe mesmo antes da primeira versao. O lock dura
        # ate o commit e serializa cadastro e ativacao, inclusive norma nova.
        source = await self._session.scalar(
            select(Source.id).where(Source.id == source_id).with_for_update()
        )
        if source is None:
            raise LookupError("Fonte nao encontrada.")

    async def list_versions(self, source_id: UUID, logical_name: str) -> list[Document]:
        result = await self._session.scalars(
            select(Document)
            .where(Document.source_id == source_id, Document.logical_name == logical_name)
            .order_by(Document.version.desc())
            .execution_options(populate_existing=True)
        )
        return list(result)

    async def get_by_id(self, document_id: UUID) -> Document | None:
        return await self._session.scalar(
            select(Document)
            .where(Document.id == document_id)
            .execution_options(populate_existing=True)
        )

    async def add(self, document: Document) -> None:
        self._session.add(document)
        await self._session.flush()

    async def save(self, document: Document) -> None:
        self._session.add(document)
        # Desativa a versao anterior antes de ativar a seguinte, respeitando
        # o indice unico parcial em cada comando SQL, nao apenas no commit.
        await self._session.flush()

    async def record_audit(self, log: AuditLog) -> None:
        self._session.add(log)
        await self._session.flush()
