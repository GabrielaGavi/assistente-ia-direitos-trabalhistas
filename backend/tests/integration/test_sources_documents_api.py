"""T023: contrato HTTP com app, services e PostgreSQL reais."""

from collections.abc import AsyncIterator
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document, DocumentStatus
from app.main import app
from app.shared.audit.models import AuditLog
from app.shared.database import get_session
from app.shared.uuid import uuid7

pytestmark = pytest.mark.integration


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def test_session() -> AsyncIterator[AsyncSession]:
        yield session

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = test_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


async def create_source(client: AsyncClient, short_name: str = "Planalto") -> dict:
    response = await client.post(
        "/api/v1/sources",
        json={
            "name": "Presidencia da Republica",
            "short_name": short_name,
            "base_url": "https://www.planalto.gov.br",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def create_document(client: AsyncClient, source_id: str, checksum: str = "a" * 64) -> dict:
    response = await client.post(
        "/api/v1/documents",
        json={
            "source_id": source_id,
            "title": "CLT",
            "logical_name": "clt",
            "checksum_sha256": checksum,
            "published_at": "1943-05-01T00:00:00Z",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_source_create_get_list_and_duplicate(client: AsyncClient) -> None:
    source = await create_source(client)
    assert source["created_at"]
    assert (await client.get(f"/api/v1/sources/{source['id']}")).json() == source
    duplicate = await client.post(
        "/api/v1/sources",
        json={
            "name": "Outra",
            "short_name": "Planalto",
            "base_url": "https://example.org",
        },
    )
    assert duplicate.status_code == 409
    assert duplicate.json() == {"detail": "Ja existe uma fonte com esta sigla."}
    other = await create_source(client, "TST")
    page = (await client.get("/api/v1/sources?offset=1&limit=1")).json()
    assert page == {"items": [other], "total": 2}
    assert (await client.get("/api/v1/sources?offset=10")).json() == {"items": [], "total": 2}


async def test_document_versioning_status_and_filtered_pages(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    source = await create_source(client)
    first = await create_document(client, source["id"])
    repeated = await create_document(client, source["id"], "A" * 64)
    assert repeated["id"] == first["id"]
    assert first["version"] == 1 and first["status"] == "PROCESSING"
    assert not first["is_active"]
    invalid = await client.patch(
        f"/api/v1/documents/{first['id']}/status", json={"is_active": True}
    )
    assert invalid.status_code == 409
    doc = await session.get(Document, UUID(first["id"]))
    doc.status = DocumentStatus.READY
    await session.flush()
    assert (
        await client.patch(
            f"/api/v1/documents/{first['id']}/status",
            json={"is_active": True},
        )
    ).json()["is_active"]
    second = await create_document(client, source["id"], "b" * 64)
    assert second["version"] == 2
    doc = await session.get(Document, UUID(second["id"]))
    doc.status = DocumentStatus.READY
    await session.flush()
    activated = await client.patch(
        f"/api/v1/documents/{second['id']}/status",
        json={"is_active": True},
    )
    assert activated.status_code == 200
    other = await create_source(client, "TST")
    await create_document(client, other["id"])
    page = (await client.get(f"/api/v1/documents?source_id={source['id']}&is_active=true")).json()
    assert page["total"] == 1 and page["items"][0]["id"] == second["id"]
    history = (
        await client.get(
            f"/api/v1/documents?source_id={source['id']}&is_active=false",
        )
    ).json()
    assert history["total"] == 1 and history["items"][0]["status"] == "INACTIVE"
    page = (await client.get(f"/api/v1/documents?source_id={source['id']}&offset=1&limit=1")).json()
    assert page["total"] == 2 and page["items"][0]["id"] == second["id"]
    assert (await client.get("/api/v1/documents?offset=100")).json() == {"items": [], "total": 3}
    deactivated = await client.patch(
        f"/api/v1/documents/{second['id']}/status",
        json={"is_active": False},
    )
    assert deactivated.status_code == 200 and not deactivated.json()["is_active"]
    assert await session.scalar(select(func.count()).select_from(AuditLog)) == 7


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/sources?offset=-1",
        "/api/v1/sources?limit=0",
        "/api/v1/sources/invalid",
        "/api/v1/documents?limit=0",
        "/api/v1/documents?offset=-1",
        "/api/v1/documents?source_id=invalid",
        "/api/v1/documents?is_active=invalid",
        "/api/v1/documents/invalid/chunks",
    ],
)
async def test_invalid_queries(client: AsyncClient, path: str) -> None:
    assert (await client.get(path)).status_code == 422


async def test_not_found_and_invalid_bodies(client: AsyncClient) -> None:
    missing = str(uuid7())
    assert (await client.get(f"/api/v1/sources/{missing}")).status_code == 404
    assert (await client.get(f"/api/v1/documents/{missing}/chunks")).status_code == 404
    assert (
        await client.patch(
            f"/api/v1/documents/{missing}/status",
            json={"is_active": True},
        )
    ).status_code == 404
    assert (
        await client.patch(
            f"/api/v1/documents/{missing}/status",
            json={},
        )
    ).status_code == 422
    assert (await client.post("/api/v1/sources", json={})).status_code == 422
    assert (await client.post("/api/v1/documents", json={})).status_code == 422
    response = await client.post(
        "/api/v1/documents",
        json={
            "source_id": missing,
            "title": "CLT",
            "logical_name": "clt",
            "checksum_sha256": "a" * 64,
        },
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Fonte nao encontrada."}
    source = await create_source(client)
    doc = await create_document(client, source["id"])
    assert (await client.get(f"/api/v1/documents/{doc['id']}/chunks")).json() == {
        "items": [],
        "total": 0,
    }


async def test_chunk_endpoint_filters_and_preserves_literal_content(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    source = await create_source(client)
    document = await create_document(client, source["id"])
    for index, section in [(7, "IV"), (2, "V"), (4, "IV")]:
        session.add(
            DocumentChunk(
                document_id=UUID(document["id"]),
                source_id=UUID(source["id"]),
                chunk_index=index,
                content=f"  Artigo {index}\n\t",
                article="Art. 130",
                section=section,
                paragraph="I",
                official_url="https://www.planalto.gov.br/#art130",
                metadata_extra={"internal": "not-public"},
            )
        )
    await session.flush()
    session.expunge_all()
    response = await client.get(
        f"/api/v1/documents/{document['id']}/chunks",
        params={
            "article": "Art. 130",
            "section": "IV",
            "offset": 1,
            "limit": 1,
        },
    )
    assert response.status_code == 200, response.text
    page = response.json()
    assert page["total"] == 2 and len(page["items"]) == 1
    chunk = page["items"][0]
    assert chunk["chunk_index"] == 7 and chunk["content"] == "  Artigo 7\n\t"
    assert chunk["document_id"] == document["id"]
    assert chunk["official_url"] == "https://www.planalto.gov.br/#art130"
    assert "metadata_extra" not in chunk
    assert (
        await client.get(
            f"/api/v1/documents/{document['id']}/chunks",
            params={"article": "Art. 999"},
        )
    ).json() == {"items": [], "total": 0}
