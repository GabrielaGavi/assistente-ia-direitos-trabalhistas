"""Testes unitarios dos schemas Pydantic de citacao.

A citacao e o contrato de confianca do produto: e o que permite ao trabalhador
conferir que a orientacao recebida vem de lei, e nao de invencao do modelo.
Por isso os testes aqui cobrem sobretudo *fidelidade* -- o trecho que sai tem
de ser exatamente o que esta no banco, sem reescrita, sem corte, sem
normalizacao de espacos.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T008 (RED) / T011 (GREEN)
    Requisitos: FR-006, FR-007
    Contrato: specs/001-fontes-e-rastreabilidade/contracts/sources-documents-api.yaml
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.citations.schemas import CitationDetailResponse, CitationResponse
from app.documents.chunk_schemas import DocumentChunkResponse
from app.shared.uuid import uuid7
from app.sources.schemas import SourceResponse

pytestmark = pytest.mark.unit

# Texto literal do Art. 130 da CLT, com a grafia e a pontuacao originais.
TRECHO_ART_130 = (
    "Após cada período de 12 (doze) meses de vigência do contrato de trabalho, "
    "o empregado terá direito a férias, na seguinte proporção: "
    "I - 30 (trinta) dias corridos, quando não houver faltado ao serviço mais "
    "de 5 (cinco) vezes;"
)
URL_OFICIAL = "https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm"


@pytest.fixture
def chunk() -> DocumentChunkResponse:
    return DocumentChunkResponse(
        id=uuid7(),
        document_id=uuid7(),
        chunk_index=42,
        content=TRECHO_ART_130,
        article="Art. 130",
        section="Capítulo IV - Das Férias Anuais",
        paragraph=None,
        official_url=URL_OFICIAL,
    )


@pytest.fixture
def fonte() -> SourceResponse:
    return SourceResponse(
        id=uuid7(),
        name="Presidência da República - Portal da Legislação",
        short_name="Planalto",
        base_url="https://www.planalto.gov.br",
        description=None,
        created_at=datetime.now(timezone.utc),
    )


class TestCitationResponse:
    def test_aceita_os_campos_do_contrato(self) -> None:
        citacao = CitationResponse(
            id=uuid7(),
            citation_number=1,
            original_quote=TRECHO_ART_130,
        )

        assert citacao.citation_number == 1

    def test_preserva_o_trecho_sem_qualquer_alteracao(self) -> None:
        """FR-007: o trecho original e exibido sem reescrita.

        Se o schema normalizasse espacos ou aparasse as pontas, o texto exibido
        deixaria de ser o texto da lei -- que e justamente o que a citacao
        promete ao usuario.
        """
        bruto = "  Art. 130.   Após cada\n\tperíodo de 12 meses...  "

        citacao = CitationResponse(id=uuid7(), citation_number=1, original_quote=bruto)

        assert citacao.original_quote == bruto

    @pytest.mark.parametrize("numero", [1, 2, 3, 99])
    def test_aceita_numeracao_sequencial_valida(self, numero: int) -> None:
        citacao = CitationResponse(id=uuid7(), citation_number=numero, original_quote="x")

        assert citacao.citation_number == numero

    @pytest.mark.parametrize("numero_invalido", [0, -1])
    def test_rejeita_numeracao_menor_que_um(self, numero_invalido: int) -> None:
        """A numeracao segue a ordem de aparicao na resposta: comeca em [1]."""
        with pytest.raises(ValidationError):
            CitationResponse(id=uuid7(), citation_number=numero_invalido, original_quote="x")

    def test_rejeita_trecho_vazio(self) -> None:
        """Citacao sem evidencia textual nao prova nada."""
        with pytest.raises(ValidationError):
            CitationResponse(id=uuid7(), citation_number=1, original_quote="")

    def test_exige_o_numero_da_citacao(self) -> None:
        with pytest.raises(ValidationError):
            CitationResponse(id=uuid7(), original_quote="x")

    def test_le_atributos_de_objeto_orm(self) -> None:
        """O router devolve o modelo SQLAlchemy direto; o schema precisa aceitar."""

        class CitacaoFalsa:
            id = uuid7()
            citation_number = 1
            original_quote = TRECHO_ART_130

        citacao = CitationResponse.model_validate(CitacaoFalsa())

        assert citacao.original_quote == TRECHO_ART_130


class TestCitationDetailResponse:
    def test_aninha_chunk_e_fonte(
        self, chunk: DocumentChunkResponse, fonte: SourceResponse
    ) -> None:
        """Cenario 1 da US1: inspecionar [1] mostra norma, artigo, trecho e link."""
        detalhe = CitationDetailResponse(
            id=uuid7(),
            citation_number=1,
            original_quote=TRECHO_ART_130,
            chunk=chunk,
            source=fonte,
        )

        assert detalhe.chunk.article == "Art. 130"
        assert detalhe.source.short_name == "Planalto"

    def test_expoe_o_link_oficial_do_governo(
        self, chunk: DocumentChunkResponse, fonte: SourceResponse
    ) -> None:
        """Sem o link, o usuario nao tem como conferir na fonte primaria."""
        detalhe = CitationDetailResponse(
            id=uuid7(),
            citation_number=1,
            original_quote=TRECHO_ART_130,
            chunk=chunk,
            source=fonte,
        )

        assert detalhe.chunk.official_url == URL_OFICIAL

    def test_exige_o_chunk(self, fonte: SourceResponse) -> None:
        """Citacao sem chunk e exatamente a alucinacao que o projeto combate."""
        with pytest.raises(ValidationError):
            CitationDetailResponse(
                id=uuid7(),
                citation_number=1,
                original_quote=TRECHO_ART_130,
                source=fonte,
            )

    def test_exige_a_fonte(self, chunk: DocumentChunkResponse) -> None:
        with pytest.raises(ValidationError):
            CitationDetailResponse(
                id=uuid7(),
                citation_number=1,
                original_quote=TRECHO_ART_130,
                chunk=chunk,
            )

    def test_serializa_para_json_do_contrato(
        self, chunk: DocumentChunkResponse, fonte: SourceResponse
    ) -> None:
        detalhe = CitationDetailResponse(
            id=uuid7(),
            citation_number=1,
            original_quote=TRECHO_ART_130,
            chunk=chunk,
            source=fonte,
        )

        corpo = detalhe.model_dump(mode="json")

        assert set(corpo) == {"id", "citation_number", "original_quote", "chunk", "source"}
        assert corpo["chunk"]["official_url"] == URL_OFICIAL


class TestDocumentChunkResponse:
    def test_campos_estruturais_sao_opcionais(self) -> None:
        """Nem toda norma tem artigo, secao ou paragrafo; o preambulo nao tem."""
        trecho = DocumentChunkResponse(
            id=uuid7(),
            document_id=uuid7(),
            chunk_index=0,
            content="Preâmbulo da norma.",
            official_url=URL_OFICIAL,
        )

        assert trecho.article is None
        assert trecho.section is None
        assert trecho.paragraph is None

    def test_exige_o_link_oficial(self) -> None:
        """FR-005: todo trecho carrega o link oficial da norma."""
        with pytest.raises(ValidationError):
            DocumentChunkResponse(
                id=uuid7(),
                document_id=uuid7(),
                chunk_index=0,
                content="x",
            )

    def test_preserva_o_conteudo_sem_alteracao(self) -> None:
        bruto = "  Art. 7º   São direitos...  \n"

        trecho = DocumentChunkResponse(
            id=uuid7(),
            document_id=uuid7(),
            chunk_index=0,
            content=bruto,
            official_url=URL_OFICIAL,
        )

        assert trecho.content == bruto
