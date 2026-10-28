"""T022: cadastro idempotente e transicao atomica de versoes documentais."""

from contextlib import AbstractAsyncContextManager
from datetime import datetime
from re import fullmatch
from typing import Protocol
from uuid import UUID

from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document, DocumentStatus
from app.shared.audit.models import AuditAction, AuditLog


class DocumentStore(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[None]: ...
    async def lock_source(self, source_id: UUID) -> None: ...
    async def list_versions(self, source_id: UUID, logical_name: str) -> list[Document]: ...
    async def get_by_id(self, document_id: UUID) -> Document | None: ...
    async def add(self, document: Document) -> None: ...
    async def save(self, document: Document) -> None: ...
    async def record_audit(self, log: AuditLog) -> None: ...
    async def list_documents(
        self,
        *,
        source_id: UUID | None,
        is_active: bool | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Document], int]: ...
    async def list_chunks(
        self,
        document_id: UUID,
        *,
        article: str | None,
        section: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[DocumentChunk], int]: ...


def validate_document_metadata(title: str, logical_name: str, checksum_sha256: str) -> None:
    """Regras originais de cadastro compartilhadas pelo service e pelo schema."""
    if not title.strip() or len(title) > 255:
        raise ValueError("Titulo deve conter entre 1 e 255 caracteres.")
    if not logical_name.strip() or len(logical_name) > 100:
        raise ValueError("Nome logico deve conter entre 1 e 100 caracteres.")
    if fullmatch(r"[0-9a-fA-F]{64}", checksum_sha256) is None:
        raise ValueError("Checksum deve ser SHA-256 hexadecimal de 64 caracteres.")


class DocumentNotFoundError(LookupError):
    """Documento solicitado nao existe."""


class InvalidDocumentStatusError(ValueError):
    """Apenas documentos prontos ou historicos podem ser ativados."""


class DocumentService:
    def __init__(self, repository: DocumentStore) -> None:
        self._repository = repository

    async def create(
        self,
        *,
        source_id: UUID,
        title: str,
        logical_name: str,
        checksum_sha256: str,
        published_at: datetime | None = None,
        actor_id: UUID | None = None,
    ) -> Document:
        validate_document_metadata(title, logical_name, checksum_sha256)
        checksum_sha256 = checksum_sha256.lower()
        async with self._repository.transaction():
            await self._repository.lock_source(source_id)
            versions = await self._repository.list_versions(source_id, logical_name)
            for existing in versions:
                if existing.checksum_sha256.lower() == checksum_sha256:
                    return existing
            doc = Document(
                source_id=source_id,
                title=title,
                logical_name=logical_name,
                version=max((item.version for item in versions), default=0) + 1,
                checksum_sha256=checksum_sha256,
                published_at=published_at,
                is_active=False,
                status=DocumentStatus.PROCESSING,
            )
            await self._repository.add(doc)
            await self._audit(doc, AuditAction.DOCUMENT_UPLOADED, None, actor_id)
            return doc

    async def list_documents(
        self,
        *,
        source_id: UUID | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Document], int]:
        return await self._repository.list_documents(
            source_id=source_id,
            is_active=is_active,
            offset=offset,
            limit=limit,
        )

    async def list_chunks(
        self,
        document_id: UUID,
        *,
        article: str | None = None,
        section: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[DocumentChunk], int]:
        # Distingue documento inexistente de documento ainda sem chunks.
        if await self._repository.get_by_id(document_id) is None:
            raise DocumentNotFoundError("Documento nao encontrado.")
        return await self._repository.list_chunks(
            document_id,
            article=article,
            section=section,
            offset=offset,
            limit=limit,
        )

    async def activate(self, document_id: UUID, *, actor_id: UUID | None = None) -> Document:
        async with self._repository.transaction():
            doc = await self._locked_document(document_id)
            if doc.status == DocumentStatus.ACTIVE and doc.is_active:
                return doc
            if doc.status not in (DocumentStatus.READY, DocumentStatus.INACTIVE):
                raise InvalidDocumentStatusError("Documento ainda nao esta pronto para ativacao.")
            versions = await self._repository.list_versions(doc.source_id, doc.logical_name)
            for previous in versions:
                if previous.id != doc.id and previous.is_active:
                    before = self._state(previous)
                    previous.is_active = False
                    previous.status = DocumentStatus.INACTIVE
                    await self._repository.save(previous)
                    await self._audit(previous, AuditAction.DOCUMENT_SUPERSEDED, before, actor_id)
            before = self._state(doc)
            doc.is_active = True
            doc.status = DocumentStatus.ACTIVE
            await self._repository.save(doc)
            await self._audit(doc, AuditAction.DOCUMENT_ACTIVATED, before, actor_id)
            return doc

    async def deactivate(self, document_id: UUID, *, actor_id: UUID | None = None) -> Document:
        async with self._repository.transaction():
            doc = await self._locked_document(document_id)
            if not doc.is_active:
                return doc
            before = self._state(doc)
            doc.is_active = False
            doc.status = DocumentStatus.INACTIVE
            await self._repository.save(doc)
            await self._audit(doc, AuditAction.DOCUMENT_DEACTIVATED, before, actor_id)
            return doc

    async def _locked_document(self, document_id: UUID) -> Document:
        doc = await self._repository.get_by_id(document_id)
        if doc is None:
            raise DocumentNotFoundError("Documento nao encontrado.")
        await self._repository.lock_source(doc.source_id)
        # Rele depois de esperar pelo lock: outra operacao pode ter ativado
        # ou desativado o documento enquanto esta requisicao aguardava.
        doc = await self._repository.get_by_id(document_id)
        if doc is None:
            raise DocumentNotFoundError("Documento nao encontrado.")
        return doc

    @staticmethod
    def _state(doc: Document) -> dict[str, str | bool]:
        return {
            "status": str(
                doc.status.value if isinstance(doc.status, DocumentStatus) else doc.status
            ),
            "is_active": doc.is_active,
        }

    async def _audit(
        self,
        doc: Document,
        action: AuditAction,
        before: dict[str, str | bool] | None,
        actor_id: UUID | None,
    ) -> None:
        await self._repository.record_audit(
            AuditLog(
                action=action,
                entity_type="Document",
                entity_id=doc.id,
                actor_id=actor_id,
                details={"before": before, "after": self._state(doc), "version": doc.version},
            )
        )
