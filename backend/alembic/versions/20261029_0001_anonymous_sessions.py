"""Acesso anonimo e propriedade exclusiva de conversas.

Revision ID: anonymous_sessions_01
Revises: 6508aac832b1
"""

import sqlalchemy as sa

from alembic import op

revision = "anonymous_sessions_01"
down_revision = "6508aac832b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "anonymous_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("questions_used", sa.Integer(), nullable=False),
        sa.Column("questions_limit", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("reset_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.CheckConstraint(
            "questions_used >= 0 AND questions_limit > 0", name="ck_anonymous_quota"
        ),
    )
    op.create_index("ix_anonymous_sessions_expires_at", "anonymous_sessions", ["expires_at"])
    op.alter_column("conversations", "user_id", nullable=True)
    op.add_column("conversations", sa.Column("anonymous_session_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_conversations_anonymous",
        "conversations",
        "anonymous_sessions",
        ["anonymous_session_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_conversations_anonymous_session_id", "conversations", ["anonymous_session_id"]
    )
    op.create_check_constraint(
        "ck_conversation_owner",
        "conversations",
        "(user_id IS NOT NULL AND anonymous_session_id IS NULL) OR "
        "(user_id IS NULL AND anonymous_session_id IS NOT NULL)",
    )


def downgrade() -> None:
    # Nao apagar conversas anonimas silenciosamente num downgrade.
    connection = op.get_bind()
    count = connection.scalar(sa.text("SELECT count(*) FROM conversations WHERE user_id IS NULL"))
    if count:
        raise RuntimeError("Migre ou arquive as conversas anonimas antes do downgrade.")
    op.drop_constraint("ck_conversation_owner", "conversations", type_="check")
    op.drop_index("ix_conversations_anonymous_session_id", table_name="conversations")
    op.drop_constraint("fk_conversations_anonymous", "conversations", type_="foreignkey")
    op.drop_column("conversations", "anonymous_session_id")
    op.alter_column("conversations", "user_id", nullable=False)
    op.drop_index("ix_anonymous_sessions_expires_at", table_name="anonymous_sessions")
    op.drop_table("anonymous_sessions")
