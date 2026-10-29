"""Inicializacao, OpenAPI e validacao HTTP; nao simula persistencia."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.models import User, UserRole
from app.documents.repository import DocumentRepository
from app.main import app
from app.shared.database import get_session
from app.shared.uuid import uuid7

pytestmark = pytest.mark.unit


@pytest.fixture(scope="session", autouse=True)
def _schema() -> None:
    """Estes testes nao acessam banco; integracao esta em tests/integration."""


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    async def unbound_session() -> AsyncIterator[AsyncSession]:
        # Sessao SQLAlchemy real sem bind: qualquer SQL indevido falha.
        # Somente erros de entrada sao testados aqui, nunca respostas de dados.
        async with AsyncSession() as session:
            yield session

    async def admin_falso() -> User:
        # Estes testes verificam o FORMATO da entrada (422 antes de SQL), nao
        # autenticacao -- autenticacao/RBAC tem suite propria
        # (test_auth_service.py). Sobrescrever a dependencia evita que todo
        # request aqui vire 401/403 por falta de token.
        return User(id=uuid7(), email="admin@teste.com", name="Admin", role=UserRole.ADMIN)

    previous = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = unbound_session
    app.dependency_overrides[get_current_user] = admin_falso
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous)


async def test_app_openapi_and_documentation(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert {
        "/api/v1/citations/{id}",
        "/api/v1/sources",
        "/api/v1/sources/{id}",
        "/api/v1/documents",
        "/api/v1/documents/{id}/status",
        "/api/v1/documents/{id}/chunks",
        "/api/v1/documents/{id}/classify",
        "/api/v1/documents/{id}/embed",
        "/api/v1/documents/{id}/file",
        "/api/v1/auth/register",
        "/api/v1/auth/login",
        "/api/v1/auth/me",
        "/api/v1/conversations",
        "/api/v1/conversations/{conversation_id}",
        "/api/v1/conversations/{conversation_id}/messages",
        "/api/v1/health",
    } <= set(paths)
    assert {"post", "get"} == paths["/api/v1/sources"].keys()
    assert {"post", "get"} == paths["/api/v1/documents"].keys()
    assert {"201", "409", "422"} <= paths["/api/v1/sources"]["post"]["responses"].keys()
    assert {"201", "404", "422"} <= paths["/api/v1/documents"]["post"]["responses"].keys()
    params = paths["/api/v1/documents/{id}/chunks"]["get"]["parameters"]
    assert {p["name"] for p in params} == {"id", "article", "section", "offset", "limit"}
    assert (await client.get("/docs")).status_code == 200
    assert (await client.get("/redoc")).status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/sources/invalid",
        "/api/v1/sources?offset=-1",
        "/api/v1/sources?limit=0",
        "/api/v1/documents?source_id=invalid",
        "/api/v1/documents?is_active=invalid",
        "/api/v1/documents?offset=-1",
        "/api/v1/documents?limit=0",
        "/api/v1/documents/invalid/chunks",
        f"/api/v1/documents/{uuid7()}/chunks?article=%20",
        f"/api/v1/documents/{uuid7()}/chunks?section=",
        f"/api/v1/documents/{uuid7()}/chunks?limit=0",
    ],
)
async def test_query_validation_precedes_sql(client: AsyncClient, path: str) -> None:
    assert (await client.get(path)).status_code == 422


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("POST", "/api/v1/sources", {}),
        ("POST", "/api/v1/sources", {"name": "Fonte", "short_name": "F", "base_url": "invalid"}),
        ("POST", "/api/v1/documents", {}),
        (
            "POST",
            "/api/v1/documents",
            {
                "source_id": str(uuid7()),
                "title": "CLT",
                "logical_name": "clt",
                "checksum_sha256": "bad",
            },
        ),
        ("PATCH", f"/api/v1/documents/{uuid7()}/status", {}),
        ("PATCH", "/api/v1/documents/invalid/status", {"is_active": True}),
    ],
)
async def test_body_validation_precedes_sql(
    client: AsyncClient,
    method: str,
    path: str,
    payload: dict,
) -> None:
    assert (await client.request(method, path, json=payload)).status_code == 422


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
        {"section": 1},
    ],
)
async def test_repository_rejects_invalid_filters_before_sql(kwargs: dict) -> None:
    async with AsyncSession() as session:
        with pytest.raises(ValueError):
            await DocumentRepository(session).list_chunks(uuid7(), **kwargs)


async def test_repository_rejects_invalid_document_id_before_sql() -> None:
    async with AsyncSession() as session:
        with pytest.raises(ValueError, match="UUID"):
            await DocumentRepository(session).list_chunks("invalid")
