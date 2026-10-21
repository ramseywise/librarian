---
title: Ship Logging Before Features
tags: [llm, eval, pattern]
summary: "Serve-time logs cannot be backfilled, so instrumentation lands in the same commit as — or strictly before — the feature it measures: log the full ordered result set with version stamps and as-displayed position (click-only logs are at zero for replay, not 80%), decide the position convention for a new slot type before the first item is served, and keep the current system as a baseline arm."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/design-roadmap/SKILL.md
  - data/raw/claude-docs/playground/skills/design-product/SKILL.md
  - data/raw/claude-docs/playground/docs/open-questions.md
  - data/raw/claude-docs/akira/docs/onboarding-comments.md
  - data/raw/claude-docs/kiez-archive/docs/onboarding-comments.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/akira/docs/open-questions.md
  - data/raw/claude-docs/kiez-archive/docs/open-questions.md
  - data/raw/claude-docs/akira/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/onboarding-comments.md
  - data/raw/claude-docs/playground/docs/onboarding-comments.md
  - data/raw/claude-docs/diskoe/docs/open-questions.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
  - data/raw/claude-docs/akira/skills/design-product/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-product/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-product/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b26-kairo-baseline.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b26-kairo-baseline.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b26-kairo-baseline.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b26-kairo-baseline.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis141-five-plus-three.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis141-five-plus-three.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis141-five-plus-three.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis141-five-plus-three.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-17-dis312-beta-acceptance-run.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-17-dis312-beta-acceptance-run.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-17-dis312-beta-acceptance-run.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-17-dis312-beta-acceptance-run.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-17-dis312-beta-acceptance-run.md
---

# Ship Logging Before Features

A recommender's planning record (repo akira) treats instrumentation as a hard blocker on
serving ranked results, for one reason: **every week without it is permanently lost
data.** Everything else here follows from that.

## What to log

- **The full ordered result set**, not clicks. Replay and offline evaluation need what
  was shown and in what order; a click-only log is at *zero* for replay, not 80%.
- **Version stamps on every row** — ranker, enrichment, prompt, vocabulary, and so on
  (seven in this project). One of them was threaded as an option and passed as `null`
  for weeks; the row shape was right and the data was not.
- **As-displayed position** separate from ranked position, so a position-randomisation
  slice can separate "clicked because good" from "clicked because on top".
- **Viewport events including the negative** — `became_visible = false` is the row that
  distinguishes "saw it and passed" from "never scrolled that far".
- **The counterfactual** where cheap: what the item would have qualified for under the
  current rules (see [[Taste vs Defect Verdict Split]]).

## Decide the shape before the first serve

When a new slot type was proposed (three alternatives under each primary result), the
highest-risk item in the research was not the similarity algorithm but the log shape.
Alternatives had no parent/child field, no position convention (outside the primary
window? compound position?), and no `result_role` value — reusing the existing enum would
conflate "why chosen" with "relationship to primary". An alternative served today under
today's ambiguous position semantics **cannot be reinterpreted once the convention is
finally chosen.** The strict reading: the logging schema change lands before or in the
same commit as the first code path that serves one.

The same applies to UI decisions that change what a log event means: an alternative
behind a collapsed drawer makes `became_visible` mean something different from a primary
on screen, so the field (`alternatives_expanded`) has to exist before the drawer ships.

**The outcome signal is part of the shape (akira acceptance run, 2026-09-29).** A
two-tester beta acceptance round was re-checked twelve days after planning. Two of its
three original blockers had cleared (the judgment recorder and the session export were
built), and two blockers nobody had seen before were now binding:

- **No outcome signal had been chosen.** Self-report, commitment click, add-to-calendar
  or poll-resolved all needed a decision and one instrumentation change *before the
  operator's first pass logged anything*. Otherwise that round can never answer "did this
  help anyone".
- **The servable pool was four items.** A twelve-moment matrix run against it tests the
  catalogue, not the ranker, because most moments have nothing real to draw from (see
  [[A Sourcing Gap Is Not an Effect Problem]]).

A re-verification that only ticks off the original blockers misses the ones that only
show up once those clear. Restate the whole blocker table each time.

## Keep the baseline arm

An A/B design proposed comparing two new rankers. The decision-relevant comparison is
each against **current production**, so the third arm is the baseline. Paired with
ablation — degrade real events to create sparse ones rather than selecting naturally
sparse ones — this gave a 2–4× variance reduction at no extra cost, and the gate was
restated from "B wins ≥70%" to "95% lower bound exceeds 0.60".

## Two suites, never averaged

Hard queries (sparse events, recurring series, niche venues) are deliberately
over-sampled but live in a separate capability suite; the regression suite holds the
modal query distribution and is the headline metric. A low score on the capability suite
is a finding, not a regression — see [[Eval Suite Maintenance]].

## Skip, recoverability tiers, and retention (feasibility study, 2026-10)

- **Skip is not observable; it is derived:** impression ∧ in-viewport ∧ ¬open ∧ ¬save ∧
  ¬share ∧ ¬plan_add. Without viewport tracking, "not seen" is conflated with "skipped",
  which penalizes positions 4–5 — exactly where exploration and long-tail picks live.
- **Sequence instrumentation by recoverability** (tiers T-0 to T-3): what cannot be
  reconstructed later ships first.
