"""Modelo das fontes juridicas oficiais.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T017
    Requisito: FR-001
"""

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["Source"]


class Source(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Orgao emissor de legislacao ou repositorio oficial."""

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # A sigla identifica a fonte na citacao exibida ao usuario ("Planalto").
    # Duplica-la tornaria a referencia ambigua, por isso e unica.
    short_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)

    base_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<Source {self.short_name}>"
