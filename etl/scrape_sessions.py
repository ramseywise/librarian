"""Scrape AI coding session history → raw/sessions/

Reads conversation history from:
  - Claude Code: ~/.claude/projects/**/*.jsonl
  - Codex:       ~/.codex/sessions/*.jsonl + ~/.codex/archived_sessions/*.jsonl

Writes one markdown file per session to raw/sessions/ (or --output-dir).
Idempotent: skips sessions already present.

Usage:
    uv run python scripts/scrape_sessions.py
    uv run python scripts/scrape_sessions.py --output-dir /path/to/raw/sessions
    uv run python scripts/scrape_sessions.py --dry-run   # print what would be written
    uv run python scripts/scrape_sessions.py --source claude
    uv run python scripts/scrape_sessions.py --source codex
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import structlog
from dotenv import load_dotenv

load_dotenv()
log = structlog.get_logger()

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "raw" / "sessions"
CLAUDE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
CODEX_DIRS = [
    Path.home() / ".codex" / "sessions",
    Path.home() / ".codex" / "archived_sessions",
]


# ---------------------------------------------------------------------------
# Claude Code JSONL
# ---------------------------------------------------------------------------

def _project_name_from_slug(slug: str) -> str:
    """Convert -Users-ramsey-wise-Workspace-playground → playground."""
    parts = slug.replace("-Users-", "").replace("-", "/").split("/")
    # drop home path segments, keep last meaningful part
    skip = {"ramsey", "wise", "Workspace", "workspace", "Downloads", "home"}
    meaningful = [p for p in parts if p and p not in skip]
    return meaningful[-1] if meaningful else slug


def _extract_user_prompts(lines: list[str]) -> list[str]:
    """Pull clean user prompt strings from Claude JSONL lines."""
    prompts = []
    for line in lines:
        try:
            d = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        if d.get("type") != "user":
            continue
        msg = d.get("message", {})
        if msg.get("role") != "user":
            continue
        content = msg.get("content", [])
        if isinstance(content, str):
            text = content.strip()
            if text and not text.startswith("<") and len(text) > 20:
                prompts.append(text[:300])
        elif isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    text = block.get("text", "").strip()
                    if text and not text.startswith("<") and len(text) > 20:
                        prompts.append(text[:300])
                        break
    return prompts


def _extract_usage(lines: list[str]) -> dict[str, int]:
    """Sum token usage across all assistant messages."""
    totals: dict[str, int] = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }
    for line in lines:
        try:
            d = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        if d.get("type") != "assistant":
            continue
        usage = d.get("message", {}).get("usage", {})
        totals["input_tokens"] += usage.get("input_tokens", 0)
        totals["output_tokens"] += usage.get("output_tokens", 0)
        totals["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
        totals["cache_write_tokens"] += usage.get("cache_creation_input_tokens", 0)
    return totals


def _session_date_from_jsonl(lines: list[str]) -> str | None:
    """Find the earliest timestamp in a Claude JSONL file."""
    for line in lines:
        try:
            d = json.loads(line.strip())
            ts = d.get("timestamp")
            if ts:
                return ts[:10]  # YYYY-MM-DD
        except json.JSONDecodeError:
            continue
    return None


def scrape_claude(output_dir: Path, dry_run: bool = False) -> int:
    if not CLAUDE_PROJECTS_DIR.exists():
        log.info("claude_projects_dir_not_found", path=str(CLAUDE_PROJECTS_DIR))
        return 0

    written = 0
    for project_dir in sorted(CLAUDE_PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        project = _project_name_from_slug(project_dir.name)

        for jsonl_file in sorted(project_dir.glob("*.jsonl")):
            session_id = jsonl_file.stem
            lines = jsonl_file.read_text(encoding="utf-8", errors="ignore").splitlines()

            date = _session_date_from_jsonl(lines) or "unknown"
            prompts = _extract_user_prompts(lines)
            usage = _extract_usage(lines)

            if not prompts:
                continue  # skip system-only sessions with no real user input

            # Build a slug from date + first prompt words
            slug = re.sub(r"[^a-z0-9]+", "-", (prompts[0] if prompts else "session").lower())[:40].strip("-")
            out_name = f"claude-{date}-{slug}-{session_id[:8]}.md"
            out_path = output_dir / out_name

            if out_path.exists():
                continue

            # Format topics from first 3 unique prompts
            topics = "\n".join(f"- {p[:200]}" for p in prompts[:5])
            total_tokens = usage["input_tokens"] + usage["output_tokens"]

            content = f"""---
tool: claude-code
project: {project}
date: {date}
session_id: {session_id}
prompts: {len(prompts)}
total_tokens: {total_tokens}
cache_read_tokens: {usage['cache_read_tokens']}
---

