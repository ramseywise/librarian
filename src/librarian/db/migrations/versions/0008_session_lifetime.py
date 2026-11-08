"""sessions.last_used_at (idle timeout), users.disabled_at (revoke a user)

Expand-only: two nullable columns. Code that predates them ignores both.

Revision ID: 0008
Revises: 0007
"""

import sqlalchemy as sa
from alembic import op

revision = "0008"
down_revision = "0007"


def upgrade() -> None:
    with op.batch_alter_table("sessions") as batch:
        batch.add_column(sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True))
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("disabled_at")
    with op.batch_alter_table("sessions") as batch:
        batch.drop_column("last_used_at")
