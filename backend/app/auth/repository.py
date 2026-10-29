"""Acesso ao PostgreSQL para usuarios."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User
from app.auth.service import EmailAlreadyRegisteredError

__all__ = ["UserRepository"]


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[None]:
        async with self._session.begin_nested():
            yield
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise

    async def get_by_email(self, email: str) -> User | None:
        return await self._session.scalar(select(User).where(User.email == email))

    async def get_by_id(self, user_id: UUID) -> User | None:
        return await self._session.scalar(select(User).where(User.id == user_id))

    async def count(self) -> int:
        return await self._session.scalar(select(func.count()).select_from(User)) or 0

    async def add(self, user: User) -> None:
        self._session.add(user)
        try:
            await self._session.flush()
        except IntegrityError as error:
            cause = error.orig.__cause__
            if (
                getattr(error.orig, "sqlstate", None) == "23505"
                and getattr(cause, "constraint_name", None) == "users_email_key"
            ):
                raise EmailAlreadyRegisteredError(user.email) from error
            raise
