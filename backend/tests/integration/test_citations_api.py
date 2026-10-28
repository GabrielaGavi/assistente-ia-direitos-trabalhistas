"""Contrato HTTP de consulta de citacoes rastreaveis (T009, etapa RED).

Requisitos: US1, FR-007 e preservacao de evidencia historica da feature 001.
O app real e a dependencia de banco sao usados com a sessao isolada da suite;
nao ha mocks de repositorio ou implementacao do endpoint neste teste.

T012-T014 tornam estes cenarios verdes. Executar apenas em
PostgreSQL descartavel: a fixture global da suite recria as tabelas.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.models import Citation
from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document, DocumentStatus
from app.main import app
from app.shared.database import get_session
from app.shared.uuid import uuid7
from app.sources.models import Source

pytestmark = pytest.mark.integration

URL_OFICIAL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"
# Texto de teste com espacos, acentos e quebras para detectar normalizacao.
TRECHO_LITERAL = "  Art. 130.   Após cada período de 12 meses...\n\tI - férias;  \n"


@pytest.fixture
async def client(session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """O HTTP consulta a mesma transacao dos dados, desfeita ao fim do teste."""

    async def sessao_de_teste() -> AsyncIterator[AsyncSession]:
        yield session

    overrides_anteriores = app.dependency_overrides.copy()
    app.dependency_overrides[get_session] = sessao_de_teste
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as cliente:
            yield cliente
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(overrides_anteriores)


@pytest.fixture
async def evidencia(session: AsyncSession) -> tuple[Source, Document, DocumentChunk, Citation]:
    """Persiste a cadeia completa, sem depender dos futuros endpoints de cadastro."""
    fonte = Source(
        name="Presidência da República",
        short_name="Planalto",
        base_url="https://www.planalto.gov.br",
        description="Portal da Legislação",
    )
    session.add(fonte)
    await session.flush()

    documento = Document(
        source_id=fonte.id,
        title="Consolidação das Leis do Trabalho",
        logical_name="clt",
        version=1,
        checksum_sha256="a" * 64,
        status=DocumentStatus.ACTIVE,
        is_active=True,
    )
    session.add(documento)
    await session.flush()

    chunk = DocumentChunk(
        document_id=documento.id,
        source_id=fonte.id,
        chunk_index=42,
        content=TRECHO_LITERAL,
        article="Art. 130",
        section="Capítulo IV - Das Férias Anuais",
        paragraph="Inciso I",
        official_url=URL_OFICIAL,
    )
    session.add(chunk)
    await session.flush()

    citacao = Citation(
        message_id=uuid7(),
        chunk_id=chunk.id,
        citation_number=1,
        original_quote=TRECHO_LITERAL,
    )
    session.add(citacao)
    await session.flush()
    # Obriga o caminho HTTP a recuperar a evidencia persistida, sem depender
    # de objetos ja presentes no identity map da sessao.
    session.expunge_all()
    return fonte, documento, chunk, citacao


async def test_retorna_citacao_com_trecho_literal_e_fonte_oficial(
    client: AsyncClient, evidencia: tuple[Source, Document, DocumentChunk, Citation]
) -> None:
    fonte, documento, chunk, citacao = evidencia

    resposta = await client.get(f"/api/v1/citations/{citacao.id}")

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["id"] == str(citacao.id)
    assert corpo["citation_number"] == 1
    assert corpo["original_quote"] == TRECHO_LITERAL
    assert corpo["chunk"] == {
        "id": str(chunk.id),
        "document_id": str(documento.id),
        "chunk_index": 42,
        "content": TRECHO_LITERAL,
        "article": "Art. 130",
        "section": "Capítulo IV - Das Férias Anuais",
        "paragraph": "Inciso I",
        "official_url": URL_OFICIAL,
    }
    assert corpo["source"]["id"] == str(fonte.id)
    assert corpo["source"]["name"] == fonte.name
    assert corpo["source"]["short_name"] == "Planalto"
    assert corpo["source"]["base_url"] == fonte.base_url
    assert corpo["source"]["description"] == fonte.description
    assert corpo["source"]["created_at"]


async def test_preserva_consulta_historica_apos_substituir_versao(
    client: AsyncClient,
    session: AsyncSession,
    evidencia: tuple[Source, Document, DocumentChunk, Citation],
) -> None:
    """Inativar impede novas evidencias, mas nao apaga citacoes anteriores."""
    fonte, documento, chunk, citacao = evidencia
    anterior = await session.get(Document, documento.id)
    assert anterior is not None
    anterior.is_active = False
    anterior.status = DocumentStatus.INACTIVE
    await session.flush()
    session.add(
        Document(
            source_id=fonte.id,
            title=documento.title,
            logical_name=documento.logical_name,
            version=2,
            checksum_sha256="b" * 64,
            status=DocumentStatus.ACTIVE,
            is_active=True,
        )
    )
    await session.flush()
    session.expunge_all()

    resposta = await client.get(f"/api/v1/citations/{citacao.id}")

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["id"] == str(citacao.id)
    assert corpo["original_quote"] == TRECHO_LITERAL
    assert corpo["chunk"]["id"] == str(chunk.id)
    assert corpo["chunk"]["document_id"] == str(documento.id)
    assert corpo["chunk"]["content"] == TRECHO_LITERAL
    assert corpo["chunk"]["official_url"] == URL_OFICIAL


async def test_retorna_404_para_citacao_inexistente(client: AsyncClient) -> None:
    resposta = await client.get(f"/api/v1/citations/{uuid7()}")

    assert resposta.status_code == 404, resposta.text


async def test_retorna_422_para_identificador_invalido(client: AsyncClient) -> None:
    resposta = await client.get("/api/v1/citations/nao-e-um-uuid")

    assert resposta.status_code == 422, resposta.text


async def test_retorna_500_sem_expor_link_invalido(
    client: AsyncClient,
    session: AsyncSession,
    evidencia: tuple[Source, Document, DocumentChunk, Citation],
) -> None:
    _, _, chunk, citacao = evidencia
    trecho = await session.get(DocumentChunk, chunk.id)
    assert trecho is not None
    trecho.official_url = "file:///evidencia-interna"
    await session.flush()

    resposta = await client.get(f"/api/v1/citations/{citacao.id}")

    assert resposta.status_code == 500, resposta.text
    assert resposta.json() == {"detail": "A citacao possui um link oficial invalido."}


async def test_openapi_documenta_consulta_e_erros(client: AsyncClient) -> None:
    resposta = await client.get("/openapi.json")
    assert resposta.status_code == 200
    operacao = resposta.json()["paths"]["/api/v1/citations/{id}"]["get"]
    assert {"200", "404", "422", "500"} <= operacao["responses"].keys()
    assert operacao["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/CitationDetailResponse"
    }
