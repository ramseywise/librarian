"""attempts.user_id NOT NULL, progress

Rows written before accounts had no user: they are the owner's (LIBRARIAN_OWNER_EMAIL), whose
row is created here if no request has made it yet. Their event keys are recomputed with the
owner's id, so a later import of the same events still adds nothing.

Revision ID: 0004
Revises: 0003
"""

import hashlib
import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from alembic import op

from librarian.config import get_settings

revision = "0004"
down_revision = "0003"

_attempts = sa.table(
    "attempts",
    sa.column("id"),
    sa.column("user_id"),
    sa.column("ts", sa.DateTime(timezone=True)),  # typed, or SQLite hands back the raw string
    sa.column("kind"),
    sa.column("item"),
    sa.column("result"),
    sa.column("event_key"),
)
_users = sa.table(
    "users",
    sa.column("id"),
    sa.column("email"),
    sa.column("role"),
    sa.column("timezone"),
    sa.column("created_at"),
)


def _owner_id(conn: sa.Connection) -> str:
    email = get_settings().owner_email.strip().lower()
    found = conn.execute(sa.select(_users.c.id).where(_users.c.email == email)).scalar()
    if found:
        return found
    owner = uuid.uuid4().hex
    conn.execute(
        _users.insert().values(
            id=owner, email=email, role="admin", timezone="UTC", created_at=datetime.now(UTC)
        )
    )
    return owner


def _backfill(conn: sa.Connection) -> None:
    rows = conn.execute(
        sa.select(
            _attempts.c.id, _attempts.c.ts, _attempts.c.kind, _attempts.c.item, _attempts.c.result
        ).where(_attempts.c.user_id.is_(None))
    ).all()
    if not rows:
        return
    owner = _owner_id(conn)
    for row in rows:
        ts = row.ts if row.ts.tzinfo else row.ts.replace(tzinfo=UTC)  # SQLite returns naive UTC
        raw = "\x1f".join((owner, ts.astimezone(UTC).isoformat(), row.kind, row.item, row.result))
        conn.execute(
            _attempts.update()
            .where(_attempts.c.id == row.id)
            .values(user_id=owner, event_key=hashlib.sha256(raw.encode("utf-8")).hexdigest())
        )


def upgrade() -> None:
    _backfill(op.get_bind())
    with op.batch_alter_table("attempts") as batch:
        batch.alter_column("user_id", existing_type=sa.String(64), nullable=False)
        batch.create_foreign_key(
            "attempts_user_fk", "users", ["user_id"], ["id"], ondelete="CASCADE"
        )
    op.create_index("attempts_user_kind", "attempts", ["user_id", "kind"])
    op.create_table(
        "progress",
        sa.Column(
            "user_id",
            sa.String(64),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("lesson_id", sa.Text, primary_key=True),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("progress")
    op.drop_index("attempts_user_kind", table_name="attempts")
    with op.batch_alter_table("attempts") as batch:
        batch.drop_constraint("attempts_user_fk", type_="foreignkey")
        batch.alter_column("user_id", existing_type=sa.String(64), nullable=True)
