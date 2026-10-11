"""Testes das migrations do Alembic.

O teste central e o de sincronia: ele cria um banco descartavel, aplica todas
as migrations do zero e compara o schema resultante com `Base.metadata`. Se
alguem alterar um modelo e esquecer de gerar a migration, ele falha aqui -- e
nao em producao, onde a tabela nao teria a coluna nova.

Esse descuido e o erro mais comum quando varias pessoas mexem nos modelos em
paralelo, que e exatamente o caso deste projeto.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T007
"""

import asyncio
from pathlib import Path

import pytest
from alembic.autogenerate import compare_metadata
from alembic.command import upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from app.shared.database import Base, get_database_settings

pytestmark = pytest.mark.integration

DIRETORIO_BACKEND = Path(__file__).resolve().parents[2]
ARQUIVO_INI = DIRETORIO_BACKEND / "alembic.ini"
DIRETORIO_VERSOES = DIRETORIO_BACKEND / "alembic" / "versions"

BANCO_DESCARTAVEL = "assistente_trabalhista_migracoes"


def _configuracao_alembic() -> Config:
    config = Config(str(ARQUIVO_INI))
    config.set_main_option("script_location", str(DIRETORIO_BACKEND / "alembic"))
    return config


class TestEstruturaDasMigrations:
    """Verificacoes baratas, sem banco."""

    def test_existe_ao_menos_uma_migration(self) -> None:
        assert list(DIRETORIO_VERSOES.glob("*.py")), "nenhuma migration encontrada"

    def test_existe_exatamente_um_head(self) -> None:
        """Dois heads significam migrations divergentes.

        Acontece quando duas pessoas geram migrations a partir do mesmo ponto;
        o `alembic upgrade head` passa a falhar para todo mundo ate alguem
        fazer o merge.
        """
        heads = ScriptDirectory.from_config(_configuracao_alembic()).get_heads()

        assert len(heads) == 1, f"migrations divergentes, heads encontrados: {heads}"

    def test_toda_migration_tem_downgrade_implementado(self) -> None:
        """Downgrade vazio impede reverter um deploy problematico."""
        script = ScriptDirectory.from_config(_configuracao_alembic())

        sem_downgrade = [
            revisao.revision
            for revisao in script.walk_revisions()
            if "pass" in (Path(revisao.path).read_text(encoding="utf-8").split("def downgrade")[1])
        ]

        assert not sem_downgrade, f"migrations sem downgrade: {sem_downgrade}"


class TestSincroniaComOsModelos:
    def test_migrations_reproduzem_o_schema_dos_modelos(
        self, test_database_url: str, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Aplica as migrations num banco limpo e exige diferenca zero.

        Teste sincrono de proposito: o `env.py` do Alembic chama
        `asyncio.run()` internamente, o que falharia dentro de um teste async
        por ja existir um event loop em execucao.
        """
        url_descartavel = (
            make_url(test_database_url).set(database=BANCO_DESCARTAVEL).render_as_string(False)
        )

        asyncio.run(_recriar_banco(test_database_url, BANCO_DESCARTAVEL))

        try:
            monkeypatch.setenv("DATABASE_URL", url_descartavel)
            get_database_settings.cache_clear()

            upgrade(_configuracao_alembic(), "head")

            diferencas = asyncio.run(_diferencas_de_schema(url_descartavel))

            assert diferencas == [], (
                "O schema das migrations divergiu dos modelos. "
                "Rode: alembic revision --autogenerate -m 'descricao'. "
                f"Diferencas: {diferencas}"
            )
        finally:
            get_database_settings.cache_clear()
            asyncio.run(_remover_banco(test_database_url, BANCO_DESCARTAVEL))


async def _recriar_banco(url_referencia: str, nome: str) -> None:
    """Recria o banco descartavel, garantindo partida limpa."""
    await _executar_fora_de_transacao(
        url_referencia,
        [f'DROP DATABASE IF EXISTS "{nome}"', f'CREATE DATABASE "{nome}"'],
    )


async def _remover_banco(url_referencia: str, nome: str) -> None:
    await _executar_fora_de_transacao(url_referencia, [f'DROP DATABASE IF EXISTS "{nome}"'])


async def _executar_fora_de_transacao(url_referencia: str, comandos: list[str]) -> None:
    """CREATE/DROP DATABASE nao podem rodar dentro de transacao."""
    url_manutencao = make_url(url_referencia).set(database="postgres").render_as_string(False)
    motor = create_async_engine(url_manutencao, isolation_level="AUTOCOMMIT")

    try:
        async with motor.connect() as conexao:
            for comando in comandos:
                await conexao.execute(text(comando))
    finally:
        await motor.dispose()


async def _diferencas_de_schema(url: str) -> list:
    """Compara o banco migrado com Base.metadata."""
    motor = create_async_engine(url)

    try:
        async with motor.connect() as conexao:
            return await conexao.run_sync(
                lambda sincrona: compare_metadata(
                    MigrationContext.configure(
                        sincrona,
                        opts={"compare_type": True, "compare_server_default": True},
                    ),
                    Base.metadata,
                )
            )
    finally:
        await motor.dispose()
