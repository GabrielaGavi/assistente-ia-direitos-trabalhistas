"""Precedencia e validacao da configuracao do provider Groq.

Mesmo padrao de `test_ai_settings.py` (Grok): `BaseSettings` so ve `.env` se
o teste nao capturar isso, o defeito passa despercebido. A validacao de
chave vazia segue o mesmo raciocinio ja aplicado ao Grok.
"""

import pytest

from app.ai.groq_settings import GroqSettings

pytestmark = pytest.mark.unit


class TestGroqSettings:
    def test_usa_modelo_padrao_quando_nao_definido(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("GROQ_MODEL", raising=False)
        monkeypatch.setenv("GROQ_API_KEY", "chave-fake")
        monkeypatch.chdir(tmp_path)

        settings = GroqSettings()

        assert settings.groq_api_key == "chave-fake"
        assert settings.groq_model == "openai/gpt-oss-20b"

    def test_variavel_de_ambiente_sobrescreve_modelo_padrao(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "chave-fake")
        monkeypatch.setenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        monkeypatch.chdir(tmp_path)

        assert GroqSettings().groq_model == "llama-3.3-70b-versatile"

    def test_le_a_chave_do_arquivo_env(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        (tmp_path / ".env").write_text("GROQ_API_KEY=chave-do-arquivo\n", encoding="utf-8")
        monkeypatch.chdir(tmp_path)

        assert GroqSettings().groq_api_key == "chave-do-arquivo"

    def test_falha_cedo_sem_api_key_configurada(self, monkeypatch, tmp_path) -> None:
        """Variavel totalmente ausente: pydantic rejeita antes do validator rodar."""
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="groq_api_key"):
            GroqSettings()

    def test_falha_com_api_key_vazia(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "")
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            GroqSettings()

    def test_falha_com_api_key_so_espacos(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "   ")
        monkeypatch.chdir(tmp_path)

        with pytest.raises(ValueError, match="GROQ_API_KEY"):
            GroqSettings()

    def test_remove_espacos_e_quebras_de_linha_nas_pontas(self, monkeypatch, tmp_path) -> None:
        monkeypatch.setenv("GROQ_API_KEY", "  chave-com-espaco-colado  \n")
        monkeypatch.chdir(tmp_path)

        assert GroqSettings().groq_api_key == "chave-com-espaco-colado"
