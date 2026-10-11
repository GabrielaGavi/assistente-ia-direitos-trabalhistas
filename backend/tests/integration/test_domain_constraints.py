"""Testes das regras de integridade aplicadas pelo banco.

Os testes unitarios de `test_domain_models.py` verificam que o mapeamento
*declara* as restricoes. Aqui verificamos que o PostgreSQL de fato as *impoe*
-- declaracao e imposicao sao coisas diferentes, e so a segunda protege os
dados.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Tasks: T010, T017, T018, T025
    Requisitos: FR-002, FR-004, FR-006
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.models import Citation
from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document
from app.shared.uuid import uuid7
from app.sources.models import Source

pytestmark = pytest.mark.integration

URL_OFICIAL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"


async def _criar_fonte(session: AsyncSession, sigla: str = "Planalto") -> Source:
    fonte = Source(
        name="Presidência da República",
        short_name=sigla,
        base_url="https://www.planalto.gov.br",
    )
    session.add(fonte)
    await session.flush()
    return fonte


async def _criar_documento(
    session: AsyncSession,
    fonte: Source,
    *,
    versao: int = 1,
    ativo: bool = False,
    nome_logico: str = "clt",
) -> Document:
    documento = Document(
        source_id=fonte.id,
        title="Consolidação das Leis do Trabalho",
        logical_name=nome_logico,
        version=versao,
        checksum_sha256=f"{versao:064d}",
        is_active=ativo,
    )
    session.add(documento)
    await session.flush()
    return documento


class TestVersaoAtivaUnica:
    """FR-004: no maximo uma versao ACTIVE por norma logica."""

    async def test_impede_duas_versoes_ativas_da_mesma_norma(self, session: AsyncSession) -> None:
        """A regra central da feature, imposta por indice unico parcial."""
        fonte = await _criar_fonte(session)
        await _criar_documento(session, fonte, versao=1, ativo=True)

        with pytest.raises(IntegrityError):
            await _criar_documento(session, fonte, versao=2, ativo=True)

    async def test_permite_varias_versoes_inativas(self, session: AsyncSession) -> None:
        """O historico precisa sobreviver: conversas antigas apontam para ele.

        Um UniqueConstraint comum sobre (source_id, logical_name) quebraria
        aqui. O indice parcial existe exatamente para nao quebrar.
        """
        fonte = await _criar_fonte(session)

        await _criar_documento(session, fonte, versao=1, ativo=False)
        await _criar_documento(session, fonte, versao=2, ativo=False)
        await _criar_documento(session, fonte, versao=3, ativo=True)

        await session.flush()

    async def test_permite_uma_ativa_por_norma_diferente(self, session: AsyncSession) -> None:
        """A regra e por norma logica, nao por fonte."""
        fonte = await _criar_fonte(session)

        await _criar_documento(session, fonte, nome_logico="clt", ativo=True)
        await _criar_documento(session, fonte, nome_logico="lei-8036-fgts", ativo=True)

        await session.flush()

    async def test_impede_versao_repetida_da_mesma_norma(self, session: AsyncSession) -> None:
        """FR-003: (fonte, norma, versao) identifica uma redacao unica."""
        fonte = await _criar_fonte(session)
        await _criar_documento(session, fonte, versao=1)

        with pytest.raises(IntegrityError):
            await _criar_documento(session, fonte, versao=1)


class TestIntegridadeReferencial:
    async def test_documento_exige_fonte_existente(self, session: AsyncSession) -> None:
        """FR-002: documento sem fonte oficial nao pode existir."""
        session.add(
            Document(
                source_id=uuid7(),
                title="Norma fantasma",
                logical_name="fantasma",
                checksum_sha256="0" * 64,
            )
        )

        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_citacao_exige_chunk_existente(self, session: AsyncSession) -> None:
        """FR-006: citacao so existe vinculada a um trecho real."""
        session.add(
            Citation(
                message_id=uuid7(),
                chunk_id=uuid7(),
                citation_number=1,
                original_quote="trecho inventado",
            )
        )

        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_apagar_documento_apaga_seus_chunks(self, session: AsyncSession) -> None:
        """SC-002: nao pode sobrar chunk orfao servindo de evidencia."""
        fonte = await _criar_fonte(session)
        documento = await _criar_documento(session, fonte)
        session.add(
            DocumentChunk(
                document_id=documento.id,
                source_id=fonte.id,
                chunk_index=0,
                content="Art. 130...",
                official_url=URL_OFICIAL,
            )
        )
        await session.flush()

        await session.delete(documento)
        await session.flush()

        restantes = await session.execute(
            DocumentChunk.__table__.select().where(DocumentChunk.document_id == documento.id)
        )

        assert restantes.first() is None


class TestUnicidades:
    async def test_sigla_da_fonte_e_unica(self, session: AsyncSession) -> None:
        await _criar_fonte(session, sigla="TST")

        with pytest.raises(IntegrityError):
            await _criar_fonte(session, sigla="TST")

    async def test_indice_do_chunk_e_unico_no_documento(self, session: AsyncSession) -> None:
        fonte = await _criar_fonte(session)
        documento = await _criar_documento(session, fonte)

        for _ in range(2):
            session.add(
                DocumentChunk(
                    document_id=documento.id,
                    source_id=fonte.id,
                    chunk_index=7,
                    content="x",
                    official_url=URL_OFICIAL,
                )
            )

        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_numeracao_da_citacao_e_unica_na_mensagem(self, session: AsyncSession) -> None:
        """FR-007: [1] nao pode aparecer duas vezes na mesma resposta."""
        fonte = await _criar_fonte(session)
        documento = await _criar_documento(session, fonte)
        trecho = DocumentChunk(
            document_id=documento.id,
            source_id=fonte.id,
            chunk_index=0,
            content="Art. 130...",
            official_url=URL_OFICIAL,
        )
        session.add(trecho)
        await session.flush()

        mensagem = uuid7()
        for _ in range(2):
            session.add(
                Citation(
                    message_id=mensagem,
                    chunk_id=trecho.id,
                    citation_number=1,
                    original_quote="Art. 130...",
                )
            )

        with pytest.raises(IntegrityError):
            await session.flush()

    async def test_mesma_numeracao_em_mensagens_diferentes_e_permitida(
        self, session: AsyncSession
    ) -> None:
        """Toda resposta comeca a contar do [1]."""
        fonte = await _criar_fonte(session)
        documento = await _criar_documento(session, fonte)
        trecho = DocumentChunk(
            document_id=documento.id,
            source_id=fonte.id,
            chunk_index=0,
            content="Art. 130...",
            official_url=URL_OFICIAL,
        )
        session.add(trecho)
        await session.flush()

        for _ in range(2):
            session.add(
                Citation(
                    message_id=uuid7(),
                    chunk_id=trecho.id,
                    citation_number=1,
                    original_quote="Art. 130...",
                )
            )

        await session.flush()
