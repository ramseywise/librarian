"""A request counter shared by every worker and replica: one fixed window per key, in the database.

`hit` is a single upsert, so concurrent workers cannot lose a count: the first hit of a key opens
a window at `now`; later hits in it add one; the first hit after the window has passed restarts
it at 1. `ON CONFLICT DO UPDATE` takes the row lock on Postgres and the write lock on SQLite, so
the read-modify-write is atomic on both. The caller learns the count including its own hit.

A fixed window opened by the first hit allows exactly `limit` hits per `window_s` for a key that
starts from idle. A caller straddling two windows can get up to 2x `limit` in a short span at
the boundary; that is the usual trade against a per-hit log.
"""

from __future__ import annotations

import math
import random
import time
from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy import Engine, case, delete

from librarian.db import tables, upsert

# Roughly one hit in this many also deletes expired rows, so the table stays small without a job.
_PRUNE_ONE_IN = 100


@dataclass(frozen=True)
class Window:
    hits: int  # including this call's hit
    retry_after_s: int  # whole seconds until the window restarts (at least 1)


def hit(
    engine: Engine,
    key: str,
    window_s: int,
    *,
    now: float | None = None,
    clock: Callable[[], float] = time.time,
) -> Window:
    """Count one hit for `key` and return the window's count so far.

    Wall-clock epoch seconds, not a monotonic clock: workers on one host or many must agree.
    Raises `SQLAlchemyError` when the database cannot be reached; the caller decides what that means.
    """
    t = tables.rate_limits
    now = clock() if now is None else now
    expired = t.c.window_start <= now - window_s
    stmt = upsert(engine, t).values(key=key, window_start=now, hits=1)
    stmt = stmt.on_conflict_do_update(
        index_elements=["key"],
        set_={
            "hits": case((expired, 1), else_=t.c.hits + 1),
            "window_start": case((expired, now), else_=t.c.window_start),
        },
    ).returning(t.c.hits, t.c.window_start)
    with engine.begin() as conn:
        count, start = conn.execute(stmt).one()
        if random.randrange(_PRUNE_ONE_IN) == 0:
            conn.execute(delete(t).where(t.c.window_start <= now - 2 * window_s))
    return Window(hits=int(count), retry_after_s=max(1, math.ceil(start + window_s - now)))


def clear(engine: Engine) -> None:
    """Forget every counter (tests, and an operator unblocking an address)."""
    with engine.begin() as conn:
        conn.execute(delete(tables.rate_limits))
