"""users, sessions, api_keys

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.Text, nullable=True),
        sa.Column("role", sa.String(16), nullable=False, server_default="member"),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="UTC"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(64),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("sessions_user", "sessions", ["user_id"])
    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(64),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("hash", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.Text, nullable=True),
        sa.Column("scopes", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("api_keys_user", "api_keys", ["user_id"])


def downgrade() -> None:
    op.drop_table("api_keys")
    op.drop_table("sessions")
    op.drop_table("users")
