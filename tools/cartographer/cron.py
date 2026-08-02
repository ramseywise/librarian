"""Cron-triggered session-corpus maintenance.

Syncs ~/.claude/sessions/ to librarian/raw/sessions/, tags new notes, appends them to
the wiki session log, and fetches arXiv/RSS material. Deterministic and key-free.

The LLM insights stage this module was built around was retired in #60: `/workflow-insights`
covers the same ground on demand, and running it unattended produced reports nobody read
while making an empty pipeline look healthy. `--facts` is now the daily job; `--cron` is
the weekly corpus sweep.

Run manually:
    uv run cartographer --cron

Or schedule via system cron / Claude Code cron.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

import structlog

log = structlog.get_logger(__name__)

# --- Paths (all relative to ~/.claude) ---

CLAUDE_DIR = Path.home() / ".claude"
SESSIONS_DIR = CLAUDE_DIR / "sessions"
INSIGHTS_DIR = CLAUDE_DIR / "docs" / "insights"

# Librarian raw/sessions/ — for wiki ingest
LIBRARIAN_RAW_SESSIONS = Path(__file__).resolve().parent.parent.parent / "raw" / "sessions"
LIBRARIAN_WIKI_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "wiki"


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------


def _parse_session_frontmatter(text: str) -> dict[str, str]:
    """Parse key-value frontmatter from a session markdown file."""
    import re

    fm: dict[str, str] = {}
    m = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return fm
    for line in m.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm


_PROJECT_DOMAIN_TAGS: dict[str, list[str]] = {
    "project-g": ["adk", "langgraph", "eval"],
    "librarian": ["rag", "mcp", "context-management"],
    "va-agents": ["adk", "voice"],
    "playground": ["infra"],
    "listen-wiseer": ["langgraph"],
    "Workspace": ["context-management"],
}


def _update_wiki_session_log(raw_sessions: Path, wiki_dir: Path) -> int:
    """Append new session rows to data/wiki/meta/session-log.md (append-only).

    Reads all session files in raw_sessions/, finds dates not yet covered in the
    log, and appends grouped date sections before the Notes/See Also footer.
    Returns the number of new date groups added.
    """
    import re

    session_log = wiki_dir / "meta" / "session-log.md"
    if not session_log.exists() or not raw_sessions.exists():
        return 0

    existing = session_log.read_text(encoding="utf-8")
    covered_dates = set(re.findall(r"### (\d{4}-\d{2}-\d{2})", existing))

    new_by_date: dict[str, list[dict]] = {}
    for f in sorted(raw_sessions.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="replace")
        fm = _parse_session_frontmatter(content)
        date = str(fm.get("date", "")).strip()
        if not date or date in covered_dates or not re.match(r"\d{4}-\d{2}-\d{2}", date):
            continue

        # First meaningful bullet from Recent prompts section as topic
        topic = "—"
        in_prompts = False
        for line in content.splitlines():
            if line.strip().startswith("## Recent prompts"):
                in_prompts = True
                continue
            if in_prompts and line.strip().startswith("##"):
                break
            if in_prompts and line.strip().startswith("- ") and len(line.strip()) > 12:
                topic = line.strip()[2:80].rstrip()
                break

        project = (fm.get("project") or "unknown").strip()
        raw_tokens = (fm.get("total_tokens") or fm.get("output_tokens") or "").strip()
        tok_str = (
            f"{int(raw_tokens) // 1000}k" if raw_tokens and raw_tokens not in ("~", "") else "—"
        )
        session_id = ((fm.get("session_id") or f.stem).strip())[:8]

        new_by_date.setdefault(date, []).append(
            {"id": session_id, "tokens": tok_str, "project": project, "topic": topic}
        )

    if not new_by_date:
        return 0

    blocks: list[str] = []
    for date_str in sorted(new_by_date.keys()):
        sessions = new_by_date[date_str]
        project = sessions[0]["project"]
        blocks.append(f"\n### {date_str} ({project})\n")
        blocks.append("| Session | ~Tokens | Topic |")
        blocks.append("|---------|---------|-------|")
        for s in sessions:
            blocks.append(f"| {s['id']} | {s['tokens']} | {s['topic']} |")

    new_block = "\n".join(blocks) + "\n"

    today = datetime.now(tz=UTC).strftime("%Y-%m-%d")
    updated = re.sub(r"(updated: )\d{4}-\d{2}-\d{2}", rf"\g<1>{today}", existing, count=1)

    insert_match = re.search(r"\n## (Notes|See Also)\n", updated)
    if insert_match:
        pos = insert_match.start()
        updated = updated[:pos] + new_block + updated[pos:]
    else:
        updated = updated.rstrip() + "\n" + new_block

    session_log.write_text(updated, encoding="utf-8")
    log.info("cron.wiki_session_log_updated", new_dates=len(new_by_date))
    return len(new_by_date)


def _tag_new_session_files(raw_sessions: Path) -> int:
    """Add semantic tags frontmatter to session files that are missing them.

    Infers tags from: project name (→ domain tags), skills_invoked, work_type.
    Skips files that already have a tags: line in their frontmatter.
    Returns count of files tagged.
    """
    import re

    if not raw_sessions.exists():
        return 0

    tagged = 0
    for f in sorted(raw_sessions.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="replace")
        # Skip if tags already present in frontmatter
        fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if fm_match and re.search(r"^tags:", fm_match.group(1), re.MULTILINE):
            continue

        fm = _parse_session_frontmatter(content)
        tags: list[str] = ["context-management"]

        project = (fm.get("project") or "").strip()
        tags.extend(_PROJECT_DOMAIN_TAGS.get(project, []))

        work_type = (fm.get("work_type") or "").strip()
        if work_type and work_type not in ("~", ""):
            tags.append(work_type.replace(" ", "-").lower())

        skills_raw = (fm.get("skills_invoked") or "").strip("[]")
        for skill in skills_raw.split(","):
            s = skill.strip().strip("'\"")
            if s and s not in ("none", "~", ""):
                tags.append(s)

        tags_str = ", ".join(sorted(set(tags)))
        new_content = re.sub(r"^(---\n)", rf"\1tags: [{tags_str}]\n", content, count=1)
        if new_content != content:
            f.write_text(new_content, encoding="utf-8")
            tagged += 1

    if tagged:
        log.info("cron.session_files_tagged", count=tagged)
    return tagged


def _sync_sessions_to_raw(sessions_dir: Path, raw_dir: Path) -> int:
    """Copy new PreCompact session notes to librarian/raw/sessions/ for wiki ingest.

    Skips files that already exist in raw_dir (by filename). Returns count copied.
    """
    if not sessions_dir.exists():
        return 0
    raw_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in sorted(sessions_dir.glob("*.md")):
        dst = raw_dir / src.name
        if not dst.exists():
            shutil.copy2(src, dst)
            copied += 1
            log.info("cron.session_synced", file=src.name)
    return copied


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


class EmptyInputError(RuntimeError):
    """A stage ran with nothing to read.

    Raised instead of continuing on empty input. Continuing made an empty run look
    byte-for-byte like a healthy one from the outside — the pipeline could not
    distinguish "no input" from "fine" and stayed broken for eleven days (#60).

    Raised today by `cartographer --facts` when the JSONL source yields no sessions;
    the LLM analysis stage that first raised it was retired in the same issue.
    """


def _rotate_hook_log() -> None:
    """Rotate ~/.claude/.hook-log.jsonl when it exceeds 10,000 lines.

    Keeps at most 2 files: current + .hook-log.jsonl.1 (overwrites previous archive).
    """
    hook_log = Path.home() / ".claude" / ".hook-log.jsonl"
    if not hook_log.exists():
        return
    lines = hook_log.read_text(encoding="utf-8").count("\n")
    if lines > 10_000:
        archive = hook_log.with_suffix(".jsonl.1")
        hook_log.rename(archive)
        log.info("cron.hook_log_rotated", archive=str(archive), lines=lines)


def fetch_arxiv_papers() -> int:
    """Fetch recent arXiv papers into raw/web/ when ARXIV_FETCH_ENABLED=true.

    Returns the number of papers written (0 if disabled or on error).
    Controlled by env var: ARXIV_FETCH_ENABLED=true (off by default).
    """
    if os.environ.get("ARXIV_FETCH_ENABLED", "").lower() != "true":
        log.debug("cron.arxiv_disabled", msg="Set ARXIV_FETCH_ENABLED=true to enable")
        return 0

    try:
        from core.scrape_arxiv import ArxivScraper

        scraper = ArxivScraper()
        written = scraper.run(dry_run=False)
        count = len(written)
        log.info("cron.arxiv_fetched", papers_fetched=count)
        return count
    except Exception as exc:
        log.warning("cron.arxiv_error", error=str(exc), exc_info=True)
        return 0


def fetch_feed_posts() -> int:
    """Fetch recent RSS/blog posts into raw/web/ when FEED_FETCH_ENABLED=true.

    Returns the number of posts written (0 if disabled or on error).
    Controlled by env var: FEED_FETCH_ENABLED=true (off by default).
    """
    if os.environ.get("FEED_FETCH_ENABLED", "").lower() != "true":
        log.debug("cron.feeds_disabled", msg="Set FEED_FETCH_ENABLED=true to enable")
        return 0

    try:
        from core.scrape_feeds import FeedScraper

        scraper = FeedScraper()
        written = scraper.run(dry_run=False)
        count = len(written)
        log.info("cron.feeds_fetched", posts_fetched=count)
        return count
    except Exception as exc:
        log.warning("cron.feeds_error", error=str(exc), exc_info=True)
        return 0


def run_cron() -> None:
    log.info("cron.start")

    # Faults are collected rather than raised so that a starved stage does not discard
    # work the other stages completed. They are re-read at the end to set the exit code.
    problems: list[str] = []

    # Sync session notes to librarian raw/ for wiki ingest
    synced = _sync_sessions_to_raw(SESSIONS_DIR, LIBRARIAN_RAW_SESSIONS)
    if synced:
        log.info("cron.sessions_synced", count=synced, dest=str(LIBRARIAN_RAW_SESSIONS))

    # Stages 1-3 all read from raw/sessions/. If it is still empty after the sync, then
    # every one of them no-op'd — invisible unless it is said out loud.
    if not any(LIBRARIAN_RAW_SESSIONS.glob("*.md")):
        msg = (
            f"no session notes in {LIBRARIAN_RAW_SESSIONS} after sync "
            f"(source: {SESSIONS_DIR}) — sync, tagging and wiki session-log all no-op'd"
        )
        log.error(
            "cron.sessions_starved", source=str(SESSIONS_DIR), dest=str(LIBRARIAN_RAW_SESSIONS)
        )
        problems.append(msg)

    # Tag any session files that are missing semantic frontmatter tags
    _tag_new_session_files(LIBRARIAN_RAW_SESSIONS)

    # Append new sessions to data/wiki/meta/session-log.md (append-only)
    wiki_dates_added = _update_wiki_session_log(LIBRARIAN_RAW_SESSIONS, LIBRARIAN_WIKI_DIR)
    if wiki_dates_added:
        log.info("cron.wiki_updated", dates_added=wiki_dates_added)

    # Fetch recent arXiv papers (opt-in via ARXIV_FETCH_ENABLED=true)
    arxiv_papers_fetched = fetch_arxiv_papers()

    # Fetch recent RSS/blog posts (opt-in via FEED_FETCH_ENABLED=true)
    feed_posts_fetched = fetch_feed_posts()

    summary = {
        "sessions_synced": synced,
        "arxiv_papers_fetched": arxiv_papers_fetched,
        "feed_posts_fetched": feed_posts_fetched,
        "problems": problems,
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }
    summary_path = INSIGHTS_DIR / "latest.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Rotate hook log if needed
    _rotate_hook_log()

    if problems:
        # The summary is written first so the failure leaves a durable trace, then the
        # non-zero exit reaches cartographer-cron.sh, which logs "cron: FAILED (exit 1)".
        log.error("cron.failed", problems=problems, count=len(problems))
        sys.exit(1)

    log.info("cron.complete", **summary)
