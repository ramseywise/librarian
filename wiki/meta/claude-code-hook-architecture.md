---
title: Claude Code Hook Architecture
tags: [meta, infra, pattern]
summary: Claude Code lifecycle hooks — PreToolUse/PostToolUse events, exit-code protocol (0=pass, 2=block), and the hook suite pattern used to enforce code quality automatically without mid-task reminders.
updated: 2026-07-14
sources:
  - raw/claude-docs/playground/docs/tooling/hooks-architecture.md
  - raw/claude-docs/_user/commands/style.md
  - raw/claude-docs/_user/commands/logging.md
  - raw/claude-docs/_user/commands/ml.md
---

# Claude Code Hook Architecture

Hooks are shell scripts invoked by the Claude Code harness at specific lifecycle events. They enforce code quality, security, and process standards automatically — the agent doesn't need to be reminded of standards mid-task.

All hooks live in `.claude/hooks/`. Registered in `.claude/settings.json`.

---

## Lifecycle Events

| Event | When it fires | Used for |
|---|---|---|
| `PreToolUse` | Before a tool call executes | Block destructive bash commands, secrets scan before writes, test gate before commits |
| `PostToolUse` | After a tool call completes | Format/lint written files, type-check, enforce code standards |
| `Stop` | When the agent finishes a turn | macOS notification, end-of-session signals |
| `UserPromptSubmit` | When the user sends a message | Phase-complete compaction signal |

---

## Exit Code Protocol

Hooks communicate back to the harness via exit code:

| Exit code | Meaning |
|---|---|
| `0` | Pass — proceed |
| `2` | Block — agent sees stderr output as an error and must fix before proceeding |
| Any other | Ignored (advisory) |

Exit code `2` is the key mechanism: the agent sees the stderr output and must fix the issue before proceeding. This creates a tight correction loop without human intervention.

---

## PostToolUse Hook Suite (Write|Edit|MultiEdit)

| Hook | Language | What it enforces |
|---|---|---|
| `code_quality.sh` | Python `.py` | No `print()`, no bare `except`, no stdlib `logging`, no pandas, no mutable defaults |
| `ts_quality.sh` | TS `.ts`/`.tsx` | No `"use client"` in layouts, no `console.log` in src, no hardcoded model strings, no `as any`; advisory file size |
| `ts_typecheck.sh` | TS `.ts`/`.tsx` | Full `tsc --noEmit` — blocks on type errors; skips if `node_modules/.bin/tsc` absent |
| `sdk_lint.sh` | Python `.py` | No bare SDK client instantiation, no hardcoded model strings, token usage advisory |
| `function_complexity_warning.sh` | All | Advisory on overly complex functions |
| `test_coverage.sh` | All | Coverage check |
| `public_api_test_check.sh` | All | Ensures public APIs have tests |
| `docs_hygiene.sh` | Docs | Doc quality enforcement |
| `memory_duplication_guard.sh` | Memory files | Prevents duplicate memory entries |
| `secrets_scan.sh` | All (PreToolUse) | Blocks writes containing secrets/tokens |

---

## PreToolUse Hooks (Bash)

| Hook | What it blocks |
|---|---|
| `risky_git_guard.sh` | Force push, reset --hard, etc. |
| `branch_guard.sh` | Direct commits to main |
| Inline: git commit | Runs pytest and `uv lock --check` — blocks if tests fail or lockfile is stale |
| Inline: pip install | Blocked — use `uv add` |
| Inline: destructive commands | `rm -rf /`, `DROP TABLE`, etc. |

---

## Adding a New Hook

1. Write the script in `.claude/hooks/<name>.sh` — exit 0 (pass) or exit 2 (block with message on stderr)
2. `chmod +x .claude/hooks/<name>.sh`
3. Add an entry to the relevant matcher in `.claude/settings.json`

Pattern for a file-type-scoped hook:

