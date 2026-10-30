---
title: Every Column Names Its Reader
tags: [infra, pattern]
summary: A column nothing selects is not documentation, it is a trap — four plausible, CHECK-constrained, well-commented status columns sat on one table while only one was read, and the dead ones were wrong about the rows that were actually published — so no column (or JSON field) is added until a named query, screen, or job reads it, and "nothing reads it" in an audit is a finding about missing plumbing, not a null result.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/playground/skills/design-system/SKILL.md
  - data/raw/claude-docs/playground/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/akira/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-28-data-stack-map.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis129-event-enum-escape.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/akira/skills/design-system/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/design-system/SKILL.md
  - data/raw/claude-docs/diskoe/skills/design-system/SKILL.md
  - data/raw/claude-docs/akira/docs/research/2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/claude-docs/akira/docs/research/2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b13b-venue-accessibility.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b13b-venue-accessibility.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b13b-venue-accessibility.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b13b-venue-accessibility.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b13b-venue-accessibility.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b13b-venue-accessibility.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b13b-venue-accessibility.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-b22-b12-operator-dashboard.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis142-redistribution-posture.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis142-redistribution-posture.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis142-redistribution-posture.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-puffin-next-version.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-puffin-next-version.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-b66-organizer-cap.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-b66-organizer-cap.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-b66-organizer-cap.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-b66-organizer-cap.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-b66-organizer-cap.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-b66-organizer-cap.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-b66-organizer-cap.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-31-data-tab-revision.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-31-data-tab-revision.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-31-data-tab-revision.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis73-occurrence-date-rule.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis340-audience-attribute.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis340-audience-attribute.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis340-audience-attribute.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-language-barrier-attribute.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-language-barrier-attribute.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-language-barrier-attribute.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-language-barrier-attribute.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-language-barrier-attribute.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-pipeline-harness-card-extract-qc.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-28-dis417-quality-panel-persistence.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis263-accepted-candidate-bridge.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis263-accepted-candidate-bridge.md
---

# Every Column Names Its Reader

A schema rule earned by a live audit of an events table (repo akira), then confirmed
twice more within a week.

## The original sin: four lifecycle columns, one real

Measured across all 476 rows:

| Column | Live distribution | Read by |
|---|---|---|
| `review_status` | draft 414 · needs_review 38 · rejected 15 · published 9 | app resolver + RLS policy — **authoritative** |
| `publish_status` | `not_publishable` × 476 | generated types only — dead *and wrong* |
| `event_lifecycle_status` | discovered 437 · needs_review 39 | generated types only — dead and wrong |
| `status` (legacy text) | two hardcoded values | written by importer, never read |

Nine events were published and publicly served while two columns said they were not.
The danger was never that they were unused — it was that they were **plausible**: CHECK
constraints, sensible vocabularies, confident comments. The next query author reaches for
`publish_status = 'published'`, gets an empty set, and debugs the wrong thing — or uses it
as a write target and creates a second visibility workflow.

## The rules

- **One lifecycle column per entity.**
- **Every new column names its reader before it is added.** If nothing selects it, it is
  not a column yet. Tables built ahead of their UI carry the reader in `COMMENT ON TABLE`
  — including honest ones that say "Phase 3, not yet built".
- **The rule applies to JSON fields too.** Adding `parent_event_id` inside an existing
  JSONB `items` column is no migration, but every reader of `items` still has to know
  the field exists or it is a dead field with a confident name.

## "Nothing reads it" is a trap, not a null result

An issue asked to "add a `redistribution_posture` column" so partner surfaces could serve
only redistributable sources. Investigation: the column already existed, correctly typed,
CHECK-constrained, commented, defaulting to the safe value — and nothing in `src/`,
migrations, views, policies, or admin screens read it. The issue was misframed: the
column was the cheap, already-done fifteen percent; the real work was the review pass to
set it and the reader to enforce it, neither of which had a line of code. A future
engineer finding the column would reasonably assume reading it is sufficient. It is not
— no join from events to sources even existed on the serving path.

The same shape appeared as a **built-but-unwired component**: a QC agent existed, was
tested, and was imported by nothing on the production path; and a "duplicate" enum value
and a detection resolver both existed while zero rows carried the value.

## Where the reader belongs

