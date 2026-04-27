"""Cron-triggered insights analysis using Claude (Anthropic API).

Reads session notes, facets (LLM-analyzed outcomes), session-meta (tokens/cost),
and friction log — then uses Claude to identify workflow patterns and suggest skills.
Also syncs ~/.claude/sessions/ to librarian/raw/sessions/ for wiki ingest.

Run manually:
    uv run cartographer --cron

Or schedule via system cron / Claude Code cron.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import anthropic
import structlog
from dotenv import load_dotenv

log = structlog.get_logger(__name__)

# --- Paths (all relative to ~/.claude) ---

CLAUDE_DIR = Path.home() / ".claude"
SESSIONS_DIR = CLAUDE_DIR / "sessions"
FRICTION_LOG = CLAUDE_DIR / "friction-log.jsonl"
COMMANDS_DIR = CLAUDE_DIR / "commands"
INSIGHTS_DIR = CLAUDE_DIR / "docs" / "insights"
FACETS_DIR = CLAUDE_DIR / "usage-data" / "facets"
SESSION_META_DIR = CLAUDE_DIR / "usage-data" / "session-meta"

# Librarian raw/sessions/ — for wiki ingest
LIBRARIAN_RAW_SESSIONS = Path(__file__).resolve().parent.parent.parent / "raw" / "sessions"

# Pricing per million tokens: (input, output, cache_write, cache_read)
_MODEL_PRICING: dict[str, tuple[float, float, float, float]] = {
    "claude-haiku-4-5": (0.80, 4.0, 1.0, 0.08),
    "claude-sonnet-4-6": (3.0, 15.0, 3.75, 0.30),
    "claude-opus-4-7": (15.0, 75.0, 18.75, 1.50),
}
_DEFAULT_PRICING = _MODEL_PRICING["claude-sonnet-4-6"]


def _get_pricing(model: str) -> tuple[float, float, float, float]:
    for prefix, pricing in _MODEL_PRICING.items():
        if model.startswith(prefix):
            return pricing
    return _DEFAULT_PRICING


# ---------------------------------------------------------------------------
# Data loaders
# ---------------------------------------------------------------------------


def _read_recent_sessions(sessions_dir: Path, days: int = 7) -> str:
    """Read all session notes from the last N days."""
    if not sessions_dir.exists():
        return ""
    cutoff = (datetime.now(tz=timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    notes: list[str] = []
    for f in sorted(sessions_dir.glob("*.md"), reverse=True):
        if f.stem[:10] >= cutoff:
            notes.append(f"### {f.name}\n\n{f.read_text(encoding='utf-8')}")
        if len(notes) >= 20:
            break
    if not notes:
        all_files = sorted(sessions_dir.glob("*.md"), reverse=True)
        if all_files:
            f = all_files[0]
            notes.append(f"### {f.name}\n\n{f.read_text(encoding='utf-8')}")
    return "\n\n---\n\n".join(notes)


def _read_friction_log(path: Path, max_lines: int = 200) -> str:
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return "\n".join(lines[-max_lines:])


def _list_commands(commands_dir: Path) -> str:
    commands: list[str] = []
    if not commands_dir.exists():
        return ""
    for f in sorted(commands_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8")
        name = f.stem
        desc = ""
        if content.startswith("---"):
            end = content.find("---", 3)
            if end > 0:
                for line in content[3:end].splitlines():
                    if line.strip().startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                        break
        commands.append(f"- {name}: {desc}")
    return "\n".join(commands)


def _load_all_facets(facets_dir: Path) -> dict[str, dict]:
    """Load all facet files indexed by session_id."""
    if not facets_dir.exists():
        return {}
    facets: dict[str, dict] = {}
    for p in sorted(facets_dir.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sid = data.get("session_id") or p.stem
            facets[sid] = data
        except Exception:
            pass
    return facets


def _format_facets_summary(facets: dict[str, dict]) -> str:
    if not facets:
        return "No facet data available."

    outcomes: dict[str, int] = {}
    categories: dict[str, int] = {}
    friction_sessions: list[str] = []

    for sid, f in facets.items():
        outcome = f.get("outcome", "unknown")
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        for cat in f.get("goal_categories", {}).keys():
            categories[cat] = categories.get(cat, 0) + 1
        if f.get("friction_detail"):
            brief = f.get("brief_summary", "")[:80]
            friction = f["friction_detail"][:100]
            friction_sessions.append(f"  [{sid[:8]}] {brief} | friction: {friction}")

    lines = [f"Total analyzed sessions: {len(facets)}", "", "Outcomes:"]
    for outcome, count in sorted(outcomes.items(), key=lambda x: -x[1]):
        lines.append(f"  {outcome}: {count}")

    lines.extend(["", "Top goal categories:"])
    for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:8]:
        lines.append(f"  {cat}: {count}")

    if friction_sessions:
        lines.extend(["", f"Sessions with friction ({len(friction_sessions)}):"])
        lines.extend(friction_sessions[:10])

    return "\n".join(lines)


def _compute_cost_summary(session_meta_dir: Path, days: int = 7) -> str:
    """Estimate cost from session-meta token counts over the last N days.

    Uses model-specific pricing when available; falls back to Sonnet 4.6.
    cache_write_tokens and cache_read_tokens are tracked separately as they
    are cheaper than regular input tokens.
    """
    if not session_meta_dir.exists():
        return "No session-meta data available."

    cutoff = datetime.now(tz=timezone.utc) - timedelta(days=days)
    sessions: list[dict] = []

    for p in session_meta_dir.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            start_str = data.get("start_time", "")
            if not start_str:
                continue
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            if start < cutoff:
                continue

            model = data.get("primary_model", "claude-sonnet-4-6")
            inp_price, out_price, cw_price, cr_price = _get_pricing(model)

            inp = data.get("input_tokens", 0)
            out = data.get("output_tokens", 0)
            cw = data.get("cache_write_tokens", 0)
            cr = data.get("cache_read_tokens", 0)

            cost = (
                inp * inp_price
                + out * out_price
                + cw * cw_price
                + cr * cr_price
            ) / 1_000_000

            sessions.append({
                "date": start_str[:10],
                "project": Path(data.get("project_path", "unknown")).name,
                "model": model,
                "input": inp,
                "output": out,
                "cache_write": cw,
                "cache_read": cr,
                "cost": cost,
                "prompts": data.get("user_message_count", 0),
            })
        except Exception:
            pass

    if not sessions:
        return f"No sessions in the last {days} days."

    total_cost = sum(s["cost"] for s in sessions)
    total_input = sum(s["input"] for s in sessions)
    total_output = sum(s["output"] for s in sessions)
    total_cache_write = sum(s["cache_write"] for s in sessions)
    total_cache_read = sum(s["cache_read"] for s in sessions)

    # Model distribution
    models: dict[str, int] = {}
    for s in sessions:
        m = s["model"]
        models[m] = models.get(m, 0) + 1

    lines = [
        f"Period: last {days} days | Sessions: {len(sessions)} | Est. cost: ${total_cost:.2f}",
        f"Tokens: {total_input:,} input / {total_output:,} output / {total_cache_write:,} cache_write / {total_cache_read:,} cache_read",
        f"Models: {', '.join(f'{m}×{c}' for m, c in sorted(models.items(), key=lambda x: -x[1]))}",
        "",
        "Top sessions by cost:",
    ]
    for s in sorted(sessions, key=lambda x: -x["cost"])[:5]:
        lines.append(
            f"  {s['date']} [{s['project']}] [{s['model'].split('-')[1]}] ${s['cost']:.3f}"
            f" ({s['prompts']} prompts, {s['input']:,}in/{s['output']:,}out"
            f"/{s['cache_read']:,}cr)"
        )
    return "\n".join(lines)


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
# Prompt
# ---------------------------------------------------------------------------


def build_analysis_prompt(
    sessions_md: str,
    friction_log: str,
    existing_commands: str,
    facets_summary: str = "",
    cost_summary: str = "",
) -> str:
    return f"""Analyze these Claude Code session artifacts and produce three outputs:

