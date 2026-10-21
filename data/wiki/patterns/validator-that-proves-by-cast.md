---
title: Validator That Proves by Cast
tags: [patterns, infra, pattern]
summary: A hand-written validator that returns its input "as T" after checking less than T claims gives a type that implies validation which never happened — measure failure counts report-only, then move request bodies to schema parsing, and benchmark before parsing database rows; a cast on a typed query result can even discard a column error the compiler had already found, so the fix there is deleting the cast.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis185-saved-read-path.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis185-saved-read-path.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis185-saved-read-path.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis185-saved-read-path.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis185-saved-read-path.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis185-saved-read-path.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis185-saved-read-path.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis304-runtime-boundary-parsing.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis304-runtime-boundary-parsing-continuation.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis304-runtime-boundary-parsing-continuation.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis304-runtime-boundary-parsing-continuation.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis304-runtime-boundary-parsing-continuation.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis304-runtime-boundary-parsing-continuation.md
---

# Validator That Proves by Cast

From an audit of akira's runtime boundaries (crawler output, API request bodies, database
rows into the feed).

## The shape

- The crawler validator checked a few fields, then returned the input `as T`. It accepted
  `NaN` numbers and non-ISO date strings, and kept unknown properties. Downstream code
  trusted `T` fully.
- An API route cast `req.json()` straight to its body type.
- The feed cast database rows to its domain type.

In all three, the type name (`ValidatedEvent`, a typed body) implied a check that did not
exist. A cast is a claim, not a proof; the compiler cannot distinguish them.

## Rollout that does not break production

1. **Report-only audit.** Run a real schema parse beside the existing path and count
   failures per field without rejecting anything. This gives the blast radius before any
   behaviour change.
2. **Schema `safeParse` on request bodies** — the cheapest, highest-risk boundary.
3. **Benchmark p95 before parsing DB rows.** Row parsing runs on every feed read; measure
   cost before turning it on.

## The Cast That Discards an Error the Compiler Already Found

A saved-items page was empty for every user. Its query embedded two enrichment columns
that did not exist. They were **view-model names** (one a rename of a real column, one
derived from two others in a route handler). The read path had reached for presentation
vocabulary and queried it as schema, so the database rejected every call. Four
independent silences kept it hidden:

1. The page destructured `{ saves }` from a `{ saves, error }` return and **discarded the
   error**.
2. An `as { data: Row[] | null; error: … }` cast replaced whatever type the query had
   inferred.
3. The unit-test fixtures **mocked the same wrong column names**, so the suite stayed
   green against a query that failed in production.
4. The end-to-end test for this journey was unconditionally skipped, with a comment that
   named this exact bug.

The finding that changed the fix: the typed query builder **had already detected the bad
column statically**. It encoded the problem as a phantom
`SelectQueryError<"column 'x' does not exist">` type. The cast was the only thing throwing
that away. Three throwaway probes confirmed it:

- (A) the current query's inferred type carried the error;
- (B) the corrected query, with no cast, assigned cleanly to a hand-written row interface;
- (C) reintroducing one wrong column name failed `tsc`.

The recurrence guard was therefore **deleting the cast**, not narrowing it. The existing
type-check gate became the guard, with no new tooling. `.returns<T>()` was rejected as an
alternative because it is exactly as unchecked as the cast and does not re-derive from the
schema.

Other parts of the fix:

- **One home for the derivation.** The tag derivation that the route already did inline
  was extracted to one shared helper, so the two callers cannot diverge again.
- **An honest error state.** The page now says *"This is a loading problem, not an empty
  list — your saves are still there"* instead of a generic error or an empty list.
- **Corrected fixtures.**
- **Red before green.** The skipped end-to-end test was unskipped and shown **red before
  the fix and green after**. If the fix is ever rolled back, the test is re-skipped with a
  comment so the tree never carries a deterministically red test.

## What the Build Found

The plan that followed the research moved the boundaries to Zod schemas. The build turned up these points:

- **CPU was never the blocker.** Parsing 1,000 feed rows took 3.27 ms at p95.
- **Test doubles were the blocker.** Many tests passed minimal objects such as `{id: 'e1'}`
  as rows. A hard parse at the database-row boundary would have rejected them, so that
  boundary's parse became **diagnostic-only**: it warns and never throws or filters.
- **Tie schemas to the existing types** with `satisfies z.ZodType<T>`, so the schema and the
  hand-written type cannot drift apart silently. Stripping unknown top-level keys was
  checked to leave content hashes unchanged.
- **Each boundary needs its own failure policy.** A single global policy does not fit:
  - Feed rows are quarantined one at a time. A bad row is dropped, not the whole feed.
  - Malformed enrichment is left out, and the item falls back to its thin form.
  - The admin labeling corpus rejects the **whole file** and names the line and fields. A
    partially loaded corpus would bias the judgments made from it.
  - An unknown `mode` query parameter used to be coerced silently. It now returns 400 and is
    validated before a database client is created.
  - CLI flags parsed with `Number()` accepted NaN, Infinity, 0 and negative values. They now
    go through one shared helper.
  - Model output uses an object-only passthrough schema. The old `typeof x === 'object'`
    check let arrays through, because `typeof []` is `'object'`.
- **`.nullable()` rejects an absent key.** It accepts `null` but not a missing key. That
  strictness exposed fixtures that had been leaving fields out.

## See Also
- [[Hide-Unknown Display Contract]] — related (presentation vocabulary belongs in a resolver, not in the query)
- [[Sanitize Never Fails, Validate Never Mutates]] — extends (a validator must reject, never silently pass through)
- [[Shadow Signal Before Gate Change]] — related (report-only first, then enforce)
- [[Fail-Closed E2E Journey Proof]] — related (the same saved-items read path, proven end to end)
