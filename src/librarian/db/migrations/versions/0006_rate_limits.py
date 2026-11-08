"""rate_limits: shared fixed-window counters for the auth routes (expand-only: one new table)

Revision ID: 0006
Revises: 0005
"""

import sqlalchemy as sa
from alembic import op

revision = "0006"
down_revision = "0005"


def upgrade() -> None:
    op.create_table(
        "rate_limits",
        sa.Column("key", sa.String(255), primary_key=True),
        sa.Column("window_start", sa.Float, nullable=False),
        sa.Column("hits", sa.Integer, nullable=False),
    )
    op.create_index("rate_limits_window_start", "rate_limits", ["window_start"])


def downgrade() -> None:
    op.drop_index("rate_limits_window_start", table_name="rate_limits")
    op.drop_table("rate_limits")
