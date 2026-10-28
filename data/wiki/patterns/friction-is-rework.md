---
title: Friction Is Rework, Not Error Rate
tags: [patterns, eval, pattern]
summary: A dashboard audit that found three of five "friction" metrics were productivity or safety signals, and redefined friction as rework — the user rephrasing or repeating a request — which no existing metric captured, leaving ~60% of true friction invisible.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-29_dashboard-tabs_friction.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-29_dashboard-tabs_context-health.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-29_dashboard-tabs_data-inventory.md
  - data/raw/claude-docs/guacamayo/docs/insights-summary.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-29-dashboard-tab-improvements.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-29-dashboard-tab-improvements.md
---

# Friction Is Rework, Not Error Rate

A session-telemetry dashboard had a "Friction & Quality" tab. A research pass asked of
each metric on it: *is this friction, or something else wearing the label?*

## The audit

| Metric | What it actually measures |
|---|---|
| Tool error rate (2–5%) | tool/environment health, partly ambiguous with user-cancelled calls |
| Hook blocks (38) | **safety working as intended** — a guard that stopped a bad commit is not friction |
| Bash antipatterns per session | model behaviour (substituting shell for native tools) — a cost signal |
| Interruptions | partly friction, partly the user steering |
| Multi-turn ratio | session shape — productivity |

Three of five were mislabelled. Counting hook blocks as friction was the sharpest
error: it rewards disabling guards.

## The redefinition

**Friction is rework**: the user had to say the same thing again. Operationally, a
rephrased or repeated request within a session (or across sessions on the same
artefact) — the model did not do what was asked and the human paid to re-ask. By that
definition, only ~40% of true friction was visible in any existing metric; the rest
needed a rework-cycle detector (request-similarity over message pairs) that did not
exist.

The data inventory confirmed the gap from the other side: friction *labels* were
counted but their text was not stored, so "which friction types are most common?" could
not be asked of the fact store at all. Captured-but-never-surfaced fields (response-time
distribution, per-session skill invocation lists) sat alongside fields nobody collected.

## Regrouping by engineering layer

The audit proposed splitting the tab into three groups, each with its own owner:

- **Prompt engineering** — model fit, sub-agent success rate, output clarity.
- **Loop engineering** — interruptions, antipatterns, rework cycles (the friction group).
- **Harness engineering** — context load, cache hit rate, tool errors, session shape.

Hook blocks move to harness as a *safety* count. The split matters because the
corrective action differs per layer: rework is fixed by better instructions, context
bloat by compaction policy, tool errors by environment.

## Companion findings on context health

The same pass found the context tab unmeasured against its own rules: a 30-turn
compaction heuristic with no turns-since-compact series, a "52% of cost in sessions over
150k tokens" claim with no cost-by-bucket metric, and input tokens absent as a series
despite being the lever the cost rules pull. The recurring shape — a rule in prose with
no metric that could falsify it — is the one the [[Falsifiable Hypothesis Gate]] exists
to stop at the source.


## Turning the audit into a plan: order by data risk

The plan that came out of this audit sorted the work into tiers **by data risk, not by
dashboard tab**:

- **Render-only, no deadline.** Input-token series, per-skill economics, per-tool trends,
  cost by context bucket, and experiment-lifecycle charts. All of this was already stored
  and only lacked series logic and a template.
- **Deadline-bound capture.** Turns-since-compact, compaction-trigger tags and
  repeated-request signals need new parser extraction into nullable columns. The source
  session logs rotate in about 5 days, so **every day of delay permanently loses a day of
  history.** These steps run first, standalone if the rest of the plan slips. The
  review-findings persistence fix (keep `source`, `id`, evidence state and merge impact
  instead of 10 of ~25 schema fields) has the same shape: cheap now, impossible to backfill
  later.
- **New infrastructure.** A post-merge disposition hook, rework-cycle detection, and
  baseline capture at experiment proposal time. Most experiments had no before-snapshot,
  so the ledger can chart lifecycle (status funnel, days to verdict) but not magnitude.

Two guardrails:

- **One owned region per auto-generated card.** The dashboard is hand-edited except for
  START/END marker regions that a daily job patches. Every new auto-refreshed card gets its
  own markers, or the cron and the hand edits overwrite each other.
- **A parser over a hand-maintained ledger must degrade, not crash.** A malformed row
  becomes "skipped N rows", never a failed build.

## See Also
- [[Session Insights]] — extends (the insights pipeline whose metrics this reclassifies)
- [[Friction Promotion Ladder]] — prerequisite-for (defines what is being promoted)
- [[Falsifiable Hypothesis Gate]] — extends (rules without metrics as the shared defect)
- [[Context Failure Modes]] — extends (context-health rules as un-instrumented hypotheses)
- [[Harness Events Are Not Task Failures]] — related (the error-attribution half of the same telemetry cleanup)
- [[Rate Metrics Measure the Logger]] — prerequisite-for (the dashboard's earlier sampling-frame audit)
- [[Dark Outcome Tier]] — related (the outcome tier the friction and cost tabs sit beneath)
