"""Modelo de usuario e autenticacao por email/senha.

Escopo reduzido de proposito em relacao ao OVERVIEW TECNICO.md: sem
`AuthIdentity` separada (nao ha OAuth do Google implementado ainda) e sem
tabela de refresh tokens (ver `app/auth/security.py`). Quando OAuth for
adicionado, a tabela `AuthIdentity` pode ser introduzida sem quebrar `User`.
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UpdatedAtMixin, UUIDPrimaryKeyMixin

__all__ = ["User", "UserRole"]


class UserRole(str, Enum):
    """RBAC minimo: ADMIN administra a base de conhecimento, USER conversa."""

    USER = "USER"
    ADMIN = "ADMIN"


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin, UpdatedAtMixin):
    __tablename__ = "users"

    # unique=True ja cria o indice que a constraint exige -- index=True seria
    # redundante (e trocaria o nome da constraint que o repositorio depende
    # de conhecer para traduzir violacao em EmailAlreadyRegisteredError).
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Hash do bcrypt (inclui o salt); nunca a senha em texto puro.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(String(20), nullable=False, default=UserRole.USER)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    def __repr__(self) -> str:
        """Omite `password_hash`: mesmo o hash nao deveria aparecer em log."""
        return f"<User {self.email} role={self.role}>"
