"""T012: consulta de citacoes e evidencias no PostgreSQL real.

Usa as fixtures transacionais da suite. Executar apenas em banco descartavel:
o conftest global recria as tabelas. Nao depende do app HTTP ainda inexistente.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.models import Citation
from app.citations.repository import CitationRepository
from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document, DocumentStatus
from app.shared.uuid import uuid7
from app.sources.models import Source

pytestmark = pytest.mark.integration

TRECHO = "  Art. 130.   Após cada período...\n\tI - férias;  \n"
URL_OFICIAL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"


@pytest.fixture
async def citacao(session: AsyncSession) -> Citation:
    fonte = Source(
        name="Presidência da República",
        short_name="Planalto",
        base_url="https://www.planalto.gov.br",
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
        chunk_index=0,
        content=TRECHO,
        article="Art. 130",
        section="Capítulo IV",
        paragraph="Inciso I",
        official_url=URL_OFICIAL,
    )
    session.add(chunk)
    await session.flush()
    registro = Citation(
        message_id=uuid7(),
        chunk_id=chunk.id,
        citation_number=1,
        original_quote=TRECHO,
    )
    session.add(registro)
    await session.flush()
    session.expunge_all()
    return registro


async def test_busca_evidencia_completa_por_id(
    session: AsyncSession, citacao: Citation
) -> None:
    evidencia = await CitationRepository(session).get_by_id(citacao.id)

    assert evidencia is not None
    # A evidencia deve estar toda carregada: a serializacao nao pode exigir
    # lazy loading assincrono nem uma sessao ainda aberta.
    session.expunge_all()
    assert evidencia.citation.id == citacao.id
    assert evidencia.citation.message_id == citacao.message_id
    assert evidencia.citation.citation_number == 1
    assert evidencia.citation.original_quote == TRECHO
    assert evidencia.chunk.id == citacao.chunk_id
    assert evidencia.chunk.content == TRECHO
    assert evidencia.chunk.article == "Art. 130"
    assert evidencia.chunk.section == "Capítulo IV"
    assert evidencia.chunk.paragraph == "Inciso I"
    assert evidencia.chunk.official_url == URL_OFICIAL
    assert evidencia.source.id == evidencia.chunk.source_id
    assert evidencia.source.name == "Presidência da República"
    assert evidencia.source.short_name == "Planalto"


async def test_retorna_none_para_id_inexistente(
    session: AsyncSession, citacao: Citation
) -> None:
    # Ha dados no banco: uma consulta sem WHERE nao pode passar neste teste.
    assert await CitationRepository(session).get_by_id(uuid7()) is None


async def test_distingue_citacoes_do_mesmo_chunk(
    session: AsyncSession, citacao: Citation
) -> None:
    outra = Citation(
        message_id=uuid7(),
        chunk_id=citacao.chunk_id,
        citation_number=2,
        original_quote=TRECHO,
    )
    session.add(outra)
    await session.flush()
    session.expunge_all()

    evidencia = await CitationRepository(session).get_by_id(outra.id)

    assert evidencia is not None
    assert evidencia.citation.id == outra.id
    assert evidencia.citation.message_id == outra.message_id
    assert evidencia.citation.citation_number == 2
    assert evidencia.chunk.id == citacao.chunk_id


async def test_consulta_historica_nao_exige_documento_ativo(
    session: AsyncSession, citacao: Citation
) -> None:
    chunk = await session.get(DocumentChunk, citacao.chunk_id)
    assert chunk is not None
    documento = await session.get(Document, chunk.document_id)
    assert documento is not None
    documento.is_active = False
    documento.status = DocumentStatus.INACTIVE
    await session.flush()
    session.expunge_all()

    evidencia = await CitationRepository(session).get_by_id(citacao.id)

    assert evidencia is not None
    assert evidencia.citation.original_quote == TRECHO
    assert evidencia.chunk.id == citacao.chunk_id
    assert evidencia.chunk.official_url == URL_OFICIAL
