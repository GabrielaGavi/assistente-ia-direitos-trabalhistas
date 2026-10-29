"""Pipeline minimo do RAG: embedding da pergunta, busca vetorial e geracao.

Escopo deliberadamente reduzido (decisao explicita do produto): busca por
similaridade de cosseno direto no pgvector, sem busca hibrida (FTS + RRF) nem
reranker. Threshold/evidencia minima tambem ficam fora desta etapa -- a unica
guarda de "sem evidencia" aqui e a lista de chunks recuperados vir vazia.
"""

from typing import Protocol
from uuid import UUID

from app.ai.provider import LLMProvider
from app.documents.chunk_models import DocumentChunk
from app.embeddings.provider import EmbeddingProvider
from app.rag.schemas import RagAnswer, RagAnswerStatus, RetrievedChunk

__all__ = ["ChunkRetriever", "RagService"]

_MENSAGEM_SEM_EVIDENCIA = (
    "Nao encontrei evidencia suficiente na base de conhecimento para responder "
    "a essa pergunta com seguranca."
)


class ChunkRetriever(Protocol):
    async def search_similar_chunks(
        self,
        *,
        embedding: list[float],
        limit: int,
        source_id: UUID | None = None,
    ) -> list[DocumentChunk]: ...


class RagService:
    def __init__(
        self,
        retriever: ChunkRetriever,
        embedding_provider: EmbeddingProvider,
        llm_provider: LLMProvider,
        *,
        top_k: int = 5,
    ) -> None:
        self._retriever = retriever
        self._embedding_provider = embedding_provider
        self._llm_provider = llm_provider
        self._top_k = top_k

    async def answer(self, question: str, *, source_id: UUID | None = None) -> RagAnswer:
        pergunta_embedding = await self._embedding_provider.embed(question)
        chunks = await self._retriever.search_similar_chunks(
            embedding=pergunta_embedding,
            limit=self._top_k,
            source_id=source_id,
        )

        if not chunks:
            return RagAnswer(
                status=RagAnswerStatus.INSUFFICIENT_EVIDENCE,
                answer=_MENSAGEM_SEM_EVIDENCIA,
                citations=[],
            )

        contexto = "\n\n".join(
            f"[{indice + 1}] {chunk.content}" for indice, chunk in enumerate(chunks)
        )
        resposta = await self._llm_provider.generate_answer(question, contexto)

        return RagAnswer(
            status=RagAnswerStatus.ANSWERED,
            answer=resposta,
            citations=[RetrievedChunk.model_validate(chunk) for chunk in chunks],
        )
