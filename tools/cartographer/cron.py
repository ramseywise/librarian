"""Cron-triggered insights analysis using the Anthropic SDK.

Reads session artifacts (SESSION.md, friction-log.jsonl, existing commands)
and uses Claude to identify workflow patterns and suggest new skills.

Run manually:
    uv run cartographer --cron

Or schedule via Claude Code remote trigger / system cron.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import structlog

from core.clients.llm import AnthropicLLM
from core.config.settings import BaseSettings

log = structlog.get_logger(__name__)

_settings = BaseSettings()

# --- Paths ---

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CLAUDE_DIR = REPO_ROOT / ".claude"
SESSIONS_DIR = CLAUDE_DIR / "sessions"
FRICTION_LOG = CLAUDE_DIR / "friction-log.jsonl"
COMMANDS_DIR = CLAUDE_DIR / "commands"
INSIGHTS_DIR = CLAUDE_DIR / "docs" / "insights"


def _read_latest_session(sessions_dir: Path) -> str:
    """Read the most recent session file from the sessions directory."""
    if not sessions_dir.exists():
        return ""
    files = sorted(sessions_dir.glob("*.md"), reverse=True)
    if not files:
        return ""
    return files[0].read_text(encoding="utf-8")


def _read_if_exists(path: Path) -> str:
    """Read file contents or return empty string."""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _read_friction_log(path: Path, max_lines: int = 200) -> str:
    """Read last N lines of friction log."""
    if not path.exists():
        return ""
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    return "\n".join(lines[-max_lines:])


def _list_commands(commands_dir: Path) -> str:
    """List existing command names and descriptions."""
    commands: list[str] = []
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


def build_analysis_prompt(
    session_md: str,
    friction_log: str,
    existing_commands: str,
) -> str:
    """Build the analysis prompt for Claude."""
    return f"""Analyze these Claude Code session artifacts and produce two outputs:

## 1. Workflow Insights (top 3-5 patterns)

For each pattern:
- **Signal**: what the data shows
- **Interpretation**: what this likely means
- **Recommendation**: one concrete change

## 2. Skill Suggestions

Review the skill candidates from SESSION.md and friction log patterns.
Compare against existing commands to avoid duplicates.

For each candidate:
- **Verdict**: GENERATE | SKIP | MERGE
- **Reason**: one sentence
- If GENERATE: provide the full command .md file content (with frontmatter)

---

## SESSION.md
```
{session_md}
```

## Friction log (recent entries)
```
{friction_log}
```

## Existing commands
```
{existing_commands}
```

---

Output as structured markdown. For any GENERATE verdict, include the complete
command file content in a fenced code block with the suggested filename.
Keep analysis terse and actionable."""


def run_analysis() -> str:
    """Run the insights analysis via shared LLM client."""
    if not _settings.anthropic_api_key:
        log.error("cron.no_api_key")
        sys.exit(1)

    session_md = _read_latest_session(SESSIONS_DIR)
    friction_log = _read_friction_log(FRICTION_LOG)
    existing_commands = _list_commands(COMMANDS_DIR)

    if not session_md and not friction_log:
        log.info("cron.no_data", msg="No session or friction data to analyze")
        return "No session data available for analysis."

    llm = AnthropicLLM(
        model=_settings.model_sonnet,
        api_key=_settings.anthropic_api_key,
    )

    prompt = build_analysis_prompt(session_md, friction_log, existing_commands)

    log.info("cron.calling_api", model=_settings.model_sonnet)
    response_text = llm.generate_sync(
        system="You are a workflow analysis assistant.",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    log.info("cron.done", output_chars=len(response_text))
    return response_text


def save_report(report: str) -> Path:
    """Save insights report to .claude/docs/insights/."""
    INSIGHTS_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
    out_path = INSIGHTS_DIR / f"{date_str}.md"

    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8")
        report = f"{existing}\n\n---\n\n# Run {datetime.now(tz=timezone.utc).strftime('%H:%M UTC')}\n\n{report}"

    out_path.write_text(f"# Insights — {date_str}\n\n{report}\n", encoding="utf-8")
    log.info("cron.saved", path=str(out_path))
    return out_path


def extract_and_write_commands(report: str) -> list[str]:
    """Parse GENERATE command blocks from report and write command files.

    Returns list of created command filenames.
    """
    created: list[str] = []
    lines = report.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if "GENERATE" in line or ("filename" in line.lower() and ".md" in line):
            # Scan ahead for fenced code block
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
    """Entry point for cron-triggered insights."""
    log.info("cron.start")
    report = run_analysis()
    out_path = save_report(report)
    created_commands = extract_and_write_commands(report)

    summary = {
        "report": str(out_path),
        "commands_created": created_commands,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
    }
    summary_path = INSIGHTS_DIR / "latest.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    log.info("cron.complete", **summary)
