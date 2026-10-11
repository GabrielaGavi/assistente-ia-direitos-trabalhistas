"""Testes unitarios do mapeamento dos modelos do dominio.

Cobrem `Source`, `Document`, `DocumentChunk` e `Citation` juntos porque a
cadeia de chaves estrangeiras os torna inseparaveis: `Citation.chunk_id`
aponta para `DocumentChunk`, que aponta para `Document`, que aponta para
`Source`. Nenhuma das tabelas pode ser criada isoladamente.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Tasks: T010, T017, T018, T025
    Requisitos: FR-001 a FR-007
"""

from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import TIMESTAMP, Boolean, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB

from app.citations.models import Citation
from app.documents.chunk_models import DocumentChunk
from app.documents.models import Document, DocumentStatus
from app.shared.uuid import uuid7
from app.sources.models import Source

pytestmark = pytest.mark.unit


def _nomes_de_constraints(modelo: type) -> set[str]:
    return {c.name for c in modelo.__table__.constraints if c.name}


def _colunas_unicas(modelo: type) -> list[tuple[str, ...]]:
    """Combinacoes unicas, venham de UniqueConstraint ou de Index(unique=True)."""
    das_constraints = [
        tuple(col.name for col in c.columns)
        for c in modelo.__table__.constraints
        if c.__class__.__name__ == "UniqueConstraint"
    ]
    dos_indices = [
        tuple(col.name for col in i.columns) for i in modelo.__table__.indexes if i.unique
    ]
    return das_constraints + dos_indices


class TestSource:
    def test_nome_da_tabela(self) -> None:
        assert Source.__tablename__ == "sources"

    @pytest.mark.parametrize(
        "campo", ["id", "name", "short_name", "base_url", "description", "created_at"]
    )
    def test_possui_os_campos_do_data_model(self, campo: str) -> None:
        assert campo in Source.__table__.c

    def test_sigla_e_unica(self) -> None:
        """ "Planalto" identifica a fonte nas citacoes; duplicar a sigla
        tornaria a referencia ambigua."""
        assert Source.__table__.c.short_name.unique is True

    def test_tamanhos_do_data_model(self) -> None:
        assert Source.__table__.c.name.type.length == 255
        assert Source.__table__.c.short_name.type.length == 50
        assert Source.__table__.c.base_url.type.length == 500

    def test_descricao_e_opcional(self) -> None:
        assert Source.__table__.c.description.nullable is True

    def test_chave_primaria_em_uuid_v7(self) -> None:
        assert Source.__table__.c.id.default.arg(None).version == 7


class TestDocumentStatus:
    def test_cobre_o_ciclo_de_vida_do_data_model(self) -> None:
        esperados = {"PROCESSING", "READY", "FAILED", "ACTIVE", "INACTIVE"}

        assert {s.value for s in DocumentStatus} == esperados

    def test_comeca_em_processing(self) -> None:
        assert Document.__table__.c.status.default.arg is DocumentStatus.PROCESSING


