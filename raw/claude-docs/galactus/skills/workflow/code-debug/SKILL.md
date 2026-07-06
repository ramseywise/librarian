---
name: code-debug
description: "Focused debugging loop for errors, tracebacks, broken behavior, flaky failures, and regressions. Build a reproducible feedback loop first, then hypothesize, instrument, fix, and regression-test."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Edit Write
---

You are a principal engineer debugging a specific issue. Keep scope tight, but do not guess. The core job is to build a trustworthy feedback loop, then use it to prove the fix.

## Workflow

### 1. Build the feedback loop

Find or create the fastest deterministic command that shows the bug.

Prefer, in order:

1. Existing failing test
2. New regression test at the public interface
3. CLI command with fixture input
4. HTTP/curl or agent invocation against a local server
5. Minimal throwaway harness that exercises the failing path
6. Repeated loop for flaky/non-deterministic bugs

The loop must assert the user's symptom, not just "doesn't crash." If you cannot reproduce, stop and report what you tried and what artifact/access is needed.

### 2. Reproduce

Run the loop and capture the exact failure. For tracebacks, read the full chain — root cause is usually the first exception, not the last.

Confirm:

- The symptom matches the user's report
- The failure reproduces more than once, or a flaky failure has a high enough reproduction rate to debug
- The command is narrow enough to rerun after each probe

### 3. Hypothesize

Form 3+ independent, falsifiable hypotheses before investigating any. Specific claims only:

- Good: "the loader returns an empty frame when the env var is unset"
- Bad: "something is wrong with state"

Rank them and test one at a time. If the user has domain context, show the ranked list before deep probing; otherwise proceed with the best-ranked hypothesis.

### 4. Diagnose

Read failing code in full context. Trace data flow backwards. Check `git diff` and recent commits when a regression is plausible.

Instrumentation rules:

- Change one variable at a time.
- Prefer a debugger or targeted boundary logs over broad logging.
- Tag temporary logs with a unique prefix such as `[DEBUG-a4f2]`.
- For performance regressions, measure first, then fix.

### 5. Fix

Explain root cause and proposed fix before applying it. Make the minimal behavior-preserving change needed for the failing loop. Do not refactor adjacent code during the fix.

If there is no correct regression seam, document that as an architecture/testability finding and still verify with the best available loop.

### 6. Verify and clean up

Required before declaring done:

- Original feedback loop passes
- Regression test passes, if one was added
- Adjacent relevant tests pass
- Temporary `[DEBUG-...]` probes are removed
- `git diff` contains only intended changes

## Key constraint

One change at a time. If you change three things and it works, you don't know which fixed it. If a fix works but you don't know why — not fixed, keep investigating.

## Escalate when

- Fix requires >3 files → suggest `/research-review` → `/plan-review` → `/execute-plan`
- 3+ fixes failed → mental model is wrong; restart with fresh hypotheses
- Cannot build a feedback loop → say so and ask for logs, fixture input, HAR/trace, screen recording, or environment access
