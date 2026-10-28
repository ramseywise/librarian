---
title: Relevance Is the Score, Enrichability Is the Gate
tags: [patterns, eval, pattern]
summary: A sampling or priority score that blends "can we enrich this from its website" with "does this item matter" ranks prose-rich chains above cultural staples; split the axes so relevance is the score and enrichability only gates (a gated item holds at full score), and source prominence from cross-source agreement rather than from the column you happen to have.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-28-enrichment-sampling-relevancy-phases.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-28-enrichment-sampling-relevancy-phases.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-28-enrichment-sampling-relevancy-phases.md
---

# Relevance Is the Score, Enrichability Is the Gate

From designing a pre-enrichment sampling score that chose which venues to spend
enrichment budget on in an events-discovery product (repo akira, 2026-09-28). The score
went through three versions in one day of operator review.

## The defect: one score, two questions

The existing review-priority score carried no within-kind information: 271 rows tied at
one value, so every restaurant ranked the same. The first relevancy score fixed the ties
but **measured enrichability, not cultural relevance**. The operator's spot-check showed
local institutions (a queer landmark bar, an electro bar, neighbourhood staples) ranked
mid-to-hold, while a restaurant chain topped its district at 99.9. Two causes:

1. **The evidence component rewarded website prose**, and cultural standing is
   uncorrelated with prose volume. The landmark bar had the right tags and a dated
   calendar in 312 characters of site text, but a thin-text gate capped it at 49. The
   electro bar's site was a JS shell (0 characters). The chain won on 15k characters of
   marketing copy.
2. **The corroboration component was the right idea pointed at an empty column.** Only
   305 of 5,633 provenance rows had any encyclopedia/wiki door, mostly museums, and none
   of the staple bars did. The signal meant to encode "local staple" did not exist for the
   very class it mattered most for.

## The fix: split the axes

**Relevance is the score; enrichability is only the gate.** A gated row keeps its full
relevance score and sits at `hold-for-secondary-sources` until it can be enriched. The
landmark bar moved from a capped 49 to 97.6 (hold, thin text). A gated staple should
read "hold", not "rank 8".

v2 components (≈100 raw, then percentile-calibrated): evidence (halved, so prose stopped
deciding), offer, intake reach (how many intake moods reach the row, the pre-enrichment
mirror of a post-enrichment feed metric), kind prior, staple/local signals, and taste.

## Signals that were computable now vs not

- **Chains are computable from the pool**: 106 of 4,529 names appeared at 2+ addresses.
  A multi-location penalty (×2 −4, ×3–4 −9, ≥5 −14) plus a brand regex for one-location
  tourist brands catches most of the cliché tier with no new data.
- **The demotion lever already existed.** An operator-set per-venue reputation flag
  demotes ranked output. The sampling lane mirrors it post-calibration (−30 percentile
  points) instead of inventing a second mechanism.
- **"Touristy" was unobservable**: no `tourists` audience value existed, and tourist
  keywords appeared in 5 rows. A demotion list holding only the operator's examples is
  not logic, which the operator called out.
- **"Best of N Italians" is not derivable from any column.** Cuisine values were raw map
  strings, and there was deliberately no scraped-rating signal.

## Local endorsement as cross-source agreement (v2.1)

The positive complement: search agents collected 615 best-of mentions (563 venues,
~40 domains) from curated city guides via web search only. Guides whose terms prohibit
automated access were excluded outright, even ones the operator liked (a legality-first
sweep, see [[Change the Channel, Not the Count]]). At most ~10 names per source page
were kept as facts (names, districts, categories, no prose), with per-mention
provenance, so the signal is **cross-source agreement, never one guide's database**.
179 matched into the pool and 27 had ≥2 independent sources. Endorsement adds up to +10
(1 source +5, 2 +8, ≥3 +10). The landmark kind prior rose from 2 to 7. The 379
unmatched names became an intake-gap list. Caveat: guides favour food over clubs, so a
low endorsement is not evidence against a music venue.

## Calibration against the operator's own labels is not validation

44 of 53 ungated operator accepts landed in the top phase. But taste (matches against
those same accepts) is a +20 component, so the agreement is **partly by construction**.
It is a reference read, never a gateable metric. The independent check is the
post-enrichment feed metrics after the first wave. The weights were designed, not
measured. Never gate them against fixtures they were tuned on (see
[[UNGATED Metric Convention]]). Percentile calibration is pool-relative, so each round
restates its pool and date.

The first wave was sized at 190 rows ≈ $0.57 across five districts, with a kind cap, and
held for operator go-ahead (see [[Spend Gate Before the Model Call]]).

## See Also
- [[Specificity-Adaptive Ranking and Slate Composition]] — related (the serve-time ranker whose reputation flag the sampling lane mirrors)
- [[UNGATED Metric Convention]] — instance-of (calibration against labels the score was built from)
- [[Offline Annotation over Online Inference]] — complements (deciding which rows get the offline annotation)
- [[Validated Concept vs Unmeasured System]] — related (designed weights vs measured ones)
- [[Kiez Project]] — instance-of
- [[Count What the Merge Already Folded]] — prerequisite-for (how the empty corroboration column was later filled)
