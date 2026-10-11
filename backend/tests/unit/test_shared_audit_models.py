"""Testes unitarios dos mixins base e do modelo de trilha de auditoria.

Verificam o mapeamento declarado (tabela, colunas, tipos, nulabilidade e
indices) sem abrir conexao com o banco: o SQLAlchemy constroi os metadados em
tempo de importacao, entao o contrato e inspecionavel isoladamente.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T005
    Requisito: FR-009 (toda alteracao administrativa registrada em AuditLog)
    ADRs: 0001 (UUID v7), 0002 (datas em UTC)
"""

from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import TIMESTAMP, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB

from app.shared.audit.models import AuditAction, AuditLog, RegistroImutavelError
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.uuid import utc_now, uuid7

pytestmark = pytest.mark.unit


class TestAuditAction:
    def test_cobre_as_acoes_exigidas_pela_especificacao(self) -> None:
        """O data-model lista estas acoes administrativas nominalmente."""
        esperadas = {
            "SOURCE_CREATED",
            "DOCUMENT_UPLOADED",
            "DOCUMENT_ACTIVATED",
            "DOCUMENT_DEACTIVATED",
        }

        assert esperadas <= {acao.value for acao in AuditAction}

    def test_valor_e_igual_ao_nome(self) -> None:
        """A coluna guarda a string; nome e valor iguais evitam divergencia."""
        for acao in AuditAction:
            assert acao.value == acao.name

    def test_e_comparavel_com_string(self) -> None:
        """Herdar de str permite comparar direto com o valor lido do banco."""
        assert AuditAction.DOCUMENT_ACTIVATED == "DOCUMENT_ACTIVATED"


class TestMixinsBase:
    def test_chave_primaria_e_uuid(self) -> None:
        coluna = AuditLog.__table__.c.id

        assert coluna.primary_key is True
        assert isinstance(coluna.type, Uuid)

    def test_chave_primaria_tem_default_gerado_pela_aplicacao(self) -> None:
        """O ID nasce na aplicacao, antes do INSERT (ADR-0001)."""
        default = AuditLog.__table__.c.id.default

        assert default is not None
        assert default.is_callable is True

    def test_default_da_chave_gera_uuid_versao_7(self) -> None:
        """Garante o ADR-0001: nenhuma entidade pode cair em uuid4 por descuido.

        Verifica o valor produzido, nao a identidade da funcao: o SQLAlchemy
        embrulha defaults chamaveis internamente.
        """
        gerado = AuditLog.__table__.c.id.default.arg(None)

        assert isinstance(gerado, UUID)
        assert gerado.version == 7

    def test_created_at_e_timestamp_com_timezone(self) -> None:
        """Garante o ADR-0002 na pratica, via type_annotation_map da Base."""
        coluna = AuditLog.__table__.c.created_at

        assert isinstance(coluna.type, TIMESTAMP)
        assert coluna.type.timezone is True

    def test_created_at_recebe_data_aware_em_utc_por_default(self) -> None:
        gerado = AuditLog.__table__.c.created_at.default.arg(None)

        assert isinstance(gerado, datetime)
        assert gerado.tzinfo is not None
        assert gerado.utcoffset().total_seconds() == 0

    def test_created_at_e_obrigatorio(self) -> None:
        assert AuditLog.__table__.c.created_at.nullable is False

    def test_mixins_sao_reutilizaveis_por_outros_modelos(self) -> None:
        """Os mixins vivem em app.shared.models, nao no modulo de auditoria,
        porque Source, Document, DocumentChunk e Citation tambem os usarao."""
        assert issubclass(AuditLog, UUIDPrimaryKeyMixin)
        assert issubclass(AuditLog, TimestampMixin)


