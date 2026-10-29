"""Dependencias do FastAPI para autenticacao e RBAC."""

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.anonymous.repository import AnonymousRepository
from app.auth.models import User, UserRole
from app.auth.repository import UserRepository
from app.auth.security import InvalidTokenError, decode_access_token
from app.auth.settings import get_auth_settings
from app.shared.database import get_session

__all__ = ["ChatActor", "get_chat_actor", "get_current_user", "require_admin"]

# tokenUrl e so documentacao do Swagger ("Authorize"); o login real e
# POST /api/v1/auth/login, ja que o corpo e JSON e nao o form OAuth2 padrao.
_esquema_bearer = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: Annotated[str | None, Depends(_esquema_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    erro_nao_autenticado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao autenticado.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise erro_nao_autenticado

    try:
        user_id = decode_access_token(token, get_auth_settings())
    except InvalidTokenError as erro:
        raise erro_nao_autenticado from erro

    user = await UserRepository(session).get_by_id(user_id)
    if user is None or not user.is_active:
        raise erro_nao_autenticado
    return user


async def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requer papel de administrador.",
        )
    return current_user


@dataclass(frozen=True)
class ChatActor:
    user_id: UUID | None = None
    anonymous_session_id: UUID | None = None


async def get_chat_actor(
    token: Annotated[str | None, Depends(_esquema_bearer)],
    session: Annotated[AsyncSession, Depends(get_session)],
    anonymous_token: Annotated[str | None, Header(alias="X-Anonymous-Token")] = None,
) -> ChatActor:
    if token is not None:
        user = await get_current_user(token, session)
        return ChatActor(user_id=user.id)
    anonymous = await AnonymousRepository(session).find(anonymous_token)
    if anonymous is None:
        raise HTTPException(
            status_code=401, detail="Sessao temporaria expirada. Inicie uma nova sessao."
        )
    return ChatActor(anonymous_session_id=anonymous.id)
