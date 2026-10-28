---
title: Silent Join Miss Reads as a Finding
tags: [infra, pattern]
summary: "When two sides of a join build their keys separately, a format drift (`osm:node:1` vs `osm:node/1`, `district::null` vs `district::(unknown)`) makes every lookup miss without an error, and the miss branch's fallback then reads as a real result — \"the crawl found nothing\", \"this kind is saturated\" — so build both sides from one exported key function, tighten the key's type to non-null, and make the miss fallback mean \"no evidence\", tested on its own branch."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-28-dis392-s2-s5-remaining.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-28-dis392-s2-s5-remaining.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-28-dis392-s2-s5-remaining.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-28-dis392-s2-s5-remaining.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-28-dis392-s2-s5-remaining.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-28-dis416-venue-priority-wiring.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-28-dis416-venue-priority-wiring.md
---

# Silent Join Miss Reads as a Finding

A string-keyed join that misses does not throw. It returns `undefined`, the caller takes its
fallback branch, and the fallback looks like a real answer. Two plans in one venue-catalogue
repo (akira, 2026-09-28/29) hit this in the same week, and in both cases the wrong output
would have been read as a result about the data rather than a defect in the code.

## Instance 1: two key formats, 100% miss, reads as "nothing found"

A new adapter fed a city-wide OSM discovery report into an existing probe pipeline. The plan
sketched the candidate id as `osm:${type}:${id}`. The site-crawl stage downstream already
keyed its results with a shared `osmKey()` helper that emits `osm:<type>/<id>`. With the
plan's format, every OSM row would have joined to no crawl result. The join's summary would
have reported `not_probed` for 100% of rows, and that reads as "the site crawl found
nothing", not "the keys don't match". The build caught it by reusing `osmKey()` instead of
writing the format again. A later review fix pulled the exclusion key into one pure
`osmPairKey(type, id)` that both the database-row loop and the candidate-side filter call,
with a test asserting a DB-shaped `{osm_type, osm_id}` row and a candidate for the same
element produce the same key.

## Instance 2: null coerced into a composite key

A two-pass priority scorer built a lookup map keyed `${district}::${kind}`. The aggregation
module that filled the map stored a null kind under a module-private `UNKNOWN_KIND` sentinel
(`(unknown)`). The lookup side used template-string coercion, so a null-kind row looked up
`district::null` and silently missed. The fix exported `UNKNOWN_KIND`, used
`kind ?? UNKNOWN_KIND` at the call site, and narrowed the lookup's signature to
`kind: string` so the type system now enforces the invariant.

## Instance 3: the miss fallback meant the opposite of "no data"

The same scorer derived `underservedEdges` per district × kind cell. A kind with candidates
but zero enriched rows had no cell in the enrichment-derived layer, so the code fell back
with `?? [] → 0`. But `0 underserved edges` means "every edge is already well covered", and
that is exactly the condition for the saturation penalty. A dense, never-enriched kind was
being penalised as saturated when the truth was "no evidence at all". The review fix made
the missing cell read as all edges underserved (the full vocabulary size), and added
fixtures for that branch directly and end to end.

## The rule

1. **One key builder, exported, called by both sides.** If the producer's key function is
   module-private, export it. Don't retype a key format in a plan snippet, a test fixture, or
   a second module.
2. **Type the key's parts as non-null.** Normalise null to the shared sentinel before the key
   is built, and make the signature reject `string | null`, so coercion can't happen.
3. **Ask what the miss fallback asserts.** `?? 0`, `?? []` and `?? false` are claims about
   the world. If "absent" and "zero" mean different things to the consumer, the fallback has
   to encode "no evidence" (or be its own state), not the neutral-looking value.
4. **Test the miss branch.** A fixture where the key is present on one side and absent on the
   other, plus one where the key comes from each side's real builder. Tests that construct
   both sides by hand with the same literal can't see format drift.
5. **Report join coverage.** A join stage should print matched / unmatched counts per
   status, so 100% unmatched is visible as an anomaly before anyone interprets it.

## Related: feeding a new population without widening a scoped table

Instance 1's adapter existed because of a scope decision. The only existing "every
candidate" entry point selected from a database table filtered by a shared review-scope
constant (one district, one batch). Inserting the city-wide report into that table would
have silently widened the review surface's denominator, which is the defect that scope
constant exists to prevent. Instead the plan added one adapter that maps a raw report row
into the row shape the population-agnostic downstream stages already consume, and reused
the existing prompt-input builder and join unchanged. Two more details from the same plan:

- **Exclude by live membership, not by the report's baked-in status.** The report carried
  a `dedupe.status` computed when it was generated. Anything imported since was invisible to
  it, so exclusion read current `(osm_type, osm_id)` membership from both tables instead.
- **Re-measure the cost before quoting the research figure.** Research had priced the run
  at about $23 for 10,445 rows on an older prompt. The exclusion join cut the population to
  4,529 inputs, and the dry run on the current prompt came out at about $10 synchronous and
  about $5 via the half-price batch API. The research's "no new code, just budget" verdict
  was right only for the model-call step. The population path still needed the adapter.

## See Also
- [[Size the Chain to Its Join Key]] — extends (measure join-key coverage before building on it; this is the format half)
- [[Silence Reads as Clean]] — instance-of (a missed lookup emits the same output as a real empty result)
- [[Silent Fallthrough in String-Keyed Discovery]] — related (string keys that fail without an error)
- [[The Untested Copy Wins]] — related (a retyped key format is a second copy)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — related (a "no new code" verdict that held for only one stage of the chain)
- [[Kiez Project]] — instance-of
