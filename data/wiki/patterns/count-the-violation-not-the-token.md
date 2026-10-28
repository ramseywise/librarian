---
title: Count the Violation, Not the Token
tags: [patterns, infra, pattern]
summary: "A boundary-refactor issue sized by grepping a token (`.from(` call sites) inflates and keeps re-inflating, from 34 to 106 to 128 files, because the count never asks whether a site is misplaced. Cluster the hits by layer against the architecture's own rules first: most were the I/O layer doing its job, and the real scope was a 39-file allowlist. Record that as premise_false, not narrowed."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis379-db-access-seam.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
---

# Count the Violation, Not the Token

From an architecture-review lane in repo akira (2026-09-23/24) titled "consolidate
database access behind a seam". The issue was sized as "34 `.from(` sites across 28
files". A one-day-later addendum re-derived 106 sites in 42 files under `app/` only. Then a
wider pass found 128 files across all of `src/`. Each recount was larger, and each was
treated as the scope.

## What the counts missed

Every recount counted raw `.from(` calls next to a database-client reference. None asked
whether a site was **misplaced**. Grouping the 127 files by directory and checking each
group against the repo's own layer rules changed the answer:

- `core/ops` (26 files) and `core/ingestion` (14 files) were the two largest buckets. The
  architecture docs define `core/` as the credentialed I/O layer that is never on the
  request path. A raw query there is core doing its documented job. There was no door for
  it to bypass.
- `products/*` internals are doors themselves, and `lib/` is shared substrate. Queries
  there are not leaks either.
- The defect the decision actually named was `app/**` code (routes, server actions, page
  loaders) reaching **past a product's door** to the database. That was a 39-file
  allowlist, not 127 files.

The plan said it plainly: the headline framing was **largely false, not merely stale**.
It recommended recording `scope_delta: premise_false` for triage telemetry rather than
`narrowed` (see [[Gate Pass Rate Measures Effort, Not Readiness]]). Two other rules applied:
re-derive the count when the work starts, and never trust a snapshot that has been sitting.

## Sizing the slice by cluster, not by site count

Inside the 39 files, the three files with the most call sites each touched two or three
data clusters. Migrating any of them meant building new access modules from nothing. The
first slice was the two files that touched **only** the source cluster. They fit the
existing module with a same-shape extension. That shrank the allowlist by 2 and showed the
ratchet still worked. Ranking by site count would have picked the hardest files first.

## Companion decisions from the same lane

- **Keep the lint rule scoped to where the defect lives.** The `db-access-boundary` rule
  stays `app/**`-only, with a named allowlist of files not yet migrated. Adding to the list
  is a diff a reviewer sees ([[Default-Deny Guard With a Named Allowlist]]). If `core/`
  consolidation is ever needed for a different reason, such as renaming a table in one
  place, that is a separately argued decision, not an extension of this rule.
- **Per-cluster access modules, not one gateway.** Products already have their own door,
  so a central gateway would duplicate them. The seam is one typed reader module per data
  cluster, for `app/` code that is not inside a product.
- **No speculative modules.** Two new tables from a concurrent plan had writers in the
  products and ingestion layers, which the rule cannot see. No empty access modules were
  built for them. A module is created by its first real `app/` caller, and the existing
  module's doc comment carries a one-line forward pointer.
- **A spec file is not a runtime input.** The per-table contract registry (cluster, PII
  class, retention) is checked at build time by a gate. Making the access seam parse it per
  request would make a spec file a runtime dependency, which nothing else in the tree does.
  It would also enforce an invariant nothing had yet violated. The two real PII invariants
  were already enforced elsewhere: pseudonym versioning at the products-layer writer, and
  user-scoped `.eq('user_id', …)` reads.

## See Also
- [[Default-Deny Guard With a Named Allowlist]] — extends (the allowlist-carrying rule this lane ratchets down)
- [[Stated Seams Drift, Enforced Seams Hold]] — related (why the seam got a lint rule at all)
- [[Gate Pass Rate Measures Effort, Not Readiness]] — related (`scope_delta: premise_false` as triage telemetry)
- [[Audit the Class, Not the Instance]] — related (classify hits before acting on a count)
- [[Data Clusters by Writer and Trust]] — prerequisite-for (the cluster taxonomy the access modules follow)
