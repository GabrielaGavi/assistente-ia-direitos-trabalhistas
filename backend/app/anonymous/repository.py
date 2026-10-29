import hashlib
import secrets
from datetime import timedelta
from uuid import UUID

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.anonymous.models import AnonymousSession
from app.shared.uuid import utc_now


class AnonymousSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    anonymous_questions_limit: int = Field(default=3, ge=1)
    anonymous_session_minutes: int = Field(default=240, ge=1)


class AnonymousRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def find(self, token: str | None, *, lock: bool = False) -> AnonymousSession | None:
        if not token or len(token) > 128:
            return None
        statement = select(AnonymousSession).where(
            AnonymousSession.token_hash == hashlib.sha256(token.encode()).hexdigest(),
            AnonymousSession.expires_at > utc_now(),
        )
        if lock:
            statement = statement.with_for_update()
        return await self.session.scalar(statement)

    async def bootstrap(self, token: str | None) -> tuple[AnonymousSession, str]:
        existing = await self.find(token)
        if existing is not None:
            assert token is not None
            return existing, token
        settings = AnonymousSettings()
        token = secrets.token_urlsafe(32)
        expires = utc_now() + timedelta(minutes=settings.anonymous_session_minutes)
        anonymous = AnonymousSession(
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            questions_used=0,
            questions_limit=settings.anonymous_questions_limit,
            reset_at=expires,
            expires_at=expires,
        )
        self.session.add(anonymous)
        await self.session.commit()
        await self.session.refresh(anonymous)
        return anonymous, token

    async def reserve(self, session_id: UUID) -> bool:
        # UPDATE condicional evita exceder a quota com requests concorrentes.
        result = await self.session.scalar(
            update(AnonymousSession)
            .where(
                AnonymousSession.id == session_id,
                AnonymousSession.expires_at > utc_now(),
                AnonymousSession.questions_used < AnonymousSession.questions_limit,
            )
            .values(questions_used=AnonymousSession.questions_used + 1)
            .returning(AnonymousSession.id)
            .execution_options(synchronize_session=False)
        )
        await self.session.commit()
        return result is not None

    async def refund(self, session_id: UUID) -> None:
        await self.session.execute(
            update(AnonymousSession)
            .where(
                AnonymousSession.id == session_id,
                AnonymousSession.questions_used > 0,
            )
            .values(questions_used=AnonymousSession.questions_used - 1)
            .execution_options(synchronize_session=False)
        )
        await self.session.commit()

    async def claim(self, token: str | None, user_id: UUID) -> None:
        # Lock serializa dois logins tentando migrar a mesma sessao.
        from app.conversations.models import Conversation

        anonymous = await self.find(token, lock=True)
        if anonymous is None:
            return
        await self.session.execute(
            update(Conversation)
            .where(Conversation.anonymous_session_id == anonymous.id)
            .values(user_id=user_id, anonymous_session_id=None)
            .execution_options(synchronize_session=False)
        )
        anonymous.expires_at = utc_now()
        await self.session.commit()
