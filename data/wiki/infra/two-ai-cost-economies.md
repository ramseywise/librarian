---
title: "Two AI Cost Economies: Durable Once, Contextual On Demand"
tags: [infra, llm, concept]
summary: Separate inference into durable intelligence computed once per catalogue item and contextual intelligence computed only when a request gives a reason — then route each to the cheapest model that clears its quality gate; the biggest lever is usually re-computation churn, not model price.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/akira/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-operating-cost-model.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-scaling-infra-strategy.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-07-aws-credits-bedrock.md
  - data/raw/claude-docs/playground/docs/research/2026-09-07-aws-credits-bedrock.md
---

# Two AI Cost Economies: Durable Once, Contextual On Demand

A cost framing from an events-recommendation product (akira) whose catalogue is enriched
by an LLM and served by a deterministic ranker.

## The two economies

**Durable intelligence** — characteristics of a catalogue item that do not change with the
viewer: vibe, energy, audience fit, price interpretation. Computed once per item at
ingestion, stored, reused on every request. Cost scales with catalogue volume.

**Contextual intelligence** — anything that depends on the person and the moment. Computed
at request time, and only when there is a reason to (an ambiguous intake, a group poll),
never as a default step. Cost scales with traffic.

> Compute durable intelligence once. Compute contextual intelligence when there is a
> reason to. Route each workload to the cheapest model that clears the quality gate.

Keeping the two separate is what makes model choice a replaceable optimisation layer
rather than an architectural commitment: *model choice is replaceable; catalogue
infrastructure is cumulative*. A model gateway keeps the provider swappable — but only
within one API shape. An OpenAI-compatible `baseURL` swap covers proxies and
compatible vendors; a different auth scheme and SDK (e.g. a cloud marketplace endpoint)
is code, not configuration — a contained branch in the gateway, but a branch.

## What the measurements changed

- **Churn beat every model swap.** Catalogue items were re-enriched 3.17× on average
  because a side path wrote a null content hash that the skip-gate treated as "always
  re-enrich". Fixing that cut modelled spend from ~$61 to ~$19/month at 5k items — more
  than any price-tier change on the table. See [[Cached Derivation Without a Recompute Path]].
- **Batch is the second lever, and it is provider-neutral in shape.** Both the first-party
  batch API and the cloud marketplace's batch job are submit-a-file, poll, collect — neither
  fits a synchronous gateway call. Build the async orchestration once and the provider
  becomes a swap.
- **Cash, not cost, can be the objective.** When inference is paid out of pocket and
  credits exist, a credit-funded model that costs more per token still beats a cheaper
  model on a card. At small-model prices the credits outlive their own expiry, so
  *under*-spending is the likelier failure: burn credits on the most capable model the
  quality bar justifies, not the cheapest. But credits pay only for that cloud's own
  services, never third-party SaaS — *credits are an optimisation, not a dependency*.
- **Quality is unmeasured until an instrument exists.** A cheap model that fails a strict
  output vocabulary emits `unclear` for everything and the sanitize chain hides it. The
  only honest comparison is a token-metered eval arm per candidate model; price tables
  without it are speculation.

## See Also
- [[LLM Inference Economics]] — extends (prefill/decode at the token level; this page is the workload level above it)
- [[Scaling Axes and Customer-Triggered Cost Cliffs]] — related (the non-inference lines of the same bill)
- [[Cached Derivation Without a Recompute Path]] — instance-of (the null hash that caused the churn)
- [[Prefix Caching]] — related
- [[Offline Annotation over Online Inference]] — instance-of (enrichment as the durable-once economy)
- [[A Trace Is Not a Number of Record]] — extends (per-purpose call ledger for the spend numbers)
