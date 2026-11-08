"""feedback: reader ratings, reports and unanswered questions (expand-only: one new table)

Revision ID: 0007
Revises: 0006
"""

import sqlalchemy as sa
from alembic import op

revision = "0007"
down_revision = "0006"


def upgrade() -> None:
    op.create_table(
        "feedback",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(64),
            sa.ForeignKey("users.id", name="feedback_user_fk", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("target", sa.String(320), nullable=False),
        sa.Column("rating", sa.SmallInteger, nullable=True),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("release", sa.String(64), nullable=True),
        sa.Column("experiment", sa.String(255), nullable=True),
    )
    op.create_index("feedback_kind_target", "feedback", ["kind", "target"])
    op.create_index("feedback_ts", "feedback", ["ts"])
    op.create_index("feedback_user", "feedback", ["user_id"])


def downgrade() -> None:
    op.drop_index("feedback_user", table_name="feedback")
    op.drop_index("feedback_ts", table_name="feedback")
    op.drop_index("feedback_kind_target", table_name="feedback")
    op.drop_table("feedback")
