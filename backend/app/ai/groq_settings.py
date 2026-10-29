"""Configuracao do provider de IA (Groq), lida de variaveis de ambiente.

Mesmo padrao de `GrokSettings`: uma classe `BaseSettings` dedicada,
cacheada por processo via `lru_cache`.
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["GroqSettings", "get_groq_settings"]


class GroqSettings(BaseSettings):
    """Credenciais e modelo usados nas chamadas a API da Groq."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    groq_api_key: str
    # "openai/gpt-oss-20b" (e nao "llama-3.3-70b-versatile", o modelo citado
    # no README/OVERVIEW original) porque so os modelos da familia GPT-OSS e
    # Qwen suportam Structured Outputs em modo "strict" na Groq hoje --
    # exigido por `classify_document` para garantir que a resposta sempre
    # valide contra `DocumentClassification`. O Llama 3.3 70B so suporta
    # "JSON Object Mode" (JSON valido, sem schema garantido), o que exigiria
    # tratar falha de validacao como caso normal, nao excepcional. Ver
    # https://console.groq.com/docs/structured-outputs e /docs/models.
    groq_model: str = "openai/gpt-oss-20b"

    @field_validator("groq_api_key")
    @classmethod
    def _chave_nao_pode_ser_vazia(cls, valor: str) -> str:
        """Falha cedo e com causa clara, em vez de deixar a Groq rejeitar depois.

        Mesmo raciocinio de `GrokSettings._chave_nao_pode_ser_vazia`: `str`
        sozinho aceita "" ou so espacos, e `.strip()` absorve o caso comum de
        colar a chave com espaco/quebra de linha a mais.
        """
        chave = valor.strip()
        if not chave:
            raise ValueError(
                "GROQ_API_KEY esta vazia. Gere uma chave em "
                "https://console.groq.com/keys e configure-a em backend/.env."
            )
        return chave


@lru_cache(maxsize=1)
def get_groq_settings() -> GroqSettings:
    """Carrega a configuracao uma unica vez por processo."""
    return GroqSettings()  # type: ignore[call-arg]
