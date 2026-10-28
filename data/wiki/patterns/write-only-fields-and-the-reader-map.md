---
title: Write-Only Fields and the Reader Map
tags: [patterns, eval, pattern]
summary: Audit every produced field by building its reader map — written by what, selected by what, read by what — because the expensive failure is a value the prompt spends lines teaching the model to produce and the pipeline then throws away at a seam.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase8-rag-rightsize-agentic-search.md
  - data/raw/claude-docs/listen-wiseer/docs/reviews/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--reviews--phase8-rag-rightsize-agentic-search.md
  - data/raw/claude-docs/akira/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/akira/docs/research/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/akira/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/akira/docs/research/2026-09-09-source-register-and-segments.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-09-source-register-and-segments.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-09-source-register-and-segments.md
  - data/raw/claude-docs/playground/docs/research/2026-09-09-source-register-and-segments.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/playground/docs/research/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/playground/docs/research/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/playground/docs/research/2026-09-10-results-surface-design.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-08-review-sweep.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-08-review-sweep.md
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-34-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-34-review.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b32-location-permission.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b32-location-permission.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b32-location-permission.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b32-location-permission.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b32-location-permission.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b32-location-permission.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b32-location-permission.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b41-operator-identity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b41-operator-identity.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis147-source-registry.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis147-source-registry.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis147-source-registry.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis147-source-registry.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis273-enrichment-output-readers.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis273-phase2-enrichment-schema-reshape.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis273-phase2-enrichment-schema-reshape.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis273-phase2-enrichment-schema-reshape.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis273-phase2-enrichment-schema-reshape.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis273-phase2-enrichment-schema-reshape.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-61-insights-section-contract.md
---

# Write-Only Fields and the Reader Map

A recurring audit shape on an LLM-enriched recommendation product (akira). The question is
never "is this field populated?" but "who reads it, and at which layer does it stop?"

## The reader map

For each field: **written by** (which prompt/vertical) → **selected by** (does the loader's
column list include it) → **read by** (which scoring dimension, UI surface, or export) →
**verdict** (KEEP / WIRE / RESHAPE / DROP). Built field-by-field from code, not from the
schema doc. Findings from one pass over ~20 enrichment fields:

- `content_type`: written by every vertical, **absent from the loader's column list**, so
  the ~15 prompt lines teaching the model to resolve bar-vs-restaurant were discarded in
  favour of the raw source field the prompt told it to treat as only a hint.
- `audience_fit`: loaded onto the candidate, then never read by any dimension.
- `commitment_level`: dead in scoring *and* fetched by the one UI page that never rendered it.
- 7 of 29 `context_tags` values and 22 of 25 `decision_signals` values: prompted for in
  detail, structurally unreachable as match targets because the only intake passthrough was
  hard-coded `null`.
- Of 14 columns synced into a source registry, 6 were load-bearing in code.

## Built-but-dropped-at-the-seam

The inverse case is as common: the hard part is done and a seam discards it.

- **A prompt-specified output with no column (akira, 2026-09-10).** The enrichment
  prompt asked the model for `description_generated` in three places. The flatten,
  validate and sanitize chain dropped it silently, because no column existed for it
  (`grep description_generated supabase/migrations/` returned zero hits). Meanwhile the
  detail page rendered the raw scraped `description`, which was the source-prose rights
  exposure the rewritten field was supposed to replace. The fix added the column and
  threaded the field through the write path. Until re-enrichment backfilled them, the
  ~266 events without the field rendered **no description at all**, not a raw snippet.
  That interim gap was chosen explicitly.

- The ranker computed per-candidate breakdowns, full order, and exclusion reasons;
  production tallied exclusions as *counts* and truncated to the top 5, so a benchmark
  corpus could not be built from what the live path kept.
- "Alternatives" (0–3 similar items per primary) were fully built — similarity function,
  thresholds, attach step, eval metric — and dropped by the feed layer, the API mapping,
  and the card component, each independently. A first grep said "not built" because the
  code lived one directory deeper.
- Two sibling link-discovery functions kept *different* path-keyword allow-lists; the
  broader one found a venue's calendar at `/termine/`, the narrower one then dropped every
  `/termine/<slug>` detail link on that page. 92 of 427 unreadable calendars needed no new
  extractor at all — only the lists unified.
- **Computed and discarded (listen-wiseer, Phase 8).** A query-understanding module
  produced `intent`, `confidence`, `entities`, `sub_queries`, `expanded_query`, and
  `retrieval_mode`; the graph read only the first four, and `sub_queries` (multi-hop
  decomposition) was threaded through state as `query_variants` with no consumer. The fix
  was to make decomposition and complexity scoring *drive* search fan-out and test them for
  real — reuse over new machinery. The reference graph being borrowed from had the same
  smell: its corrective-loop signal `should_continue_crag()` was defined but never wired.
  Read the wired graph, not the module list, before borrowing a pattern
  ([[Provenance-Tiered Confidence Gate]]).

