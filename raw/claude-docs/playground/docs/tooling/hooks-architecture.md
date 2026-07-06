# Hook Architecture

How the Claude Code hook suite works in this project.

## Overview

Hooks are shell scripts invoked by the Claude Code harness at specific lifecycle events. They enforce code quality automatically so the agent doesn't need to be reminded of standards mid-task.

All hooks live in `.claude/hooks/`. They're registered in `.claude/settings.json`.

## Hook lifecycle events

| Event | When it fires | What we use it for |
|---|---|---|
| `PreToolUse` | Before a tool call executes | Block destructive bash commands, secrets scan before writes, test gate before commits |
| `PostToolUse` | After a tool call completes | Format/lint written files, type-check, enforce code standards |
| `Stop` | When the agent finishes a turn | macOS notification |
| `UserPromptSubmit` | When the user sends a message | Phase-complete compaction signal |

## Exit codes

Hooks communicate back to the harness via exit code:

| Exit code | Meaning |
|---|---|
| `0` | Pass — proceed |
| `2` | Block — the agent sees the stderr output as an error and must fix before proceeding |
| Any other | Ignored (advisory) |

## Current hooks (PostToolUse on Write|Edit|MultiEdit)

| Hook | Language | What it enforces |
|---|---|---|
| `code_quality.sh` | Python `.py` | No `print()`, no bare `except`, no stdlib `logging`, no pandas, no mutable defaults |
| `ts_quality.sh` | TS `.ts`/`.tsx` | No `"use client"` in layouts, no `console.log` in src, no hardcoded model strings, no `as any`; advisory file size |
| `ts_typecheck.sh` | TS `.ts`/`.tsx` in `ts_google_adk/` | Full `tsc --noEmit` — blocks on type errors; skips if `node_modules/.bin/tsc` absent |
| `sdk_lint.sh` | Python `.py` | No bare SDK client instantiation, no hardcoded model strings, token usage advisory |
| `function_complexity_warning.sh` | All | Advisory on overly complex functions |
| `test_coverage.sh` | All | Coverage check |
| `public_api_test_check.sh` | All | Ensures public APIs have tests |
| `docs_hygiene.sh` | Docs | Doc quality enforcement |
| `memory_duplication_guard.sh` | Memory files | Prevents duplicate memory entries |
| `secrets_scan.sh` | All (PreToolUse) | Blocks writes containing secrets/tokens |

## PreToolUse hooks (Bash)

| Hook | What it blocks |
|---|---|
| `risky_git_guard.sh` | Force push, reset --hard, etc. |
| `branch_guard.sh` | Commits to main directly |
| Inline: git commit | Runs pytest and `uv lock --check` — blocks if tests fail or lockfile is stale |
| Inline: pip install | Blocked — use `uv add` |
| Inline: destructive commands | `rm -rf /`, `DROP TABLE`, etc. |

## Adding a new hook

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

## `ts_typecheck.sh` design notes

`tsc --noEmit` runs on the full `ts_google_adk/` project (not per-file) because TypeScript's type checker needs cross-file context. It uses `tsconfig.json` which has `"incremental": true`, so after the first run it only re-checks changed files via `.tsbuildinfo`. The hook skips gracefully when `node_modules/.bin/tsc` is absent — install deps with `npm install` from `ts_google_adk/` to activate it.

## Friction log

Failed Bash commands (non-zero exit) are logged to `.claude/friction-log.jsonl`. This is a signal for `/claude-insights` to identify patterns of repeated failures.
