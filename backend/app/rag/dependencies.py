"""Composicao do `RagService` para uso em rotas FastAPI.

Fica separado de `app/rag/service.py` de proposito: `RagService` so conhece
os `Protocol`s (`ChunkRetriever`, `EmbeddingProvider`, `LLMProvider`); este
modulo e que decide os adapters concretos (Groq, sentence-transformers,
`DocumentRepository`), seguindo o mesmo limite entre porta e composicao
usado pelos outros `get_..._provider()` do projeto.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.groq_provider import get_groq_provider
from app.documents.repository import DocumentRepository
from app.embeddings.sentence_transformer_provider import get_embedding_provider
from app.rag.service import RagService
from app.shared.database import get_session

__all__ = ["get_rag_service"]


def get_rag_service(session: Annotated[AsyncSession, Depends(get_session)]) -> RagService:
    return RagService(
        retriever=DocumentRepository(session),
        embedding_provider=get_embedding_provider(),
        llm_provider=get_groq_provider(),
    )
