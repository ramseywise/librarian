"""chat_usage

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"

_ID = sa.BigInteger().with_variant(sa.Integer(), "sqlite")


def upgrade() -> None:
    op.create_table(
        "chat_usage",
        sa.Column("id", _ID, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("user_key", sa.String(64), nullable=False),
        sa.Column("day", sa.Date, nullable=False),
        sa.Column("requests", sa.Integer, nullable=False, server_default="0"),
        sa.Column("input_tokens", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.BigInteger, nullable=False, server_default="0"),
        sa.Column("usd", sa.Float, nullable=False, server_default="0"),
        sa.UniqueConstraint("user_key", "day", name="chat_usage_user_day"),
    )


def downgrade() -> None:
    op.drop_table("chat_usage")
