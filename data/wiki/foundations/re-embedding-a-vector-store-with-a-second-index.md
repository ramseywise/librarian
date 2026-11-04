---
title: "Re-embedding a Vector Store with a Second Index"
tags: [foundations, pattern]
summary: "A new embedding model is a schema change the database cannot see: queries still run and return garbage, so build a second collection, dual write, shadow test on retrieval, then swap an alias and keep the old one for rollback."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--04-schema-and-data-migrations.md
---

# Re-embedding a Vector Store with a Second Index

Vectors from two embedding models are not comparable even at the same dimension. In a simulation with two random projections standing in for models, model A on index A gave recall@10 of 0.426; model B on index A gave 0.000 with no error (chance would be 0.0005). Only the collapse and the staleness carry over, not the figures. So no in-place migration: the expand phase is a whole second index.

## Steps

1. **Expand:** build a new collection from a snapshot, the slow and costly step.
2. **Dual write:** documents edited during the build go to both, or are replayed from a change log. Without it, 100% of the 500 documents edited during the build were stale in the new index.
3. **Verify:** run the retrieval evaluation set against the new collection (recall@10 = 0.551 in the simulation), querying with the model matching the index.
4. **Cut over:** one atomic alias change; vector stores and search engines provide aliases, some with several actions in one call.
5. **Contract later:** rollback is a second alias change while the old collection still exists and receives writes.

Record the model name and version with the collection so a mismatch becomes a checkable error.

## See Also
- [[Expand, Migrate, Contract]] — related
- [[Parallel Run and Reconcile at the Grain People Read]] — related
