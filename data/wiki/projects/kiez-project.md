---
title: Kiez Project
tags: [langgraph, infra, foundations, project]
summary: A Berlin "what's on tonight" venue map and assistant — open-data pipelines (discover, images, events, enrich, score, kulturdaten, refresh, advance; LangGraph in Python until 2026-10-21, now TypeScript on Vercel Workflows), a Next.js app with a pure replayable ranker, an optional model-parsed assistant, Supabase Postgres, and a spend switch that keeps every model call explicit; most of its design rules are written down before the code.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/kiez/docs/3d-video.md
  - data/raw/claude-docs/kiez/docs/assistant.md
  - data/raw/claude-docs/kiez/docs/deploy.md
  - data/raw/claude-docs/kiez/docs/enrichment.md
  - data/raw/claude-docs/kiez/docs/env.md
  - data/raw/claude-docs/kiez/docs/graphs.md
  - data/raw/claude-docs/kiez/docs/ranking.md
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-itineraries.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-itineraries.md
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-venue-clips-prototype.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-venue-clips-prototype.md
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-venue-photo-catalogue.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-venue-photo-catalogue.md
  - data/raw/repos/kiez/CLAUDE.md
  - data/raw/repos/kiez/README.md
---

# Kiez Project

A personal product: discover Berlin venues from open data, enrich them with checkable
facts, and answer "what's on tonight?" through a feed, a map and an assistant. Several
docs are stamped "written before the code" and are kept current by tests (`make
graphs-doc` regenerates the graph doc and the tests check it is current).

## Pipelines

**Runtime change (2026-10-21):** the pipeline moved from Python/LangGraph to TypeScript
on Vercel Workflows, in `web/pipeline/`. The Python version was moved out of the repo
into an archive. The table below describes the original LangGraph graphs. The current
shape is in *Pipeline after the TypeScript move* further down.


| Graph | Flow | Note |
|---|---|---|
| `discover` | fetch_osm → normalize → dedup → upsert → fetch_facts | new venues start as `candidate`; `--publish` is an explicit, human-run step that makes named, in-scope, unmerged candidates `visible` |
| `images` | select → fetch_imageinfo → licence_filter → write | only CC0 / PD / CC BY / CC BY-SA kept, each with author, credit and licence link beside it; files whose categories suggest people are skipped |
| `events` | select → robots → fetch → follow → extract → upsert → schedule → artists | schema.org Event markup from venues' own sites; follows up to two programme pages; category and genre by **rules**, not a model; robots.txt respected |
| `enrich` | select → per venue (collect → shape → gate → generate → qc) → write | see [[Spend Gate Before the Model Call]] and [[Evidence-Labelled Generation with Deterministic QC]] |
| `refresh` | discover → images → events → [enrich] | each step is another graph run as a subgraph; this one only orders them |
| `assistant` | parse → search_events → respond_events \| respond_venues \| respond_itinerary | see [[Dual Parser with Shared Shape]] |

Status is a separate decision from existence throughout: venues and events land as
`candidate`; showing them is a distinct, auditable step.

### Pipeline after the TypeScript move

- **Plain functions, graph owns order.** Each graph is a set of plain node functions that
  can be tested separately. The graph decides order and branching, never the logic. Zod
  schemas sit at every boundary, and a pipeline logger is used rather than `console`
  outside CLIs. Every run is logged in `pipeline_runs`. On Vercel each node runs as a
  Workflows step capped at **300 s**.
