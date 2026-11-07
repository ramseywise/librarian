"""attempts and meta

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None

_ID = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "attempts",
        sa.Column("id", _ID, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("item", sa.Text, nullable=False),
        sa.Column("scope", sa.Text, nullable=False),
        sa.Column("result", sa.String(16), nullable=False),
        sa.Column("payload", sa.Text, nullable=True),
        sa.Column("event_key", sa.String(64), nullable=False, unique=True),
    )
    op.create_index("attempts_kind_item", "attempts", ["kind", "item"])
    op.create_table(
        "meta",
        sa.Column("key", sa.String(128), primary_key=True),
        sa.Column("value", sa.Text, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("meta")
    op.drop_index("attempts_kind_item", table_name="attempts")
    op.drop_table("attempts")