class TestAuditLog:
    def test_nome_da_tabela(self) -> None:
        assert AuditLog.__tablename__ == "audit_logs"

    @pytest.mark.parametrize(
        "campo",
        ["id", "action", "entity_type", "entity_id", "actor_id", "details", "created_at"],
    )
    def test_possui_os_campos_do_data_model(self, campo: str) -> None:
        assert campo in AuditLog.__table__.c

    def test_action_e_string_50_obrigatoria(self) -> None:
        coluna = AuditLog.__table__.c.action

        assert isinstance(coluna.type, String)
        assert coluna.type.length == 50
        assert coluna.nullable is False

    def test_entity_type_e_string_50_obrigatoria(self) -> None:
        coluna = AuditLog.__table__.c.entity_type

        assert isinstance(coluna.type, String)
        assert coluna.type.length == 50
        assert coluna.nullable is False

    def test_entity_id_e_uuid_obrigatorio(self) -> None:
        coluna = AuditLog.__table__.c.entity_id

        assert isinstance(coluna.type, Uuid)
        assert coluna.nullable is False

    def test_actor_id_e_opcional(self) -> None:
        """A ativacao pode partir de uma rotina automatica, sem usuario humano."""
        assert AuditLog.__table__.c.actor_id.nullable is True

    def test_details_e_jsonb_opcional(self) -> None:
        """Guarda o estado anterior e posterior da mudanca."""
        coluna = AuditLog.__table__.c.details

        assert isinstance(coluna.type, JSONB)
        assert coluna.nullable is True

    def test_entity_id_e_indexado(self) -> None:
        """Auditar uma norma e consultar por entity_id; sem indice vira seq scan."""
        colunas_indexadas = {
            coluna.name for indice in AuditLog.__table__.indexes for coluna in indice.columns
        }

        assert "entity_id" in colunas_indexadas

    def test_created_at_nao_e_atualizavel(self) -> None:
        """Trilha imutavel: nao existe onupdate no carimbo de criacao."""
        assert AuditLog.__table__.c.created_at.onupdate is None


class TestImutabilidade:
    """O data-model define o AuditLog como 'registro imutavel'.

    Uma trilha que pode ser editada nao prova nada: se um registro de ativacao
    indevida puder ser alterado depois, a auditoria perde a funcao. O modelo
    bloqueia UPDATE e DELETE no nivel da aplicacao.
    """

    def test_update_e_bloqueado(self) -> None:
        with pytest.raises(RegistroImutavelError, match="alterado"):
            AuditLog._bloquear_alteracao(None, None, AuditLog())

    def test_delete_e_bloqueado(self) -> None:
        with pytest.raises(RegistroImutavelError, match="removido"):
            AuditLog._bloquear_remocao(None, None, AuditLog())

    def test_erro_de_imutabilidade_e_runtime_error(self) -> None:
        assert issubclass(RegistroImutavelError, RuntimeError)


class TestConstrucao:
    def test_aceita_os_campos_minimos(self) -> None:
        registro = AuditLog(
            action=AuditAction.DOCUMENT_ACTIVATED,
            entity_type="Document",
            entity_id=uuid7(),
        )

        assert registro.action == AuditAction.DOCUMENT_ACTIVATED
        assert registro.entity_type == "Document"
        assert registro.actor_id is None
        assert registro.details is None

    def test_aceita_detalhes_de_mudanca_de_estado(self) -> None:
        detalhes = {"antes": {"is_active": False}, "depois": {"is_active": True}}

        registro = AuditLog(
            action=AuditAction.DOCUMENT_ACTIVATED,
            entity_type="Document",
            entity_id=uuid7(),
            actor_id=uuid7(),
            details=detalhes,
        )

        assert registro.details == detalhes

    def test_repr_nao_vaza_detalhes(self) -> None:
        """`details` pode conter conteudo administrativo; o repr vai para log."""
        registro = AuditLog(
            action=AuditAction.SOURCE_CREATED,
            entity_type="Source",
            entity_id=uuid7(),
            details={"segredo": "nao deve aparecer"},
        )

        assert "nao deve aparecer" not in repr(registro)
        assert "SOURCE_CREATED" in repr(registro)


def test_datetime_do_dominio_e_aware() -> None:
    """Sanidade: o default usado pelos mixins produz data com fuso."""
    agora = utc_now()

    assert isinstance(agora, datetime)
    assert agora.tzinfo is not None
