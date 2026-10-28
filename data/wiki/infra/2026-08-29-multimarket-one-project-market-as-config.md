---
title: Multimarket — One Project, Market as Config
tags: [infra, decision]
summary: For a single-city product that may expand, the decision was one database with market as a config value (and a `market_id` column only when a second market exists) over one project per market — because N migration chains multiply the exact failure the repo had already shipped twice (unapplied migrations), and A is the code shape that B's deployment topology still permits later.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/research/2026-08-29-multimarket-platform.md
  - data/raw/claude-docs/akira/docs/research/2026-08-29-multimarket-platform.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-08-29-multimarket-platform.md
  - data/raw/claude-docs/diskoe/docs/research/2026-08-29-multimarket-platform.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b73-market-config.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b73-market-config.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b73-market-config.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b73-market-config.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b73-market-config.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b73-market-config.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b73-market-config.md
---

# Multimarket — One Project, Market as Config

**Decision (2026-08-29, repo akira):** land market as a configuration value now; defer
the `market_id` column until a second market exists; one Supabase project; a project per
market only if a partner contract requires data residency.

## Options

| Option | Isolation | Cost |
|---|---|---|
| A. `market_id` column, one project | logical — RLS adds a predicate | one migration chain, one drift check; every query gains a predicate, every index a leading column |
| B. one project per market | physical — residency, blast radius | *N* chains that must not diverge; drift check runs *N* times; cross-market features need a federation layer that does not exist |
| C. one project, one schema per market | middle | tooling assumes `public`; types and RLS regenerate per schema — most friction, least benefit |

## Why A

Not scale. **B multiplies the exact failure this repo already has** — a migration marked
done and never applied, twice. A and B are not exclusive: A is the code shape, B is a
deployment topology it permits later by pointing the database URL at a different project
per deployment, *if* market is already a config value rather than a literal.

## Rules that came with it

- **Config that should be data, source-keyed extractors — never per-market folders.** A
  `markets/<x>.ts` carries language, timezone, vocabulary hooks; extractors are keyed by
  source, not by city. Per-market folders are duplication that drifts, which is the
  repo's known failure shape (a publish gate vendored in two places, fixed once).
- **Service seams are database clusters, not function calls.** Ingest never imports
  enrichment; the app never imports core; enrichment never publishes (its lifecycle write
  is guarded to `draft`/`needs_review`). Each of the three future services is already a
  cluster boundary, which is what makes a later split cheap.
- **Shared gates become a package before any repo split.** Visibility rules read by two
  services must live in one package or each vendors its copy. "Do not skip to repos."
- **No `licensed_feed` source type until something reads it** — the
  [[Every Column Names Its Reader]] rule applied to enums.

## Landing the config (B-73, 2026-08)

The plan that turned the decision into code added rules of its own:

- **Plain module import, not a context provider.** Every UI site reads a market value
  that is fixed per deployment. A React context provider is for values that vary per
  request (multi-tenant in one deployment) — that is the named trigger to introduce one.
- **Re-export the vocabulary, never copy it.** `market.vocab.event` *is* the existing
  allowed-values constant (same object), so there is still one source of truth.
- **Default parameters keep call-site signatures.** Functions gain a market argument
  defaulting to the current market, so the move touches no callers.
- **Byte-identical behaviour for the existing market is the revert signal.** Any diff in
  the existing market's output means the move changed logic.
- **Extract what one instance can teach; defer what needs a second.** The `Market` shape
  and how the call sites reach it are knowable from one city. A date-parsing locale table
  and real default-source values are not — they are named as deferred (with
  `defaultSources: []` as an explicit placeholder), not designed against no data.
- **The trigger gates execution, not plan content.** The plan was written and reviewed
  while execution waited for the first real second-market conversation.
- **Recount inherited scope numbers.** The issue said "18 timezone sites"; the recount
  found 19 in 13 files, and every example path in the issue was stale.

## See Also
- [[Split Service Deployment]] — alternative-to (the topology this decision defers)
- [[Migration Done Means Pushed and Probed]] — depends-on (the failure B would multiply)
- [[Every Column Names Its Reader]] — related
- [[Production Hardening Patterns]] — related
- [[Named-Trigger Deferral]] — instance-of (execution gated on a real second market)
