"""Porta (Ports and Adapters) para provedores de embeddings.

O dominio depende apenas deste `Protocol`. `SentenceTransformerEmbeddingProvider`
e o adapter concreto (local, sem custo de API); outro provedor pode
substitui-lo sem alterar quem consome embeddings.
"""

from typing import Protocol

__all__ = ["EmbeddingProvider"]


class EmbeddingProvider(Protocol):
    async def embed(self, text: str) -> list[float]: ...
