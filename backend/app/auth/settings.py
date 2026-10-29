"""Configuracao de autenticacao (JWT), lida de variaveis de ambiente."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["AuthSettings", "get_auth_settings"]


class AuthSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    # Sem refresh token nesta etapa (ver app/auth/security.py): expiracao mais
    # longa que os ~15 minutos do OVERVIEW para nao forcar relogin constante.
    jwt_expires_minutes: int = 60

    @field_validator("jwt_secret_key")
    @classmethod
    def _chave_nao_pode_ser_vazia(cls, valor: str) -> str:
        chave = valor.strip()
        if not chave:
            raise ValueError(
                "JWT_SECRET_KEY esta vazia. Gere uma com "
                "`python -c \"import secrets; print(secrets.token_urlsafe(48))\"` "
                "e configure-a em backend/.env."
            )
        return chave


@lru_cache(maxsize=1)
def get_auth_settings() -> AuthSettings:
    """Carrega a configuracao uma unica vez por processo."""
    return AuthSettings()  # type: ignore[call-arg]
