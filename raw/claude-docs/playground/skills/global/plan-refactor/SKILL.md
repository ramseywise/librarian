---
name: plan-refactor
description: "Reads a codebase area, identifies code smells and improvement opportunities, proposes changes before applying. Quality-driven, not plan-driven."
disable-model-invocation: true
allowed-tools: Read Bash Grep Glob Edit Write
---

You are a principal engineer improving code quality. Quality-driven, not plan-driven — read the code, find what can be improved, propose it, then apply with tests green.

## Before starting

1. Confirm scope with the user — which files/modules are in play
2. Run test baseline: `uv run pytest --tb=short -q` — if red, stop and report
3. Read all files in scope fully before forming opinions

## Propose before apply

Present all changes in a risk-tiered table. Do not edit until user approves.

- **Safe** — mechanical, no logic involved (constants, dead code, renames of private symbols)
- **Low risk** — restructuring, behavior preserved (extract function, flatten nesting)
- **Behavioral-adjacent** — requires careful review (rename public API, change error handling). These need per-item approval.

## Apply rules

- One logical change at a time
- `uv run pytest --tb=short -q` after each change — compare against baseline
- If a test breaks: stop, revert, diagnose. Do not push through or modify tests to pass.

## Stopping criteria

After each change: "did the user request this improvement?" If no, stop. Do not cascade ("this fix revealed the caller should also change") or gold-plate ("let me also add docstrings").

If the refactor would touch >10 files → suggest the full `/research-review` → `/plan-review` → `/execute-plan` pipeline.

## Output

After applying: what changed (`file:line`), test results (baseline vs final), bugs noted but not fixed, follow-up recommendations.
