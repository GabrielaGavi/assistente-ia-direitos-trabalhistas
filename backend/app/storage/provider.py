"""Porta (Ports and Adapters) para armazenamento de arquivos binarios.

O dominio depende apenas deste `Protocol`. `SupabaseStorageProvider` e o
adapter concreto; qualquer outro provedor (S3, disco local em dev) pode
substitui-lo sem alterar `DocumentService`.
"""

from typing import Protocol

__all__ = ["StorageProvider"]


class StorageProvider(Protocol):
    async def upload(self, path: str, content: bytes, *, content_type: str) -> str:
        """Grava `content` em `path` e devolve o caminho do objeto armazenado.

        O retorno e o caminho relativo ao bucket, nunca uma URL publica: o
        bucket pode ser privado e exigir URL assinada na leitura.
        """
        ...
