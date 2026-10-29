"""Endpoints de cadastro, login e perfil do usuario autenticado."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.anonymous.repository import AnonymousRepository
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.auth.repository import UserRepository
from app.auth.schemas import TokenResponse, UserLogin, UserRegister, UserResponse
from app.auth.security import create_access_token
from app.auth.service import AuthService, EmailAlreadyRegisteredError, InvalidCredentialsError
from app.auth.settings import get_auth_settings
from app.shared.database import get_session

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar novo usuario",
    responses={409: {"description": "Email ja cadastrado"}},
)
async def register(
    payload: UserRegister,
    session: Annotated[AsyncSession, Depends(get_session)],
    anonymous_token: Annotated[str | None, Header(alias="X-Anonymous-Token")] = None,
) -> TokenResponse:
    try:
        user = await AuthService(UserRepository(session)).register(**payload.model_dump())
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    await AnonymousRepository(session).claim(anonymous_token, user.id)
    return _token_response(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar e obter token de acesso",
    responses={401: {"description": "Email ou senha invalidos"}},
)
async def login(
    payload: UserLogin,
    session: Annotated[AsyncSession, Depends(get_session)],
    anonymous_token: Annotated[str | None, Header(alias="X-Anonymous-Token")] = None,
) -> TokenResponse:
    try:
        user = await AuthService(UserRepository(session)).login(**payload.model_dump())
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(error)) from error
    await AnonymousRepository(session).claim(anonymous_token, user.id)
    return _token_response(user)


@router.get("/me", response_model=UserResponse, summary="Perfil do usuario autenticado")
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)


def _token_response(user: User) -> TokenResponse:
    token = create_access_token(user.id, get_auth_settings())
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))
