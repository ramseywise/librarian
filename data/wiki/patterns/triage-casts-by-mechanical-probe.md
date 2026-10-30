---
title: Triage Casts by Mechanical Probe
tags: [patterns, infra, pattern]
summary: "Before triaging a large population of `as unknown as` casts, regenerate the type oracle, then run two whole-tree probes: rewrite every double cast to a single `as`, then to `satisfies`. Sort each site into delete / named zod adapter / keep with a greppable `keeping:` reason. Distrust probe passes that come from an untyped client, where `any` satisfies everything."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis327-supabase-types-contract.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis327-supabase-types-contract.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis327-supabase-types-contract.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis327-supabase-types-contract.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis327-supabase-types-contract.md
---

# Triage Casts by Mechanical Probe

akira had 71 `as unknown as` casts on database results across 43 files. They had accumulated
because nothing regenerated the generated DB types (see [[Stated Seams Drift, Enforced Seams Hold]]).
This issue restored the generated file as the boundary contract and then triaged the casts.
The same order applies to any cast population.

## 1. Fix the oracle first

You cannot judge whether a cast is wrong against the stale types that caused it. So
regenerate first. That regeneration added exactly the three predicted objects, and it
surfaced a **hidden hand-edit**: four RPC parameters carried `| null` in the committed file.
The generator cannot emit that, because a PL/pgSQL parameter has no `NOT NULL` to read. The
committed file had been hand-relaxed. *That is the same disease as a cast, one level up.* It
survives until someone regenerates, and then it reads as drift. The fix was one named type-level
shim, `rpcArgs<Fn, NullableParams>`. It widens only the parameters a caller names and
keeps every other argument checked. Two `@ts-expect-error` tests prove the non-widened ones
still fail.

**The drift check against the live database runs after merge, never in the PR gate.** The
live database runs ahead of `main` whenever a branch has pushed its migration but not merged
it. That is a normal state, so a PR-gate check would go red on unrelated PRs. The drift report
names the **tables** that changed, not a raw diff, and it strips the generated date header so
the date alone never causes a false red.

## 2. Two whole-tree probes (each fully reverted)

| Probe | Result | What it told us |
|---|---|---|
| Rewrite every `as unknown as T` to `as T` | **0 errors** | No cast was bridging genuinely incomparable types. The `unknown` hop was decoration everywhere, so none of the casts was load-bearing in the way the double form suggests |
| Rewrite every `as unknown as T` to `satisfies T` | 123 errors in 28 files | The 17 files with zero errors are the **delete shortlist**, but only a shortlist |

**The caveat that changed the plan:** the publishing and importer sites passed the
`satisfies` probe for the wrong reason. They took an un-parameterised `SupabaseClient`, so
`data` was `any`, and `any` satisfies anything. Deleting those casts would have removed the
cast without adding any checking. The honest fix was typing the client as
`SupabaseClient<Database>`, which surfaces real mismatches. So the delete bucket was smaller
than the probe suggested, and the adapter bucket was larger than the issue estimated.

## 3. Three buckets

- **(a) Delete** when the generated type was already right. Example: `row as unknown as
  Record<string, unknown>` became `{ ...row }`.
- **(b) Adapt** behind a named boundary function. `parseRows` validates against a zod
  schema per read. A weaker `parseSelectedRows` handles reads with a hand-written select
  string: it checks that every selected column comes back as a key, with the key list
  **derived from the select string** so it cannot drift from it. Call-site adapters replaced
  repeated claims about one shape. One shape had been cast separately at five CLI
  entrypoints, and three error handlers each reached into an untyped event with their own
  cast. A narrow schema checks only the fields that decide visibility and passes the display
  half through.
- **(c) Keep**, each with a `keeping:` reason comment, so `grep keeping:` enumerates them.
  Legitimate reasons: TS2589 depth limits, per-table types that do not unify across a union
  table name, and a recursive `Json` alias that no interface is assignable to.

Result: 73 grep hits became 19 real casts, each inside an adapter or carrying a reason.

## Defects the triage surfaced

- A generated type predated the columns its query selected. That explains why only one of
  four sibling reads needed a cast.
- **Test fakes misrepresented the contract.** Fakes returned only their seeded keys, while
  PostgREST returns every selected column (null where empty). Five fixtures relied on this.
  The fixtures were widened rather than the schemas loosened, because loosening would
  destroy the dropped-column detection the adapters exist for. See
  [[Mocked-Away Body Hides the Defect]].
- **eslint, not `tsc`, caught that one cluster's schemas had landed while their call sites
  were never replaced.**

## Related observation (sibling plans)

A hand-maintained row-type mirror that lagged the generated types misled a concurrent
research pass. It concluded that a provenance column did not exist and designed around
adding one. Any mirror of generated types is a second oracle that can be wrong.

## See Also
- [[Stated Seams Drift, Enforced Seams Hold]] — extends (the drift mechanism that produced the casts; this is the cleanup)
- [[TypeScript any Escapes]] — extends (casts are the `any` problem at a DB boundary)
- [[Brand the Funnel's Output]] — extends (a cast used deliberately as the single producer of a nominal type)
- [[Migration Done Means Pushed and Probed]] — extends ("pushed, probed, and the types regenerated")
- [[Mocked-Away Body Hides the Defect]] — extends (fakes that lie about the contract)
- [[Runtime Validation with Zod]] — prerequisite-for (the named zod adapter outcome)
