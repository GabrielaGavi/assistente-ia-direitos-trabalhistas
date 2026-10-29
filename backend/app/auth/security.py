"""Hash de senha (bcrypt) e token de acesso (JWT), sem estado nem I/O.

Sem refresh token nesta etapa: exigiria uma tabela de sessoes, rotacao e
revogacao (ver OVERVIEW TECNICO.md, secao 11) -- escopo proprio, deixado para
quando o fluxo de login precisar de sessoes de longa duracao.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
import jwt

from app.auth.settings import AuthSettings

__all__ = [
    "InvalidTokenError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]


class InvalidTokenError(ValueError):
    """Token ausente, expirado, malformado ou com assinatura invalida."""


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(user_id: UUID, settings: AuthSettings) -> str:
    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": agora,
        "exp": agora + timedelta(minutes=settings.jwt_expires_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: AuthSettings) -> UUID:
    """Devolve o `user_id` do token ou levanta `InvalidTokenError`."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as erro:
        raise InvalidTokenError("Token de acesso invalido ou expirado.") from erro

    try:
        return UUID(payload["sub"])
    except (KeyError, ValueError) as erro:
        raise InvalidTokenError("Token de acesso sem identificador de usuario valido.") from erro
