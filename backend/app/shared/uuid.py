"""Geracao de identificadores UUID v7 e utilitarios de data em UTC.

A constituicao do projeto exige que todo identificador de dominio seja um
UUID v7 (time-ordered) e que toda data persistida seja *timezone-aware* em UTC.

UUID v7 carrega o epoch em milissegundos nos 48 bits mais significativos, o que
mantem os indices B-tree do PostgreSQL com boa localidade de escrita --
diferente do UUID v4, que distribui as chaves aleatoriamente pelo indice.

A biblioteca padrao do Python so expoe UUID v1/v3/v4/v5 ate a versao 3.13,
por isso a geracao e delegada a `uuid_utils` e convertida para `uuid.UUID`
nativo, garantindo interoperabilidade com SQLAlchemy e Pydantic.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T003
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import uuid_utils

__all__ = ["utc_now", "uuid7"]


def uuid7() -> UUID:
    """Gera um identificador UUID v7 como `uuid.UUID` da biblioteca padrao.

    Returns:
        UUID: identificador da versao 7, ordenavel cronologicamente.
    """
    return UUID(bytes=uuid_utils.uuid7().bytes)


def utc_now() -> datetime:
    """Retorna o instante atual como `datetime` *aware* no fuso UTC.

    Usado como `default` dos campos `created_at`/`updated_at` do dominio. Evita
    `datetime.utcnow()`, que devolve um objeto *naive* e e depreciado desde o
    Python 3.12.

    Returns:
        datetime: instante atual com `tzinfo` igual a `timezone.utc`.
    """
    return datetime.now(timezone.utc)
