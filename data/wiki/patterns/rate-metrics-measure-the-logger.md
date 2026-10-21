---
title: Rate Metrics Measure the Logger
tags: [patterns, eval, pattern]
summary: "When what gets recorded depends on the instrumentation setup (a session wrote a note only if it compacted), population-rate metrics measure the logger and cannot be trended across a setup change. Make the regime an explicit column, trend only per-row properties, and check each field's meaning with one query before building a chart on it."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-19-context-engineering-dashboard.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-19-context-engineering-dashboard.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-15-gua-120-dashboard-metrics.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-15-gua-120-dashboard-metrics.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-46-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-46-research.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-46-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-46-plan.md
---

# Rate Metrics Measure the Logger

From the research and plan behind guacamayo's context-engineering dashboard. The goal
was a trend of Claude Code session health across months. The data covered two
instrumentation eras: summary notes from April to June, and raw session JSONL from July.

## Survivorship baked into the sampling frame

In the note era, a session produced a note **only because it compacted** (242 of 252
notes). So "compaction %" in that era is close to 100% by construction. A chart running
from April into July would show compaction collapsing. That is a change in the logger,
not in the sessions.

The fix was to treat the instrumentation **regime** as the independent variable and not
normalize it away:

- Every fact row carries a `regime` column. It comes from a small hand-owned lookup
  table, not from inference, and unmapped dates are labelled `unclassified`.
- **Per-row properties** (cost, cache hit rate, context size per session) are comparable
  across regimes. They get continuous trend lines with regime bands shaded behind them.
- **Population-rate metrics** (compaction %, sessions per week) depend on the sampling
  frame. They render as **separate per-regime panels**, each labelled with its frame. A
  test asserts that no rate metric produces a series that crosses a regime boundary.

A regime column makes survivorship visible. It does not remove it.

## Check every field before charting it

Two fields that looked usable were not:

- **A templated, never-populated field.** `friction_count` was present on 100% of notes
  and zero on 100%. Charting it would have shown friction "starting" the day the new
  logger began. A field that is always present and always constant is a missing field.
  The planned LLM backfill from note prose was gated on a 10-note spike: yield was 1 of
  10 against a 5 of 10 gate (most bodies were unfilled skeletons), so it was a **NO-GO
  with no spend**. Friction was declared "July forward only" on the dashboard itself.
- **A field with a misleading name.** `total_tokens` looked like context size. One query
  showed it equalled `input + output` exactly (235 of 235), excluding cache, so it
  measured output volume. The flagship "median session size fell from 220k to 184k"
  chart was cancelled before it was built. That check cost one query.

## Confounds and lost history

- **Segment by session kind before claiming cause.** Many short meta-sessions (tooling
  and config work) pull the median down whatever the hygiene rules are. The drift also
  *began before* the rule it seemed to show working. The dashboard was told not to
  claim causation, and meta-sessions are split from work sessions.
- **Compute-and-discard loses history.** The insights pipeline computed stats and kept
  none, and local session logs were retained for about five days. Every day without a
  store was history lost. The answer was an append-only, one-row-per-session fact table
  plus a staleness warning when snapshots stop arriving.
- **A draining buffer sampled on a schedule measures the drain.** A growth inbox that
  the consolidator empties to zero undercounts if polled. Promotion events must be
  logged when the transform runs.

## Schema presence is not data population (GUA-120)

A compaction-yield column existed in the schema but was populated on only 182 rows against
417 compaction events. A tile computed from it would describe 44% of events while rendering
identically to a full-population tile. The fix had two parts:

- an **era fence**: a named set of metrics valid only from the date their writer landed;
- a **rendered sub-population frame**: the tile shows `n=182`.

Adding a metric touched four sites, and the fence-membership site is the one that carries
the correctness requirement. A decoy store also turned up: a `sessions.db.bak` whose recent
mtime did not mean recent content. Pick the source by its content range, not its timestamp.

## Follow-up: the regression that ran backwards (GUA-46)

A later issue reported an "autocompact regression": it was active briefly, then stopped.
That framing came from hand-typed prose on this same dashboard. Raw transcripts showed
the **opposite**. There were zero `trigger: "auto"` compaction events on four days, even
though five sessions went past 300k tokens, and at least one every day from the fifth
day on. The dashboard's own embedded chart data rose across the boundary. Nobody had
checked the prose against the chart beside it, and the chart's hardcoded data array had
also gone stale. Nothing local explained the change, so the cause was upstream.

Two lessons for this dashboard:
- **A boolean collapses the axis the question is about.** `compacted` could not
  distinguish a manual `/compact` from the automatic mechanism, so answering the
  question meant grepping raw JSONL. The durable fix was persisting the per-event
  `trigger` and `preTokens`, so the next apparent regression needs no archaeology.
- **Narrative text on a dashboard is an unverified claim** that sits next to its own
  evidence. Treat it like a status column ([[Re-Derive, Never Re-Read]]).

## See Also
- [[Workflow Pipeline Telemetry Audit]] — related (the same lesson: telemetry measures where it was logged)
- [[Friction Is Rework, Not Error Rate]] — extends (the later reclassification of this dashboard's friction metrics)
- [[Every Column Names Its Reader]] — related (a field nobody populated is one nobody read)
- [[Falsifiable Hypothesis Gate]] — related (check the metric's meaning before believing the trend)
- [[Single Writer, Offline Consolidation]] — related (the draining inbox the consolidator empties)
- [[Hardcoded Dashboard Cells Are Expiring Claims]] — related (the other way a tile lies while rendering normally)
- [[Cumulative Metric Hides the Fix]] — related (a field's historical absence keeps a cumulative bucket from moving)
- [[Measuring Fixed Context Overhead]] — related (a one-time measurement recorded in the same dashboard's coverage table)