Resist adding a predicate to a generic layer that has no concept of the join. In the
redistribution case the visibility helper operated on the displayed row, not its upstream
source; the right seam was the existing hard-filter function that already carried the
`surface` the rule depended on. One reader, at the layer that already has the inputs.

## Dashboard panels: compute, persist, or say "unmeasured"

The same rule applied to an admin quality dashboard (repo akira, 2026-09-28). Each panel
showing NOT AVAILABLE gets exactly one of three verdicts: **compute it live** from data
that already exists; **persist** it (append-only, with a named reader); or **record a
"stays unmeasured" decision** that cites its blocker. Don't build dead instrumentation
for a feature with no live caller. A panel waiting on a nonexistent feature is a
decision to write down, not a table to create.

The follow-up plan resolved ten signals across four issue bullets. What it added to the rule:

- **A structurally guaranteed invariant is a convention, not a metric.** "No served order
  without a log row" holds by construction, so it was recorded as a review and lint
  convention, not a panel (D-178).
- **Adoption telemetry for a feature with no caller is dead code.** It stays unmeasured
  until the feature has a live caller (D-176).
- **A disclosed proxy beats a fake rate.** A per-rule fire rate that needs an unpersisted
  probe input stays a labelled proxy (D-175).
- **Name the real blocker.** 5xx counts were blocked on the production host's log access,
  not on the data model, so no table was added (D-177).
- **Write derived tiers at the caller.** Persisting a tier from the call site keeps the
  classifier pure.
- **A join-based live panel drifts from the as-served state.** It recomputes from today's
  rows, not what was shown at the time. The operator chose to build it anyway, with the
  drift written down.

## A Graded Vocabulary With No Cutover Has No Reader

An audience attribute was proposed as a graded scale. Its only consumer was a filter, and
no rule said which grade counts as "yes", so the graded value had zero readers. **For a
filter consumer, resolve to a boolean at authoring time.** The adopted shape:

- **Default-deny, off-by-default hard-filter flag.** Unknown never passes the filter, and
  the filter is off until a user opts in.
- **Don't collide with an existing axis.** The obvious name overlapped an existing
  `audience_fit` field with different semantics.
- **Authoring order:** enrichment is the primary author, content kind is a weak prior,
  and human verification confirms.

## Exclusion Filters Fail Open Until the Backfill (akira, 2026-09-21)

> **Sequencing, not contradiction (resolved 2026-10-30).** The section above, from the
> research doc, describes the end state: default-deny, so unknown never passes. The executed
> plan ships fail-open *until the backfill runs*. Default-deny over an unpopulated column
> empties the pool on merge day. Flip to default-deny once the backfill has populated it.

The executed plan for the same audience attribute shipped its reader (a hard-filter flag
in the eligibility gate) and the column in the same change, unlike the previous attribute,
which shipped column and labelling with no served-path consumer. That exposed a merge-day
hazard. The first predicate excluded anything not explicitly `'false'`, and the B2B surface
set the flag unconditionally. No row would carry a value until the new prompt version's
backfill ran, so the whole B2B candidate pool would have been empty on merge day.

The operator's resolution:

- **Only an explicit `'true'` excludes.** `NULL` (not yet enriched), `undefined` (a
  content kind that never carries the field) and `'unknown'` are all served. The flag is a
  documented no-op until real values exist, and it tightens on its own as the backfill
  fills rows.
- **Pin the load-bearing case as its own test.** "`null`/`undefined` is served" got a named
  test, separate from the `'unknown'` case, so a later enum cleanup cannot flip it silently.
- **Write the asymmetry into the spec row, not only the plan.** The accessibility clause
  next to it in the same gate is default-deny. Fail-open reads like a bug to anyone who has
  not seen the reasoning, so the decision row states it.

The two clauses are consistent once you look at which way each filter points. A
*requirement* filter (only show barrier-free) must deny unknowns, or a missing check
reaches the user as a promise. An *exclusion* filter (hide resident-leaning) over a column
nobody has populated yet must pass unknowns, or it removes everything.

