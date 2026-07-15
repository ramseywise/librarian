"""Codemap indexing manifest — tracks which repo files have been parsed.

Each line in tools/codemap/manifest.jsonl is one indexed file:
  {"file_id": "librarian:etl/manifest.py", "hash": "sha256:...", "indexed_at": "2026-07-15"}

Use check() before parsing to skip unchanged files.
Use mark() after parsing to record the result.

Same dedup shape as etl/manifest.py, keyed by file_id (repo_id:rel_path)
instead of a wiki-relative path — separate manifest file since this tracks
a different domain (source code, not raw/ ingest sources).
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
MANIFEST_PATH = REPO_ROOT / "tools" / "codemap" / "manifest.jsonl"


def _load() -> dict[str, dict]:
    if not MANIFEST_PATH.exists():
        return {}
    entries = {}
    for line in MANIFEST_PATH.read_text().splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            entries[entry["file_id"]] = entry
    return entries


def _save(entries: dict[str, dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(e, ensure_ascii=False) for e in entries.values()]
    MANIFEST_PATH.write_text("\n".join(lines) + "\n")


def file_hash(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{h[:16]}"


def check(file_id: str, path: Path) -> tuple[bool, str]:
    """Return (needs_parse, reason). False means skip — already indexed unchanged."""
    if not path.exists():
        return False, f"file not found: {path}"
    current_hash = file_hash(path)
    entries = _load()
    if file_id not in entries:
        return True, "not yet indexed"
    if entries[file_id]["hash"] != current_hash:
        return True, f"changed since {entries[file_id]['indexed_at']}"
    return False, f"already indexed on {entries[file_id]['indexed_at']} (unchanged)"


def mark(file_id: str, path: Path) -> None:
    """Record a completed parse for file_id."""
    entries = _load()
    entries[file_id] = {
        "file_id": file_id,
        "hash": file_hash(path),
        "indexed_at": date.today().isoformat(),
    }
    _save(entries)


def remove(file_id: str) -> None:
    """Drop a manifest entry — used when a previously-indexed file is deleted."""
    entries = _load()
    if file_id in entries:
        del entries[file_id]
        _save(entries)


def known_file_ids() -> set[str]:
    return set(_load().keys())
