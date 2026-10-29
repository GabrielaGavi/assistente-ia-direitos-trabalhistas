"""T022/T027: documentos, transacoes e consulta estruturada de chunks."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document
from app.documents.service import DuplicateChunkIndexError
from app.shared.audit.models import AuditLog
from app.sources.models import Source
from app.sources.service import SourceNotFoundError


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
            raise SourceNotFoundError(source_id)

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

    async def save_chunk(self, chunk: DocumentChunk) -> None:
        self._session.add(chunk)
        try:
            await self._session.flush()
        except IntegrityError as error:
            cause = error.orig.__cause__
            if (
                getattr(error.orig, "sqlstate", None) == "23505"
                and getattr(cause, "constraint_name", None) == "uq_chunk_document_index"
            ):
                raise DuplicateChunkIndexError(
                    f"Chunk {chunk.chunk_index} ja existe para este documento."
                ) from error
            raise

    async def search_similar_chunks(
        self,
        *,
        embedding: list[float],
        limit: int = 5,
        source_id: UUID | None = None,
    ) -> list[DocumentChunk]:
        """Os `limit` chunks mais proximos de `embedding` por distancia de cosseno.

        Restrito a chunks com embedding gerado e a documentos ativos: um
        documento ainda em `PROCESSING`/`READY` ou ja `INACTIVE` nunca deve
        fundamentar uma resposta (ver OVERVIEW TECNICO.md, secao 26).
        """
        filtros = [DocumentChunk.embedding.is_not(None), Document.is_active.is_(True)]
        if source_id is not None:
            filtros.append(DocumentChunk.source_id == source_id)

        resultado = await self._session.scalars(
            select(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(*filtros)
            .order_by(DocumentChunk.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return list(resultado)

    async def list_documents(
        self,
        *,
        source_id: UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Document], int]:
        if type(offset) is not int or type(limit) is not int or offset < 0 or limit < 1:
            raise ValueError("Offset deve ser inteiro nao negativo e limit inteiro positivo.")
        filters = []
        if source_id is not None:
            filters.append(Document.source_id == source_id)
        if is_active is not None:
            filters.append(Document.is_active == is_active)
        total = await self._session.scalar(
            select(func.count()).select_from(Document).where(*filters)
        )
        items = await self._session.scalars(
            select(Document)
            .where(*filters)
            .order_by(Document.created_at, Document.id)
            .offset(offset)
            .limit(limit)
        )
        return list(items), total or 0

    async def list_chunks(
        self,
        document_id: UUID,
        *,
        article: str | None = None,
        section: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[DocumentChunk], int]:
        """Pagina de chunks e total filtrado, por igualdade de artigo/secao.

        Preserva os IDs de documento/fonte e todos os metadados do modelo.
        A constraint (document_id, chunk_index) torna a ordem deterministica.
        Executa duas consultas, sem lazy loads, e nao carrega documentos.
        Documento ausente ou sem resultados retorna ([], 0); o service e
        responsavel por distinguir ausencia do documento no contrato HTTP.
        """
        if not isinstance(document_id, UUID):
            raise ValueError("document_id deve ser um UUID.")
        if type(offset) is not int or type(limit) is not int or offset < 0 or limit < 1:
            raise ValueError("Offset deve ser inteiro nao negativo e limit inteiro positivo.")
        for name, value, maximum in (("article", article, 50), ("section", section, 100)):
            if value is not None and (
                not isinstance(value, str) or not value.strip() or len(value) > maximum
            ):
                raise ValueError(f"{name} deve conter entre 1 e {maximum} caracteres.")

        filters = [DocumentChunk.document_id == document_id]
        if article is not None:
            filters.append(DocumentChunk.article == article)
        if section is not None:
            filters.append(DocumentChunk.section == section)
        total = await self._session.scalar(
            select(func.count()).select_from(DocumentChunk).where(*filters)
        )
        items = await self._session.scalars(
            select(DocumentChunk)
            .where(*filters)
            .order_by(DocumentChunk.chunk_index)
            .offset(offset)
            .limit(limit)
        )
        return list(items), total or 0
