"""Configuracao do provider de embeddings, lida de variaveis de ambiente.

Mesmo padrao de `GrokSettings`: classe `BaseSettings` dedicada, cacheada por
processo via `lru_cache`.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["EmbeddingSettings", "get_embedding_settings"]


class EmbeddingSettings(BaseSettings):
    """Modelo local (sentence-transformers) usado para gerar embeddings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Multilingue, 384 dimensoes, roda em CPU -- sem custo de API. Mudar de
    # modelo com dimensao diferente exige nova migration (ver
    # app.documents.chunk_models.EMBEDDING_DIMENSIONS).
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def get_embedding_settings() -> EmbeddingSettings:
    """Carrega a configuracao uma unica vez por processo."""
    return EmbeddingSettings()