## 1. Workflow Insights (top 3-5 patterns)

For each pattern:
- **Signal**: what the data shows
- **Interpretation**: what this likely means
- **Recommendation**: one concrete change

## 2. Cost & Context Analysis

Review the cost summary. Flag expensive sessions relative to their goal.
Note cache efficiency (high cache_read = good prefix reuse; high cache_write on short
sessions = context bloat). Suggest one prompt/workflow change to reduce cost.

## 3. Skill Suggestions

Review friction patterns and recurring multi-step workflows.
Compare against existing commands to avoid duplicates.

For each candidate:
- **Verdict**: GENERATE | SKIP | MERGE
- **Reason**: one sentence
- If GENERATE: provide the full command .md file content (with frontmatter)

---

## Session Notes (last 7 days)
```
{sessions_md}
```

## Friction log (recent entries)
```
{friction_log}
```

## Existing commands
```
{existing_commands}
```

## Facets — LLM-analyzed outcomes
```
{facets_summary}
```

## Cost & Token Summary
```
{cost_summary}
```

---

Output as structured markdown. For any GENERATE verdict, include the complete
command file content in a fenced code block with the suggested filename.
Keep analysis terse and actionable."""


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------


def run_analysis() -> str:
    # Load .env so the crontab context can find the key
    load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=False)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        log.error("cron.no_api_key", msg="Set ANTHROPIC_API_KEY")
        sys.exit(1)

    model = os.environ.get("CRON_MODEL", "claude-haiku-4-5-20251001")
    client = anthropic.Anthropic(api_key=api_key)

    sessions_md = _read_recent_sessions(SESSIONS_DIR)
    friction_log = _read_friction_log(FRICTION_LOG)
    existing_commands = _list_commands(COMMANDS_DIR)
    facets = _load_all_facets(FACETS_DIR)
    facets_summary = _format_facets_summary(facets)
    cost_summary = _compute_cost_summary(SESSION_META_DIR)

    if not sessions_md and not friction_log and not facets:
        log.info("cron.no_data", msg="No session or friction data to analyze")
        return "No session data available for analysis."

    log.info(
        "cron.data_loaded",
        sessions=sessions_md.count("### "),
        facets=len(facets),
    )

    prompt = build_analysis_prompt(
        sessions_md, friction_log, existing_commands, facets_summary, cost_summary
    )

    log.info("cron.calling_api", model=model)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system="You are a workflow analysis assistant. Be terse and specific.",
        messages=[{"role": "user", "content": prompt}],
    )
    response_text = message.content[0].text if message.content else ""
    log.info("cron.done", output_chars=len(response_text))
    return response_text


def save_report(report: str) -> Path:
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    out_path = INSIGHTS_DIR / f"{date_str}.md"

    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        run_time = datetime.now(tz=timezone.utc).strftime("%H:%M UTC")
        report = f"{existing}\n\n---\n\n# Run {run_time}\n\n{report}"

    out_path.write_text(f"# Insights — {date_str}\n\n{report}\n", encoding="utf-8")
    log.info("cron.saved", path=str(out_path))
    return out_path


def extract_and_write_commands(report: str) -> list[str]:
    created: list[str] = []
    lines = report.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "GENERATE" in line or ("filename" in line.lower() and ".md" in line):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            if j < len(lines):
                k = j + 1
                content_lines: list[str] = []
                while k < len(lines) and not lines[k].strip().startswith("```"):
                    content_lines.append(lines[k])
                    k += 1
                content = "\n".join(content_lines).strip()
                if content.startswith("---") and "name:" in content:
                    for cl in content_lines:
                        if cl.strip().startswith("name:"):
                            name = (
                                cl.split(":", 1)[1].strip().strip('"').replace(" ", "_")
                            )
                            filename = f"{name}.md"
                            cmd_path = COMMANDS_DIR / filename
                            cmd_path.write_text(content + "\n", encoding="utf-8")
                            created.append(filename)
                            log.info("cron.command_created", file=filename)
                            break
                i = k + 1
                continue
        i += 1
    return created


def run_cron() -> None:
    log.info("cron.start")

    # Sync session notes to librarian raw/ for wiki ingest
    synced = _sync_sessions_to_raw(SESSIONS_DIR, LIBRARIAN_RAW_SESSIONS)
    if synced:
        log.info("cron.sessions_synced", count=synced, dest=str(LIBRARIAN_RAW_SESSIONS))

    report = run_analysis()
    out_path = save_report(report)
    created_commands = extract_and_write_commands(report)

    summary = {
        "report": str(out_path),
        "commands_created": created_commands,
        "sessions_synced": synced,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
    summary_path = INSIGHTS_DIR / "latest.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log.info("cron.complete", **summary)
