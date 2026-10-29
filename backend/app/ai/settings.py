"""Configuracao do provider de IA (xAI / Grok), lida de variaveis de ambiente.

Mesmo padrao de `DatabaseSettings` em `app.shared.database`: uma classe
`BaseSettings` dedicada por integracao externa, cacheada por processo via
`lru_cache`, em vez de um unico `AppSettings` global.
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["GrokSettings", "get_grok_settings"]


class GrokSettings(BaseSettings):
    """Credenciais e modelo usados nas chamadas a API da xAI."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    xai_api_key: str
    # Mantido configuravel: a xAI muda a lista de modelos disponiveis com
    # frequencia, e travar o nome no codigo exigiria deploy para trocar.
    # "grok-4" nao existe na lista oficial (docs.x.ai/docs/models); o padrao
    # usa o modelo de uso geral recomendado pela documentacao.
    xai_model: str = "grok-4.7"

    @field_validator("xai_api_key")
    @classmethod
    def _chave_nao_pode_ser_vazia(cls, valor: str) -> str:
        """Falha cedo e com causa clara, em vez de deixar a xAI rejeitar depois.

        `str` sozinho aceita "" ou so espacos -- um `.env` com
        `XAI_API_KEY=` (sem valor) passaria pela validacao do pydantic e so
        falharia na primeira chamada de rede, com um erro generico da xAI que
        nao aponta para a causa real. `.strip()` tambem absorve o caso comum
        de colar a chave com um espaco ou quebra de linha a mais.
        """
        chave = valor.strip()
        if not chave:
            raise ValueError(
                "XAI_API_KEY esta vazia. Gere uma chave em "
                "https://console.x.ai/team/default/api-keys e configure-a em "
                "backend/.env."
            )
        return chave


@lru_cache(maxsize=1)
def get_grok_settings() -> GrokSettings:
    """Carrega a configuracao uma unica vez por processo."""
    return GrokSettings()  # type: ignore[call-arg]
