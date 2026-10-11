"""Testes de integracao do contrato das fixtures de banco.

Antes de qualquer repositorio depender delas, estes testes provam contra um
PostgreSQL real que a conexao funciona, que as extensoes exigidas estao
presentes e -- o ponto central -- que um teste nao enxerga o que outro gravou.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T006
"""

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.audit.models import AuditAction, AuditLog, RegistroImutavelError
from app.shared.uuid import uuid7

pytestmark = pytest.mark.integration


class TestConexao:
    async def test_conecta_e_executa_consulta(self, session: AsyncSession) -> None:
        resultado = await session.execute(text("SELECT 1"))

        assert resultado.scalar_one() == 1

    async def test_servidor_e_postgresql_16_ou_superior(self, session: AsyncSession) -> None:
        """O plano tecnico exige PostgreSQL 16."""
        versao = (await session.execute(text("SHOW server_version"))).scalar_one()
        maior = int(str(versao).split(".")[0])

        assert maior >= 16

    @pytest.mark.parametrize("extensao", ["uuid-ossp", "vector"])
    async def test_extensoes_exigidas_estao_instaladas(
        self, session: AsyncSession, extensao: str
    ) -> None:
        presente = (
            await session.execute(
                text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = :nome)"),
                {"nome": extensao},
            )
        ).scalar_one()

        assert presente is True

    async def test_timezone_do_servidor_preserva_offset(self, session: AsyncSession) -> None:
        """Confirma que timestamptz devolve data aware, base do ADR-0002."""
        agora = (await session.execute(text("SELECT NOW()"))).scalar_one()

        assert agora.tzinfo is not None


class TestSchema:
    async def test_tabela_de_auditoria_foi_criada(self, session: AsyncSession) -> None:
        existe = (
            await session.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = 'audit_logs')"
                )
            )
        ).scalar_one()

        assert existe is True

    async def test_created_at_e_timestamptz_no_banco(self, session: AsyncSession) -> None:
        """Prova no banco real o que o teste unitario afirma no mapeamento."""
        tipo = (
            await session.execute(
                text(
                    "SELECT data_type FROM information_schema.columns "
                    "WHERE table_name = 'audit_logs' AND column_name = 'created_at'"
                )
            )
        ).scalar_one()

        assert tipo == "timestamp with time zone"

    async def test_details_e_jsonb_no_banco(self, session: AsyncSession) -> None:
        tipo = (
            await session.execute(
                text(
                    "SELECT udt_name FROM information_schema.columns "
                    "WHERE table_name = 'audit_logs' AND column_name = 'details'"
                )
            )
        ).scalar_one()

        assert tipo == "jsonb"


class TestPersistencia:
    async def test_grava_e_le_registro_de_auditoria(self, session: AsyncSession) -> None:
        registro = AuditLog(
            action=AuditAction.DOCUMENT_ACTIVATED,
            entity_type="Document",
            entity_id=uuid7(),
            details={"antes": {"is_active": False}, "depois": {"is_active": True}},
        )
        session.add(registro)
        await session.flush()

        lido = await session.get(AuditLog, registro.id)

        assert lido is not None
        assert lido.action == AuditAction.DOCUMENT_ACTIVATED
        assert lido.details["depois"]["is_active"] is True

    async def test_id_e_created_at_sao_preenchidos_automaticamente(
        self, session: AsyncSession
    ) -> None:
        registro = AuditLog(
            action=AuditAction.SOURCE_CREATED,
            entity_type="Source",
            entity_id=uuid7(),
        )
        session.add(registro)
        await session.flush()

        assert registro.id is not None
        assert registro.id.version == 7
        assert registro.created_at.tzinfo is not None

    async def test_actor_id_aceita_nulo(self, session: AsyncSession) -> None:
        """Acoes de rotina automatica nao tem usuario humano responsavel."""
        registro = AuditLog(
            action=AuditAction.DOCUMENT_UPLOADED,
            entity_type="Document",
            entity_id=uuid7(),
            actor_id=None,
        )
        session.add(registro)
        await session.flush()

        assert registro.actor_id is None


class TestImutabilidadeNoBanco:
    """Valida contra banco real a guarda que o teste unitario cobre isoladamente."""

    async def test_update_em_registro_persistido_e_bloqueado(self, session: AsyncSession) -> None:
        registro = AuditLog(
            action=AuditAction.DOCUMENT_ACTIVATED,
            entity_type="Document",
            entity_id=uuid7(),
        )
        session.add(registro)
        await session.flush()

        registro.action = AuditAction.DOCUMENT_DEACTIVATED

        with pytest.raises(RegistroImutavelError, match="alterado"):
            await session.flush()

    async def test_delete_de_registro_persistido_e_bloqueado(self, session: AsyncSession) -> None:
        registro = AuditLog(
            action=AuditAction.SOURCE_CREATED,
            entity_type="Source",
            entity_id=uuid7(),
        )
        session.add(registro)
        await session.flush()

        await session.delete(registro)

        with pytest.raises(RegistroImutavelError, match="removido"):
            await session.flush()


class TestIsolamentoEntreTestes:
    """O ponto central da T006.

    Os dois testes abaixo sao deliberadamente acoplados pela ordem: o primeiro
    grava e confirma, o segundo prova que nada sobrou. Se o isolamento
    quebrar, o segundo falha -- e e exatamente esse o alarme que se quer.
    """

    ENTIDADE = "IsolamentoProva"

    async def test_1_grava_e_confirma(self, session: AsyncSession) -> None:
        session.add(
            AuditLog(
                action=AuditAction.SOURCE_CREATED,
                entity_type=self.ENTIDADE,
                entity_id=uuid7(),
            )
        )
        # commit de verdade: com join_transaction_mode="create_savepoint" ele
        # libera um SAVEPOINT, sem confirmar a transacao externa do teste.
        await session.commit()

        total = await self._contar(session)

        assert total == 1

    async def test_2_nao_enxerga_o_que_o_anterior_gravou(self, session: AsyncSession) -> None:
        total = await self._contar(session)

        assert total == 0

    async def _contar(self, session: AsyncSession) -> int:
        consulta = (
            select(func.count()).select_from(AuditLog).where(AuditLog.entity_type == self.ENTIDADE)
        )
        return (await session.execute(consulta)).scalar_one()
