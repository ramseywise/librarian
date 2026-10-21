---
title: Harness Events Are Not Task Failures
tags: [patterns, eval, pattern]
summary: "When classifying agent sessions or errors from transcripts, permission prompts, interrupts and tool-plumbing errors are harness events, not task failures. Success needs a positive fact, otherwise the outcome is unknown, and errors are attributed by who owns the fix. The headline count is not the signal; its composition is."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-companion-summarizer-outcome-fidelity.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-companion-summarizer-outcome-fidelity.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-6-failure-taxonomy.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-6-failure-taxonomy.md
---

# Harness Events Are Not Task Failures

Two guacamayo efforts, both deriving outcomes from Claude Code transcripts, ran into the
same trap. One was a heuristic session summarizer labelling each session success,
failure, waiting or unknown. The other was the insights pipeline reporting error counts.

## The outcome classifier

The first version marked 242 sessions success and 42 failure. Every "success" came from
a default branch. A spot-check of five remaining "failures" found **one real one**:

| errorHint source | Real failure? |
|---|---|
| Python traceback alongside a failing test | yes |
| "Permission to use Bash with command …" | no, a permission prompt |
| `<tool_use_error>` from the permission handler | no, harness plumbing |
| bare `Exit code 2` | no, nothing to diagnose |
| bare `Exit code 1` | no, nothing to diagnose |

Three structural causes:

1. **`is_error` was trusted unconditionally.** The harness sets it for permission
   rejections and user interrupts, which say nothing about the task.
2. **The error regex was too broad.** Patterns like `\w*Error:` matched
   `<tool_use_error>` and ordinary log lines, inflating error hints from 42 to 107.
3. **A bare error hint was enough for "failure".** A permission denial during
   exploration is not a failed task.

The fixes:

- Classify permission, interrupt and tool-use-error results as **harness events** and
  exclude them from task error signals.
- Drop a bare exit code as evidence.
- Count an error hint as failure only alongside a failing test or a non-zero
  build/test command.
- **Success requires a positive fact** (files changed, commit made, tests passed).
  Otherwise the outcome is `unknown`.

After the fixes, unknown went from 0 to about 80, success from 242 to about 165, and
failure fell to 20, all 8 of them spot-checked real.

The working rules from that loop:

- **Re-spot-check after every change.** The headline count is not the signal; its
  composition is.
- Rebuild the compiled output before every eval re-run.
- "0 crashes / 0 zero-fact reads" is a regression gate.

## Attribute errors by who owns the fix

The insights pipeline reported 119 `command_failed`, 52 `file_not_found` and 28
`permission_denied` as flat counts. A wrong spec, a code bug, a missing dependency and a
quota limit all looked the same, so "fix X" could not be prioritised. The taxonomy that
followed has one rule: **a category is only worth having if it maps to a different
remediation.**

| Category | Owner and remediation | Typical signal |
|---|---|---|
| spec | rewrite prompt or acceptance criteria | tool succeeded, outcome wrong (invisible to error counts) |
| code | fix the code | `command_failed` with no retry, or a retry that also failed |
| env | fix infra, or wait for quota | `permission_denied` that is not a hook block, rate limit, CI dependency rot |
| tool | fix hook or tool config | hook block, tool timeout, MCP error |
| transient | none; watch for recurrence | failed once, the retry succeeded |

Design choices worth reusing:

- **Rule-based first.** Classify from error name + tool + retry pattern + hook-block
  presence. It costs nothing, is auditable, and leaves an LLM pass as a follow-up if
  recall is poor.
- **Keep it in the skill layer first.** The lookup table lives in the insights skill,
  not the parser, so a wrong rule has a small blast radius.
- **Report `unknown` instead of force-fitting.** A high unknown rate means the table
  needs more rules.
- **Degrade honestly.** If retry data is missing, merge transient into code with a
  "(retry unknown)" note rather than guessing.
- **Defer what the signal cannot see.** Spec errors need session-level outcome
  detection, which is the positive-fact outcome classifier above, so they were left
  for v2.

## See Also
- [[Friction Is Rework, Not Error Rate]] — related (the same pipeline reclassifying friction metrics)
- [[Silence Reads as Clean]] — related (a default branch reporting success is silence read as clean)
- [[Session Insights]] — extends (the insights pipeline whose error counts this attributes)
- [[Rate Metrics Measure the Logger]] — related (telemetry semantics checked before trusting a count)
- [[LLM-as-Judge Evaluation]] — related (spot-check composition, not the aggregate)
