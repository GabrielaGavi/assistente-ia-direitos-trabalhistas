"""Ambiente de execucao das migrations do Alembic.

A URL de conexao e lida de `DATABASE_URL` (variavel de ambiente ou
`backend/.env`), nunca do `alembic.ini`. Assim nenhuma credencial entra no
repositorio e a mesma migration roda contra o banco local, o de testes e o
Supabase apenas trocando a variavel.

Uso:
    alembic revision --autogenerate -m "descricao"   # gera a migration
    alembic upgrade head                             # aplica
    alembic downgrade -1                             # desfaz a ultima

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T007
"""

import asyncio
from logging.config import fileConfig

from sqlalchemy.engine import Connection

# Importado pelo efeito colateral de registrar as tabelas em Base.metadata.
# Sem isto o autogenerate nao enxerga as tabelas e gera uma migration vazia --
# ou pior, um DROP TABLE. Modelos novos entram em app/models_registry.py.
import app.models_registry  # noqa: F401
from alembic import context
from app.shared.database import Base, create_database_engine, get_database_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    """URL de conexao, obtida da mesma configuracao usada pela aplicacao.

    Reaproveita `DatabaseSettings` em vez de ler `os.environ` diretamente, para
    que migration e aplicacao nunca divirjam sobre de onde vem a URL -- e para
    que o `backend/.env` seja respeitado aqui tambem.
    """
    try:
        return get_database_settings().database_url
    except Exception as erro:  # ValidationError quando a variavel falta
        raise RuntimeError(
            "DATABASE_URL nao definida. Copie backend/.env.example para "
            "backend/.env ou exporte a variavel antes de rodar o alembic."
        ) from erro


def run_migrations_offline() -> None:
    """Gera o SQL das migrations sem conectar ao banco (`alembic upgrade --sql`)."""
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Sem compare_type, uma mudanca de String(50) para String(100) passaria
        # despercebida pelo autogenerate.
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Aplica as migrations por meio de um engine assincrono.

    Reaproveita `create_database_engine` -- a mesma funcao usada pela
    aplicacao -- para que a migration tambem ganhe TLS automatico contra
    provedores remotos (Supabase, Neon) e o ajuste do pooler em modo
    "transaction" (porta 6543), em vez de duplicar essa logica aqui.
    """
    connectable = create_database_engine(_database_url())

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
