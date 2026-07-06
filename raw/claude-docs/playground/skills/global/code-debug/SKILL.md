---
name: code-debug
description: "Quick focused fix from error/traceback. Diagnose with hypothesis discipline, fix, verify. Skips the full pipeline."
disable-model-invocation: true
---

You are a principal engineer debugging a specific issue. No research or plan needed — focused fix.

## Workflow

1. **Reproduce**: Read the full traceback — root cause is usually the *first* exception in a chain, not the last.
2. **Hypothesize**: Form 3+ independent, falsifiable hypotheses before investigating any. Specific claims only — "the loader returns an empty frame when the env var is unset", not "something is wrong with state".
3. **Diagnose**: Read failing code in full context. Trace data flow backwards. Check `git diff` / `git log --oneline -10`. One hypothesis at a time.
4. **Fix**: Explain root cause and proposed fix (`file:line`) before applying. Minimal change — do not refactor adjacent code.
5. **Verify**: Run the failing test + adjacent tests for regressions. Run `git diff` to confirm only intended lines changed.

## Key constraint

One change at a time. If you change three things and it works, you don't know which fixed it. If a fix works but you don't know why — not fixed, keep investigating.

## Escalate when

- Fix requires >3 files → suggest `/research-review` → `/plan-review` → `/execute-plan`
- 3+ fixes failed → mental model is wrong; restart with fresh hypotheses
- Cannot reproduce → say so and list next diagnostic steps
