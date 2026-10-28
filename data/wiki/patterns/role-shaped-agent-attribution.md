---
title: Dispatch-Shaped Agents Hide Cost
tags: [infra, pattern]
summary: "When subagents are named by the mechanism that launched them (general-purpose, Explore, Plan) rather than the job they do, cost attribution fails by design: about 90% of subagent spend stayed unattributed. The fix is named role contracts for the 4–5 costliest recurring workflows, with ad-hoc dispatch left generic, plus an attribution rule that never guesses."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-23-context-engineering-v2.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-23-context-engineering-v2.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-24-GUA-26-usage-observability.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-24-GUA-26-usage-observability.md
---

# Dispatch-Shaped Agents Hide Cost

## The gap

A usage dashboard over coding-agent session transcripts could not attribute about **90% of
subagent cost** (139M tokens across 190 transcripts). The first diagnosis was missing
labels. The real diagnosis was a **design gap, not a labeling gap.** The agent names in
use (`general-purpose`, `Explore`, `Plan`, the review scanners) are *dispatch-shaped*:
they name the mechanism, not the job. Perfect labeling would still produce a breakdown
like "general-purpose spawned general-purpose", which says nothing about which workflow
spent the money.

## The fix: role contracts for the top workflows only

- Pick the **4–5 highest-cost recurring workflows** and give each a named agent with a
  role contract: a role-shaped name, a scope and an output.
- Leave one-off dispatch as generic. Naming every spawn adds ceremony without improving
  attribution where the money is.
- Target: the unattributed bucket shrinks from ~90% to ~20–30%. The proposed test was a
  named-subagent trial on the execute workflow.
- **Any topology view waits on this.** A per-session agent DAG (parent–child spawn edges,
  cost flow) was deferred until role-named agents exist *and* at least 20 sessions of
  named-agent data have been collected and checked. Without role names the graph is
  uninformative.

## Attribution without guessing

The instrumentation that came next (session-transcript parsing into a fact store)
attributes child transcripts in priority order:

1. If the child transcript carries an authoritative attribution field (newer CLI
   versions write one), use it.
2. Otherwise, if the parent made exactly N agent spawns and there are exactly N child
   transcripts, match them **by spawn order**. Each spawn's type, description and model
   come from the parent's agent tool-use blocks, with the type defaulting to
   `general-purpose`.
3. Otherwise, mark the child **`UNATTRIBUTED`**. Do not guess.

The count-equality condition is the important part. Positional matching is only safe when
nothing can have shifted the positions. A wrong attribution corrupts per-type cost tables
silently, while an explicit unattributed bucket stays visible and can be measured.

The same work added two cheap signals:

- A **session-intent classifier** (execution / scoping / meta / unknown, from skill use,
  read:edit ratio and which paths were edited), so a compliance rate like "execution
  sessions that invoke a skill" has the right denominator. It was labeled v1 heuristic on
  the dashboard.
- A count of explicit friction labels.

## Recurring review defect

One `json.loads` in the new parser had no guard, in a file where every other parse was
guarded. One malformed row would have crashed the whole dashboard build. When a codebase
has a guard convention, the single unguarded call site is the defect to look for.

## See Also
- [[Dark Outcome Tier]] — related (the same dashboard review that found Tier 0 unmeasured)
- [[Session Insights]] — extends (the transcript analytics this attribution feeds)
- [[Rate Metrics Measure the Logger]] — related (what gets recorded depends on how the logger is set up)
- [[Skill Preloading via Agent Definition]] — related (named agent definitions are where role contracts live)