```bash
#!/usr/bin/env bash
path=$(echo "$CLAUDE_TOOL_INPUT" | jq -r '.file_path // empty')
[ -z "$path" ] && exit 0
echo "$path" | grep -qE '\.ts$' || exit 0   # scope to TS files

# ... checks ...

[ -n "$issues" ] && { printf "%s\n" "$issues" >&2; exit 2; }
exit 0
```

---

## TypeScript Type-Check Hook Design

`ts_typecheck.sh` runs `tsc --noEmit` on the full project (not per-file) because TypeScript's type checker needs cross-file context. Uses `tsconfig.json` with `"incremental": true` — after the first run, only re-checks changed files via `.tsbuildinfo`. Skips gracefully when `node_modules/.bin/tsc` is absent.

---

## Friction Log

Failed Bash commands (non-zero exit) are logged to `.claude/friction-log.jsonl`. This is input signal for `/claude-insights` to identify patterns of repeated failures — surface systematic friction points across sessions.

---

## Style Standards Behind `code_quality.sh`

`code_quality.sh`'s terse enforcement list (no `print()`, no bare `except`, no stdlib `logging`, no pandas, no mutable defaults) is the compiled-down version of three fuller personal convention references (`~/.claude/skills` style docs, invoked as `/style`, `/logging`, `/ml` in projects that opt in). The hook checks the letter of these; the docs below are the rationale.

### `/style` — Python & Data Conventions

- **Tooling:** `uv` only (`uv add`/`uv run`/`uv sync`) — never pip or poetry; ruff for lint/format; pyright for type checking; `from __future__ import annotations` everywhere; type annotations on all signatures; f-strings only
- **Data:** Polars not pandas (lazy frames for large data, eager for small); DuckDB for local analytics/joins; Parquet for cached intermediates, never CSV; `snake_case` columns
- **API/IO:** `httpx` not `requests`, async-first; always close connections; Pydantic models at API boundaries, not raw dicts
- **Don'ts:** no hardcoded paths/secrets/hyperparameters (config/env vars only), no mutable default arguments, no bare `except`, no notebooks committed with output cells

### `/logging` — structlog Standard

- `utils.logging` (structlog) is the only logger — never stdlib `logging` or `print()` in `src/`
- One logger per module: `log = get_logger(__name__)`
- Startup: `configure_logging()` for colored console (dev) or `configure_logging(render_json=True)` for JSON lines (prod/CI)
- Event names are dot-separated `module.action` (e.g. `sync.playlists`, `train.gmm.fit`) — never free-form strings; counts/IDs are bound as structured fields, not f-string-interpolated
- `debug` for per-item loops, `info` for phase transitions, `error` for caught exceptions; `structlog.contextvars.bind_contextvars(run_id=...)` for request/session scope

### `/ml` — ML/DS Best Practices

- **Reproducibility:** seed everywhere (`np.random.seed(42)`, `random_state=42`, Polars `seed=`); hyperparameters in config, never inline; log params/metrics at train time; artifacts saved via joblib to `models/`, never committed
- **Pipelines:** wrap preprocessing + model in sklearn `Pipeline` to prevent data leakage; fit scaler on train split only; `CalibratedClassifierCV` for calibrated probabilities
- **Evaluation:** always report accuracy/precision/recall/f1/roc_auc/precision@K; silhouette score for clustering; compare against a naive baseline; log results as structured fields
- **Data:** notebooks for exploration only, validated logic moves to `src/`; no pandas in ML code (Polars in, numpy arrays to sklearn); no training inside notebooks — notebooks call `python -m module.train`

These three are personal cross-project engineering conventions (not agent-design patterns) — included here because they're the documented source of truth the `code_quality.sh`/`sdk_lint.sh` hooks mechanically enforce.

---

## See Also
- [[Claude Workflow System]]
- [[Session Knowledge Capture Patterns]]
- [[Production Hardening Patterns]]
