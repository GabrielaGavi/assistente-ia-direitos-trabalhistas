"""Modelo de conversas e mensagens.

Inclui acesso anonimo com migracao de propriedade ao entrar na conta.
Sem `AIExecution` (uma tentativa por
mensagem, sem historico de retries) e sem streaming SSE (a resposta e
sincrona). `Message.status` ainda reserva `FAILED` para quando o provider de
IA falhar, para o front distinguir "sem resposta" de "erro".
"""

from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UpdatedAtMixin, UUIDPrimaryKeyMixin

__all__ = ["Conversation", "Message", "MessageRole", "MessageStatus"]


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"


class MessageStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Conversation(Base, UUIDPrimaryKeyMixin, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "conversations"
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND anonymous_session_id IS NULL) OR "
            "(user_id IS NULL AND anonymous_session_id IS NOT NULL)",
            name="ck_conversation_owner",
        ),
    )

    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    anonymous_session_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("anonymous_sessions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        return f"<Conversation {self.id!s} user={self.user_id!s}>"


class Message(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(String(20), nullable=False)
    status: Mapped[MessageStatus] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return f"<Message {self.role} status={self.status}>"