# Claude Code Session — {date} ({project})

**First prompt:** {prompts[0] if prompts else 'unknown'}

## Prompts ({len(prompts)} total)

{topics}

## Stats

| Metric | Value |
|---|---|
| Input tokens | {usage['input_tokens']:,} |
| Output tokens | {usage['output_tokens']:,} |
| Cache read | {usage['cache_read_tokens']:,} |
| Cache write | {usage['cache_write_tokens']:,} |
"""

            if dry_run:
                print(f"[claude] would write: {out_name} ({len(prompts)} prompts, {total_tokens:,} tokens)")
            else:
                out_path.write_text(content, encoding="utf-8")
                log.info("wrote_session", source="claude", file=out_name)
            written += 1

    return written


# ---------------------------------------------------------------------------
# Codex JSONL
# ---------------------------------------------------------------------------

def _codex_session_meta(lines: list[str]) -> dict:
    """Extract git/cwd metadata from the first few Codex JSONL lines."""
    meta: dict = {}
    for line in lines[:5]:
        try:
            d = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        # Top-level session record
        if "git" in d:
            git = d["git"]
            meta["branch"] = git.get("branch", "")
            repo = git.get("repository_url", "")
            meta["repo"] = repo.split("/")[-1].replace(".git", "") if repo else ""
            meta["date"] = d.get("timestamp", "")[:10]
            meta["session_id"] = d.get("id", "")
    return meta


def _codex_prompts(lines: list[str]) -> list[str]:
    prompts = []
    for line in lines:
        try:
            d = json.loads(line.strip())
        except json.JSONDecodeError:
            continue
        if d.get("type") == "message" and d.get("role") == "user":
            content = d.get("content", [])
            for block in content:
                if isinstance(block, dict) and block.get("type") == "input_text":
                    text = block.get("text", "").strip()
                    # Skip environment context blocks
                    if text and not text.startswith("<environment_context") and len(text) > 20:
                        # Strip IDE context headers
                        clean = re.sub(r"^#\s*Context from my IDE.*?\n.*?\n", "", text, flags=re.DOTALL).strip()
                        if clean and len(clean) > 20:
                            prompts.append(clean[:300])
                            break
    return prompts


def scrape_codex(output_dir: Path, dry_run: bool = False) -> int:
    written = 0
    for codex_dir in CODEX_DIRS:
        if not codex_dir.exists():
            continue
        for jsonl_file in sorted(codex_dir.rglob("*.jsonl")):
            lines = jsonl_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            meta = _codex_session_meta(lines)
            prompts = _codex_prompts(lines)

            if not prompts or not meta:
                continue

            date = meta.get("date") or jsonl_file.stem[:10]
            project = meta.get("repo") or "unknown"
            session_id = meta.get("session_id") or jsonl_file.stem
            branch = meta.get("branch", "")

            slug = re.sub(r"[^a-z0-9]+", "-", (prompts[0] if prompts else "session").lower())[:40].strip("-")
            out_name = f"codex-{date}-{slug}-{session_id[:8]}.md"
            out_path = output_dir / out_name

            if out_path.exists():
                continue

            topics = "\n".join(f"- {p[:200]}" for p in prompts[:5])

            content = f"""---
tool: codex
project: {project}
date: {date}
branch: {branch}
session_id: {session_id}
prompts: {len(prompts)}
---

# Codex Session — {date} ({project})

**Branch:** {branch}
**First prompt:** {prompts[0] if prompts else 'unknown'}

## Prompts ({len(prompts)} total)

{topics}
"""

            if dry_run:
                print(f"[codex] would write: {out_name} ({len(prompts)} prompts, branch: {branch})")
            else:
                out_path.write_text(content, encoding="utf-8")
                log.info("wrote_session", source="codex", file=out_name)
            written += 1

    return written


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape AI session history → raw/sessions/")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--source", choices=["claude", "codex", "all"], default="all")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be written, don't write")
    args = parser.parse_args()

    if not args.dry_run:
        args.output_dir.mkdir(parents=True, exist_ok=True)

    total = 0
    if args.source in ("claude", "all"):
        n = scrape_claude(args.output_dir, dry_run=args.dry_run)
        log.info("claude_sessions_scraped", count=n)
        total += n

    if args.source in ("codex", "all"):
        n = scrape_codex(args.output_dir, dry_run=args.dry_run)
        log.info("codex_sessions_scraped", count=n)
        total += n

    print(f"\n{'[dry-run] ' if args.dry_run else ''}Total sessions: {total} → {args.output_dir}")


if __name__ == "__main__":
    main()
