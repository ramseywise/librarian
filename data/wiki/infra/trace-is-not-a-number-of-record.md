---
title: A Trace Is Not a Number of Record
tags: [infra, observability, decision]
summary: An LLM tracing tool hooked into the AI SDK is debugging evidence, not a ledger — it misses every model-call seam that bypasses the SDK (batch, raw provider APIs), is off wherever keys aren't set (often all of production), and has no first-class error class or retention you control — so per-purpose spend and error numbers need a separate append-only call ledger written best-effort at every seam.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/akira/docs/research/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis144-langfuse-seam.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis144-langfuse-seam.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis144-langfuse-seam.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis144-langfuse-seam.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis144-langfuse-seam.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-qc-eval-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis397-model-call-ledger.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis397-model-call-ledger.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis397-model-call-ledger.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis435-cli-model-default.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis435-cli-model-default.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis435-cli-model-default.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis435-cli-model-default.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis435-cli-model-default.md
---

# A Trace Is Not a Number of Record

In diskoe the team had already wired [[Langfuse Platform]] tracing (via the AI SDK's OTel
spans: purpose as `functionId`, prompt version/hash in trace metadata, model and token
usage from standard gen-ai attributes). An issue then asked for a per-purpose model-call
ledger in Postgres. The research question was whether tracing had made the ledger
redundant. It hadn't, and the reasons generalize.

## What the trace does not cover

| Gap | Why |
|---|---|
| **Seams that bypass the SDK** | The Batch API path and a raw Bedrock Converse client don't go through the AI SDK, so they emit no spans. The scheduled enrichment sweep runs through batch — invisible even with keys set. |
| **Request-path calls** | Tracing was deliberately CLI-only; lazy-starting an OTel SDK inside a web route was rejected. Every future request-path call inherits the gap. |
| **Production** | Off without keys, and no deploy workflow had the keys. Production: zero traces. A caller can skip setting env vars; it can't accidentally skip a DB write. |
| **Error class** | A span records input/output/duration, not `ok` / `error_class` as a queryable field. |
| **Retention and data location** | Whatever the vendor plan gives, with prompt/completion text stored off your infrastructure and outside your data-contract registry. |

On top of the gaps there is a **policy** line: acceptance numbers and spend were kept out
of the tracing tool *by decision*. A trace is for debugging; a number shown on an admin
dashboard must come from a retained, queryable store you own.

## The ledger shape

- **Cluster:** interaction. Deleting a row changes nothing a user sees; it is append-only
  measurement of a decision already made ([[Data Clusters by Writer and Trust]]).
- **Write at every seam, not one function.** Here that was four: `generate()`,
  `generateStructured()`, the Converse client, and the batch submit/collect lifecycle
  (batch latency and tokens are only known at collect time). Writing only in the main
  gateway reproduces the tracing tool's blind spot.
- **Best-effort writes.** The gateway's contract was "does not catch errors"; a ledger
  write must not add a new failure path to a call that propagates cleanly. Swallow and log.
- **One writer module** (a shared insert helper) so the data-contract entry names one file.
- **Readers named before columns** ([[Every Column Names Its Reader]]): an offline report
  feeding the admin dashboard's enrichment tab — never a live query from the route.
- Columns reuse the gateway's existing vocabulary (purpose, provider, model, prompt
  version, tokens, latency, ok, error class). Open question: a per-item correlation column
  — without one the ledger answers "what did enrichment cost today" but not "which venue
  burned it".

## The defect a ledger would have caught on call one

```ts
const model = opts.model ?? creds.model
```

`creds.model` was correctly resolved from the provider flag, but a dev probe always passed
`opts.model = flagValue('model') ?? DEFAULT_ENRICHMENT_MODEL` — an OpenAI model id. Run with
the provider set to Bedrock and no `--model`, every call sent `gpt-4.1-mini` to the Bedrock
endpoint and got HTTP 400. A caller-side default silently outranked the provider-resolved
value. A per-call row with `provider`, `model`, `error_class` makes that visible
immediately; a trace only shows it to someone with keys who happens to look. The fix is
structural: the default belongs in the resolver (`resolveModelId(purpose, env)`), not at
each caller.

## The adoption invariants that came first (akira, 2026-09-21)

