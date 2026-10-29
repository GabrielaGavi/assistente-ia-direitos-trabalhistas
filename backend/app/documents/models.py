"""Modelo dos documentos normativos versionados.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T018
    Requisitos: FR-002, FR-003, FR-004
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UpdatedAtMixin, UUIDPrimaryKeyMixin

__all__ = ["Document", "DocumentStatus"]


class DocumentStatus(str, Enum):
    """Ciclo de vida de um documento normativo."""

    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Document(Base, UUIDPrimaryKeyMixin, TimestampMixin, UpdatedAtMixin):
    """Uma redacao especifica de uma norma, identificada por versao.

    Versoes antigas nunca sao apagadas: uma conversa de meses atras precisa
    continuar apontando para a redacao que vigorava na epoca, senao a
    auditoria da resposta perde o sentido.
    """

    __tablename__ = "documents"

    source_id: Mapped[UUID] = mapped_column(ForeignKey("sources.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Identificador estavel da norma entre versoes, ex. "clt-decreto-lei-5452-1943".
    logical_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # SHA-256 em hexadecimal ocupa exatamente 64 caracteres. Serve para
    # detectar reenvio do mesmo conteudo e evitar versao duplicada.
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)

    published_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Nasce inativo: o documento ainda nao foi auditado e nao pode fundamentar
    # resposta nenhuma ate ser ativado explicitamente.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    status: Mapped[DocumentStatus] = mapped_column(
        String(20), nullable=False, default=DocumentStatus.PROCESSING
    )

    # Caminho do arquivo original (PDF/etc.) no Supabase Storage, relativo ao
    # bucket -- nunca uma URL publica: o bucket pode ser privado e exigir URL
    # assinada na leitura. Nulo para documentos sem arquivo binario de origem
    # (ex.: cadastrados so com os trechos ja estruturados).
    original_file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "source_id",
            "logical_name",
            "version",
            name="uq_document_source_logical_version",
        ),
        # FR-004: no maximo uma versao ativa por norma logica.
        #
        # Indice PARCIAL, e nao UniqueConstraint comum: um unique sobre
        # (source_id, logical_name) proibiria duas versoes *inativas* da mesma
        # norma -- exatamente o historico que precisamos preservar. A clausula
        # WHERE restringe a regra as linhas ativas.
        Index(
            "uq_document_versao_ativa",
            "source_id",
            "logical_name",
            unique=True,
            postgresql_where=text("is_active"),
        ),
    )

    def __repr__(self) -> str:
        return f"<Document {self.logical_name} v{self.version} ativo={self.is_active}>"
