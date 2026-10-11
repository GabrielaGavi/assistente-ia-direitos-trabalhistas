"""Modelo das citacoes rastreaveis.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T010
    Requisitos: FR-006, FR-007
"""

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["Citation"]


class Citation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Vinculo imutavel entre uma resposta do assistente e a evidencia legal.

    Nao tem `updated_at` de proposito. O data-model define a citacao como
    vinculo imutavel: se o texto citado pudesse ser editado depois, a resposta
    arquivada deixaria de ser auditavel -- nao haveria como saber o que o
    usuario de fato leu.
    """

    __tablename__ = "citations"

    # Sem ForeignKey: o dominio de conversas ainda nao existe, e cria-la agora
    # acoplaria esta feature a um modulo que sera especificado depois.
    message_id: Mapped[UUID] = mapped_column(nullable=False, index=True)

    # FR-006: a citacao so existe amarrada a um trecho real de documento.
    chunk_id: Mapped[UUID] = mapped_column(
        ForeignKey("document_chunks.id"), nullable=False, index=True
    )

    citation_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Copia literal do trecho no momento da resposta. Guardar a copia, e nao
    # so o ponteiro, preserva o que o usuario leu mesmo que a norma mude.
    original_quote: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("message_id", "citation_number", name="uq_citation_message_number"),
    )

    def __repr__(self) -> str:
        """Omite `original_quote`: o trecho e longo e o repr acaba em log."""
        return f"<Citation [{self.citation_number}] chunk={self.chunk_id!s}>"