The tracing tool had been adopted a week earlier, on a free tier with 30-day retention. The
adoption decision fixed three permanent invariants, and the ledger research above follows
from the third:

1. **Wired at the model seam only.** No provider client exists outside the model module.
   One `initTelemetry()`/`flushTelemetry()` pair lives there, and every model-calling CLI
   awaits the flush in a `finally`.
2. **Never gates.** No gate, test or publish decision depends on the tracer being reachable.
   Missing keys mean tracing is off, logged once, never a failure.
3. **Holds no number of record.** Every rate that justifies a threshold is still written to
   a targets file or a dated doc with N, model and prompt hash. *The tracer is where you
   look; git is where it is recorded.*

Two build findings from the same slice:

- **The vendor's example was not the SDK's contract.** The plan threaded per-call metadata
  (content id, prompt version and hash, run id) through the SDK's telemetry options, based
  on a vendor changelog example. The installed type declarations had no `metadata` field.
  Only `functionId: purpose` shipped. The metadata was deferred as a named follow-up and the
  plan's research section got a dated CORRECTION block, rather than a silent workaround.
  Check vendor-integration shapes against the installed `.d.ts`, not the docs page.
- **`process.exit()` skips the flush.** With the flush chained in `.finally()`, an
  outer-catch `process.exit(1)` terminates before the flush runs, so every failed run lost
  its trace, and a failed run's trace is usually the more valuable one. All outer-catch
  exits became `process.exitCode = 1`.

The same issue moved the LLM-judge rubrics out of the eval tree, which nothing else may
import, so an online QC sweep could use them. A pure move failed the lint import boundary
because the shared base class stayed behind. The base was split instead: the model-calling
half (the rubric contract and verdict schema) moved beside the rubrics, and the eval side
kept a thin adapter that reshapes a verdict into its grader-result type. The acceptance test
was a byte-identical eval summary and gate exit code before and after the move.

## Ledger plan decisions (akira #397 plan, 2026-09-29)

- **One writer, four call sites.** A shared `recordModelCall()` that swallows its own
  errors and logs a warning, called from `generate()`, `generateStructured()`,
  `submitBatch()` and `collectBatch()`. The Bedrock Converse branch had exactly one caller,
  `generate()`, so wrapping that covered it. That was verified by grep, not assumed.
- **Batch gets two row kinds.** Submit writes one row (accepted/rejected, item count, no
  tokens yet), so a batch that is never collected still leaves a trace. Collect writes one
  row per result item, with null latency because the batch API reports none. Both carry the
  provider batch id so a report can join them.
- **No per-item correlation column.** Nothing reads it yet ([[Every Column Names Its Reader]]).
  Add it later with the reader that needs it.
- **Tokens, not dollars.** No pricing table existed anywhere in the tree, so the report shows
  tokens, call counts, error-class mix and p50/p95 latency per purpose per day.
- **Request-path seams are named, not silently skipped.** The embedding call sits on the
  ranked request path, so instrumenting it needs its own latency decision. The plan listed it
  as out of scope and kept `embedding` in the purpose CHECK for later.
- **The never-throws writer is itself the risk.** A ledger that fails forever (wrong table,
  RLS) would never surface, so tests assert that a warning fires on every failure path.
- The caller-default defect found in the research was filed as its own issue (#435) rather
  than folded into the plan. Its fix is written up in [[Caller Default Shadows the Resolver]].

## Operator checklists aren't plans

The other half of the issue (enabling provider invocation logging, a dashboard, a billing
alarm) contained no code. It belonged as a release-checklist line and two env-inventory
rows, not a plan doc.

## See Also
- [[Caller Default Shadows the Resolver]] — extends (the caller-side fix for the defect above)
- [[Langfuse Platform]] — alternative-to
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — extends
- [[Spend Gate Before the Model Call]] — extends
- [[Every Column Names Its Reader]] — prerequisite-for
- [[Silence Reads as Clean]] — extends
- [[One Check Shape for Quality Verdicts]] — extends (trace for debugging, store for the rate)
- [[Observability and Runtime Patterns]] — extends
- [[Kiez Project]] — instance-of
- [[Item Lifecycle Ledger as a New Table]] — extends (a per-item ledger with loud best-effort writes)