class TestDocument:
    def test_nome_da_tabela(self) -> None:
        assert Document.__tablename__ == "documents"

    @pytest.mark.parametrize(
        "campo",
        [
            "id",
            "source_id",
            "title",
            "logical_name",
            "version",
            "checksum_sha256",
            "published_at",
            "is_active",
            "status",
            "created_at",
            "updated_at",
        ],
    )
    def test_possui_os_campos_do_data_model(self, campo: str) -> None:
        assert campo in Document.__table__.c

    def test_pertence_a_exatamente_uma_fonte(self) -> None:
        """FR-002: todo documento tem uma fonte oficial primaria."""
        coluna = Document.__table__.c.source_id

        assert coluna.nullable is False
        assert {fk.column.table.name for fk in coluna.foreign_keys} == {"sources"}

    def test_versao_inicial_e_um(self) -> None:
        assert Document.__table__.c.version.default.arg == 1

    def test_nasce_inativo(self) -> None:
        """Documento recem-criado ainda nao foi auditado; nao pode responder."""
        assert Document.__table__.c.is_active.default.arg is False

    def test_checksum_tem_64_caracteres(self) -> None:
        """SHA-256 em hexadecimal ocupa exatamente 64 caracteres."""
        assert Document.__table__.c.checksum_sha256.type.length == 64

    def test_versao_e_unica_por_norma_logica(self) -> None:
        """FR-003: versionamento imutavel por (fonte, norma, versao)."""
        assert ("source_id", "logical_name", "version") in _colunas_unicas(Document)

    def test_apenas_uma_versao_ativa_por_norma(self) -> None:
        """FR-004: no maximo uma versao ACTIVE por norma logica.

        Garantido por indice unico PARCIAL -- unique comum proibiria duas
        versoes inativas da mesma norma, que e justamente o historico que o
        projeto precisa preservar para auditar conversas antigas.
        """
        parciais = [
            indice
            for indice in Document.__table__.indexes
            if indice.unique and indice.dialect_options["postgresql"].get("where") is not None
        ]

        assert parciais, "faltou o indice unico parcial da versao ativa"

        alvo = parciais[0]
        assert {c.name for c in alvo.columns} == {"source_id", "logical_name"}

    def test_data_de_publicacao_e_opcional(self) -> None:
        """Nem toda norma cadastrada traz a data do Diario Oficial."""
        assert Document.__table__.c.published_at.nullable is True

    def test_tipos_do_data_model(self) -> None:
        assert isinstance(Document.__table__.c.version.type, Integer)
        assert isinstance(Document.__table__.c.is_active.type, Boolean)
        assert isinstance(Document.__table__.c.created_at.type, TIMESTAMP)
        assert Document.__table__.c.created_at.type.timezone is True


class TestDocumentChunk:
    def test_nome_da_tabela(self) -> None:
        assert DocumentChunk.__tablename__ == "document_chunks"

    @pytest.mark.parametrize(
        "campo",
        [
            "id",
            "document_id",
            "source_id",
            "chunk_index",
            "content",
            "article",
            "section",
            "paragraph",
            "page_number",
            "official_url",
            "metadata_extra",
            "created_at",
        ],
    )
    def test_possui_os_campos_do_data_model(self, campo: str) -> None:
        assert campo in DocumentChunk.__table__.c

    def test_some_junto_com_o_documento(self) -> None:
        """Chunk orfao viraria evidencia sem norma -- o cenario que o SC-002 proibe."""
        fks = list(DocumentChunk.__table__.c.document_id.foreign_keys)

        assert fks[0].column.table.name == "documents"
        assert fks[0].ondelete == "CASCADE"

    def test_indice_e_unico_dentro_do_documento(self) -> None:
        assert ("document_id", "chunk_index") in _colunas_unicas(DocumentChunk)

    def test_conteudo_e_text_sem_limite(self) -> None:
        """Artigo longo nao pode ser truncado: o trecho tem de sair literal."""
        assert isinstance(DocumentChunk.__table__.c.content.type, Text)
        assert DocumentChunk.__table__.c.content.nullable is False

    def test_link_oficial_e_obrigatorio(self) -> None:
        """FR-005: sem o link o usuario nao confere na fonte primaria."""
        coluna = DocumentChunk.__table__.c.official_url

        assert coluna.nullable is False
        assert coluna.type.length == 1000

    @pytest.mark.parametrize("campo", ["article", "section", "paragraph", "page_number"])
    def test_metadados_estruturais_sao_opcionais(self, campo: str) -> None:
        assert DocumentChunk.__table__.c[campo].nullable is True

    def test_metadata_extra_e_jsonb(self) -> None:
        assert isinstance(DocumentChunk.__table__.c.metadata_extra.type, JSONB)


class TestCitation:
    def test_nome_da_tabela(self) -> None:
        assert Citation.__tablename__ == "citations"

    @pytest.mark.parametrize(
        "campo",
        ["id", "message_id", "chunk_id", "citation_number", "original_quote", "created_at"],
    )
    def test_possui_os_campos_do_data_model(self, campo: str) -> None:
        assert campo in Citation.__table__.c

    def test_aponta_obrigatoriamente_para_um_chunk(self) -> None:
        """FR-006: citacao so existe vinculada a um trecho de documento."""
        coluna = Citation.__table__.c.chunk_id

        assert coluna.nullable is False
        assert {fk.column.table.name for fk in coluna.foreign_keys} == {"document_chunks"}

    def test_numeracao_e_unica_dentro_da_mensagem(self) -> None:
        """FR-007: [1] e [2] na mesma resposta nao podem colidir."""
        assert ("message_id", "citation_number") in _colunas_unicas(Citation)

    def test_trecho_literal_e_obrigatorio_e_sem_limite(self) -> None:
        coluna = Citation.__table__.c.original_quote

        assert isinstance(coluna.type, Text)
        assert coluna.nullable is False

    def test_tipos_do_data_model(self) -> None:
        assert isinstance(Citation.__table__.c.message_id.type, Uuid)
        assert isinstance(Citation.__table__.c.citation_number.type, Integer)

    def test_nao_tem_updated_at(self) -> None:
        """ "Vinculo imutavel entre a resposta e a evidencia", diz o data-model."""
        assert "updated_at" not in Citation.__table__.c


