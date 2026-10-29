from datetime import datetime

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin


class AnonymousSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "anonymous_sessions"
    __table_args__ = (
        CheckConstraint("questions_used >= 0 AND questions_limit > 0", name="ck_anonymous_quota"),
    )

    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    questions_used: Mapped[int] = mapped_column(default=0, nullable=False)
    questions_limit: Mapped[int] = mapped_column(nullable=False)
    reset_at: Mapped[datetime] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False, index=True)
