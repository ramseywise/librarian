"""The sisyphus drill log, imported into one user's drill attempts.

The log (`drills/coding/drill-log.md` in the private sisyphus checkout) is a Markdown table the
owner keeps by hand. The server never reads it: the owner imports it on their own machine with
`librarian db import-drill-log`, and from then on its rows are drill attempts like any run
recorded in the app. Only the Date, QID, Aid and Score columns are read; the free-text Note column
never leaves the file.

A row has a date but no time, so it is stored at 12:00 UTC on that date, plus one second for each
earlier row of the same drill that day. Re-importing the same log therefore adds nothing, and an
appended row adds one attempt. The result is "pass" when the score has marks and none is a ✗.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import Engine

from librarian.db import get_engine
from librarian.db.attempt_rows import add_attempt

SCOPE = "drill-log"
_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}$")


def parse(text: str) -> list[dict[str, str]]:
    """Rows of the log's table, keeping only date, qid, aid and score. Note text is dropped here."""
    rows, header = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if header is None:
            if "QID" in cells:
                header = cells
            continue
        if set(cells[0]) <= {"-", ":"} or len(cells) < len(header):
            continue
        row = dict(zip(header, cells, strict=False))
        rows.append(
            {
                "date": row.get("Date", ""),
                "qid": row.get("QID", ""),
                "aid": row.get("Aid", ""),
                "score": row.get("Score", ""),
            }
        )
    return rows


def result_of(score: str) -> str:
    return "pass" if "✓" in score and "✗" not in score else "fail"


def import_log(path: Path, user_id: str, engine: Engine | None = None) -> tuple[int, int, int]:
    """Add the log's rows to `user_id`'s drill attempts. Returns (read, added, skipped).

    A row without a QID or a YYYY-MM-DD date is skipped. The file is only read.
    """
    engine = engine or get_engine()
    rows = parse(path.read_text(encoding="utf-8"))
    seen: dict[tuple[str, str], int] = {}
    added = skipped = 0
    with engine.begin() as conn:
        for row in rows:
            qid, day = row["qid"], row["date"]
            if not qid or not _DATE_RE.match(day):
                skipped += 1
                continue
            n = seen.get((day, qid), 0)
            seen[(day, qid)] = n + 1
            ts = datetime.fromisoformat(day).replace(hour=12, tzinfo=UTC) + timedelta(seconds=n)
            payload = {"score": row["score"], "aid": row["aid"], "source": SCOPE}
            added += add_attempt(
                conn,
                engine,
                user_id=user_id,
                ts=ts,
                kind="drill",
                item=qid,
                scope=SCOPE,
                result=result_of(row["score"]),
                payload=json.dumps({k: v for k, v in payload.items() if v}, ensure_ascii=False),
            )
    return len(rows), added, skipped
