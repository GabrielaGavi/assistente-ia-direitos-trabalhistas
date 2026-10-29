"""Contratos de entrada/saida do cadastro, login e perfil do usuario."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.auth.models import UserRole

__all__ = ["TokenResponse", "UserLogin", "UserRegister", "UserResponse"]


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str
    role: UserRole
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
