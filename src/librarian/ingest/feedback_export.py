"""`librarian feedback export --since YYYY-MM-DD`: reader feedback as a raw source.

Writes `data/raw/feedback/<today>.md` (`source_type: feedback`, `confidence: low`) with one section
per target: the signal, the counts and the readers' notes verbatim, ready for `/ingest`. It is
anonymised by construction: the rows are read without their user ids, answers are counted but
their ids are not given, and a note is dropped (never edited) when it holds an email address, a
phone number, a link to a person's profile, an `@handle`, a secret, a term on the sensitive-terms
list or the name of a private page. A target that names a private page is left out whole. The
file is new each run: raw is append-only, so an existing one is never overwritten.

Nothing on the server calls this; the owner runs it, reads the file, then runs `/ingest`.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import Path

import yaml

from librarian.config import get_settings
from librarian.db import get_engine
from librarian.feedback import Feedback, since
from librarian.ingest import sensitive

# A link to a person: a profile page on a social or code-hosting site, or an @handle.
_PROFILE_URL_RE = re.compile(
    r"https?://(?:[\w-]+\.)?(?:linkedin|twitter|x|facebook|instagram|github|gitlab|t|bsky|"
    r"mastodon\.social|medium|substack|tiktok|youtube|reddit)\.(?:com|me|app|social)/\S+",
    re.IGNORECASE,
)
_HANDLE_RE = re.compile(r"(?<![\w.])@[A-Za-z0-9_]{2,}")
# Local phone formats the sensitive scan (international `+` numbers only) does not see.
_LOCAL_PHONE_RE = re.compile(r"(?<![\w.-])(?:\(\d{3}\)\s*|\d{3}[ .-])\d{3}[ .-]\d{4}(?![\w-])")


class ExportError(Exception):
    """The export cannot be written (existing file, bad date)."""


def _names(wiki_dir: Path) -> re.Pattern[str] | None:
    """Sensitive terms and private page names, as one pattern."""
    return sensitive.terms_pattern(
        [*sensitive.load_terms(wiki_dir), *sensitive.private_names(wiki_dir)]
    )


def is_clean(text: str, names: re.Pattern[str] | None) -> bool:
    """True when nothing in `text` names a person, a contact detail, a secret or a private page."""
    if sensitive.scan_text(text, names):
        return False
    return not (
        _PROFILE_URL_RE.search(text) or _HANDLE_RE.search(text) or _LOCAL_PHONE_RE.search(text)
    )


def _private_target(kind: str, target: str, names: re.Pattern[str] | None) -> bool:
    if kind == "lesson" and (target.startswith("private/") or "/private/" in target):
        return True
    return bool(names and names.search(target))


def _quote(note: str) -> str:
    return "\n".join(f"> {line}" if line.strip() else ">" for line in note.splitlines())


def _notes(rows: Sequence[Feedback], names: re.Pattern[str] | None) -> tuple[list[str], int]:
    """The clean notes of `rows` (verbatim, in time order, repeats dropped) and how many were dropped."""
    kept: list[str] = []
    dropped = 0
    for r in rows:
        if not r.body:
            continue
        if is_clean(r.body, names):
            if r.body not in kept:
                kept.append(r.body)
        else:
            dropped += 1
    return kept, dropped


def render(
    rows: Sequence[Feedback], start: date, end: date, names: re.Pattern[str] | None = None
) -> str:
    """The markdown file for `rows`."""
    by_target: dict[str, dict[str, list[Feedback]]] = {
        k: defaultdict(list) for k in ("page", "lesson", "unanswered")
    }
    answers = [r for r in rows if r.kind == "answer"]
    withheld_targets = 0
    for r in rows:
        if r.kind == "answer":
            continue
        if _private_target(r.kind, r.target, names) or not is_clean(r.target, names):
            withheld_targets += 1
        else:
            by_target[r.kind][r.target].append(r)

    dropped = 0
    out: list[str] = []

    def section(title: str, kind: str, noun: str) -> None:
        nonlocal dropped
        groups = by_target[kind]
        if not groups:
            return
        out.extend([f"## {title}", ""])
        for target, items in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            notes, bad = _notes(items, names)
            dropped += bad
            heading = f"`{target}`" if kind != "unanswered" else f"“{target}”"
            out.extend([f"### {heading}", "", f"- {noun}: {len(items)}"])
            if notes:
                out.extend(["- Notes:", ""])
                for n in notes:
                    out.extend([_quote(n), ""])
            else:
                out.append("")

    section("Pages reported", "page", "Reports")
    section("Lessons reported", "lesson", "Reports")
    if answers:
        up = sum(1 for r in answers if r.rating == 1)
        down = sum(1 for r in answers if r.rating == -1)
        notes, bad = _notes(answers, names)
        dropped += bad
        out.extend(["## Chat answers", "", f"- Rated up: {up}", f"- Rated down: {down}"])
        if notes:
            out.extend(["- Notes:", ""])
            for n in notes:
                out.extend([_quote(n), ""])
        else:
            out.append("")
    section("Unanswered questions", "unanswered", "Readers who asked")

    counts = Counter(r.kind for r in rows)
    header = [
        f"# Reader feedback {start.isoformat()} to {end.isoformat()}",
        "",
        "Signals from readers of the wiki, anonymised: no emails, user ids or answer ids. "
        "Low confidence: a reader's report is a lead to check against the page, not a fact. "
        f"{counts['answer']} answer ratings, {counts['page']} page reports, "
        f"{counts['lesson']} lesson reports, {counts['unanswered']} unanswered questions. "
        f"{dropped} notes and {withheld_targets} items were left out by the privacy gate.",
        "",
    ]
    meta = {
        "source_type": "feedback",
        "confidence": "low",
        "title": f"Reader feedback {start.isoformat()} to {end.isoformat()}",
        "period": f"{start.isoformat()}..{end.isoformat()}",
    }
    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    return "---\n" + front + "\n---\n\n" + "\n".join(header + out).rstrip() + "\n"


def export(
    rows: Sequence[Feedback],
    start: date,
    out_dir: Path,
    *,
    today: date | None = None,
    wiki_dir: Path | None = None,
) -> Path:
    """Write the file for `rows` into `out_dir` and return its path. Raises `ExportError` if it exists."""
    end = today or datetime.now(UTC).date()
    path = out_dir / f"{end.isoformat()}.md"
    if path.exists():
        raise ExportError(f"{path} already exists; raw is append-only, so it is not overwritten")
    names = _names(wiki_dir or get_settings().wiki_dir)
    text = render(rows, start, end, names)
    out_dir.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:  # "x": still refuses if it appeared meanwhile
        f.write(text)
    return path


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="librarian feedback export", description=__doc__)
    ap.add_argument("--since", required=True, help="first day to include, YYYY-MM-DD (UTC)")
    ap.add_argument("--out", type=Path, default=None, help="default: data/raw/feedback")
    args = ap.parse_args(list(argv) if argv is not None else None)
    try:
        start = date.fromisoformat(args.since)
    except ValueError:
        print(
            f"librarian feedback export: --since must be YYYY-MM-DD, got {args.since!r}",
            file=sys.stderr,
        )
        return 2
    out_dir = args.out or get_settings().raw_dir / "feedback"
    rows = since(get_engine(), datetime(start.year, start.month, start.day, tzinfo=UTC))
    try:
        path = export(rows, start, out_dir)
    except ExportError as e:
        print(f"librarian feedback export: {e}", file=sys.stderr)
        return 1
    print(f"wrote {path} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
