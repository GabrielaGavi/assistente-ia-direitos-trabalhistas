"""Acesso ao PostgreSQL para conversas, mensagens e as citacoes que geram."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.citations.models import Citation
from app.conversations.models import Conversation, Message

__all__ = ["ConversationRepository"]


class ConversationRepository:
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

    async def add_conversation(self, conversation: Conversation) -> None:
        self._session.add(conversation)
        await self._session.flush()

    async def get_conversation(self, conversation_id: UUID) -> Conversation | None:
        return await self._session.scalar(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.deleted_at.is_(None)
            )
        )

    async def list_conversations(
        self, user_id: UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[Conversation], int]:
        filtros = (Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        total = await self._session.scalar(
            select(func.count()).select_from(Conversation).where(*filtros)
        )
        items = await self._session.scalars(
            select(Conversation)
            .where(*filtros)
            .order_by(Conversation.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(items), total or 0

    async def add_message(self, message: Message) -> None:
        self._session.add(message)
        await self._session.flush()

    async def list_anonymous_conversations(
        self, session_id: UUID, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[Conversation], int]:
        filters = (
            Conversation.anonymous_session_id == session_id,
            Conversation.deleted_at.is_(None),
        )
        total = await self._session.scalar(
            select(func.count()).select_from(Conversation).where(*filters)
        )
        items = await self._session.scalars(
            select(Conversation)
            .where(*filters)
            .order_by(Conversation.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(items), total or 0

    async def list_messages(self, conversation_id: UUID) -> list[Message]:
        return list(
            await self._session.scalars(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.asc())
            )
        )

    async def add_citation(self, citation: Citation) -> None:
        self._session.add(citation)
        await self._session.flush()

    async def list_citations_by_message_ids(self, message_ids: list[UUID]) -> list[Citation]:
        if not message_ids:
            return []
        return list(
            await self._session.scalars(
                select(Citation)
                .where(Citation.message_id.in_(message_ids))
                .order_by(Citation.citation_number.asc())
            )
        )