- **New and changed graphs:**
  - `images` gained a `collect_categories` node (the venue's Commons category) and an
    opt-in `classify` node (subject plus a people flag). `classify` is not ported yet and
    fails before writing.
  - `events` is now select → robots → fetch → extract → upsert → artists.
  - `enrich`'s gate branches four ways: `skip`, `rules_only`, `would_send` (dry run) or
    `generate`. Write is versioned via `is_current` and adds an embedding.
  - New `score` graph: open-data relevancy per venue.
  - New `kulturdaten` graph: a CC BY city event calendar, matched to venues by postcode
    plus name.
  - New `advance` graph: crawl what is due, assess readiness, enrich complete venues,
    publish what is ready.
  - `refresh` now runs discover → images → events → kulturdaten → [enrich] → score →
    retention SQL.
- **Spend stays manual.** A weekly cron (Mondays 03:17 UTC) starts `refresh` *without*
  enrichment; `enrich` starts only by hand, from the CLI or an admin route. `enrich --fake`
  runs the whole graph against a fake model at no cost.
- **The schema is the only contract.** `db/` owns the Postgres schema. The pipeline writes
  it and the Next.js app reads it. They share only the DB module and the tag lists, and the
  app's routes start the pipeline's workflows. The landing page is a separate static site
  deployed as a Cloudflare Worker.
- **Seed or pipeline, never both.** A fictional dev seed (25 venues) supports web work
  without a pipeline run. Mixed with real data, the seed outranks it.
- **Gate needs no secrets.** `make gate` runs the table-to-contract check, the evals and
  the web check (tsc, eslint, vitest), with no database and no model key. Eval targets
  get a threshold only from a measured pass rate on real output. A grader whose fixtures
  came from the function it grades does not gate. Today `event_category`, `artist_names`
  and `genre_names` are gated; the rest are UNGATED.
- **Images:** the licence allow-list is unchanged, and the rule is now stated as "no people
  as the subject".

## Design rules that recur

- **Spend is a switch.** Billable calls are refused unless `KIEZ_ALLOW_SPEND=1`; the
  product works with no model (rules parsers, rules-only facet rows, assembled replies).
- **Everything the visitor sees is traceable** — facets to the record they rest on, slates
  to a logged serve with version and inputs ([[Replayable Slate Ranker]]).
- **Versions everywhere**: `TAGS_VERSION`, `PROMPT_VERSION`, `RANKER_VERSION`,
  `SHELVES_VERSION`; a change bumps the version and, for enrichment, re-runs everything
  because the version is part of the input hash.
- **Judgement-chosen constants are labelled as such** (ranking weights, taste boost) and
  paired with the mechanism that will measure them ([[Explore Slice for Position Bias]]).
- **Evals ungated until measured** ([[UNGATED Metric Convention]]); fixture expectations
  come from the spec text, not the code.
- **Docs enforced by the gate**: `make gate` fails if an env var is read and not in the
  env table ([[Gate vs Ship Make Targets]]).

## Events: rules over models

Event status is read from schema.org `eventStatus` or a word in the title (cancelled /
postponed in either language); the word is cut from the stored title so a re-crawl updates
the same row. Artist genres come from a MusicBrainz lookup of act names in the title,
mapped head-last ("indie pop" is pop); namesakes whose genres disagree yield nothing;
lookups cached per name for 180 days with the MBID kept as attribution.

## Deployment gotchas recorded

- Use the Postgres **session pooler** (port 5432) for the pipeline, migrations and the web
  app; the transaction pooler breaks prepared statements and the driver's long queries.
- The hosted free tier pauses a project after a week without traffic; the weekly pipeline
  cron keeps it awake, but the first request after a pause is slow.
- Magic-link sign-in: the default template only works in the browser that requested it
  (PKCE); set the template link to the `token_hash` form so a link opened in a phone's
  mail app also works, with a callback that accepts both.
- The web app needs TCP to Postgres, so it is a Node host rather than a plain edge worker;
  landing page and app are split accordingly, with DNS proxied for one and DNS-only for
  the other so the host's certificate works.

## Derived media and licences (planned)

Façade videos or 3D views generated from several openly licensed photos: the output's
licence is **the most restrictive of its inputs**, share-alike outputs are stored apart,
every source author is credited, identifiable people are blurred or the photo skipped, and
anything not explicitly licensed is excluded regardless of non-commercial intent. The
first experiment is deliberately small (20 venues, the cheapest method) with a stop rule:
"judge by eye whether the result adds anything a still photo doesn't; stop there if it
doesn't."

**Outcome (2026-10):** the clip experiment was built and rejected at that gate (motion
sickness; the real want was interiors and food, which the source photos lacked), and the
follow-up photo catalogue found open sources cover landmark venues only — see
[[A Sourcing Gap Is Not an Effect Problem]]. A planned "evening around an anchor" feature is
designed in [[Itinerary as Anchored Slot Composition]].

## See Also
- [[Spend Gate Before the Model Call]] — extends
- [[Evidence-Labelled Generation with Deterministic QC]] — extends
- [[Replayable Slate Ranker]] — extends
- [[Explore Slice for Position Bias]] — extends
- [[Dual Parser with Shared Shape]] — extends
- [[Assembled, Not Generated Replies]] — extends
- [[UNGATED Metric Convention]] — extends
- [[Gate vs Ship Make Targets]] — extends
- [[Listen-Wiseer Project]] — related (sibling personal project; LangGraph + eval discipline)
- [[Multi-Step Graph Orchestration]] — instance-of (graphs composed as subgraphs under `refresh`)
- [[One Facet Per Fact]] — instance-of (the venue facet split)
- [[Starved Tag Triage: Edge, Prompt, or Supply]] — instance-of
- [[Embedding Side Table, Not Column]] — instance-of
- [[Outcome Signal Ladder]] — instance-of
- [[A Trace Is Not a Number of Record]] — instance-of
- [[Itinerary as Anchored Slot Composition]] — instance-of (planned)
- [[A Sourcing Gap Is Not an Effect Problem]] — instance-of
- [[Silent Join Miss Reads as a Finding]] — instance-of
- [[Idempotency Lives on the Link Column, Not the Synthetic Key]] — instance-of
- [[Quality-Gate Dashboard in Pipeline Order]] — instance-of
