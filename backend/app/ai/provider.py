"""Porta (Ports and Adapters) para provedores de IA generativa.

O dominio depende apenas deste `Protocol`. `GrokLLMProvider` e o adapter
concreto; qualquer outro provedor pode substitui-lo sem alterar
`DocumentService` nem os testes que usam um fake.
"""

from typing import Protocol

from app.ai.schemas import DocumentClassification

__all__ = ["LLMProvider"]


class LLMProvider(Protocol):
    async def classify_document(self, text: str) -> DocumentClassification: ...
    async def generate_answer(self, question: str, context: str) -> str: ...