- **Retention silently caps the replay corpus.** A 90-day raw-retention rule means the
  offline replay set never grows past 90 days unless a derived, de-identified corpus job
  ships in T-0. Never log raw coordinates; keep taste vectors in a separate deletable store;
  interleaving and A/B need a data-protection impact assessment.
- **UNRECOVERABLE requirements ship in the same commit** with the full field list and the
  cost stated in time ("wait 90 days again") — and predict the descope: T-0 shipped marked
  BUILT with 5 of 7 version stamps.

## Mark unrecoverable requirements and predict their descope

Planning skills give traffic-generated data its own requirement class, **`UNRECOVERABLE`**.
For each such requirement, state three things:

- what ships it (the same commit as the feature)
- the complete field list, enumerated
- what skipping it costs **in units of time**, e.g. "we wait 90 days again"

One shipped logging contract said "logging exists" and had no column for 5 of 7 version
stamps and 5 of 9 per-item fields. Then name the likely trim before anyone proposes it.
Viewport tracking and a small randomization slice are "usually the first thing cut" and
"feel like reasonable trims in week three". By week three the person proposing the cut is
right about everything except recoverability.

## When the Serve Is Gated on the Log Write (akira log-completeness plan, 2026-08)

An audit of akira's serve-time result-set log found that several required fields were absent.
The values had been computed during the request, then flattened away before the served-item
type was built, or discarded at the HTTP boundary. The plan's lessons:

- **New log columns are nullable.** The serve awaits the log write and refuses to serve if the
  write fails. A NOT NULL column plus one caller that wasn't updated would turn an observability
  change into an outage.
- **Size each gap by type before fixing it:** pure passthrough of a value that already exists,
  a small computation from an intermediate value, genuinely new instrumentation (`latency_ms`),
  or blocked on an unratified decision (`degraded_mode` was added as a nullable column with no
  writer). Never log a value that has no source.
- **Untyped insert payloads hide gaps.** The recorder took `rows: unknown`, so the compiler
  could not report the missing fields. The fix is a spy-based regression test that asserts the
  exact row shape.
- A populated but mislabelled column was the worst defect. See [[Mislabelled Column Is Worse Than Missing]].

## Staff views pollute the served-set stream

A desk-side "tonight" page for venue staff got serve-time logging *by construction*: it
fetched through the same recommendations endpoint with `surface: 'concierge'` and the
operator code, so the same recorder wrote the log row. The cost of reusing the path is
that every staff page load, including refreshes, logs as a served result set. That
inflates the surface's metrics, and the rows cannot be told apart from guest views until
an `is_operator_view` flag exists. Staff share taps were consciously not logged, because
a new interaction kind needs a schema change and nothing measured it. The rule: when a
non-user principal reuses a logged path, decide the viewer-role field before the first
serve, for the same reason as the slot-position convention above.

## Build It Dark, Pin the Boundary With a Leak Test (akira 5+3 plan, 2026-09)

The alternatives feature was split so the open log-shape question could not block
everything. Phases 1–2 built the deterministic similarity function and the composer's
alternatives selection as a pure, eval-gated capability. That needed no schema change, no UI
decision, and no serving change. Serving and logging waited for a human to choose the
position convention. Then the schema change and the serving change land **in the same
commit**.

The plan proved, against the code, that the dark phase **could not serve or log an
alternative**:

- The served order was built one candidate per slot from `slot.event_id`, so a new
  `slot.alternatives` field never entered the logged items.
- The API route picked exactly three fields off the composition object, never `slots`.

The proof held only for today's code. Spreading the object wholesale or flattening the new
field would compile cleanly and silently ship an alternative with no log semantics. So the
proof became two regression tests:

- The logged items equal the primaries, and no alternative id appears among them.
- The JSON response never carries `slots` or `alternatives`.

Each test was checked by temporarily breaking the boundary in a scratch edit and watching it
fail. "A discipline with no test is a comment." Two smaller rules from the same plan:
alternatives are a **ceiling with honest scarcity** (0–3, never padded to 3), and an
always-visible layout was preferred over expand-on-demand because a collapsed drawer would
need a typed-column migration on the viewport-event table.

## See Also
- [[Validated Concept vs Unmeasured System]] — extends (why the system was unmeasured in the first place)
- [[Eval Suite Maintenance]] — extends (the regression / capability split)
- [[Taste vs Defect Verdict Split]] — related (counterfactual logging at serve time)
- [[Experiment Tracking Schemas]] — related (the version stamps are the join key to the config)
- [[Observability and Runtime Patterns]] — extends
- [[Offline Annotation over Online Inference]] — related (a deterministic serving path is what makes the logged serve replayable)
- [[Fallback Mistaken for the Design]] — related (the surface review whose log-shape consequence this page states)
- [[Traffic-Gated Evaluation Ladder]] — prerequisite-for (replay and IPW-NDCG consume this log)
- [[Four-Stage Design Pipeline with Backflow]] — related (UNRECOVERABLE requirement class)
- [[Mislabelled Column Is Worse Than Missing]] — extends (the sharpest defect in a serve-log audit)
- [[Adversarially Independent Baseline Arm]] — extends (how to build the baseline arm so it could actually win)
- [[Frozen Version Stamps on Logged Results]] — related (freezing the intake instrument before the same acceptance round)
