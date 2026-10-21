---
title: Hardcoded Dashboard Cells Are Expiring Claims
tags: [patterns, infra, pattern]
summary: "Every hand-typed number or status on a dashboard, docstring, or CLAUDE.md is a claim with an expiry date (one card went stale within an hour, another said 0% while the live figure was 23%); tier the static content, regenerate what drifts, render never-run instead of a literal, and alert on recency and breadth rather than exit code."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-dashboard-static-to-telemetry.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-meta-feedback-liveness-signal.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-telemetry-truth-pass.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-18-gua-137-dashboard-facelift.md
---

# Hardcoded Dashboard Cells Are Expiring Claims

Finding from the guacamayo telemetry dashboard (2026-08). A hand-maintained card looks
exactly like a computed one. It goes stale silently, and the reader cannot tell which is
which.

## Measured decay

- A hand-maintained verdict card went stale **within an hour** of being written: it said 4
  decisive verdicts when the live count was 18.
- A Session Health card said **"0% over 150k tokens"** while the live figure was **23%**.
- About 343KB of an 808KB page sat in hidden regions that **were still regenerating** on
  every build. Nobody saw that content, but it still cost build time.
- A module docstring and the project CLAUDE.md quoted signal-registry counts ("59 rows, 7
  registered", "56 signals, 18 registered") taken from a one-day snapshot. Both were wrong
  within days.

## Tier the static content

| Tier | Action |
|---|---|
| Stale and already wrong | Replace with a computed value now |
| Will drift (any count, rate or status) | Generate from telemetry |
| Legitimately static (architectural verdicts, narrative) | Keep, and date it |
| Hidden but still regenerating | Remove or stop generating |

Docstrings and CLAUDE.md describe the **structure** ("N signal names across entries and the
unobservable list"). The number belongs in the live output. An executor told to update a
count must recount when executing, not paste the planned figure.

## A manual gate still has a liveness signal

The Feedback stage on the pipeline view was a hardcoded literal, so it was structurally
incapable of changing. The justification was that the stage is a human gate. But *being a
human gate and being observable are independent*: a manual step still has a last-fire
time. The fix:

- Derive the cell from the gate's log.
- The resolver returns `None` when the log is absent, **never 0**. A stage that has never
  run renders as grey "never run".
- Test fixtures must not write the real log, or the tests fabricate liveness.
- Check the documented log path against the code. In this case CLAUDE.md named the wrong
  file.

## Other rendering rules from the same pass

- A sparkline with fewer than 2 points shows "no trend (n=N)", never a fabricated flat
  line. Missing days are skipped, not zero-filled.
- Every injected HTML marker must exist exactly once, enforced by a test. The injector
  skips a missing marker silently.
- Do not take "latest" as the last item in a file. Retro headers were stored out of order
  (R0, R1, R10, R11, R9…), so `headers[-1]` reported a stale retro as the newest, with
  "never" as its date. Sort by the key before taking the last item.
- Alert on **recency and breadth** (when was this last produced, and how many sources fed
  it), not on exit code. A job that exits 0 having refreshed nothing is the common failure.

## See Also
- [[Telemetry Claim Verification Gate]] — extends
- [[Silence Reads as Clean]] — extends
- [[Rate Metrics Measure the Logger]] — extends
- [[Unit Tests Encode the Checker's Assumption]] — extends
