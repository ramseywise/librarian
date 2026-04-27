"""Backfill cost + facet data into session note frontmatter.

Scans ~/.claude/sessions/ and librarian/raw/sessions/ for notes that lack
est_cost_usd and updates their YAML frontmatter using session-meta and facets.

Usage:
    uv run cartographer --enrich
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import frontmatter
import structlog
from dotenv import load_dotenv

log = structlog.get_logger(__name__)

CLAUDE_DIR = Path.home() / ".claude"
FACETS_DIR = CLAUDE_DIR / "usage-data" / "facets"
SESSION_META_DIR = CLAUDE_DIR / "usage-data" / "session-meta"
LIBRARIAN_RAW_SESSIONS = Path(__file__).resolve().parent.parent.parent / "raw" / "sessions"

_MODEL_PRICING: dict[str, tuple[float, float, float, float]] = {
    "claude-haiku-4-5": (0.80, 4.0, 1.0, 0.08),
    "claude-sonnet-4-6": (3.0, 15.0, 3.75, 0.30),
    "claude-opus-4-7": (15.0, 75.0, 18.75, 1.50),
}
_DEFAULT_PRICING = _MODEL_PRICING["claude-sonnet-4-6"]

_WORK_TYPES = ["debug", "feature", "refactor", "review", "planning", "research", "config", "chat"]
_OUTPUT_TYPES = ["pr", "plan_doc", "code_change", "decision", "wiki_page", "analysis", "config_change", "none"]

_CLASSIFY_SYSTEM = "You classify Claude Code sessions. Respond with valid JSON only, no explanation."
_CLASSIFY_PROMPT = """\
Classify this Claude Code session.

Underlying goal: {underlying_goal}
Outcome: {outcome}
Skills invoked: {skills}
First prompt: {first_prompt}
Key user messages:
{messages}
Files touched: {files_touched}
Brief summary: {brief_summary}

Pick ONE value for each field:

work_type options:
  debug — fixing errors or failures
  feature — implementing new functionality
  refactor — restructuring existing code
  review — code/PR review or audit
  planning — planning docs, roadmaps, task breakdown
  research — analysis, comparison, exploration
  config — setup, environment, CI/CD, infra
  chat — discussion with no concrete output

output_type options:
  pr — pull request created or merged
  plan_doc — planning or design document written
  code_change — code modified (no PR)
  decision — architectural decision documented
  wiki_page — wiki or knowledge base page written
  analysis — research or analysis document
  config_change — config files changed
  none — no durable artifact

key_output: one short phrase naming the specific file, PR, or decision (or "none")

