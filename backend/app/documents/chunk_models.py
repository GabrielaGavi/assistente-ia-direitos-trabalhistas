"""Modelo dos trechos normativos estruturados.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T025
    Requisito: FR-005
"""

from typing import Any
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["DocumentChunk"]

# Dimensao do modelo de embedding usado pelo RAG (ver app/embeddings). Mudar
# de modelo com dimensao diferente exige nova migration para a coluna.
EMBEDDING_DIMENSIONS = 384


class DocumentChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Unidade atomica de evidencia: o trecho literal que fundamenta a resposta."""

    __tablename__ = "document_chunks"

    # ondelete CASCADE: um chunk sem documento seria evidencia sem norma de
    # origem, que e justamente o que o SC-002 proibe ("zero citacoes apontando
    # para documentos orfaos").
    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Desnormalizado de proposito: a exibicao da citacao precisa da fonte, e
    # guardar o vinculo direto evita um JOIN extra no caminho mais quente.
    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False)

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)

    # Text, nao String(n): truncar um artigo longo quebraria a fidelidade do
    # trecho, que e o que a citacao promete.
    content: Mapped[str] = mapped_column(Text, nullable=False)

    official_url: Mapped[str] = mapped_column(String(1000), nullable=False)

    # Opcionais: preambulos e ementas nao pertencem a artigo, secao ou
    # paragrafo nenhum, e nem toda norma vem de PDF paginado.
    article: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    paragraph: Mapped[str | None] = mapped_column(String(50), nullable=True)
    page_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    metadata_extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Vetor semantico do `content`, usado pela busca por similaridade do RAG.
    # Nulo até o chunk ser processado pelo `EmbeddingProvider` -- chunks
    # recem-criados nao entram na busca vetorial enquanto isso nao acontece.
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS), nullable=True
    )

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_chunk_document_index"),
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk #{self.chunk_index} {self.article or 'sem artigo'}>"
