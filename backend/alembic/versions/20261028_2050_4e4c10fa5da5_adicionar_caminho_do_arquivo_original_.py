"""adicionar caminho do arquivo original no storage

Revision ID: 4e4c10fa5da5
Revises: 556761232fe2
Create Date: 2026-10-28 20:50:31.627799

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e4c10fa5da5"
down_revision: str | Sequence[str] | None = "556761232fe2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "documents",
        sa.Column("original_file_path", sa.String(length=1000), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("documents", "original_file_path")