## Rules

- **Every produced attribute needs a named reader or an eval metric**, and preferably both;
  an attribute with neither is cost without signal.
- **Distinguish a vocabulary gap from a corpus gap.** A segment nobody can tag (value
  absent from the vocabulary) needs a prompt change plus re-enrichment plus a metric; a
  segment with vocabulary but no rows needs sourcing. They look identical in a count of
  tagged items and have different fixes.
- **Serve what you already have before sourcing more.** 35 hospitality rows existed with a
  complete vocabulary and no read path; that is a wiring gap, not a sourcing gap.
- **Split wiring slices from prompt/schema slices.** Pure wiring (loader columns, mapping
  tables, a hard filter) ships independently and is gated by existing metrics; anything
  touching a prompt or schema waits for the experiment runner.

## Upload metadata that never reaches the pipeline

A review of an early galactus build found the same defect at an API seam. On upload, a
`role` column (`sender`/`receiver`) was validated against an allow-list, stored, made
filterable in the store, and echoed back in the 201 response. All of that told clients
the distinction mattered. Neither generation caller passed `role=`, so a company with PDFs
under both roles had its receiver documents ingested as sender facts. That broke the
prompt layer's own stated design ("a flat list invites the model to mix them"). A store-level test of
the filter kept the suite green, because no test sent mixed roles through the API. The
reader map would have shown it at once: the field had a writer and a selector, but no
reader on the path that mattered.

