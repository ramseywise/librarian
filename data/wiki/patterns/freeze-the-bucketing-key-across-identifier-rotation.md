---
title: Freeze the Bucketing Key Across Identifier Rotation
tags: [patterns, infra, eval, pattern]
summary: A deterministic split that is recomputed on read (holdout, experiment arm) must not key on an identifier you plan to rotate, such as a pseudonym. Rotating it silently re-buckets every existing user. Decouple the bucketing key, freeze it as exactly the old function, say why in a comment so nobody "fixes" it, and version the pseudonym scheme instead of rewriting history.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis374-data-platform-maturity.md
---

# Freeze the Bucketing Key Across Identifier Rotation

From a data-platform hardening plan (repo akira, 2026-09-23). The spec required interaction
logs to carry a salted HMAC pseudonym with 90-day key rotation. The code used unsalted
SHA-256, while a doc comment called it "salted". The function's own comment explained the
gap: it matched a migration backfill exactly, so rows from before and after the migration
shared one pseudonym. A one-line swap to HMAC would have split every user's history in two.

## Version the scheme, never rewrite history

- **Rows written under v1 stay frozen.** A rotation is a new scheme version with its own
  secret (`..._SECRET_V<n>`), never a reused key and never an in-place rewrite. A version
  column on the row records which scheme produced it.
- **Keep every retired secret.** Rotation only changes which version *new* writes use. An
  export or erasure job that must find all of a known user's rows computes the pseudonym
  under every version that has ever existed and matches with `IN`.
- **Write paths and read paths fail differently.** The write paths were already in a
  try/catch, so they could fail loudly on a missing secret without turning a save into a
  500. The read paths were not, so a throwing pseudonym function would crash a page render
  or an eval export. A read must never throw on a missing secret. It must also match *any*
  version a user's rows may carry, or a user's own history disappears the day the new secret
  is set.

## The blocking finding: three "reads" were bucketing

The plan listed four call sites as "read paths that reproduce a pseudonym to match existing
rows" and told each to switch from `.eq` to `.in` over all versions. A refine pass checked
the tree. **Only one was a matching read.** The other three passed a single pseudonym into a
pure hash, `computeBenchmarkHoldout(pseudonym, kind, itemId) → boolean`. That function
decides which side of a train/benchmark split a signal falls on
([[Write-Time Deterministic Holdout]]). There was no lookup to widen. And as soon as the v2
secret was set:

- live re-derivation on every render would compute holdout status under v2 for users whose
  stored rows were bucketed under v1, so the boolean **flips for existing users**;
- a write-time recomputation would bucket new review rows under v2 while the same user's
  save rows stayed v1, breaking the stated invariant that both tables share one split.

**Reading the stored column does not fix it.** The render-time check runs for arbitrary
items the user never interacted with, so there is no stored row to read. The write-time
check runs before the row exists. Recomputing is part of the design, so the input to the
bucketing must stay stable across rotation forever.

## The resolution: a frozen holdout key

- Add `deriveHoldoutKey(userId)`, defined as **exactly the old unsalted `sha256(userId)`**.
  Any other function, even a better-looking salted one, would re-bucket every historical
  row and silently invalidate the benchmark.
- `computeBenchmarkHoldout` takes that key instead of the pseudonym. The three recompute
  sites already held the raw user id, so no new data reaches any module.
- **State the cost so nobody "fixes" it later.** An unsalted hash of the user id stays in
  the codebase after the privacy migration removes it everywhere else. That is acceptable
  only because the output is a transient bucketing input. It is never written to a column,
  never returned, and never used as an identifier. Only the boolean is persisted. The
  function carries a comment saying exactly this. Without it, a future reader will see drift
  and "correct" it into an HMAC, which re-buckets every user in a way no test would catch.
- **Two tests make the decoupling a guarantee, not a claim.** One checks that the key
  reproduces known v1 values for fixed ids. The other checks that the holdout verdict does
  not change for a user whose pseudonym moved from v1 to v2.
- **Record it as a contract invariant** in the change-contract spec, not only in the plan.

## The general rule

When a value is derived from an identifier and then **recomputed rather than stored**, it
inherits every future change to that identifier. Before you rotate, rehash or re-namespace
an id, list every place that recomputes a hash of it. Separate an identity's two jobs. One
is *matching rows*, which must follow rotation. The other is *bucketing*, which must never
follow it.

## See Also
- [[Write-Time Deterministic Holdout]] — extends (the holdout this protects; recompute-on-read sites are its weak point)
- [[Study-Scoped Pseudonymous Attribution]] — related (a second pseudonym namespace in the same app)
- [[Changing a Derived Default Is a Migration]] — related (changing a function whose output is stored or recomputed is a data change)
- [[Fixing an Accidentally Load-Bearing Bug]] — related (the unsalted hash looked like drift but was holding history together)
