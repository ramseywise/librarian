"""invites, login_tokens, audit, users.last_seen_at

Revision ID: 0005
Revises: 0004
"""

import sqlalchemy as sa
from alembic import op

revision = "0005"
down_revision = "0004"


def upgrade() -> None:
    op.create_table(
        "invites",
        sa.Column("email", sa.String(320), primary_key=True),
        sa.Column("invited_by", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "login_tokens",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("login_tokens_email", "login_tokens", ["email", "created_at"])
    op.create_table(
        "audit",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(64), nullable=True),
        sa.Column("action", sa.String(32), nullable=False),
        sa.Column("target", sa.Text, nullable=True),
    )
    op.create_index("audit_ts", "audit", ["ts"])
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.drop_column("last_seen_at")
    op.drop_index("audit_ts", table_name="audit")
    op.drop_table("audit")
    op.drop_index("login_tokens_email", table_name="login_tokens")
    op.drop_table("login_tokens")
    op.drop_table("invites")
