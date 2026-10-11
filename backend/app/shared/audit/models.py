"""Trilha de auditoria das acoes administrativas sobre a base juridica.

O FR-009 exige registro de toda alteracao de status administrativo de
documentos (criacao, ativacao, desativacao e substituicao de versao), e o
SC-003 cobra 100% dessas alteracoes em trilha verificavel.

Rastreabilidade:
    Feature: 001-fontes-e-rastreabilidade
    Task: T005
    Requisitos: FR-009, SC-003
    ADRs: 0001 (UUID v7), 0002 (datas em UTC)
"""

from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy import String, event
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base
from app.shared.models import TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["AuditAction", "AuditLog", "RegistroImutavelError"]


class RegistroImutavelError(RuntimeError):
    """Levantado ao tentar alterar ou remover um registro imutavel."""


class AuditAction(str, Enum):
    """Acoes administrativas registraveis.

    Herda de `str` para que a comparacao com o valor lido do banco funcione
    diretamente, sem conversao explicita.
    """

    SOURCE_CREATED = "SOURCE_CREATED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_ACTIVATED = "DOCUMENT_ACTIVATED"
    DOCUMENT_DEACTIVATED = "DOCUMENT_DEACTIVATED"
    DOCUMENT_SUPERSEDED = "DOCUMENT_SUPERSEDED"


class AuditLog(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Registro imutavel de um evento administrativo.

    A coluna `action` guarda a string da acao em vez de um ENUM do PostgreSQL:
    acrescentar um valor novo a um ENUM exige `ALTER TYPE` em migration, e a
    lista de acoes tende a crescer conforme novos fluxos administrativos
    surgem. A validacao fica no `AuditAction` em Python.

    Nao ha `updated_at`: uma trilha que pode ser editada nao prova nada. Se um
    registro de ativacao indevida puder ser alterado depois, a auditoria perde
    a funcao -- por isso UPDATE e DELETE sao bloqueados (ver abaixo).
    """

    __tablename__ = "audit_logs"

    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(nullable=False, index=True)

    # Nulo quando a acao parte de uma rotina automatica, sem usuario humano.
    actor_id: Mapped[UUID | None] = mapped_column(nullable=True)

    # Estado anterior e posterior da mudanca, ex.:
    # {"antes": {"is_active": false}, "depois": {"is_active": true}}
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        """Representacao enxuta para log.

        Omite `details` de proposito: o campo carrega estado administrativo e
        o `repr` costuma acabar em arquivo de log ou rastreamento de erro.
        """
        return (
            f"<AuditLog id={self.id!s} action={self.action} "
            f"entity={self.entity_type}:{self.entity_id!s}>"
        )

    @staticmethod
    def _bloquear_alteracao(mapper: Any, connection: Any, target: "AuditLog") -> None:
        """Impede UPDATE em registros da trilha."""
        raise RegistroImutavelError(
            "Registro de auditoria nao pode ser alterado. "
            "A trilha e imutavel por exigencia do FR-009; "
            "para corrigir um evento, registre um novo AuditLog."
        )

    @staticmethod
    def _bloquear_remocao(mapper: Any, connection: Any, target: "AuditLog") -> None:
        """Impede DELETE em registros da trilha."""
        raise RegistroImutavelError(
            "Registro de auditoria nao pode ser removido. "
            "A trilha e imutavel por exigencia do FR-009."
        )


# A guarda vive no nivel do ORM: cobre o uso normal da aplicacao, que e o
# objetivo aqui. Nao substitui permissoes no banco contra acesso direto via SQL.
event.listen(AuditLog, "before_update", AuditLog._bloquear_alteracao)
event.listen(AuditLog, "before_delete", AuditLog._bloquear_remocao)
