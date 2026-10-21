---
title: Brand the Funnel's Output
tags: [patterns, prompting, pattern]
summary: "When every caller must route a value through one shaping function before a model call, a union type cannot express 'went through this function'. A nominal brand can: make the shaper the only producer with one cast at its return, and require the brand at the consumer. Prove it with a red-then-green bypass, and name the boundary the brand does not reach."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis318-enrichment-prompt-input-type.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis318-enrichment-prompt-input-type.md
---

# Brand the Funnel's Output

akira's enrichment pipeline had shipped a defect where two callers handed the model
differently shaped input, and 9 of 11 prompt lines read `unknown` (see
[[Input-Starved Enrichment]]). The fix funnelled every caller through one
`shapeEnrichmentInput` function. The follow-up asked how to stop a future caller from
skipping the funnel.

## Why a union fails

The first sketch typed the model-call parameter as a union of the two raw shapes. After the
funnel existed, no caller passed either raw shape. Every caller passed the shaper's output,
a shallow copy with some fields filled or moved. A union written narrowly rejects every
real call. Written loosely, it accepts any object with the right field names, whether or not
it went through shaping. **Structural types cannot express provenance.**

## The brand

```ts
declare const shaped: unique symbol
export type EnrichmentPromptInput = Record<string, unknown> & { readonly [shaped]: true }
```

- **One producer.** The shaper's single `return` gets the only cast in the codebase.
- **Consumers require it.** The model-call boundary (`runEnrichment`, `enrichContent`) takes
  the brand instead of `Record<string, unknown>`.
- **A subtype, not a disjoint type.** Every downstream helper typed
  `Record<string, unknown>` still compiles unchanged when handed a branded value. Only a
  plain record passed into a brand-typed parameter is rejected. That asymmetry is what "sole
  producer" means in the type system.
- **Zero runtime change.** The edits were two signatures, one cast, and two test fixtures,
  which got a local `asPromptInput()` helper.

## Prove it catches the defect class

The execution ran a deliberate bypass. It passed the raw validated handoff at a real call
site and got `TS2345: Argument of type 'NormalizedEnrichmentHandoff' is not assignable to
parameter of type 'EnrichmentPromptInput'`. Then it restored the file from a byte-identical
backup. When the signatures were narrowed, the `tsc` errors were checked by **listing the
distinct files** with errors, not by counting them. Errors in only the two predicted test
files proved no uncited production caller existed.

## Name what the brand does not cover

The prompt-builder module was frozen by a separate issue, so the brand stops at the
model-call boundary. A hand-written call to the prompt builder that skips shaping still
type-checks. The plan recorded this as an **accepted residual gap**, with the instruction
that if a defect ever enters through it, the fix is to revisit that decision. The gap is not
evidence the brand was wrong. A type guarantee with an unstated edge reads as total
coverage.

## See Also
- [[Input-Starved Enrichment]] — extends (the defect class the funnel and brand guard)
- [[Triage Casts by Mechanical Probe]] — extends (the same repo's work on making types state real contracts)
- [[Stated Seams Drift, Enforced Seams Hold]] — instance-of (a seam moved from convention into the compiler)
- [[TypeScript any Escapes]] — extends (a fourth tool beside real type, `unknown`, and generic)
