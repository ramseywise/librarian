---
title: Cumulative Metric Hides the Fix
tags: [eval, meta, pattern]
summary: "An acceptance criterion measured on an all-time cumulative table cannot be falsified when part of the historical numerator is unfixable by design. Old rows that predate the field stay in the bucket forever, so the shipped fix looks like it failed. Split the bucket by cause, then measure the criterion on a rolling window after the change."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-45-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-45-research.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-45-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-45-plan.md
---

# Cumulative Metric Hides the Fix

From guacamayo GUA-45, "named sub-agent role contracts". The issue's acceptance
criterion was "unattributed sub-agent cost share < 30%", read from the session
dashboard's attribution table. The research found the unattributed bucket was really
**two causes blended together**:

1. **Data-availability gap.** Transcripts from before a CLI version have no attribution
   field at all, so their cost cannot be attributed whatever the agent was doing. Naming
   agents cannot fix it, and backfilling is impossible because the field never existed
   for those versions. The table had 217 unattributed transcripts against 102 attributed
   ones, which fits a large historical backlog.
2. **Dispatch-shape gap.** This was the real target. On *attributed* transcripts, spawns
   defaulted to `general-purpose` (72% of spawn counts, 9% of attributed cost) because
   the calling skills passed no named agent type.

Naming agents shrinks cause 2 going forward. On the cumulative since-inception table,
cause 1's carryover keeps the aggregate above 30% until enough new sessions outweigh it.
**The fix would ship, work, and read as a failure.**

## The rule

- **Decompose a bucket metric by cause before using it as an acceptance criterion.**
  Each cause has its own remedy, and some have none.
- **Measure on a rolling window after the change**, e.g. the last N sessions after the
  version cutover. If the metrics code has no windowing parameter, adding one is in
  scope, because without it the criterion cannot be measured. GUA-45 added a
  `--since`/`--window` option to the attribution totals for exactly this reason.
- Write down which reading the criterion uses. The cumulative and windowed views give
  different verdicts on whether the change "worked".

## The re-scope that came with it

The same research found that the issue's five candidate workflows were a mix of four
situations: already solved (two scanners had role contracts), architecturally forbidden
(the execute skill bans sub-agents in its first line), no dispatch at all (git operations
and a one-shot Python insights script), and genuinely the target (research fan-out
scouts). The plan shipped **one** named contract and recorded a "no action" disposition
for the other four. Inventing delegation to hit the issue's "4–5 workflows" headcount
would have been the anti-pattern its architecture reference warns against: "do not spin
up a subagent to avoid writing a tool". See [[Verify the Issue's Premise Before
Planning]].

## See Also
- [[Rate Metrics Measure the Logger]] — extends (the same dashboard; there the logger changed, here the field's availability did)
- [[Verify the Issue's Premise Before Planning]] — related (the candidate list did not survive inspection either)
- [[When a Lens Earns Agenthood]] — related (delegation only for isolation or parallelism, never to hit a count)
- [[Falsifiable Hypothesis Gate]] — related (an acceptance criterion that cannot fail checks nothing)
