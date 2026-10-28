---
title: Claude Code Hook Architecture
tags: [meta, infra, pattern]
summary: Claude Code lifecycle hooks — PreToolUse/PostToolUse events, exit-code protocol (0=pass, 2=block), and the hook suite pattern used to enforce code quality automatically without mid-task reminders.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/dev/hooks-architecture.md
  - data/raw/claude-docs/playground/docs/tooling/hooks-architecture.md
  - data/raw/claude-docs/_user/commands/style.md
  - data/raw/claude-docs/_user/commands/logging.md
  - data/raw/claude-docs/_user/commands/ml.md
  - data/raw/claude-docs/project-g/docs/dev/hooks-architecture.md
  - data/raw/claude-docs/playground/docs/archived/ts-copilot-plan.md
  - data/raw/repos/galactus/CLAUDE.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-gal-14-observed-transitions.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-gal-14-observed-transitions.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-7-hook-telemetry.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-7-hook-telemetry.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-8-ci-drift-hook.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-8-ci-drift-hook.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-consciousness-identity-model.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-consciousness-identity-model.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-01-CLA-74-status-writers-validation.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-01-CLA-74-status-writers-validation.md
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

## Extension-Gated Hooks Leave New Languages Ungated

A hook audit before adding TypeScript work to a mostly-Python repo (playground, 2026-04) found that **every PostToolUse and PreToolUse hook matched on `.py$`**. The TypeScript agent got no `tsc --noEmit`, no ESLint, no `console.log` guard and no SDK-pattern lint. `review_gate.sh` didn't gate `.ts` or `.tsx` either, so TS edits skipped the review step entirely. Nothing failed, which is why nobody noticed. When a repo gains a language, audit the hook matchers, not just the linters. The same plan added an advisory tool-count hook that warns above 22 tools, ahead of the model's degradation point around 25.

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

## Per-Hook Telemetry (guacamayo GH-7)

The motivating failure: the bash-antipattern hook was moved from advisory to blocking,
and antipatterns per session went **up** (25.8 → 27.85). That was noticed only through
a manual insights pass. Hook blocks were counted in aggregate (18 in a day) but never
attributed to a hook. There was no false-positive rate and no override tracking. The
plan had three layers:

- **Capture.** A shared `log_event()` in `lib.sh` appends one JSON line per block to a
  hook log. The log schema allows `exit_code: 0` from day one, so advisory hooks can
  join later to measure noise.
- **Parse.** The session-telemetry parser reads the log and emits per-hook block
  counts plus an **override proxy**: a block immediately followed by the same tool
  call, which approximates a false positive without parsing transcripts.
- **Verify.** A ledger metric type `hook-blocks:<name>` lets a retro check a hook
  hypothesis automatically.

Design rules:

- **Logging must never prevent the block.** Under `set -e`, a failed write would kill
  the hook before it exits 2, so the write is wrapped in `|| true`. The cost is that a
  failed write goes unseen. [[Silence Reads as Clean]] records that as a later finding:
  masked log failures make recurrence counts under-report.
- **Extract inline hooks to scripts before instrumenting them.** Inline telemetry
  would make `settings.json` unreadable.
- **Bound the log.** Cap the context field at 200 characters, and rotate in the weekly
  cron with a two-file cap.
- **Measure, don't change.** The telemetry issue explicitly left hook behaviour
  (blocking vs advisory) out of scope.

A matcher naming a renamed tool is a hook that never fires, with no error. See
[[Config Reference Rot]], which also covers the advisory write-time CI path-check hook.
[[Conservation Gate on Accumulator Clear]] is a blocking PostToolUse example that checks
a count invariant instead of a pattern.

## `set -e` Swallows the Heredoc's Exit Code (guacamayo CLA-74)

A Status-validator hook ran a python3 heredoc under `set -euo pipefail` and then read
`status=$?` on the next line. When python exited 10, `set -e` aborted the script on the
heredoc line. The `status=$?` line never ran, `log_event` was skipped, and the hook exited
10, which Claude Code treats as neither pass nor block. The fix is
`python3 ... <<'PY' || status=$?`, which keeps the non-zero exit inside the script so the
hook can handle it.

The same hook defined the warn-vs-block scope. It validates only fields that are
**required for a given state**: `Review:` on EXECUTED and `Superseded-by:` on SUPERSEDED.
It does not flag optional metadata, because a hook that nags about optional fields gets
ignored.

## See Also
- [[Claude Workflow System]]
- [[Session Knowledge Capture Patterns]]
- [[Production Hardening Patterns]]
- [[Friction Promotion Ladder]] — extends (warn hooks as the cheapest conditional injection point)
- [[Observed Transitions, Not Declared]] — instance-of (only PreToolUse can observe the prior file state)
- [[Vendored Hooks Resolve to the Global Copy]] — extends (a symlinked $CLAUDE_PROJECT_DIR runs the global hook, not the repo copy)
- [[Config Reference Rot]] — related (stale matchers fail silently; a CI path-check hook)
- [[Conservation Gate on Accumulator Clear]] — instance-of (an exit-2 count-invariant PostToolUse hook)
