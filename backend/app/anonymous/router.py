from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.anonymous.repository import AnonymousRepository
from app.shared.database import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class AnonymousResponse(BaseModel):
    anonymous_token: str
    questions_used: int
    questions_limit: int
    expires_at: datetime


@router.post(
    "/anonymous", response_model=AnonymousResponse, summary="Iniciar ou retomar acesso sem conta"
)
async def bootstrap_anonymous(
    session: Annotated[AsyncSession, Depends(get_session)],
    anonymous_token: Annotated[str | None, Header(alias="X-Anonymous-Token")] = None,
) -> AnonymousResponse:
    anonymous, token = await AnonymousRepository(session).bootstrap(anonymous_token)
    return AnonymousResponse(
        anonymous_token=token,
        questions_used=anonymous.questions_used,
        questions_limit=anonymous.questions_limit,
        expires_at=anonymous.expires_at,
    )
