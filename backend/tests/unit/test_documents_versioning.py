"""T015: contrato de comportamento para DocumentService (T022).

FR-003/FR-004 e US2: sequencia por fonte/norma, checksum idempotente,
ativacao exclusiva e preservacao do historico. Nao duplica testes do indice
PostgreSQL em tests/integration/test_domain_constraints.py.

Interface da T022: DocumentService(repository), create(**dados)
e activate(document_id). Repositorio: list_versions(source_id, logical_name),
get_by_id(document_id), add(document), save(document). Os testes verificam
estado observavel, sem exigir ordem ou quantidade de chamadas.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from copy import deepcopy
from hashlib import sha256
from unittest import IsolatedAsyncioTestCase
from uuid import UUID

import pytest

from app.documents.models import Document, DocumentStatus
from app.shared.audit.models import AuditLog
from app.shared.uuid import uuid7

pytestmark = pytest.mark.unit


@pytest.fixture(scope="session", autouse=True)
def _schema() -> None:
    """Substitui apenas neste modulo a fixture global que abre PostgreSQL."""


class MemoryDocumentRepository:
    """Armazena documentos sem decidir versao, deduplicacao ou ativacao.

    Copias impedem que uma mutacao nao persistida pareca uma gravacao valida.
    Nao simula constraints ou transacoes: isso exige teste em PostgreSQL.
    """

    def __init__(self, documents: list[Document]) -> None:
        self.documents = {document.id: deepcopy(document) for document in documents}
        self.audit_logs: list[AuditLog] = []

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        before = deepcopy(self.documents), deepcopy(self.audit_logs)
        try:
            yield
        except Exception:
            self.documents, self.audit_logs = before
            raise

    async def lock_source(self, source_id: UUID) -> None:
        """Concorrencia entre sessoes e verificada no PostgreSQL real."""

    async def record_audit(self, log: AuditLog) -> None:
        self.audit_logs.append(deepcopy(log))

    async def list_versions(self, source_id: UUID, logical_name: str) -> list[Document]:
        return [
            deepcopy(document)
            for document in self.documents.values()
            if document.source_id == source_id and document.logical_name == logical_name
        ]

    async def get_by_id(self, document_id: UUID) -> Document | None:
        document = self.documents.get(document_id)
        return deepcopy(document) if document is not None else None

    async def add(self, document: Document) -> None:
        if document.id is None:
            document.id = uuid7()
        self.documents[document.id] = deepcopy(document)

    async def save(self, document: Document) -> None:
        self.documents[document.id] = deepcopy(document)


def document(
    source_id: UUID,
    *,
    version: int = 1,
    logical_name: str = "clt",
    status: DocumentStatus = DocumentStatus.INACTIVE,
    checksum: str | None = None,
) -> Document:
    return Document(
        id=uuid7(),
        source_id=source_id,
        title="Documento de teste",
        logical_name=logical_name,
        version=version,
        checksum_sha256=checksum or sha256(f"{logical_name}-v{version}".encode()).hexdigest(),
        status=status,
        is_active=status == DocumentStatus.ACTIVE,
    )


class TestDocumentsVersioning(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.source_id = uuid7()
        self.repository = MemoryDocumentRepository([])

    def service(self):
        # Import tardio manteve a coleta disponivel durante a etapa RED.
        from app.documents.service import DocumentService

        return DocumentService(self.repository)

    async def create(self, *, logical_name: str = "clt", checksum: str = "a" * 64):
        return await self.service().create(
            source_id=self.source_id,
            title="Documento de teste",
            logical_name=logical_name,
            checksum_sha256=checksum,
        )

    async def test_primeira_versao_comeca_em_um_e_inativa(self) -> None:
        created = await self.create()
        stored = self.repository.documents[created.id]
        self.assertEqual(stored.version, 1)
        self.assertFalse(stored.is_active)
        self.assertEqual(stored.status, DocumentStatus.PROCESSING)
        self.assertEqual(stored.checksum_sha256, "a" * 64)

    async def test_nova_redacao_incrementa_maior_versao_sem_alterar_historico(self) -> None:
        previous = document(self.source_id, version=3, status=DocumentStatus.ACTIVE)
        first = document(self.source_id, version=1)
        self.repository = MemoryDocumentRepository([previous, first])
        before = dict(previous.__dict__)

        created = await self.create()

        self.assertEqual(self.repository.documents[created.id].version, 4)
        stored = self.repository.documents[previous.id]
        for field in ("title", "version", "checksum_sha256", "status", "is_active"):
            self.assertEqual(getattr(stored, field), before[field])
        self.assertEqual(len(self.repository.documents), 3)

    async def test_sequencia_e_independente_por_norma(self) -> None:
        self.repository = MemoryDocumentRepository([document(self.source_id, version=8)])
        created = await self.create(logical_name="fgts")
        self.assertEqual(self.repository.documents[created.id].version, 1)

    async def test_sequencia_e_independente_por_fonte(self) -> None:
        self.repository = MemoryDocumentRepository([document(uuid7(), version=8)])
        created = await self.create()
        self.assertEqual(self.repository.documents[created.id].version, 1)

    async def test_checksum_repetido_retorna_versao_existente_sem_criar_ou_ativar(self) -> None:
        existing = document(self.source_id, checksum="a" * 64)
        self.repository = MemoryDocumentRepository([existing])
        created = await self.create()
        self.assertEqual(created.id, existing.id)
        self.assertEqual(len(self.repository.documents), 1)
        self.assertFalse(self.repository.documents[existing.id].is_active)

    async def test_checksum_historico_nao_cria_versao_redundante(self) -> None:
        old = document(self.source_id, checksum="a" * 64)
        active = document(self.source_id, version=2, status=DocumentStatus.ACTIVE)
        self.repository = MemoryDocumentRepository([old, active])
        created = await self.create()
        self.assertEqual(created.id, old.id)
        self.assertEqual(len(self.repository.documents), 2)
        self.assertTrue(self.repository.documents[active.id].is_active)

    async def test_mesmo_checksum_em_outra_norma_nao_deduplica(self) -> None:
        other = document(self.source_id, logical_name="fgts", checksum="a" * 64)
        self.repository = MemoryDocumentRepository([other])
        created = await self.create()
        self.assertNotEqual(created.id, other.id)
        self.assertEqual(len(self.repository.documents), 2)

    async def test_mesmo_checksum_em_outra_fonte_nao_deduplica(self) -> None:
        other = document(uuid7(), checksum="a" * 64)
        self.repository = MemoryDocumentRepository([other])
        created = await self.create()
        self.assertNotEqual(created.id, other.id)
        self.assertEqual(len(self.repository.documents), 2)

    async def test_ativacao_ready_desativa_anterior_e_preserva_outras_normas_e_fontes(self) -> None:
        old = document(self.source_id, version=2, status=DocumentStatus.ACTIVE)
        ready = document(self.source_id, version=3, status=DocumentStatus.READY)
        history = document(self.source_id, version=1)
        other_law = document(self.source_id, logical_name="fgts", status=DocumentStatus.ACTIVE)
        other_source = document(uuid7(), status=DocumentStatus.ACTIVE)
        self.repository = MemoryDocumentRepository([old, ready, history, other_law, other_source])

        await self.service().activate(ready.id)

        stored = self.repository.documents
        self.assertTrue(stored[ready.id].is_active)
        self.assertEqual(stored[ready.id].status, DocumentStatus.ACTIVE)
        self.assertFalse(stored[old.id].is_active)
        self.assertEqual(stored[old.id].status, DocumentStatus.INACTIVE)
        self.assertEqual(stored[old.id].checksum_sha256, old.checksum_sha256)
        self.assertEqual(stored[old.id].version, old.version)
        self.assertFalse(stored[history.id].is_active)
        self.assertTrue(stored[other_law.id].is_active)
        self.assertTrue(stored[other_source.id].is_active)
        versions = await self.repository.list_versions(self.source_id, "clt")
        self.assertEqual(sum(item.is_active for item in versions), 1)
        self.assertEqual(len(stored), 5)

    async def test_ativacao_sem_anterior_ativa(self) -> None:
        ready = document(self.source_id, status=DocumentStatus.READY)
        self.repository = MemoryDocumentRepository([ready])
        await self.service().activate(ready.id)
        self.assertTrue(self.repository.documents[ready.id].is_active)
        self.assertEqual(self.repository.documents[ready.id].status, DocumentStatus.ACTIVE)

    async def test_processing_nao_pode_ser_ativado(self) -> None:
        await self.check_invalid_activation(DocumentStatus.PROCESSING)

    async def test_failed_nao_pode_ser_ativado(self) -> None:
        await self.check_invalid_activation(DocumentStatus.FAILED)

    async def check_invalid_activation(self, status: DocumentStatus) -> None:
        old = document(self.source_id, status=DocumentStatus.ACTIVE)
        invalid = document(self.source_id, version=2, status=status)
        self.repository = MemoryDocumentRepository([old, invalid])
        service = self.service()
        with self.assertRaises(ValueError):
            await service.activate(invalid.id)
        self.assertTrue(self.repository.documents[old.id].is_active)
        self.assertEqual(self.repository.documents[old.id].status, DocumentStatus.ACTIVE)
        self.assertFalse(self.repository.documents[invalid.id].is_active)
        self.assertEqual(self.repository.documents[invalid.id].status, status)

    async def test_ativacao_inexistente_nao_altera_versao_atual(self) -> None:
        old = document(self.source_id, status=DocumentStatus.ACTIVE)
        self.repository = MemoryDocumentRepository([old])
        service = self.service()
        with self.assertRaises(LookupError):
            await service.activate(uuid7())
        self.assertTrue(self.repository.documents[old.id].is_active)
        self.assertEqual(self.repository.documents[old.id].status, DocumentStatus.ACTIVE)