The tri-state shape (`'true' | 'false' | 'unknown'`, with `NULL` meaning "not yet
enriched") was kept over a nullable boolean. It mirrored the previous attribute's
enum pipeline, and it separates "the model could not tell" from "never asked".

## Tri-State With a Default-Deny Filter (akira, 2026-08)

akira modelled venue accessibility as `confirmed` / `confirmed_not` / `unknown`, with the
column defaulting to `unknown`. Only `confirmed` passes the barrier-free hard filter. With a
boolean, "not yet checked" would merge into one of the two answers. With default-deny, a
missing check can never reach a user as a promise.

## Stored Vocabulary Disjoint From the Runtime Classifier (akira operator dashboard, 2026-08)

A stored `health_status` column used a vocabulary that shared no values with the runtime
classifier's output, so the column could not be read as the classifier's verdict. The dashboard
computes health at render time and shows the stored value separately as "Last stored status",
which makes the drift visible instead of hidden. Separately, a dashboard on a table with no
read policy returned silent zeros. See [[Written-but-Inert RLS Policies]].

## Don't Key a New Rule on an Existing Enum Literal (akira redistribution plan, 2026-09)

The research behind the redistribution filter proposed gating it on the `surface` value
`'concierge'`. The plan read the call sites and found that three production routes **already
sent** `surface: 'concierge'` for a hosted QR pilot. The design scope explicitly says that
surface is *not* redistribution: "a page on our own domain". All 92 sources were still at the
default `review_needed`. So the filter would have gone live at merge and excluded every
concierge pool. The route would then have fallen through silently to its empty-result demo
branch, and real guests would have seen placeholder events. An enum literal's meaning is
whatever the live callers already use it for, not what its name suggests.

The adopted shape:

- **A dedicated off-by-default flag** in the same hard-filter function, with a default-deny
  clause: only `may_sublicense` passes, and null or missing posture excludes. No caller sets
  the flag.
- **Two regression guards.** One test at the filter level, and one at the call-site level for
  the realistic regression of someone editing the call site.
- **Stated honestly as advancing, not closing.** The filter enforces nothing today. It turns
  eventual enforcement into a one-line flip, and it removes the "nowhere to enforce it"
  excuse for delaying the human terms review. It does not do the review. A future surface
  that sets the flag but forgets to populate the posture map excludes everything: safe, but
  opaque.

## A Human Reader Can Count, Under Two Conditions

Three new evidence columns (terms URL, reviewed-at, reviewed-by) were written by a manual
legal review and read by nothing in code. The change contract forbade that, and review
flagged it. The resolution amended the contract instead of inventing an admin UI. A named
**human** reader counts if:

1. The migration header names the reader and the decision the column serves.
2. The data-stack map records the column in the same branch.

The column names were prefixed so they would not collide with two existing "reviewed"
concepts on the same table (intake bookkeeping and crawl health). The columns were also
confirmed absent from the upstream sync's upsert payload, so a re-sync cannot overwrite a
recorded review.

## A Named Future Reader Is Not a Reader (akira venue bridge, 2026-09)

A plan added an `activities.description` column and justified it by naming its reader: the
enrichment prompt, via a sibling plan's input-shaping map, which would add the reading row "once
the column exists". The fix-stage review reverted the migration and every line that wrote the
column. The sibling plan had not landed, so the reader was aspirational, and the change contract
requires a reader **in the tree**, not a named future one. Ownership moved to the sibling plan,
which now adds the column and the row that reads it as one change. A decision recorded as
"decided" by the owner was overturned on this rule alone, and the plan kept both the struck
original steps and the revert note.

## Workflow outputs need a consumer too

The same rule holds outside schemas. An audit of an agent memory system found handover
notes written at every session end and **never read** at the next wake, plus a commands
layer with zero invocations. The redesign drew every artefact as producer → processor
→ destination → verified-by. An output with no consuming row was removed rather than
kept "for later". See [[Single Writer, Offline Consolidation]].

## Phantom Fields and the Honest Null (akira organizer cap, 2026-08)

A hard cap of two events per organizer needed an organizer identity that did not exist.
Duplicate detection already accepted an `organizer_id` — **a type-only field with no
column behind it**, which the importer never passed. The landing:

- **Name the whole read path first**: select list → row type → candidate type →
  composition adapter → ledger → threshold table. Seven files, no other reader.
- **Nullable, seeded only where the proxy is correct.** Backfill from the content-source
  id only where the source type *is* an organizer (an organizer site or event-series
  page); a venue site spans many organizers, so those rows stay null. Null is the honest
  state until the graph work validates a real identity, and **null means uncapped, not
  broken**.
- **Count before pushing.** If zero rows qualify, the cap is correct but unexercised.
- **Bespoke per-column backfills do not scale past two or three.** Record the fill rate
  of every column the ranker reads and build an imputation inventory instead of a new
  one-off seed per migration.

The mirror defect showed up when the schema was drawn as an entity graph: a per-occurrence
table **written on every import and read by nothing** (three writes, one test, one
generated type, zero selects) — so the ranker could not tell a six-week exhibition from a
one-night event even though the data existed.

## A Whole Table With No Serving Reader (akira occurrence rule, 2026-09)

The rule scales up from columns to tables. An occurrence table was migrated in, recorded as
"Built" with "existing queries unchanged", and written on every ingest. Its only reader
was the importer itself. That status line was accurate, and it described exactly the gap.
Meanwhile every serving reader kept consulting a collapsed earliest-date copy, so
recurring events read as expired after their first date. An issue filed months later asked
how to *design* occurrence detection, because nothing visible showed the data already
existed. A "Built" status for a table should name its first serving query, not only its
writer. See [[Event–Occurrence Split, Added Behind the Old Column]].

## Naming the Reader Up Front (akira, 2026-09)

Two later plans applied the rule before any column existed:

- **A new enrichment attribute shipped to its measurement readers only.** An audience
  language-barrier field (`none` / `english` / `english_friendly` / `german_only` /
  `unknown`). It describes the audience's barrier, not the listing's language: a
  German-language listing for a concert is `none`. Its decision row named its readers: the
  human label queue and the test-retest agreement report. It explicitly kept the column
  out of the served path's select list, because an unpushed column in a served select is
  a known outage class. No ranking modifier, filter or intake question until there is a
  measured fill rate and its own decision row, and `unknown` must never hard-filter. The
  column is nullable with a CHECK, and NULL means "enriched before prompt v5". A test
  asserting that every flattened key is a column of the *generated* insert type forced a
  two-phase build: push the migration and regenerate types before code can emit the key.
- **A venue-context table was costed and rejected for having no reader.** A pipeline plan
  needed venue "About" prose as LLM input. A `venue_about` table would cost the same crawl
  plus a migration, and had no production reader yet. So the text was derived per run
  from the cached HTML. The table becomes correct the day the LLM tier is wired into the
  importer, which is where it gets its reader. A `venues.description` column was rejected
  outright: it would look renderable while holding text the rights review forbids
  rendering.

## Rejected at review: a column with no reader in this PR (akira candidate bridge, 2026-09)

A bridge PR added a column that no code in the PR read. Its reader was planned for a later
issue. The reader contract rejected it. The migration was dropped from the PR and the
column moved to the issue that adds its reader, so the two ship together. The cost was one
migration less, and the schema never held a field that nothing read.

## See Also
- [[Event–Occurrence Split, Added Behind the Old Column]] — instance-of (a whole table whose only reader was its writer)
- [[Migration Done Means Pushed and Probed]] — related (the other half of the schema conventions)
- [[Taste vs Defect Verdict Split]] — instance-of (a plan that named readers before adding columns)
- [[Written-but-Inert RLS Policies]] — related (a policy no row can satisfy is the same trap in the security layer)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (plausible-but-dead values discovered by grep)
- [[Production Hardening Patterns]] — extends
- [[Four-Source Provenance Contract]] — related (the named provenance columns)
- [[Mislabelled Column Is Worse Than Missing]] — extends (a column with a reader can still be lying to it)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — related (the legacy status column the machine was writing)
- [[Landed Is Not Complete]] — related (a complete row with an unenforced join key)
- [[Single Writer, Offline Consolidation]] — related (the rule applied to agent workflow outputs)
- [[Rate Metrics Measure the Logger]] — related (a field present on every row and never populated)
- [[Done-When the Cheapest Write Can Meet]] — related (same plan; a migration reverted for a future-only reader)
- [[Insert-Only Upserts Strand Normalizer Fixes]] — related
- [[Keep the Source Subtype Before the First Collapse]] — instance-of (migration and its one reader shipped in the same branch)
- [[Quality-Gate Dashboard in Pipeline Order]] — related (the dashboard whose NOT AVAILABLE panels got these verdicts)
