"""Acesso assincrono ao PostgreSQL: engine, fabrica de sessoes e Base declarativa.

Esta camada e a unica que conhece o SQLAlchemy em nivel de conexao. Repositorios
recebem uma `AsyncSession` pronta e nao constroem engines proprios, preservando a
fronteira exigida pelo Principio V (Ports and Adapters).

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T004
    ADRs: 0002 (datas em UTC), 0005 (SQLAlchemy em Python puro)
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import TIMESTAMP
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError, NoSuchModuleError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

__all__ = [
    "Base",
    "DatabaseSettings",
    "create_database_engine",
    "create_session_factory",
    "dispose_engine",
    "get_database_settings",
    "get_engine",
    "get_session",
    "get_session_factory",
]

_DRIVER_ESPERADO = "postgresql+asyncpg"


class Base(DeclarativeBase):
    """Base declarativa de todos os modelos do dominio.

    O `type_annotation_map` faz o ADR-0002 valer por construcao: qualquer campo
    anotado como `Mapped[datetime]` vira `TIMESTAMP WITH TIME ZONE`, sem que cada
    modelo precise lembrar de passar `timezone=True`. Sem isso, o padrao do
    SQLAlchemy seria `TIMESTAMP WITHOUT TIME ZONE` e o fuso se perderia na gravacao.
    """

    type_annotation_map = {
        datetime: TIMESTAMP(timezone=True),
    }


class DatabaseSettings(BaseSettings):
    """Configuracao de banco lida de variaveis de ambiente ou de `backend/.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str
    database_echo: bool = False


@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    """Carrega a configuracao uma unica vez por processo."""
    return DatabaseSettings()  # type: ignore[call-arg]


def _validar_driver_assincrono(url: str) -> None:
    """Falha cedo e com mensagem clara se a URL nao usar driver assincrono.

    Colar `postgresql://` no `.env` e um erro comum. Sem esta guarda, o problema
    so apareceria no primeiro acesso ao banco, com um erro interno do SQLAlchemy
    cuja mensagem nao aponta para a causa real.
    """
    try:
        dialeto = make_url(url).get_dialect()
    except (ArgumentError, NoSuchModuleError) as erro:
        raise ValueError(
            f"URL de banco invalida: {erro}. "
            f"Esperado um driver assincrono, por exemplo "
            f"'{_DRIVER_ESPERADO}://usuario:senha@host:5432/banco'."
        ) from erro

    if not getattr(dialeto, "is_async", False):
        raise ValueError(
            f"A URL do banco precisa usar um driver assincrono. "
            f"Recebido '{make_url(url).drivername}', que e sincrono. "
            f"Use '{_DRIVER_ESPERADO}', por exemplo "
            f"'{_DRIVER_ESPERADO}://usuario:senha@host:5432/banco'."
        )


def create_database_engine(url: str, *, echo: bool = False) -> AsyncEngine:
    """Cria o engine assincrono.

    Args:
        url: URL de conexao com driver assincrono (`postgresql+asyncpg://...`).
        echo: emite no log todo SQL gerado. Util para depurar, ruidoso no dia a dia.

    Returns:
        AsyncEngine configurado.

    Raises:
        ValueError: se a URL nao usar um driver assincrono.
    """
    _validar_driver_assincrono(url)

    return create_async_engine(
        url,
        echo=echo,
        # A Neon encerra conexoes ociosas. Sem o pre-ping, a aplicacao pegaria
        # uma conexao morta do pool e falharia na primeira query apos o ocio.
        pool_pre_ping=True,
        # Recicla conexoes antes do limite tipico de inatividade do provedor.
        pool_recycle=300,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Cria a fabrica de sessoes vinculada ao engine.

    `expire_on_commit=False` e obrigatorio aqui: com o padrao `True`, acessar um
    atributo depois do commit dispara recarga lazy, e em codigo assincrono isso
    levanta `MissingGreenlet` no momento em que o FastAPI serializa a resposta.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
    )


_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Devolve o engine do processo, criando-o na primeira chamada."""
    global _engine

    if _engine is None:
        configuracao = get_database_settings()
        _engine = create_database_engine(
            configuracao.database_url,
            echo=configuracao.database_echo,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Devolve a fabrica de sessoes do processo, criando-a na primeira chamada."""
    global _session_factory

    if _session_factory is None:
        _session_factory = create_session_factory(get_engine())
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependencia do FastAPI que fornece uma sessao por requisicao.

    Nao faz commit automatico: quem decide o limite da transacao e o service,
    porque regras como a transicao de versao ativa de um documento (T022)
    precisam agrupar varias operacoes em uma unica transacao.

    O rollback em caso de excecao evita que uma sessao com estado sujo volte
    ao pool e contamine a proxima requisicao.
    """
    fabrica = get_session_factory()

    async with fabrica() as sessao:
        try:
            yield sessao
        except Exception:
            await sessao.rollback()
            raise


async def dispose_engine() -> None:
    """Fecha o pool de conexoes. Chamado no encerramento da aplicacao e nos testes."""
    global _engine, _session_factory

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _session_factory = None
