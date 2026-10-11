"""Testes da configuracao da propria suite.

Existem por causa de um bug real: o `conftest.py` lia `TEST_DATABASE_URL` com
`os.getenv`, que nao enxerga o `backend/.env`. Quem editasse a variavel la nao
veria efeito nenhum e a suite seguiria apontando para o banco padrao -- sem
erro, sem aviso. O defeito passou despercebido porque o padrao e o valor do
`.env.example` sao identicos.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T006 (correcao encontrada em auditoria)
"""

from pathlib import Path

import pytest

from tests.conftest import URL_PADRAO_DE_TESTE, ConfiguracaoDeTeste

pytestmark = pytest.mark.unit

URL_FICTICIA = "postgresql+asyncpg://usuario:senha@exemplo:5432/outro_banco"


class TestPrecedenciaDaConfiguracao:
    def test_usa_o_padrao_quando_nada_esta_definido(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Sem variavel e sem .env, a suite roda contra o banco do docker-compose."""
        monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
        monkeypatch.chdir(tmp_path)

        assert ConfiguracaoDeTeste().test_database_url == URL_PADRAO_DE_TESTE

    def test_le_a_url_do_arquivo_env(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        """Regressao do bug: antes da correcao, o .env era ignorado."""
        monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
        (tmp_path / ".env").write_text(f"TEST_DATABASE_URL={URL_FICTICIA}\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        assert ConfiguracaoDeTeste().test_database_url == URL_FICTICIA

    def test_variavel_de_ambiente_vence_o_arquivo_env(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """Permite apontar a suite para outro banco pontualmente, sem editar arquivo."""
        (tmp_path / ".env").write_text(
            "TEST_DATABASE_URL=postgresql+asyncpg://do-arquivo/banco\n", encoding="utf-8"
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("TEST_DATABASE_URL", URL_FICTICIA)

        assert ConfiguracaoDeTeste().test_database_url == URL_FICTICIA

    def test_ignora_outras_variaveis_do_env(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """O .env tem DATABASE_URL, APP_ENV e outras; nenhuma pode quebrar a carga."""
        monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
        (tmp_path / ".env").write_text(
            "DATABASE_URL=postgresql+asyncpg://dev/banco\n"
            "DATABASE_ECHO=true\n"
            "APP_ENV=development\n"
            f"TEST_DATABASE_URL={URL_FICTICIA}\n",
            encoding="utf-8",
        )
        monkeypatch.chdir(tmp_path)

        assert ConfiguracaoDeTeste().test_database_url == URL_FICTICIA
