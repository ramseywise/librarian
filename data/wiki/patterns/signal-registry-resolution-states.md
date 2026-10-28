---
title: Signal Registry with Resolution States
tags: [patterns, eval, pattern]
summary: Declaring every metric an experiment ledger may cite in one registry — (name, kind, resolver | UNOBSERVABLE, description) — and resolving each ledger row to one of four states (registered / needs-collection / unobservable / unregistered), which turned 49 unmeasurable hypotheses into an explicit collection backlog.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-19-telemetry-decision-log-and-hypothesis-skill.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-19_claude-setup-telemetry-review.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-29_dashboard-tabs_experiments.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-07-31_LIB-59-ledger-metric-chart-mapping.md
  - data/raw/claude-docs/guacamayo/skills/track/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_git-activity-granularity.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_skill-auto-extraction.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-58-experiment-verdicts-as-data.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-59-ledger-chart-annotations.md
---

# Signal Registry with Resolution States

## The finding that forced it

An audit of guacamayo's tooling ledger (the table of workflow hypotheses with typed
metrics) found **49 of 59 hypotheses unmeasurable**: every row whose metric was a
`presence:` or `absence:` claim had no resolver anywhere in the telemetry code, so
nothing could ever score it. 66% of the ledger was unfalsifiable, which meant the ledger
could only grow — rows entered as `hypothesis` and nothing could move them to
`verified` or `failed`. A separate dashboard-mapping pass had reached the same shape
from the other side: only 1 of 31 experiments mapped to any continuous timeseries.

The root cause was not missing instrumentation so much as **no place where "which
signals exist" was declared**. Metric names in the ledger were free text; the dashboard
had its own mapping dict; the verdict scorer had a third.

## The registry

`telemetry/signals.py` holds one entry per signal:

```
(name, kind, resolver | UNOBSERVABLE, description)
```

- `kind` ∈ `session | git | hooklog | repofile | unobservable` — the data plane the
  signal is read from.
- `resolver` is a callable, or the sentinel `UNOBSERVABLE` when the signal is
  intentionally declared but cannot be collected (so its absence from scoring is a
  decision, not an oversight).
- `repofile` resolvers are declared as `(repo, path-glob, pattern)` triples. A missing
  repo resolves to `None`, **never to a false absence** — the empty checkout is not
  evidence that the pattern is gone (see [[Silence Reads as Clean]]).

## Classifying what the ledger was asking for

Before writing resolvers, hypotheses were sorted by what kind of evidence they needed:

| Class | Source of truth | Count (approx.) |
|---|---|---|
| A | store-backed (already in the facts DB) | ~8 |
| B | repo-file content (needs a `repofile` resolver) | ~20 |
| C | unobservable — behavioural claims with no artefact | ~25–30 |

Class C is the honest category: "sessions compact more aggressively" or "the model
notices X" leave no artefact. Declaring them `UNOBSERVABLE` keeps them visible as
hypotheses while removing them from the scorable denominator.

## The four resolution states

Each ledger row's metric resolves against the registry to exactly one of:

- **registered** — a resolver exists and ran; the row is scorable.
- **needs-collection** — registered with a resolver, but the data it reads is not yet
  being collected (a collection backlog item).
- **unobservable** — registered with `UNOBSERVABLE`; a deliberate non-metric.
- **unregistered** — the metric name resolves to nothing; the row is malformed.

A dashboard renders the counts per state with a typed reason per row, replacing the
earlier binary "measurable: yes/no". Result after one implementation pass: scorable rows
7 → 18, unregistered 49 → 0, needs-collection 8, unobservable 30, no typed metric 3.
The unobservable count did not shrink — the point was to make it a number rather than
a silent majority.

## The companion gate

The registry is only useful if new rows cannot bypass it; that is the job of the
[[Falsifiable Hypothesis Gate]], which refuses a ledger row unless its metric resolves
to a registered signal. Together they turn the ledger from a wish list into a scorable
experiment set, in the sense of [[Experiment Tracking Schemas]].

## Needs-collection backlog is diagnosed, not assumed

A research pass on three rows all filed as blocked on one collection change found one needed
only a PR title column and two needed a new branch-grain table; a skill-candidate signal
was blocked because the parser discarded tool-call order. The registry state says *that*
a signal can't be scored; diagnosing *why* decides the fix — see [[Analysis Gap vs Collection Gap]].
At authoring time the `track` skill reads the registry rather than guessing and maps each
state to an action: registered → use it; needs-collection → emit the collection change
first; unobservable → rewrite the claim; unregistered → register in the same change.

## Two more states worth separating (librarian experiment ledger, 2026-07)

- **Insufficient data is not inconclusive.** An experiment-verdict plan stored
  `insufficient_data` (too few runs to judge) separately from `inconclusive` (enough runs,
  no effect). Collapsing them hides which experiments only need more time.
- **Unmapped is logged, not dropped.** A chart-annotation plan mapped only `ratio:`
  metrics to chart series. Ledger rows with other metric kinds are skipped with a warning
  naming them, so a new metric kind surfaces instead of vanishing from the chart.

## See Also
- [[Falsifiable Hypothesis Gate]] — prerequisite-for (the gate consults this registry)
- [[Experiment Tracking Schemas]] — extends (metric identity as a precondition for diffable runs)
- [[Silence Reads as Clean]] — extends (None-not-false for missing sources)
- [[Session Insights]] — extends (the insights pipeline whose recommendations become ledger rows)
- [[Analysis Gap vs Collection Gap]] — extends
- [[Telemetry Claim Verification Gate]] — extends (UNMEASURABLE verdicts route to a registry entry)
- [[Deterministic Skill-Candidate Detection]] — instance-of (a needs-collection signal)
- [[Re-Derive, Never Re-Read]] — extends
