"""adicionar embedding vetorial aos chunks

Revision ID: 800ce0dce698
Revises: 4e4c10fa5da5
Create Date: 2026-10-28 20:50:32.531147

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "800ce0dce698"
down_revision: str | Sequence[str] | None = "4e4c10fa5da5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_INDICE_EMBEDDING = "ix_document_chunks_embedding_cosine"


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.add_column(
        "document_chunks",
        sa.Column("embedding", Vector(384), nullable=True),
    )
    # HNSW com vector_cosine_ops: a busca do RAG usa distancia de cosseno
    # (ver OVERVIEW TECNICO.md, secao 33). Criar o indice com a tabela ainda
    # vazia e barato; recriar depois de popular milhoes de linhas nao seria.
    op.create_index(
        _INDICE_EMBEDDING,
        "document_chunks",
        ["embedding"],
        unique=False,
        postgresql_using="hnsw",
        postgresql_ops={"embedding": "vector_cosine_ops"},
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(_INDICE_EMBEDDING, table_name="document_chunks")
    op.drop_column("document_chunks", "embedding")
    # A extensao "vector" nao e removida aqui: outras tabelas podem depender
    # dela, e um DROP EXTENSION ... CASCADE seria destrutivo demais para um
    # downgrade automatico.
