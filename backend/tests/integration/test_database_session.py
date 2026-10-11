"""Testes da camada de injecao de dependencia de sessao.

Cobrem `get_engine`, `get_session_factory`, `get_session` e `dispose_engine` --
as funcoes que o FastAPI usara como dependencia (T029) e que os testes
unitarios da T004 nao alcancam por exigirem banco real.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T004 (lacuna de cobertura identificada em auditoria)
"""

from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.shared import database as modulo_database
from app.shared.database import (
    dispose_engine,
    get_database_settings,
    get_engine,
    get_session,
    get_session_factory,
)

pytestmark = pytest.mark.integration


@pytest.fixture
async def ambiente_configurado(
    test_database_url: str, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[None]:
    """Aponta a configuracao global para o banco de testes e limpa os singletons.

    Os singletons do modulo sao estado de processo; sem a limpeza no final, um
    engine criado aqui vazaria para os testes seguintes.
    """
    monkeypatch.setenv("DATABASE_URL", test_database_url)
    monkeypatch.setenv("DATABASE_ECHO", "false")
    get_database_settings.cache_clear()
    await dispose_engine()

    yield

    await dispose_engine()
    get_database_settings.cache_clear()


class TestConfiguracao:
    async def test_le_a_url_do_ambiente(
        self, ambiente_configurado: None, test_database_url: str
    ) -> None:
        assert get_database_settings().database_url == test_database_url

    async def test_echo_desligado_por_padrao(self, ambiente_configurado: None) -> None:
        assert get_database_settings().database_echo is False


class TestSingletons:
    async def test_get_engine_devolve_sempre_a_mesma_instancia(
        self, ambiente_configurado: None
    ) -> None:
        """Um engine por processo: cada engine carrega seu proprio pool de
        conexoes, e criar varios esgotaria o limite de conexoes do banco."""
        assert get_engine() is get_engine()

    async def test_get_engine_devolve_async_engine(self, ambiente_configurado: None) -> None:
        assert isinstance(get_engine(), AsyncEngine)

    async def test_get_session_factory_devolve_sempre_a_mesma_instancia(
        self, ambiente_configurado: None
    ) -> None:
        assert get_session_factory() is get_session_factory()

    async def test_fabrica_usa_o_engine_do_processo(self, ambiente_configurado: None) -> None:
        assert get_session_factory().kw["bind"] is get_engine()


class TestGetSession:
    async def test_fornece_sessao_funcional(self, ambiente_configurado: None) -> None:
        gerador = get_session()
        sessao = await gerador.__anext__()

        try:
            assert isinstance(sessao, AsyncSession)
            assert (await sessao.execute(text("SELECT 1"))).scalar_one() == 1
        finally:
            await gerador.aclose()

    async def test_devolve_a_conexao_ao_pool_no_final(self, ambiente_configurado: None) -> None:
        """Uma conexao nao devolvida e um vazamento: depois de algumas
        requisicoes o pool esgota e a aplicacao trava esperando conexao.

        Verifica o pool em vez de `session.is_active`, que em SQLAlchemy 2.x
        indica o estado da transacao e nao se a sessao foi fechada.
        """
        pool = get_engine().pool
        ocupadas_antes = pool.checkedout()

        gerador = get_session()
        sessao = await gerador.__anext__()
        await sessao.execute(text("SELECT 1"))

        assert pool.checkedout() == ocupadas_antes + 1

        await gerador.aclose()

        assert pool.checkedout() == ocupadas_antes

    async def test_propaga_a_excecao_do_consumidor(self, ambiente_configurado: None) -> None:
        """A dependencia nao pode engolir o erro: o FastAPI precisa ve-lo."""
        gerador = get_session()
        await gerador.__anext__()

        with pytest.raises(ValueError, match="falha simulada"):
            await gerador.athrow(ValueError("falha simulada"))

    async def test_faz_rollback_quando_o_consumidor_falha(
        self, ambiente_configurado: None, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sem o rollback, uma sessao com estado sujo voltaria ao pool e
        contaminaria a requisicao seguinte."""
        chamadas: list[str] = []
        rollback_original = AsyncSession.rollback

        async def rollback_espiao(self: AsyncSession) -> None:
            chamadas.append("rollback")
            await rollback_original(self)

        monkeypatch.setattr(AsyncSession, "rollback", rollback_espiao)

        gerador = get_session()
        await gerador.__anext__()

        with pytest.raises(ValueError):
            await gerador.athrow(ValueError("falha simulada"))

        assert chamadas == ["rollback"]


class TestDisposeEngine:
    async def test_limpa_os_singletons(self, ambiente_configurado: None) -> None:
        """Chamado no encerramento da aplicacao e entre testes."""
        get_engine()
        get_session_factory()

        await dispose_engine()

        assert modulo_database._engine is None
        assert modulo_database._session_factory is None

    async def test_engine_seguinte_e_uma_nova_instancia(self, ambiente_configurado: None) -> None:
        primeiro = get_engine()

        await dispose_engine()

        assert get_engine() is not primeiro

    async def test_pode_ser_chamado_sem_engine_criado(self, ambiente_configurado: None) -> None:
        """Encerrar a aplicacao antes de qualquer requisicao nao pode quebrar."""
        await dispose_engine()
        await dispose_engine()
