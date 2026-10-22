"""T013: regras de consulta e links, sem banco ou aplicacao HTTP.

TestCase e AsyncMock da biblioteca padrao tambem sao coletados pelo pytest.
Os doubles representam o contrato de leitura do repositorio, nao o ORM.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock
from uuid import uuid4

from app.citations.service import (
    CitationNotFoundError,
    CitationService,
    InvalidCitationLinkError,
)

URL_OFICIAL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"
TRECHO = "  Art. 130.   Após cada período...\n\tI - férias;  \n"


class TestCitationService(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.citation_id = uuid4()
        source_id = uuid4()
        self.evidence = SimpleNamespace(
            citation=SimpleNamespace(
                id=self.citation_id, citation_number=1, original_quote=TRECHO
            ),
            chunk=SimpleNamespace(
                id=uuid4(),
                document_id=uuid4(),
                source_id=source_id,
                chunk_index=42,
                content=TRECHO,
                article="Art. 130",
                section="Capítulo IV",
                paragraph=None,
                official_url=URL_OFICIAL,
            ),
            source=SimpleNamespace(
                id=source_id,
                name="Presidência da República",
                short_name="Planalto",
                base_url="https://www.planalto.gov.br",
                description=None,
                created_at=datetime(2026, 10, 9, tzinfo=timezone.utc),
            ),
        )
        self.repository = SimpleNamespace(get_by_id=AsyncMock(return_value=self.evidence))
        self.service = CitationService(self.repository)

    async def test_monta_detalhe_sem_alterar_texto_ou_metadados(self) -> None:
        detalhe = await self.service.get_by_id(self.citation_id)

        self.repository.get_by_id.assert_awaited_once_with(self.citation_id)
        self.assertEqual(detalhe.id, self.citation_id)
        self.assertEqual(detalhe.citation_number, 1)
        self.assertEqual(detalhe.original_quote, TRECHO)
        self.assertEqual(detalhe.chunk.id, self.evidence.chunk.id)
        self.assertEqual(detalhe.chunk.document_id, self.evidence.chunk.document_id)
        self.assertEqual(detalhe.chunk.chunk_index, 42)
        self.assertEqual(detalhe.chunk.content, TRECHO)
        self.assertEqual(detalhe.chunk.article, "Art. 130")
        self.assertEqual(detalhe.chunk.section, "Capítulo IV")
        self.assertIsNone(detalhe.chunk.paragraph)
        self.assertEqual(detalhe.source.id, self.evidence.source.id)
        self.assertEqual(detalhe.source.short_name, "Planalto")
        self.assertEqual(detalhe.source.base_url, self.evidence.source.base_url)

    async def test_preserva_link_cadastrado_com_ancora_e_parametros(self) -> None:
        url = f"{URL_OFICIAL}?origem=arquivo#art130"
        self.evidence.chunk.official_url = url

        detalhe = await self.service.get_by_id(self.citation_id)

        self.assertEqual(detalhe.chunk.official_url, url)
        self.assertEqual(self.evidence.chunk.official_url, url)

    async def test_preserva_snapshot_da_citacao_historica(self) -> None:
        # O detalhe nao deve recalcular o snapshot a partir do chunk atual.
        self.evidence.chunk.content = "Conteúdo diferente do snapshot arquivado."

        detalhe = await self.service.get_by_id(self.citation_id)

        self.assertEqual(detalhe.original_quote, TRECHO)
        self.assertEqual(detalhe.chunk.content, self.evidence.chunk.content)

    async def test_inexistente_levanta_erro_de_dominio(self) -> None:
        self.repository.get_by_id.return_value = None

        with self.assertRaises(CitationNotFoundError) as contexto:
            await self.service.get_by_id(self.citation_id)

        self.assertEqual(contexto.exception.citation_id, self.citation_id)

    async def test_nao_inventa_link_para_url_ausente_relativa_ou_insegura(self) -> None:
        for url in ("", "/ccivil_03/clt.htm", "javascript:alert(1)", "https://"):
            with self.subTest(url=url):
                self.evidence.chunk.official_url = url
                with self.assertRaises(InvalidCitationLinkError):
                    await self.service.get_by_id(self.citation_id)

    async def test_propaga_falha_do_repositorio(self) -> None:
        self.repository.get_by_id.side_effect = RuntimeError("falha de persistencia")

        with self.assertRaisesRegex(RuntimeError, "falha de persistencia"):
            await self.service.get_by_id(self.citation_id)