class TestConstrucao:
    def test_monta_a_cadeia_completa_em_memoria(self) -> None:
        fonte = Source(
            name="Presidência da República",
            short_name="Planalto",
            base_url="https://www.planalto.gov.br",
        )
        documento = Document(
            source_id=uuid7(),
            title="Consolidação das Leis do Trabalho",
            logical_name="clt-decreto-lei-5452-1943",
            checksum_sha256="a" * 64,
        )
        trecho = DocumentChunk(
            document_id=uuid7(),
            source_id=uuid7(),
            chunk_index=0,
            content="Art. 130...",
            official_url="https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm",
        )
        citacao = Citation(
            message_id=uuid7(),
            chunk_id=uuid7(),
            citation_number=1,
            original_quote="Art. 130...",
        )

        assert fonte.short_name == "Planalto"
        assert documento.logical_name == "clt-decreto-lei-5452-1943"
        assert trecho.chunk_index == 0
        assert citacao.citation_number == 1

    def test_repr_identifica_a_fonte_pela_sigla(self) -> None:
        fonte = Source(name="x", short_name="Planalto", base_url="https://x")

        assert "Planalto" in repr(fonte)

    def test_repr_do_documento_mostra_versao_e_estado(self) -> None:
        """O que importa no log e qual redacao esta respondendo."""
        documento = Document(
            source_id=uuid7(),
            title="CLT",
            logical_name="clt",
            version=2,
            checksum_sha256="a" * 64,
            is_active=True,
        )

        texto = repr(documento)

        assert "clt" in texto
        assert "v2" in texto
        assert "True" in texto

    def test_repr_do_chunk_mostra_indice_e_artigo(self) -> None:
        trecho = DocumentChunk(
            document_id=uuid7(),
            source_id=uuid7(),
            chunk_index=7,
            content="x",
            article="Art. 130",
            official_url="https://x",
        )

        assert "#7" in repr(trecho)
        assert "Art. 130" in repr(trecho)

    def test_repr_do_chunk_sem_artigo_nao_quebra(self) -> None:
        """Preambulos nao tem artigo; o log precisa continuar legivel."""
        trecho = DocumentChunk(
            document_id=uuid7(),
            source_id=uuid7(),
            chunk_index=0,
            content="x",
            official_url="https://x",
        )

        assert "sem artigo" in repr(trecho)

    def test_repr_da_citacao_nao_vaza_o_trecho(self) -> None:
        """O trecho pode ser longo; o repr vai para log e rastreamento de erro."""
        citacao = Citation(
            message_id=uuid7(),
            chunk_id=uuid7(),
            citation_number=1,
            original_quote="texto muito longo da norma que nao deve aparecer no log",
        )

        assert "nao deve aparecer" not in repr(citacao)


def test_tipos_de_identificador_sao_uuid() -> None:
    for modelo in (Source, Document, DocumentChunk, Citation):
        assert isinstance(modelo.__table__.c.id.type, Uuid)
        assert isinstance(modelo.__table__.c.id.default.arg(None), UUID)


def test_todas_as_datas_sao_aware() -> None:
    for modelo in (Source, Document, DocumentChunk, Citation):
        coluna = modelo.__table__.c.created_at
        assert coluna.type.timezone is True
        assert isinstance(coluna.default.arg(None), datetime)


def test_strings_do_documento_respeitam_o_data_model() -> None:
    assert Document.__table__.c.title.type.length == 255
    assert Document.__table__.c.logical_name.type.length == 100
    assert isinstance(Document.__table__.c.title.type, String)
