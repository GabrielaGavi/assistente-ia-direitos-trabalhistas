"""T022: persistencia, auditoria e atomicidade em PostgreSQL real."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import Document, DocumentStatus
from app.shared.audit.models import AuditAction, AuditLog
from app.shared.uuid import uuid7
from app.sources.models import Source

pytestmark = pytest.mark.integration


@pytest.fixture
async def source(session: AsyncSession) -> Source:
    source = Source(name="Fonte de teste", short_name="Teste", base_url="https://example.org")
    session.add(source)
    await session.flush()
    return source


def service(session: AsyncSession):
    from app.documents.repository import DocumentRepository
    from app.documents.service import DocumentService

    return DocumentService(DocumentRepository(session))


async def create(session: AsyncSession, source: Source, checksum: str = "a" * 64):
    return await service(session).create(
        source_id=source.id,
        title="Norma de teste",
        logical_name="teste",
        checksum_sha256=checksum,
    )


async def test_criacao_deduplica_e_incrementa_com_auditoria(session, source):
    first = await create(session, source)
    repeated = await create(session, source)
    second = await create(session, source, "b" * 64)
    assert repeated.id == first.id
    assert (first.version, second.version) == (1, 2)
    assert second.status == DocumentStatus.PROCESSING
    assert second.is_active is False
    logs = (await session.scalars(select(AuditLog))).all()
    assert len(logs) == 2
    assert {log.entity_id for log in logs} == {first.id, second.id}
    assert all(log.action == AuditAction.DOCUMENT_UPLOADED for log in logs)


async def test_substituicao_persiste_historico_e_audita_ator(session, source):
    first = await create(session, source)
    first.status = DocumentStatus.READY
    await session.flush()
    await service(session).activate(first.id)
    second = await create(session, source, "b" * 64)
    second.status = DocumentStatus.READY
    await session.flush()
    actor = uuid7()
    await service(session).activate(second.id, actor_id=actor)
    await session.refresh(first)
    await session.refresh(second)
    assert (first.status, first.is_active) == (DocumentStatus.INACTIVE, False)
    assert (second.status, second.is_active) == (DocumentStatus.ACTIVE, True)
    assert first.checksum_sha256 == "a" * 64
    logs = (await session.scalars(select(AuditLog).where(AuditLog.actor_id == actor))).all()
    assert {log.action for log in logs} == {
        AuditAction.DOCUMENT_SUPERSEDED,
        AuditAction.DOCUMENT_ACTIVATED,
    }
    old = next(log for log in logs if log.entity_id == first.id)
    assert old.details["before"]["is_active"] is True
    assert old.details["after"]["is_active"] is False


async def test_falha_na_auditoria_reverte_toda_substituicao(session, source, monkeypatch):
    from app.documents.repository import DocumentRepository
    from app.documents.service import DocumentService

    first = await create(session, source)
    first.status = DocumentStatus.READY
    await session.flush()
    await service(session).activate(first.id)
    second = await create(session, source, "b" * 64)
    second.status = DocumentStatus.READY
    await session.flush()
    first_id, second_id = first.id, second.id
    repository = DocumentRepository(session)

    async def fail(*args, **kwargs):
        raise RuntimeError("Falha simulada de auditoria")

    monkeypatch.setattr(repository, "record_audit", fail)
    with pytest.raises(RuntimeError, match="Falha simulada"):
        await DocumentService(repository).activate(second_id)
    # O savepoint da operacao falha deve preservar o estado anterior.
    stored_first = await session.get(Document, first_id)
    stored_second = await session.get(Document, second_id)
    assert stored_first.is_active is True
    assert stored_second.status == DocumentStatus.READY
    assert stored_second.is_active is False


async def test_desativacao_e_idempotencia_de_ativacao(session, source):
    doc = await create(session, source)
    doc.status = DocumentStatus.READY
    await session.flush()
    await service(session).activate(doc.id)
    await service(session).activate(doc.id)
    logs = (await session.scalars(select(AuditLog))).all()
    assert len(logs) == 2  # cadastro e uma ativacao
    await service(session).deactivate(doc.id)
    await session.refresh(doc)
    assert (doc.status, doc.is_active) == (DocumentStatus.INACTIVE, False)
    logs = (await session.scalars(select(AuditLog))).all()
    assert len(logs) == 3
    assert any(log.action == AuditAction.DOCUMENT_DEACTIVATED for log in logs)


async def test_fonte_inexistente_nao_cria_documento(session):
    with pytest.raises(LookupError):
        await service(session).create(
            source_id=uuid7(),
            title="Teste",
            logical_name="teste",
            checksum_sha256="a" * 64,
        )
    assert (await session.scalars(select(Document))).all() == []
    assert (await session.scalars(select(AuditLog))).all() == []


@pytest.fixture
async def concurrent_store(engine):
    from sqlalchemy import delete
    from sqlalchemy.ext.asyncio import async_sessionmaker

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        source = Source(
            name="Fonte concorrente", short_name=str(uuid7()), base_url="https://example.org"
        )
        session.add(source)
        await session.commit()
        source_id = source.id
    try:
        yield factory, source_id
    finally:
        async with factory() as session:
            ids = select(Document.id).where(Document.source_id == source_id)
            await session.execute(delete(AuditLog).where(AuditLog.entity_id.in_(ids)))
            await session.execute(delete(Document).where(Document.source_id == source_id))
            await session.execute(delete(Source).where(Source.id == source_id))
            await session.commit()


async def concurrent_create(factory, source_id, checksum):
    async with factory() as session:
        return await service(session).create(
            source_id=source_id,
            title="Concorrencia",
            logical_name="teste",
            checksum_sha256=checksum,
        )


async def test_cadastros_concorrentes_mesmo_checksum_sao_idempotentes(concurrent_store):
    import asyncio

    factory, source_id = concurrent_store
    first, second = await asyncio.wait_for(
        asyncio.gather(
            concurrent_create(factory, source_id, "a" * 64),
            concurrent_create(factory, source_id, "a" * 64),
        ),
        timeout=10,
    )
    assert first.id == second.id
    async with factory() as session:
        docs = (
            await session.scalars(select(Document).where(Document.source_id == source_id))
        ).all()
        assert len(docs) == 1
        logs = (await session.scalars(select(AuditLog).where(AuditLog.entity_id == first.id))).all()
        assert len(logs) == 1


async def test_cadastros_concorrentes_redacoes_distintas_nao_repetem_versao(concurrent_store):
    import asyncio

    factory, source_id = concurrent_store
    docs = await asyncio.wait_for(
        asyncio.gather(
            concurrent_create(factory, source_id, "a" * 64),
            concurrent_create(factory, source_id, "b" * 64),
        ),
        timeout=10,
    )
    assert {doc.version for doc in docs} == {1, 2}
    assert len({doc.id for doc in docs}) == 2


async def test_ativacoes_concorrentes_mantem_uma_unica_versao_ativa(concurrent_store):
    import asyncio

    factory, source_id = concurrent_store
    first = await concurrent_create(factory, source_id, "a" * 64)
    second = await concurrent_create(factory, source_id, "b" * 64)
    async with factory() as session:
        for doc in (
            await session.scalars(select(Document).where(Document.source_id == source_id))
        ).all():
            doc.status = DocumentStatus.READY
        await session.commit()

    async def activate(document_id):
        async with factory() as session:
            await service(session).activate(document_id)

    await asyncio.wait_for(asyncio.gather(activate(first.id), activate(second.id)), timeout=10)
    async with factory() as session:
        docs = (
            await session.scalars(select(Document).where(Document.source_id == source_id))
        ).all()
        assert sum(doc.is_active for doc in docs) == 1
        assert {doc.status for doc in docs} == {DocumentStatus.ACTIVE, DocumentStatus.INACTIVE}
        logs = (
            await session.scalars(
                select(AuditLog).where(
                    AuditLog.entity_id.in_([first.id, second.id]),
                )
            )
        ).all()
        assert len(logs) == 5  # dois cadastros, duas ativacoes, uma substituicao


async def test_versoes_e_checksum_sao_isolados_por_fonte_e_norma(session, source):
    first = await create(session, source)
    other = Source(name="Outra fonte", short_name="Outra", base_url="https://example.org")
    session.add(other)
    await session.flush()
    second = await create(session, other)
    third = await service(session).create(
        source_id=source.id,
        title="Outra norma",
        logical_name="outra",
        checksum_sha256="a" * 64,
    )
    assert len({first.id, second.id, third.id}) == 3
    assert (first.version, second.version, third.version) == (1, 1, 1)


async def test_falha_de_auditoria_na_criacao_nao_deixa_documento(session, source, monkeypatch):
    from app.documents.repository import DocumentRepository
    from app.documents.service import DocumentService

    repository = DocumentRepository(session)

    async def fail(log):
        raise RuntimeError("Auditoria indisponivel")

    monkeypatch.setattr(repository, "record_audit", fail)
    with pytest.raises(RuntimeError, match="Auditoria indisponivel"):
        await DocumentService(repository).create(
            source_id=source.id,
            title="Teste",
            logical_name="teste",
            checksum_sha256="a" * 64,
        )
    assert (await session.scalars(select(Document))).all() == []
    assert (await session.scalars(select(AuditLog))).all() == []


@pytest.mark.parametrize("status", [DocumentStatus.PROCESSING, DocumentStatus.FAILED])
async def test_status_invalido_preserva_versao_atual_e_auditoria(session, source, status):
    first = await create(session, source)
    first.status = DocumentStatus.READY
    await session.flush()
    await service(session).activate(first.id)
    invalid = await create(session, source, "b" * 64)
    invalid.status = status
    await session.flush()
    first_id, invalid_id = first.id, invalid.id
    with pytest.raises(ValueError):
        await service(session).activate(invalid_id)
    first = await session.get(Document, first_id)
    invalid = await session.get(Document, invalid_id)
    assert first.is_active is True
    assert invalid.is_active is False
    assert invalid.status == status
    assert len((await session.scalars(select(AuditLog))).all()) == 3
