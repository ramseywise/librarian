---
title: Quality Document
tags: [llm, agents, infra, pattern]
summary: "A per-area health record (grade, verification, agent legibility, test stability, boundary compliance, key gaps) that agents and humans both read, so codebase quality is tracked rather than assumed — sessions fix the lowest grade first, and simplification passes have a baseline."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--08-maturity-and-failure-modes.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--references.md
---

# Quality Document

A per-area health record that **both agents and humans read**, so codebase quality is
*tracked* rather than assumed.

| Domain / layer | Grade | Verification | Agent legibility | Test stability | Boundary compliance | Key gaps |
|---|---|---|---|---|---|---|
| Auth | A | passing | clear | stable | compliant | — |
| Payments | C | partial (callback untested) | logic spread over 3 files | 2 flaky | violations | callback e2e |

**Grades:** **A** all verification passing, clean and legible · **B** passing with minor
gaps · **C** partially working, hard for agents to follow · **D** broken or structurally
unsound.

Note the column that is unusual for a human-team scorecard: **agent legibility** — whether an
agent arriving cold can follow the code. Logic spread across files is a defect in an
agent-maintained codebase even when it works.

## Three Jobs

1. **Work selection.** A fresh session reads it and **fixes the lowest grade first** —
   priority is a lookup, not a judgment call re-derived every session.
2. **Trend.** The periodic cleanup loop updates it, so its change history shows whether the
   repository is getting stronger or weaker.
3. **Baseline.** It gives the subtraction pass in [[Iterative Harness Simplification]]
   something to measure against.

Update it after significant sessions and before a new phase of work — not on a separate
cleanup day, which never comes.

## See Also
- [[Harness Maturity and Failure Modes]] — part-of
- [[Runtime vs Process Observability]] — complements (a process-layer artifact)
- [[Long-Horizon Execution]] — complements (another file-backed state artifact a fresh session reads)
- [[Iterative Harness Simplification]] — prerequisite-for
