---
title: Model Gateway Is Transport, Call Site Owns Meaning
tags: [llm, infra, pattern]
summary: One lint-enforced module is the only importer of provider SDKs, but it stays pure transport — two typed exports, no error wrapping, no spend ledger — because error classification, budget stops and model choice belong to the call site, and the defects a gateway review finds are all places where the call site's meaning was dropped on the way through.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b70-model-gateway.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/akira/docs/reviews/2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/playground/docs/reviews/2026-08-29-b70-model-gateway.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-08-29-b70-model-gateway.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-08-29-b70-model-gateway.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b70-model-gateway.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b70-model-gateway.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b70-model-gateway.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-g3-spend-cap.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-g3-spend-cap.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-g3-spend-cap.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-07-dis202-batch-enrichment.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis214-bedrock-nova-lite.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis214-bedrock-nova-lite.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis214-bedrock-nova-lite.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis214-bedrock-nova-lite.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis214-bedrock-nova-lite.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis214-bedrock-nova-lite.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis214-bedrock-nova-lite.md
---

# Model Gateway Is Transport, Call Site Owns Meaning

A single provider seam for every model call (repo akira, 2026-08). The seam itself is
the easy part; the design question is what the gateway must **not** absorb.

## The shape

- **One importer, lint-enforced.** A `no-restricted-imports` rule bans the provider SDK
  everywhere, with an override scoped to `src/model/**`. A stated "one model seam" is
  bypassed within weeks; an enforced one holds ([[Stated Seams Drift, Enforced Seams Hold]]).
- **Two typed exports, not an overload or a provider handle:** `generate` (text) and
  `generateStructured<T>` (returns `T | null`). Handing callers a provider client would
  reopen the seam; an overloaded signature hides which contract a caller is on.
- **An injection parameter (`_env`) for tests**, so tests do not need module mocks of the
  provider.
- **A back-edge is allowed only while it is named.** The gateway briefly read model bounds
  from `agents/` (a reverse arrow); the plan recorded it as a known asymmetry and a later
  restructure closed it.

## What stays out of the gateway

| Concern | Why it is not the gateway's |
|---|---|
| **Error wrapping** | Call sites classify `TimeoutError` / `AbortError` into their own per-item failure vocabulary. A gateway that catches and re-wraps erases the identity they branch on. The contract is "does not catch errors". |
| **Spend ledger** | A spend ceiling is a run-orchestration concern — checked before a call, recorded after. A ledger parameter on `generate()` would make transport decide meaning. See [[Spend Gate Before the Model Call]]. |
| **Budget stop semantics** | A later spend-cap issue proposed moving the guard into the gateway and was rejected: the runners already consult `ledger.exhausted` per item, and a spend stop must be a normal, explicable per-item outcome, not an exception unwinding a half-finished batch ([[A Capped Run Is Not a Clean Run]]). |

## Defect classes a gateway review finds

All five share one shape: meaning resolved at the call site that the production path
silently discards.

1. **Caller override dropped on the production path.** `options.model` was resolved,
   passed to the injected test seam, and stamped into the parse context — but the real
   `generate()` call omitted it. Tests using the seam passed; production ignored every
   model experiment. Forward the raw caller value, not a pre-resolved local, so the
   gateway's env resolution still applies when the caller passes nothing.
2. **Persisted provenance from a local, not from the result.** The recorded model name
   came from a locally pre-computed value instead of `result.model`. They agreed only
   because both read the same env var — coincidence, not construction. Record what the
   gateway reports it called.
3. **Duplicated default constants.** The same default model id lived in four places;
   the next bump edits one and config drifts silently. One home in `model/`, everyone
   imports ([[The Untested Copy Wins]]).
4. **Comments that claim an import that does not exist** — documentation of wiring that
   was never done.
5. **Types looser than behaviour.** `usage` typed optional but always returned pushes
   null checks onto every caller for nothing.

## A second seam, recorded as an exception

Batch enrichment needed a provider batch API the gateway's two exports do not cover. Rather
than widen the gateway, a separate `batchGateway` module became the **only other** importer of
the raw provider SDK, and the lint override and plan recorded it as a named exception. A
second seam is acceptable when it is enumerated; an unlisted one is the start of drift. See
[[Batch Path Through the Synchronous Chain]] for how the batch output re-enters the
synchronous runner.

## Adding a second provider: adapter vs. proxy (superseded)

A later plan weighed adding a second cloud provider behind the gateway:

- **Native adapter over a translation proxy.** A proxy promises "any provider behind one
  OpenAI-shaped API", but batch jobs need bespoke per-provider work either way, so the proxy's
  main appeal was moot and it would add a deployed service to operate.
- **Credentials as a discriminated union.** `resolveCredentials` returned a union per
  provider, so a client builder that met a provider it could not serve (e.g. batch on the new
  provider) had to refuse explicitly — the compiler forces the branch instead of a silent
  fallback to the default provider.
- **Built inert against mocks, then superseded.** The adapter was merged unused, tested only
  against mocked clients. A later check falsified the premise the plan rested on, and the plan
  was marked SUPERSEDED. Merging inert code against mocks defers exactly the verification that
  would have killed it ([[A Fake That Conforms to a Broken Seam]]).

## See Also
- [[Stated Seams Drift, Enforced Seams Hold]] — instance-of (the enforced model seam)
- [[Spend Gate Before the Model Call]] — related (where the budget check lives instead)
- [[A Capped Run Is Not a Clean Run]] — related (the spend-cap decision that kept the guard out)
- [[A Trace Is Not a Number of Record]] — related (a ledger written best-effort at every seam without breaking "does not catch errors")
- [[A Fake That Conforms to a Broken Seam]] — related (test seams that pass while production drops the argument)
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — related (why provider swappability is worth a seam)
- [[Batch Path Through the Synchronous Chain]] — related (the batch seam and how its output rejoins the runner)
- [[Caller Default Shadows the Resolver]] — related (a caller-side default that defeats the gateway's provider resolution)
