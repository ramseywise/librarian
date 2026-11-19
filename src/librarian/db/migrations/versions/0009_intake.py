"""intake: placement sittings, their answers, and a tier per user and subject (expand-only: three new tables)

Revision ID: 0009
Revises: 0008
"""

import sqlalchemy as sa
from alembic import op

revision = "0009"
down_revision = "0008"


def upgrade() -> None:
    op.create_table(
        "intakes",
        sa.Column("id", sa.String(32), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(64),
            sa.ForeignKey("users.id", name="intakes_user_fk", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("profile", sa.Text, nullable=False),
        sa.Column("interests", sa.Text, nullable=True),
    )
    op.create_index("intakes_user", "intakes", ["user_id", "started_at"])
    op.create_table(
        "intake_responses",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer, "sqlite"), primary_key=True),
        sa.Column(
            "intake_id",
            sa.String(32),
            sa.ForeignKey("intakes.id", name="intake_responses_intake_fk", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(64), nullable=False),
        sa.Column("question_key", sa.String(160), nullable=False),
        sa.Column("depth", sa.String(16), nullable=False),
        sa.Column("block", sa.SmallInteger, nullable=False),
        sa.Column("result", sa.String(16), nullable=True),
        sa.Column("ms", sa.Integer, nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("intake_id", "question_key", name="intake_responses_once"),
    )
    op.create_table(
        "placements",
        sa.Column(
            "user_id",
            sa.String(64),
            sa.ForeignKey("users.id", name="placements_user_fk", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("subject", sa.String(64), primary_key=True),
        sa.Column("suggested_tier", sa.String(16), nullable=False),
        sa.Column("chosen_tier", sa.String(16), nullable=False),
        sa.Column("source", sa.String(16), nullable=False),
        sa.Column("borderline_with", sa.String(16), nullable=True),
        sa.Column(
            "intake_id",
            sa.String(32),
            sa.ForeignKey("intakes.id", name="placements_intake_fk", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("placements")
    op.drop_table("intake_responses")
    op.drop_index("intakes_user", table_name="intakes")
    op.drop_table("intakes")
