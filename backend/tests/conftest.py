"""Fixtures compartilhadas dos testes, incluindo acesso assincrono ao banco.

Estrategia de isolamento -- cada teste roda dentro de uma transacao externa que
e descartada ao final:

    conexao ──▶ transacao externa (BEGIN)
                   └─▶ AsyncSession com join_transaction_mode="create_savepoint"

Com esse modo, `session.commit()` dentro do teste cria e libera um SAVEPOINT em
vez de confirmar a transacao externa. O teste exercita o codigo de producao tal
como ele e -- inclusive os commits feitos pelos services -- e mesmo assim o
`rollback` final desfaz tudo.

A alternativa comum, apagar as tabelas entre os testes, e mais lenta e deixa o
banco sujo quando um teste falha no meio.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T006
    ADR: 0004 (PostgreSQL como banco de testes)
"""

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

# `app.shared.audit.models` e importado pelo efeito colateral de registrar as
# tabelas em Base.metadata. Cada novo modelo do dominio precisa ser importado
# aqui para que o create_all da fixture de schema o enxergue.
from app.shared.audit import models as _audit_models  # noqa: F401
from app.shared.database import Base, create_database_engine

URL_PADRAO_DE_TESTE = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/assistente_trabalhista_test"
)


@pytest.fixture(scope="session")
def test_database_url() -> str:
    """URL do banco de testes.

    Lida de `TEST_DATABASE_URL` quando definida, com um padrao que corresponde
    ao servico declarado no `docker-compose.yml` -- assim a suite roda sem
    configuracao previa em qualquer maquina do grupo.
    """
    return os.getenv("TEST_DATABASE_URL", URL_PADRAO_DE_TESTE)


@pytest_asyncio.fixture(scope="session")
async def engine(test_database_url: str) -> AsyncIterator[AsyncEngine]:
    """Engine unico da suite, descartado ao final."""
    motor = create_database_engine(test_database_url)

    yield motor

    await motor.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _schema(engine: AsyncEngine) -> AsyncIterator[None]:
    """Recria o schema no inicio da suite e o remove no fim.

    O `drop_all` inicial garante partida limpa mesmo que uma execucao anterior
    tenha sido interrompida e deixado tabelas para tras.
    """
    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.drop_all)
        await conexao.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conexao:
        await conexao.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """Sessao isolada por teste: tudo o que ela gravar e desfeito ao final."""
    async with engine.connect() as conexao:
        transacao = await conexao.begin()

        sessao = AsyncSession(
            bind=conexao,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )

        try:
            yield sessao
        finally:
            await sessao.close()
            if transacao.is_active:
                await transacao.rollback()
