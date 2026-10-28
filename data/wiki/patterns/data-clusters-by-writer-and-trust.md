---
title: Data Clusters by Writer and Trust
tags: [patterns, infra, pattern]
summary: Group tables by who writes them and what breaks if a row vanishes — "would deleting this row change what a user sees tomorrow?" — and never FK a measurement row to a product row that ages out.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/akira/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis37-replay-corpus.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis41-expired-event-sweep.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/playground/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis288-favourites-feedback-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis336-accommodation-census.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis336-accommodation-census.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis379-db-access-seam.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis379-db-access-seam.md
---

# Data Clusters by Writer and Trust

A schema convention worked out on a recommendation product (akira) once telemetry,
retention, and human labels all started competing for the same tables.

## The test

Every table belongs to one cluster, decided by one question: **would deleting this row
change what a user sees tomorrow?**

| Cluster | Writer | Deletion changes the product? | Examples |
|---|---|---|---|
| **Content** | ingestion pipeline, enrichment | Yes — catalogue, venues, enrichment rows | events, venues, AI enrichments |
| **Product state** | the user, via the app | Yes — saves, polls, profiles | saves, collections, poll votes |
| **Interaction / measurement** | service role only, append-only | No — logs, replay corpora, human labels | result-set logs, viewport events, rater labels |

The clusters have different trust classes. Measurement rows are written only by the
service role because *a client-forgeable log makes every metric derived from it unusable*;
product rows are client-writable under row-level security; content rows are written only
by the pipeline. Mixing clusters in one table (e.g. recording product-triggered saves in a
pure telemetry sink) blurs the line and later forces a retention policy on data that
should never have had one.

### A row that fails the test both ways gets its own cluster

A B2B prospect table (hotels discovered from OSM as possible paying customers) fits none of
the three: deleting a row changes nothing a guest sees (not content or product), yet it is
read back by an operator as a worklist (not measurement), and it answers "who might buy",
not "what did a user do". Forcing it into the content/source cluster would put it one
accept-button away from the public read path. The answer was a narrowly scoped **seventh
cluster, `prospect`**: a different writer and trust class, never joined onto a guest read
path by construction, RLS on with **no policy** (default-deny, mirroring the partner table),
no anon read. When a new table fails the deletion test in both directions, that is evidence
for a new cluster, not for bending an existing one.

## Rules that follow

- **One lifecycle column per table.** A `status` column that no query filters on is a trap:
  it looks like state management and is actually dead weight that will drift. Four such
  columns on the events table were dropped once nobody could name a reader.
- **Reference an ageing row through a plain column, never a cascading FK.** A 90-day
  retention job archived result-set descriptors and deleted the source rows; two
  interaction tables FK'd `result_set_id ... ON DELETE CASCADE` and lost every row in the
  same transaction, with no snapshot. The replay corpus and the human-labels table already
  demonstrated the fix: store the id as a bare uuid, validate with a trigger, let the parent
  age out.
- **Don't FK across a content-kind union.** When candidates come from several verticals
  (events, activities, venues), a single `event_id` FK rejects two of the three. Use a
  `(content_kind, id)` pair with a trigger that checks the right table.
- **Key labels to the specific enrichment row, not the content item.** A later
  re-enrichment must not silently reinterpret an old human judgment.
- **Build the retention/minimisation job while the table is small.** Deciding "90 days" is
  cheap at 18 rows and expensive at millions; the decision was recorded months before the
  job existed, and the gap is where the cascade bug lived.
- **A bare-uuid reference opts the row out of retention, too.** The retention job reached
  its child tables only through a hard-coded cascade, with no generic sweep of the
  interaction cluster. A log that stores `result_set_id` as a bare uuid is therefore kept
  indefinitely until a retention policy names it explicitly. Erasure still works through a
  separate `user_id ... on delete cascade` to the auth table. Any impression join older
  than 90 days must read the archive, which has no interaction detail.
- **Grant the validation-trigger function to whoever writes the table.** Copying the
  `service_role`-only grant from an admin-written log onto a user-written table (saves)
  would silently break every real user's save.

### No foreign key in either direction makes rollback one statement

The plan that built the prospect table took the isolation further. It added **no foreign
key from any supply-side table to the prospect table, and none from it to the venue
tables**, and the two share no column that would make a join natural. The whole feature
therefore rolls back with a single `DROP TABLE`: nothing references it, no ranker reads it,
no UI renders it. The "one careless join" argument cuts both ways. The plan also applied a
fill-rate reader test to the column list. A tag present on 1.4% of rows (`beds`) got no
column. Personal-name OSM tags are never read even opportunistically, which keeps the census
at zero personal-data exposure. And the operator-editable `contact_status` was deferred
until the BD tool that would read it exists.


## A Per-Table Contract Registry, Gated Both Ways (akira, 2026-09-23)

A data-platform plan turned the cluster taxonomy into a checked registry. A YAML file holds
one entry per live table (cluster, writer, PII class, readers, retention), and a gate diffs
it against the generated database types:

- **It fails in both directions.** `undocumented` (a live table with no entry) and `orphaned`
  (an entry for a dropped table) both fail. An env-var inventory check elsewhere is one-way
  for a reason: CLI-consumed names have no reader a scan can see. Tables have no such blind
  spot, because every live table is enumerated in the generated types.
- **A sentinel for what cannot be researched in one sitting.** A missing `cluster` hard-fails,
  since every migration header already declares one. `readers`/`pii` may carry `TODO_HUMAN`,
  which prints as a counted warning. Retention is never invented: a table with no ageing job
  gets `unspecified`, not a plausible-looking number.
- **It is a build-time spec, not a runtime input.** A follow-up DB-access plan declined to
  make the access seam parse the registry per request
  ([[Count the Violation, Not the Token]]).

## See Also
- [[Artifact Is Not Evidence: Push and Probe]] — complements (how the cascade loss was found)
- [[Cached Derivation Without a Recompute Path]] — extends (a lifecycle column that is a stale cache of another column)
- [[Append-Only Human Labels]] — instance-of (the interaction-cluster conventions applied to rater data)
- [[Data Engineering Foundations]] — extends (append-only logs and lifecycle as schema design, not afterthought)
- [[RLS On, No Policy for Server-Mediated Tables]] — related (the partner-table posture the default-deny convention mirrors)
- [[Write-Time Deterministic Holdout]] — related (a split column added to an interaction-cluster log)
- [[Edit In Place by Diffing on the Natural Key]] — related (a cascade that makes reinsert-on-edit wipe user rows)
- [[Count the Violation, Not the Token]] — related (per-cluster access modules follow this taxonomy)
- [[Decision-ID Reservation Across Concurrent Plans]] — related (the same plan's ledger, also checked both ways)
