"""Mixins reutilizaveis pelos modelos do dominio.

Centralizam as duas restricoes que a constituicao impoe a toda entidade --
chave primaria em UUID v7 e datas *timezone-aware* em UTC -- para que cada
modelo novo as receba por heranca, em vez de depender de o autor lembrar.

Ficam em `app.shared` e nao em `app.shared.audit` porque `Source`, `Document`,
`DocumentChunk` e `Citation` tambem os utilizam; mante-los no modulo de
auditoria criaria uma dependencia invertida entre os dominios.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T005
    ADRs: 0001 (UUID v7), 0002 (datas em UTC)
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.shared.uuid import utc_now, uuid7

__all__ = ["TimestampMixin", "UUIDPrimaryKeyMixin", "UpdatedAtMixin"]


class UUIDPrimaryKeyMixin:
    """Chave primaria UUID v7 gerada pela aplicacao.

    O `default` chamavel faz o ID existir antes do INSERT, permitindo que o
    service monte o objeto completo sem conhecer o ciclo da transacao
    (Principio V). Ver ADR-0001 para a comparacao com UUID v4 e BIGSERIAL.
    """

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)


class TimestampMixin:
    """Carimbo de criacao em UTC.

    O tipo da coluna vem do `type_annotation_map` da `Base`, que mapeia
    `datetime` para `TIMESTAMP(timezone=True)` -- ver ADR-0002.
    """

    created_at: Mapped[datetime] = mapped_column(default=utc_now, nullable=False)


class UpdatedAtMixin:
    """Carimbo de ultima alteracao em UTC, atualizado automaticamente.

    Aplicavel a entidades mutaveis como `Document`. Nao deve ser combinado com
    registros imutaveis, como a trilha de auditoria.
    """

    updated_at: Mapped[datetime] = mapped_column(
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
