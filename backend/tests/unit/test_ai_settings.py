"""Precedencia e validacao da configuracao do provider Grok.

Mesmo motivo do `test_conftest_config.py`: `BaseSettings` so ve `.env` se o
teste nao capturar isso, o defeito passa despercebido. A validacao de chave
vazia existe porque a auditoria encontrou uma `XAI_API_KEY` invalida em
producao -- falhar cedo, com mensagem clara, é melhor do que deixar a xAI
rejeitar a chamada de rede com um erro generico.
"""

import pytest

from app.ai.settings import GrokSettings

pytestmark = pytest.mark.unit


class TestGrokSettings:
    def test_usa_modelo_padrao_quando_nao_definido(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("XAI_MODEL", raising=False)
        monkeypatch.setenv("XAI_API_KEY", "chave-fake")
        monkeypatch.chdir(tmp_path)

        settings = GrokSettings()

        assert settings.xai_api_key == "chave-fake"
        assert settings.xai_model == "grok-4.7"

    def test_variavel_de_ambiente_sobrescreve_modelo_padrao(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("XAI_API_KEY", "chave-fake")
        monkeypatch.setenv("XAI_MODEL", "grok-5-fast")
        monkeypatch.chdir(tmp_path)

        assert GrokSettings().xai_model == "grok-5-fast"

    def test_le_a_chave_do_arquivo_env(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        (tmp_path / ".env").write_text("XAI_API_KEY=chave-do-arquivo\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        assert GrokSettings().xai_api_key == "chave-do-arquivo"

    def test_falha_cedo_sem_api_key_configurada(self, monkeypatch, tmp_path) -> None:
        """Variavel totalmente ausente: pydantic rejeita antes do validator rodar."""
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="xai_api_key"):
            GrokSettings()

    def test_falha_com_api_key_vazia(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("XAI_API_KEY", "")
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="XAI_API_KEY"):
            GrokSettings()

    def test_falha_com_api_key_so_espacos(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("XAI_API_KEY", "   ")
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="XAI_API_KEY"):
            GrokSettings()

    def test_remove_espacos_e_quebras_de_linha_nas_pontas(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("XAI_API_KEY", "  chave-com-espaco-colado  \n")
        monkeypatch.chdir(tmp_path)

        assert GrokSettings().xai_api_key == "chave-com-espaco-colado"