Respond with JSON only: {{"work_type": "...", "output_type": "...", "key_output": "..."}}"""


def _get_pricing(model: str) -> tuple[float, float, float, float]:
    for prefix, pricing in _MODEL_PRICING.items():
        if model.startswith(prefix):
            return pricing
    return _DEFAULT_PRICING


def _build_meta_index(meta_dir: Path) -> dict[str, dict]:
    index: dict[str, dict] = {}
    if not meta_dir.exists():
        return index
    for p in meta_dir.glob("*.json"):
        try:
            index[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return index


def _build_facets_index(facets_dir: Path) -> dict[str, dict]:
    index: dict[str, dict] = {}
    if not facets_dir.exists():
        return index
    for p in facets_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sid = data.get("session_id") or p.stem
            index[sid] = data
        except Exception:
            pass
    return index


def _find_meta_by_start_time(stem: str, meta_index: dict[str, dict]) -> dict | None:
    """Match YYYY-MM-DDTHHMM stem to session-meta via start_time."""
    if len(stem) < 15 or "T" not in stem:
        return None
    date_part = stem[:10]
    time_part = stem[11:]
    if len(time_part) < 4:
        return None
    target = f"{date_part}T{time_part[:2]}:{time_part[2:4]}"
    for meta in meta_index.values():
        if meta.get("start_time", "").startswith(target):
            return meta
    return None


def _compute_cost(inp: int, out: int, cw: int, cr: int, model: str) -> float:
    inp_price, out_price, cw_price, cr_price = _get_pricing(model)
    return (inp * inp_price + out * out_price + cw * cw_price + cr * cr_price) / 1_000_000


def _find_transcript(session_id: str) -> Path | None:
    if not session_id:
        return None
    for p in (CLAUDE_DIR / "projects").glob(f"**/{session_id}.jsonl"):
        return p
    return None


def _extract_user_messages(transcript_path: Path, max_msgs: int = 8) -> list[str]:
    import re
    messages: list[str] = []
    for raw in transcript_path.read_text(errors="replace").splitlines():
        if not raw.strip():
            continue
        try:
            r = json.loads(raw)
        except Exception:
            continue
        if r.get("type") != "user":
            continue
        content = r.get("message", {}).get("content", "")
        text = (
            " ".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
            if isinstance(content, list)
            else str(content)
        )
        text = re.sub(r"<[^>]+>.*?</[^>]+>", "", text, flags=re.DOTALL).strip()
        if text and len(text) > 5:
            messages.append(text[:300])
    return messages[-max_msgs:]


def _classify_session(
    meta: dict[str, Any] | None,
    facet: dict[str, Any] | None,
    transcript_path: Path | None,
    api_key: str,
) -> dict[str, str] | None:
    import anthropic as _anthropic
    context = {
        "underlying_goal": (facet or {}).get("underlying_goal", "unknown"),
        "outcome": (facet or {}).get("outcome", "unknown"),
        "skills": ", ".join((facet or {}).get("goal_categories", {}).keys()) or "none",
        "first_prompt": str((meta or {}).get("first_prompt", "unknown"))[:200],
        "messages": "none",
        "files_touched": str((meta or {}).get("files_modified", 0)),
        "brief_summary": (facet or {}).get("brief_summary", ""),
    }
    if transcript_path and transcript_path.exists():
        msgs = _extract_user_messages(transcript_path)
        context["messages"] = "\n".join(f"- {m}" for m in msgs) or "none"

    try:
        client = _anthropic.Anthropic(api_key=api_key)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=128,
            system=_CLASSIFY_SYSTEM,
            messages=[{"role": "user", "content": _CLASSIFY_PROMPT.format(**context)}],
        )
        text = msg.content[0].text.strip() if msg.content else ""
        if not text:
            return None
        if text.startswith("```"):
            text = "\n".join(text.split("\n")[1:]).split("```")[0].strip()
        result = json.loads(text)
        if result.get("work_type") in _WORK_TYPES and result.get("output_type") in _OUTPUT_TYPES:
            return result
        log.debug("enrich.classify_bad_enum", result=result)
    except Exception as e:
        log.debug("enrich.classify_failed", error=str(e))
    return None


def _enrich_file(
    path: Path,
    meta_index: dict[str, dict],
    facets_index: dict[str, dict],
    stats: dict[str, int],
    api_key: str = "",
) -> None:
    try:
        post = frontmatter.load(str(path))
    except Exception:
        # Bad YAML (e.g. compact files with multiline branch values) — skip silently
        stats["skipped_no_data"] += 1
        return

    session_id = str(post.metadata.get("session_id", ""))
    meta: dict[str, Any] | None = meta_index.get(session_id)
    facet: dict[str, Any] | None = facets_index.get(session_id)

    # Fallback: match new-format stems by start_time
    if meta is None and not session_id:
        stem = path.stem
        meta = _find_meta_by_start_time(stem, meta_index)

    updates: dict[str, Any] = {}

    # Step 2–3: cost enrichment (skip if already present)
    if "est_cost_usd" in post.metadata:
        stats["skipped_already"] += 1
    else:
        if meta is None and facet is None:
            # No cost data and no API key for classification — skip entirely
            if not api_key:
                stats["skipped_no_data"] += 1
                return
        else:
            if meta:
                inp = meta.get("input_tokens", 0)
                out = meta.get("output_tokens", 0)
                # cache_read may be in existing frontmatter (PreCompact writes it)
                cr = post.metadata.get("cache_read_tokens", 0) or 0
                cw = 0
                model = "claude-sonnet-4-6"

                updates["input_tokens"] = inp
                updates["output_tokens"] = out
                updates["est_cost_usd"] = round(_compute_cost(inp, out, cw, cr, model), 6)

            if facet:
                if facet.get("outcome") and "outcome" not in post.metadata:
                    updates["outcome"] = facet["outcome"]
                if facet.get("underlying_goal"):
                    updates["underlying_goal"] = facet["underlying_goal"][:200]

    # Step 4: Classification pass — skip if work_type already present
    if api_key and "work_type" not in post.metadata:
        transcript = _find_transcript(session_id)
        classification = _classify_session(meta, facet, transcript, api_key)
        if classification:
            updates.update(classification)
            stats.setdefault("classified", 0)
            stats["classified"] += 1

    # Step 5: nothing to write
    if not updates:
        stats["skipped_no_data"] += 1
        return

    for k, v in updates.items():
        post.metadata[k] = v

    path.write_text(frontmatter.dumps(post), encoding="utf-8")
    log.info("enrich.enriched", file=path.name, cost=updates.get("est_cost_usd"))
    stats["enriched"] += 1


def _get_api_key() -> str:
    """Resolve API key: env → dotenv → .env file."""
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=False)
    return os.environ.get("ANTHROPIC_API_KEY", "")


def run_enrich(scan_dirs: list[Path] | None = None) -> None:
    api_key = _get_api_key()

    if scan_dirs is None:
        scan_dirs = [CLAUDE_DIR / "sessions", LIBRARIAN_RAW_SESSIONS]

    meta_index = _build_meta_index(SESSION_META_DIR)
    facets_index = _build_facets_index(FACETS_DIR)

    log.info("enrich.start", meta_files=len(meta_index), facets=len(facets_index))

    stats = {"enriched": 0, "skipped_already": 0, "skipped_no_data": 0, "errors": 0}

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            log.warning("enrich.dir_missing", path=str(scan_dir))
            continue
        for f in sorted(scan_dir.glob("*.md")):
            try:
                _enrich_file(f, meta_index, facets_index, stats, api_key)
            except Exception as e:
                log.warning("enrich.error", file=f.name, error=str(e))
                stats["errors"] += 1

    log.info("enrich.complete", **stats)
    print(
        f"Classified: {stats.get('classified', 0)} | "
        f"Enriched: {stats['enriched']} | "
        f"Already done: {stats['skipped_already']} | "
        f"No data: {stats['skipped_no_data']} | "
        f"Errors: {stats['errors']}"
    )
