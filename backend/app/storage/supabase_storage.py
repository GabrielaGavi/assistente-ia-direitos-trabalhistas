"""Adapter concreto da porta `StorageProvider`, usando a REST API do Supabase Storage.

Chama a API HTTP diretamente via `httpx` em vez de adicionar o SDK `supabase`
como dependencia -- o contrato e pequeno (um `POST` para gravar um objeto) e
isso evita trazer toda a superficie do cliente oficial so por isso.

Contrato: `POST {SUPABASE_URL}/storage/v1/object/{bucket}/{path}`, com
`apikey`/`Authorization: Bearer` usando a service role key e o corpo bruto do
arquivo. Confirmado contra a implementacao do cliente oficial
(`storage-js`), que chama exatamente este endpoint.
"""

from functools import lru_cache

import httpx

from app.storage.settings import SupabaseStorageSettings, get_supabase_storage_settings

__all__ = ["SupabaseStorageError", "SupabaseStorageProvider", "get_supabase_storage_provider"]


class SupabaseStorageError(RuntimeError):
    """A API do Supabase Storage respondeu com erro."""


class SupabaseStorageProvider:
    def __init__(self, settings: SupabaseStorageSettings) -> None:
        self._base_url = settings.supabase_url.rstrip("/")
        self._bucket = settings.supabase_storage_bucket
        self._headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
        }

    async def upload(self, path: str, content: bytes, *, content_type: str) -> str:
        caminho_limpo = path.strip("/")
        url = f"{self._base_url}/storage/v1/object/{self._bucket}/{caminho_limpo}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resposta = await client.post(
                url,
                content=content,
                headers={
                    **self._headers,
                    "Content-Type": content_type,
                    "x-upsert": "true",
                },
            )

        if resposta.status_code >= 400:
            raise SupabaseStorageError(
                f"Falha ao enviar '{caminho_limpo}' para o Supabase Storage "
                f"(HTTP {resposta.status_code}): {resposta.text}"
            )

        return caminho_limpo


@lru_cache(maxsize=1)
def get_supabase_storage_provider() -> SupabaseStorageProvider:
    """Instancia unica por processo, criada so quando efetivamente requisitada."""
    return SupabaseStorageProvider(get_supabase_storage_settings())
