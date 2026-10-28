---
title: Automated Paper Discovery Pipeline
tags: [meta, rag, pattern, conflict]
summary: "A design for feeding new research papers into a curriculum and wiki automatically: fetch arXiv by category, enrich with Semantic Scholar without blocking, score relevance into three bands (auto-include, human queue, archive), dedup on the arXiv ID, and hard-cap daily volume so ~100+ papers/day become ~5 worth reading."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_paper_discovery.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-25-LAE-30-34-learning-depth.md
  - data/raw/repos/learn-ai-engineering/.claude--docs--plans--2026-07-25-LAE-30-34-learning-depth.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--SOURCES.md
  - data/raw/repos/librarian/.claude--skills--learn--SKILL.md
---

# Automated Paper Discovery Pipeline

A research design (not yet built at the time of the source) for keeping the
learn-ai-engineering readings and this wiki current with new papers. Most of the effort
goes into *rejecting* papers. The ML-relevant arXiv categories publish roughly 100–130
papers a day, and the estimate is that only about 7–10 a day map to a curriculum pillar.

## Source APIs

| Source | Gives you | Limits |
|---|---|---|
| **arXiv API** | Category feeds, abstracts, a stable ID; free, no auth | Abstract only; ~30 req/s soft limit with backoff (disputed — the build plan cites 1 request per 3 s for automated access; see `_conflicts.md`) |
| **Semantic Scholar** | One-sentence TLDRs, citation graph, related papers | ~100 req/min on the free tier; ingestion lags arXiv by hours |
| **Papers with Code** | Links from paper to implementation repo | Coverage only for papers with code |
| **arXiv RSS** | Simplest daily feed | Dedup is harder: you parse XML entries instead of keying on IDs |

The recommended combination is the **arXiv category feed as the backbone, with Semantic
Scholar for enrichment**. arXiv is first and complete. Semantic Scholar is richer but late.

## Flow

```
fetch (arXiv, daily cron) → enrich (optional) → classify → gate → ingest → publish
```

Three design rules hold the flow together:

- **Enrichment never blocks.** If Semantic Scholar has not indexed a paper yet, proceed on
  the arXiv data and attach the TLDR later. A pipeline that waits on its slowest optional
  source stalls on exactly the newest papers, which are the ones it exists to catch.
- **Three-band relevance gate.** Score above 0.75: auto-include. 0.5–0.75: queue for a human.
  Below 0.5: archive, but keep the raw record. Start the auto threshold high and lower it
  once the false-accept rate is known. A wrong auto-include adds noise to the curriculum,
  while a wrong queue entry costs only a minute of review.
- **Classify cheaply first.** The MVP scorer is keyword weights over title and abstract,
  mapped to pillars, for example "2+ of prompt/context/harness/eval/agent" for the
  ai-engineering pillar. A model-based classifier is a later phase. Full-pipeline cost was
  estimated at a few dollars a month, and almost all of it is the wiki-synthesis step.

## Dedup

The **arXiv ID is the primary key**, because it is immutable and unique. Fallbacks, in
falling order of reliability: PDF hash, a recent-fetch window (skip anything fetched in the
last 7 days), and title-token similarity when no ID exists. One manifest keyed by ID
records fetch date, score, pillar, and status (pending / approved / archived). Dedup runs
on fetch *and* on ingest, because the same paper can come back through a second feed.
This is the same role the raw-source manifest plays in [[Karpathy LLM Wiki Pattern]].

## Overwhelm is the main risk

The failure the source rates as most likely to kill the pipeline is not a technical one.
It is the reader drowning. The mitigations are deliberately blunt:

- a **hard cap of 5 papers a day**, regardless of how many clear the gate
- bucketing by pillar, so a review session covers one topic
- a **weekly digest** instead of daily notifications, plus a weekly review of the
  auto-included list where wrong picks are archived out of the readings but kept in raw

Manual review was estimated at about 5 minutes per paper (skim abstract and TLDR, then
decide). Reliable auto-acceptance is what brings the daily load down to something
sustainable. Archiving instead of deleting keeps raw append-only, so a threshold change can
be replayed against the history.

## Build-time decisions

The follow-up build plan made the design concrete inside this wiki's own tooling, and
changed several of the research defaults:

- **Integrate, don't stand alone.** The wiki already had a drop zone for web content in
  raw, a URL-ingest path, a manifest for dedup, and a cron runner. Paper discovery became one
  more step in the existing cron, running *before* the session-analysis pass, so papers are
  in raw before analysis starts. The learning repo it serves gets no writes at all.
- **The cron only fetches.** It never compiles. Papers wait in raw until someone runs a named
  skill (`/learn`) that ingests the queue and surfaces the top three items relevant to current
  work. The plan calls this "start conservative": auto-ingest can be added as a flag later if
  the manual step proves too slow. The fetch step is also **off by default** behind an env
  flag.
- **Weekly, not daily.** The window is 7 days to match the existing session-analysis cron.
  That brings the human-review cadence in line with the weekly digest above.
- **Keyword filter after fetch, inside the scraper.** A broad ML category publishes about
  200 papers a week, and without a filter it floods raw and makes ingest expensive. The plan
  starts with a tight keyword list (LLM, language model, RL, alignment, RAG, agentic, RLHF,
  DPO) and widens it only if coverage proves too narrow.
- **The arXiv ID sits next to the hash.** The existing manifest deduplicates by file hash, and
  a re-fetched abstract that is only reformatted would get a new hash. The arXiv ID is
  stored as its own manifest field and used as the primary key.
- **No automated curriculum writes.** A human reads the `/learn` output and decides which
  papers to link from a pillar's reading list, as links, not PDF copies, so the feed cannot
  churn the curriculum structure.
- **Content first, feed second.** The plan scheduled the RL pillar's synthesis notes before
  the feed. Once the notes exist, incoming papers have pages to cross-link to.

## The manual sweep registry it replaces

Before (and alongside) the arXiv feed, non-paper sources were swept by hand from a small
registry file. Its rules are worth keeping for any feed that gets automated later:

- **Admission needs cadence *and* yield.** A source earns a row only if it publishes on a
  schedule and has already produced at least one note. One-off citations belong in a note's
  `sources:`, not the registry.
- **Two tiers.** Tier 1 primaries (first-party engineering writing, original research) are cited
  directly. Tier 2 aggregators are **gap-detectors, not citations of record** — when an aggregator
  post is good, cite the primary source underneath it. An aggregator's value is coverage and cadence.
- **Fact-check aggregator numbers.** One high-volume aggregator's guide had a release date off by
  a day and a star count inflated roughly 2× on verification, while the load-bearing experimental
  figures held. Its only real contribution was pointing at two primary sources worth citing.
- **Log what was skipped.** Each sweep records what landed *and* what was assessed and skipped as
  already covered at equal depth, plus a last-swept date per source, so the next pass does not redo it.
- **Framing mismatches are noted, not adopted.** An aggregator's five-layer stack omitted eval as a
  layer; the registry records that the six-pillar model treats eval as a peer and keeps its own frame.

Extending the paper fetcher to RSS was the stated route to automating these sweeps.

## See Also
- [[Karpathy LLM Wiki Pattern]] — extends (an automated source feed into the raw layer)
- [[Skill-Knowledge Information Flow]] — instance-of (one more inbound channel to the knowledge base)
- [[AI Engineering Curriculum Structure]] — complements (the pillars papers are routed to)