The same review dropped a proposed blocker ("receiver PDFs aren't validated like sender
PDFs") as intended behaviour. Checking that wrong finding is what surfaced the real one
in the same code path.

## A seed field whose documented writer does not exist

A template added a `non_functional:` block to a design YAML with a comment saying the
discovery interview fills it. The interview's instructions wrote the answers only to
DESIGN.md prose; a repo-wide grep found the definition, a comment pointing at it, a gate
row that read DESIGN.md instead, and nothing else. The plan had accepted "nothing *reads*
it, so nothing catches drift" — but nothing *wrote* it either, so the keys stay null
forever and there is no drift to catch. A declared, reserved seed field is defensible;
a comment naming a writer that does not exist misleads whoever builds on it next. Fix:
add the write, or reword the comment to "reserved; no writer yet."

## Readers without a writer

The reverse audit finds fields that every consumer reads and nothing produces:

- **Near-me location.** The intake type had `near_me_location`, the interpreter read it,
  and the location-fit dimension used it when present. The form never called the browser
  geolocation API, so choosing "Near me" always fell to a constant 0.4 and
  `location_coordinates_missing`, and distance ranking was dead on that path. The fix was
  one component. Request location on the tap that already showed intent (no second
  button). Use coarse accuracy, because scoring buckets at 1.5 and 5 km and GPS spin-up
  buys nothing. On denial, unset the choice and offer the district picker. On timeout,
  keep the choice and let scoring degrade.
- **Operator district.** The intake already preferred `operator_district` over the
  user's manual district and marked the question `supplied`, but nothing turned an
  operator code into a district. The new resolver only had to *produce* the value
  ([[Async Seam Before the Table]]).

In both cases a grep for the field shows plenty of hits, all of them reads. Tracing each
consumer back to its writer is what exposes the gap.

## Moving the writer from a sync to a human

The follow-up plan removed the external-document sync entirely. The Postgres table was
already the only thing any automated path read, so only the *writer* changed, from a
sync script to a person editing rows in the database's table editor. The reader map
became the before/after contract: for each load-bearing column, the old writer, the new
writer, and the unchanged readers. A new test loaded the registry from a fixture the sync
never touched, which proved the read path did not depend on where rows came from.

- **The constraint type decides how a typo fails.** Three columns were `TEXT CHECK (...)`.
  In the table editor these are free-text fields, so a wrong case fails loudly on save.
  An unconstrained `TEXT[]` column takes any value, and a typo there saves silently and
  only shows up when the importer's exact-string branching skips the row. The how-to
  for the human editor called out that silent field specifically. Converting to native
  enums, which would give a dropdown, was flagged as separate schema work.
- **Gate the deletion on a data-safety check.** Before deleting the sync, the steps were:
  a refresh-only fetch, a row-count cross-check against the table, one final full sync,
  and a committed one-time CSV export of all columns. The export included the write-only
  ones, which may hold the only copy of editorial notes. Its README says the table, not
  the file, is current.
- **Have a fallback for a credential that may already be dead.** The sync's token was
  documented nowhere, so nothing had kept it current. If it failed, the plan compared
  against the last independently corroborated row count, still exported from Postgres,
  and named the accepted loss in the PR: any edits made since the last successful sync.
  An expired credential makes the snapshot incomplete. It is not a reason to keep a dead
  sync path alive.
- **Correct a stale issue body when closing it.** The issue claimed a sequencing
  dependency on the scheduled-ingestion work that research had shown did not exist. The
  plan said to correct the issue text when closing, so nobody re-adds the gate later.

## Executing the wiring slice (akira DIS-273 plan, 2026-09)

The plan that acted on the enrichment reader audit added these lessons:

- **A guard ahead of the "no preference" branch zeroes a whole content class.** Standing
  content (activities, bars, restaurants) scored a hard 0 on a 15–20%-weighted time-fit
  dimension even when the user never asked for a time. The `!start_at` check ran before the
  no-time-preference branch. The cheap fix was reordering the branches. The richer
  availability signal turned out to be pure wiring as well, because the columns were already
  written, so it shipped in the same phase.
- **Select only what gets a reader in this slice.** Four activity-only columns were already
  written, but only the two that got a designed reader were added to the loader's column
  list. The other two wait for a reader ([[Every Column Names Its Reader]]).
- **Update fixtures in the same step as each wiring change**, not in a trailing "update evals"
  step, so the eval gate never goes red for the next agent to untangle blind.
- **A grader and a test each kept a hand-maintained copy of the same constant.** Review
  found that the format-crossing map existed twice, once in the gated grader and once in a
  unit test, with nothing keeping them in sync. Fix: export it once from the ranker table
  that owns it. Keep the grader building its universe from the *enrichment* vocabularies,
  never from the table it checks, so it cannot pass by construction. Proved non-vacuous:
  removing one entry turned both checks red.
- **Dropping a field has a reader outside the pipeline.** One field slated for removal was
  also one of the three dimensions a human rating screen asks about, and the screen's labels
  were about to be persisted. Remove the field before the rating screen is updated, and
  raters keep judging a dimension the model no longer produces.
- **Prompt and schema slices wait for the runner.** That is
  [[Offline Prompt Experiment Runner]].

## Acting on a DROP verdict (akira DIS-273 phase 2)

The schema-reshape phase acted on the audit's DROP verdicts and found that "no pipeline
reader" is not the same as "no reader":

- **Deprecate in place when off-path readers exist.** One field marked for DROP was named in
  a human-label CHECK constraint, in a rater-agreement (κ) export, and in two rater UIs. A
  `DROP COLUMN` would have broken all three. The field instead stopped being generated and
  was marked deprecated, and removal waits until those readers move.
- **Freeze the control before editing.** The current prompt was committed as a frozen
  control variant *before* any prompt edits, so the reshaped prompt is compared against what
  actually ran, not against a reconstruction.
- **A prompt hash guard forces the version bump.** A test pins the SHA-256 of the prompt
  text, so every edit failed until `PROMPT_VERSION` was bumped (v1 to v4 across the phase).
  Logged results therefore always say which prompt produced them
  ([[Frozen Version Stamps on Logged Results]]).
- **Re-check the audit's premises before acting.** One "write-only" field already had a
  reader for one content vertical. The plan corrected the premise rather than dropping a
  field that was in use.

## See Also
- [[Cached Derivation Without a Recompute Path]] — complements (the writer-side twin: stored, never recomputed)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — complements (a check with a blind spot is the same audit applied to guards)
- [[Frozen Version Stamps on Logged Results]] — extends (what the exposure code must log once it keeps the breakdown)
- [[RAG Eval Gate Contract]] — related (row pools and failure labels as the eval-side reader map)
- [[Fallback Mistaken for the Design]] — related (the review that found alternatives built but dropped at the serving seam)
- [[Parsed Then Dropped at the Insert Mapper]] — extends (parsed with no writer: the mirror seam)
- [[Size the Chain to Its Join Key]] — extends (a chain sized for a key 97% of rows lack)
- [[Every Column Names Its Reader]] — extends
- [[Async Seam Before the Table]] — related (the producer built for a seam whose consumer already existed)
- [[Offline Prompt Experiment Runner]] — related (the try-before-shipping tool the prompt/schema slices wait on)
- [[Keep the Source Subtype Before the First Collapse]] — extends (the reverse seam: a column read by the prompt but hard-coded empty by every writer)
- [[Defined but Never Wired]] — extends (the output-side twin: a prompt constant defined and never passed to the call)
