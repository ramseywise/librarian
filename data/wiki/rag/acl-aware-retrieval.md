---
title: ACL-Aware Retrieval and Tenant Isolation
tags: [rag, infra, comparison]
summary: "Where to enforce who-may-see-what in a shared vector/hybrid index: post-filter starves the candidate pool, pre-filter loses ANN, metadata-aware ANN plus RLS is the default, and similarity search adds leak modes exact-match queries never had."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_team-rag.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_librarian-retrieval.md
---

# ACL-Aware Retrieval and Tenant Isolation

A RAG index shared by more than one team, client, or permission level needs an access
filter on every query. That sounds like a `WHERE` clause. In fact it is a retrieval-quality
problem, a database-security problem, and a vector-specific leak problem all at once.
(Source: a research survey for a zero-budget, volunteer-maintained team knowledge base.
Medium confidence: these are literature claims, not measurements on this wiki's own system.)

## Where the filter runs: three choices

| Strategy | Mechanism | Failure |
|---|---|---|
| **Post-filter** | Run ANN over the whole corpus, then drop unauthorized hits | **Pool starvation.** When the authorized subset is sparse, the graph walk uses up its k candidates before enough authorized ones survive. At 1% selectivity, recall@10 drops from 0.97 to 0.79. |
| **Pre-filter** | Restrict to authorized rows, then search | Search over the filtered subset turns into a brute-force scan and the ANN graph is no longer used. Fast filter, slow search. |
| **Metadata-aware ANN** (hybrid indexing) | Index the scalar ACL fields and keep ANN restricted to the filtered subset without leaving the graph | Needs an index that understands the metadata natively. This is the production default. |

Selectivity decides between the first two. At about 10% selectivity pre-filtering wins, and at
50% or more post-filtering does. Systems that care measure selectivity per tenant.

**Filter columns are not auto-indexed.** Many vector stores *accept* a `tenant_id` filter
without indexing it. Every query then scans the corpus before filtering, and the bill shows up
as CPU and latency, not as an error. Explicitly index every field used in a filter.

## Who enforces it

| Layer | Strength | Weakness |
|---|---|---|
| **Postgres RLS** | The final gatekeeper. A forgotten `WHERE` still returns nothing, which makes it the hardest layer to bypass by accident. Suits ad-hoc code review. | Has footguns (below) |
| **Application layer** (middleware checks `tenant_id`) | Flexible, with per-endpoint policies | Only a suggestion, not a guarantee. Forgotten filters, bulk imports and migrations without tenant context, and analytics queries that need cross-tenant aggregates all slip through. |
| **Separate index per tenant** | Strongest isolation. Use it for high-sensitivity tenants such as client data. | Costs more. Industry practice is split, and shared-plus-filter wins at zero budget. |

### RLS footguns

1. **`SET` vs `SET LOCAL` under pooling.** `SET app.tenant_id = …` lasts for the life of
   the connection, so with a pooler the next request inherits the previous tenant. Always use
   `SET LOCAL`, which is transaction-scoped.
2. **Owner and superuser bypass.** Table owners and superusers skip RLS by default. The app must
   connect as a dedicated non-owner, non-superuser role.
3. **`SECURITY DEFINER` functions** owned by a privileged role can quietly bypass RLS. A
   misowned bulk helper is the usual way this happens.

RLS also has blind spots inside the database itself. It gates rows, not columns
([[RLS Gates Rows, Not Columns]]), and a policy can be written yet inert
([[Written-but-Inert RLS Policies]]).

## Failure modes specific to vector search

- **Similarity search is cross-tenant by nature.** An exact-match query with a forgotten filter
  often returns nothing. A similarity query with a forgotten filter returns *similar documents
  from any tenant*. So the tenant filter must be a required argument of the query API, never
  an optional one.
- **Membership inference.** Crafted queries can probe whether a document exists in another
  tenant's index from similarity scores alone. The filter has to apply before scores are visible.
- **Noisy-neighbour recall.** One tenant that is much larger, or has an unusual embedding
  distribution, can dominate graph regions and drag down recall for smaller tenants.
- **Bulk hard deletes damage HNSW.** Removing many vectors at once can disconnect graph
  regions, and latency and recall then suffer for *every* tenant. Soft-delete instead
  (mark the vectors, rebuild asynchronously).

## Logs and traces are a second leak surface

Query text and retrieved chunks carry the same restricted content as the index. Redact them
at the shipper (e.g. an OTel Collector processor), before they leave the process. Audit lines
should record counts and IDs (`documents_returned=5 restricted_docs_accessed=1`) with the
query itself redacted.

## Path-prefix privacy is not tenancy

A single-user wiki that keeps private material under one directory and checks a path prefix
at read time has *one* boundary, private versus public. That design does not generalize to
per-row ownership by several writers. Moving to multi-tenant means a real ownership column and
enforcement at one of the layers above. It is not a longer prefix list.

## Hybrid search does not remove hard queries

Fusing BM25 and dense results ([[Reciprocal Rank Fusion (RRF)]]) solves score normalization.
It does not help with negation, entity disambiguation, or rare identifiers. Route those to an
explicit reranking or override path.

## See Also
- [[Reciprocal Rank Fusion (RRF)]] — extends (the fusion step these filtered candidate pools feed)
- [[RLS Gates Rows, Not Columns]] — prerequisite-for (RLS scope limits before relying on it for tenancy)
- [[Written-but-Inert RLS Policies]] — extends (policies that exist but never bind)
- [[Vector Database Comparison]] — extends (backend choice determines which filtering strategy is available)
- [[Multi-Writer Agent Memory Systems Comparison]] — extends (the same scoping-vs-auth question for memory stores)
