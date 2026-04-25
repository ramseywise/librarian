"""Ingest manifest — tracks what's been compiled into the wiki.

Each line in raw/manifest.jsonl is one ingested file:
  {"path": "raw/web/foo.md", "hash": "sha256:...", "ingested_at": "2026-04-24", "wiki_pages": [...]}

Use check() before ingesting to skip unchanged files.
Use mark() after ingesting to record the result.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
MANIFEST_PATH = REPO_ROOT / "raw" / "manifest.jsonl"


def _load() -> dict[str, dict]:
    if not MANIFEST_PATH.exists():
        return {}
    entries = {}
    for line in MANIFEST_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            entries[entry["path"]] = entry
    return entries


def _save(entries: dict[str, dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(e, ensure_ascii=False) for e in entries.values()]
    MANIFEST_PATH.write_text("\n".join(lines) + "\n")


def file_hash(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{h[:16]}"


def check(path: str | Path) -> tuple[bool, str]:
    """Return (needs_ingest, reason). False means skip — already ingested unchanged."""
    p = Path(path)
    rel = str(p.relative_to(REPO_ROOT)) if p.is_absolute() else str(p)
    if not p.exists():
        return False, f"file not found: {rel}"
    current_hash = file_hash(p)
    entries = _load()
    if rel not in entries:
        return True, "not yet ingested"
    if entries[rel]["hash"] != current_hash:
        return True, f"changed since {entries[rel]['ingested_at']}"
    return False, f"already ingested on {entries[rel]['ingested_at']} (unchanged)"


def mark(path: str | Path, wiki_pages: list[str]) -> None:
    """Record a completed ingest for path."""
    p = Path(path)
    rel = str(p.relative_to(REPO_ROOT)) if p.is_absolute() else str(p)
    entries = _load()
    entries[rel] = {
        "path": rel,
        "hash": file_hash(p),
        "ingested_at": date.today().isoformat(),
        "wiki_pages": wiki_pages,
    }
    _save(entries)


def coverage_gaps(raw_dir: str | Path = "raw") -> list[dict]:
    """Return raw .md files with no manifest entry, grouped by directory."""
    root = REPO_ROOT / raw_dir
    entries = _load()
    gaps = []
    for f in sorted(root.rglob("*.md")):
        rel = str(f.relative_to(REPO_ROOT))
        if rel not in entries:
            gaps.append({"path": rel, "size_kb": round(f.stat().st_size / 1024, 1)})
    return gaps


def summary() -> dict:
    entries = _load()
    gaps = coverage_gaps()
    return {
        "ingested": len(entries),
        "pending": len(gaps),
        "total_wiki_pages_touched": sum(len(e.get("wiki_pages", [])) for e in entries.values()),
    }


if __name__ == "__main__":
    s = summary()
    print(f"Ingested: {s['ingested']}  Pending: {s['pending']}  Wiki pages touched: {s['total_wiki_pages_touched']}")
    for gap in coverage_gaps()[:20]:
        print(f"  PENDING  {gap['path']}  ({gap['size_kb']} KB)")
