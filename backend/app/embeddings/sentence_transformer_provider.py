"""Adapter concreto da porta `EmbeddingProvider`, usando sentence-transformers.

Roda em CPU, localmente, sem custo de API nem chave externa -- a contrapartida
e o tempo/memoria de carregar o modelo na primeira chamada (download unico do
Hugging Face, depois cacheado em disco) e a latencia de inferencia por chunk.
"""

import asyncio
from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.embeddings.settings import EmbeddingSettings, get_embedding_settings

__all__ = ["SentenceTransformerEmbeddingProvider", "get_embedding_provider"]


class SentenceTransformerEmbeddingProvider:
    """Gera embeddings localmente; o modelo so e carregado no primeiro uso."""

    def __init__(self, settings: EmbeddingSettings) -> None:
        self._model_name = settings.embedding_model
        self._model: SentenceTransformer | None = None

    def _modelo(self) -> SentenceTransformer:
        # Carregar aqui (e nao no __init__) evita baixar/alocar o modelo so
        # por o provider ter sido instanciado -- so quem efetivamente chama
        # `embed` paga esse custo.
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    async def embed(self, text: str) -> list[float]:
        # sentence-transformers e sincrono e usa CPU; roda numa thread para
        # nao bloquear o event loop do FastAPI durante a inferencia.
        return await asyncio.to_thread(self._codificar, text)

    def _codificar(self, text: str) -> list[float]:
        vetor = self._modelo().encode(text, normalize_embeddings=True)
        return vetor.tolist()


@lru_cache(maxsize=1)
def get_embedding_provider() -> SentenceTransformerEmbeddingProvider:
    """Instancia unica por processo, criada so quando efetivamente requisitada."""
    return SentenceTransformerEmbeddingProvider(get_embedding_settings())
