"""T027: filtros estruturados e paginacao no PostgreSQL, sem mocks."""

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document
from app.documents.repository import DocumentRepository
from app.shared.uuid import uuid7
from app.sources.models import Source

pytestmark = pytest.mark.integration


@pytest.fixture
async def documents(session: AsyncSession) -> list[Document]:
    sources = [
        Source(name=name, short_name=name, base_url="https://example.org")
        for name in ("Planalto", "TST")
    ]
    session.add_all(sources)
    await session.flush()
    docs = [
        Document(source_id=source.id, title="CLT", logical_name="clt", checksum_sha256="a" * 64)
        for source in sources
    ]
    session.add_all(docs)
    await session.flush()
    for doc in docs:
        for index, article, section in [
            (9, "Art. 130", "IV"),
            (1, "Art. 129", "IV"),
            (4, "Art. 130", "V"),
        ]:
            session.add(
                DocumentChunk(
                    document_id=doc.id,
                    source_id=doc.source_id,
                    chunk_index=index,
                    content=f"  Texto literal {index}\n",
                    article=article,
                    section=section,
                    paragraph="I",
                    official_url="https://example.org/norma#art130",
                    page_number=3,
                    metadata_extra={"origin": "pdf"},
                )
            )
    await session.flush()
    session.expunge_all()
    return docs


async def test_filter_order_and_source_association(
    session: AsyncSession,
    documents: list[Document],
) -> None:
    repo = DocumentRepository(session)
    items, total = await repo.list_chunks(documents[0].id)
    assert total == 3
    assert [item.chunk_index for item in items] == [1, 4, 9]
    assert all(item.document_id == documents[0].id for item in items)
    assert all(item.source_id == documents[0].source_id for item in items)
    assert items[1].content == "  Texto literal 4\n"
    assert items[1].page_number == 3 and items[1].metadata_extra == {"origin": "pdf"}
    items, total = await repo.list_chunks(documents[0].id, article="Art. 130")
    assert total == 2 and [item.chunk_index for item in items] == [4, 9]
    items, total = await repo.list_chunks(documents[0].id, section="IV")
    assert total == 2 and [item.chunk_index for item in items] == [1, 9]
    items, total = await repo.list_chunks(documents[0].id, article="Art. 130", section="IV")
    assert total == 1 and items[0].chunk_index == 9


async def test_pages_and_empty_results(session: AsyncSession, documents: list[Document]) -> None:
    repo = DocumentRepository(session)
    items, total = await repo.list_chunks(documents[0].id, article="Art. 130", offset=1, limit=1)
    assert total == 2 and items[0].chunk_index == 9
    assert await repo.list_chunks(documents[0].id, offset=100) == ([], 3)
    assert await repo.list_chunks(uuid7()) == ([], 0)
    assert await repo.list_chunks(documents[0].id, article="130") == ([], 0)
    assert await repo.list_chunks(documents[0].id, article="' OR 1=1 --") == ([], 0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"offset": -1},
        {"limit": 0},
        {"limit": -1},
        {"offset": 1.5},
        {"limit": True},
        {"article": ""},
        {"article": " "},
        {"article": "x" * 51},
        {"section": "x" * 101},
    ],
)
async def test_invalid_parameters(session: AsyncSession, kwargs: dict) -> None:
    with pytest.raises(ValueError):
        await DocumentRepository(session).list_chunks(uuid7(), **kwargs)


async def test_no_n_plus_one(session: AsyncSession, documents: list[Document]) -> None:
    statements = []
    connection = await session.connection()

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(connection.sync_connection, "before_cursor_execute", record)
    try:
        items, total = await DocumentRepository(session).list_chunks(documents[0].id)
        assert total == 3
        assert all(item.content and item.source_id for item in items)
    finally:
        event.remove(connection.sync_connection, "before_cursor_execute", record)
    assert len(statements) == 2
