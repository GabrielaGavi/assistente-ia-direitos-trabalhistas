"""`DocumentService.add_chunk`/`mark_ready`: fakes, sem banco e sem rede.

Cobrem o fechamento dos dois gaps de ingestao manual: cadastrar um trecho
sem pipeline de PDF/OCR, e liberar o documento para `activate` sem um
worker automatico.
"""

from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from uuid import uuid4

from app.documents.models import Document, DocumentStatus
from app.documents.service import (
    DocumentHasNoChunksError,
    DocumentNotFoundError,
    DocumentService,
    InvalidDocumentStatusError,
)
from app.shared.audit.models import AuditAction


@asynccontextmanager
async def _sem_transacao():
    yield


def _documento(status: DocumentStatus = DocumentStatus.PROCESSING) -> Document:
    return Document(
        id=uuid4(),
        source_id=uuid4(),
        title="CLT",
        logical_name="clt",
        version=1,
        checksum_sha256="a" * 64,
        is_active=False,
        status=status,
    )


def _repository(**overrides) -> SimpleNamespace:
    base = {
        "transaction": _sem_transacao,
        "get_by_id": AsyncMock(return_value=None),
        "save_chunk": AsyncMock(),
        "save": AsyncMock(),
        "record_audit": AsyncMock(),
        "list_chunks": AsyncMock(return_value=([], 0)),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


class TestAddChunk(IsolatedAsyncioTestCase):
    async def test_documento_inexistente_levanta_erro(self) -> None:
        service = DocumentService(_repository(get_by_id=AsyncMock(return_value=None)))

        with self.assertRaises(DocumentNotFoundError):
            await service.add_chunk(
                uuid4(), chunk_index=0, content="Art. 1.", official_url="https://x.org"
            )

    async def test_cadastra_chunk_copiando_source_id_do_documento(self) -> None:
        doc = _documento()
        repository = _repository(get_by_id=AsyncMock(return_value=doc))
        service = DocumentService(repository)

        chunk = await service.add_chunk(
            doc.id,
            chunk_index=0,
            content="Art. 129. Ferias.",
            official_url="https://example.org/clt#art129",
            article="Art. 129",
            actor_id=uuid4(),
        )

        self.assertEqual(chunk.document_id, doc.id)
        self.assertEqual(chunk.source_id, doc.source_id)
        self.assertEqual(chunk.article, "Art. 129")
        repository.save_chunk.assert_awaited_once_with(chunk)
        repository.record_audit.assert_awaited_once()
        (log,) = repository.record_audit.await_args.args
        self.assertEqual(log.action, AuditAction.DOCUMENT_CHUNK_ADDED)
        self.assertEqual(log.details["chunk_index"], 0)


class TestMarkReady(IsolatedAsyncioTestCase):
    async def test_documento_inexistente_levanta_erro(self) -> None:
        service = DocumentService(_repository(get_by_id=AsyncMock(return_value=None)))

        with self.assertRaises(DocumentNotFoundError):
            await service.mark_ready(uuid4())

    async def test_documento_fora_de_processing_levanta_erro(self) -> None:
        doc = _documento(status=DocumentStatus.READY)
        service = DocumentService(_repository(get_by_id=AsyncMock(return_value=doc)))

        with self.assertRaises(InvalidDocumentStatusError):
            await service.mark_ready(doc.id)

    async def test_documento_sem_chunks_levanta_erro(self) -> None:
        doc = _documento()
        repository = _repository(
            get_by_id=AsyncMock(return_value=doc),
            list_chunks=AsyncMock(return_value=([], 0)),
        )
        service = DocumentService(repository)

        with self.assertRaises(DocumentHasNoChunksError):
            await service.mark_ready(doc.id)

    async def test_transiciona_para_ready_com_chunks(self) -> None:
        doc = _documento()
        repository = _repository(
            get_by_id=AsyncMock(return_value=doc),
            list_chunks=AsyncMock(return_value=([object()], 1)),
        )
        service = DocumentService(repository)

        resultado = await service.mark_ready(doc.id, actor_id=uuid4())

        self.assertEqual(resultado.status, DocumentStatus.READY)
        repository.save.assert_awaited_once_with(doc)
        repository.record_audit.assert_awaited_once()
        (log,) = repository.record_audit.await_args.args
        self.assertEqual(log.action, AuditAction.DOCUMENT_READY)
