---
title: Runtime vs Process Observability
tags: [llm, agents, infra, concept]
summary: "Harness observability has two layers — runtime signals (logs, traces, lifecycle) answer what the system did; process artifacts (plans, contracts, rubrics, scored verdicts) answer why a change should be accepted — and the harness, not the agent, must collect both."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--08-maturity-and-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--references.md
---

# Runtime vs Process Observability

"Add logging" covers half of observability. A harness needs two layers that answer
different questions:

| Layer | Signals | Answers |
|---|---|---|
| **Runtime** | Logs, traces, process lifecycle (start → ready → shutdown), critical-path checkpoints, data flow between components, resource trends, errors *with context* | *What did the system do?* |
| **Process** | Plans, sprint contracts, rubrics, acceptance criteria, scored verdicts | *Why should this change be accepted?* |

- **Without runtime signals** the agent can't tell "correct" from "looks correct", and its
  retries become guesses.
- **Without process artifacts** evaluation comes down to taste. "It doesn't feel right" gives
  the generator nothing to fix; "contrast 2.1:1, WCAG AA needs 4.5:1" does.

## The Harness Collects the Signals, Not the Agent

Agents don't log what they don't know they need, formats drift between sessions, and
contracts and rubrics are structured artifacts that print statements can't produce. The
practical shape:

- **Structured logs** on startup and the critical path, queryable locally.
- **One repeatable workload** the agent re-runs after every change: query → correlate →
  reason → fix → restart → re-run → verify.
- **One trace per session, one span per task, sub-spans per verification step**, on
  OpenTelemetry conventions so it plugs into standard tooling — the raw material for
  trace-driven improvement in [[Verification Loops]].
- For UI work, a **browser validation loop**: snapshot before, trigger exactly one path,
  snapshot after, compare, fix the smallest responsible layer, re-run until the same path is
  clean twice.

Process artifacts are the sprint contracts and rubrics of [[Verification Loops]]; the
[[Quality Document]] is the long-lived one.

## See Also
- [[Harness Maturity and Failure Modes]] — part-of
- [[Observability and Runtime Patterns]] — complements (tool choice and tracing architecture)
- [[Verification Loops]] — prerequisite-for
- [[Quality Document]] — complements
