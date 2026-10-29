"""Dependencias do FastAPI para autenticacao e RBAC."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User, UserRole
from app.auth.repository import UserRepository
from app.auth.security import InvalidTokenError, decode_access_token
from app.auth.settings import get_auth_settings
from app.shared.database import get_session

__all__ = ["get_current_user", "require_admin"]

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
