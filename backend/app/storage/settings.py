"""Configuracao do Supabase Storage, lida de variaveis de ambiente."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["SupabaseStorageSettings", "get_supabase_storage_settings"]


class SupabaseStorageSettings(BaseSettings):
    """Credenciais e bucket usados para gravar arquivos originais."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str
    # Service role key: o backend grava arquivos ignorando Row Level
    # Security. Nunca e exposta ao frontend.
    supabase_service_role_key: str
    supabase_storage_bucket: str = "documentos-originais"


@lru_cache(maxsize=1)
def get_supabase_storage_settings() -> SupabaseStorageSettings:
    """Carrega a configuracao uma unica vez por processo."""
    return SupabaseStorageSettings()  # type: ignore[call-arg]
