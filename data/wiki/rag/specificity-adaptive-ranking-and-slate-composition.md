---
title: Specificity-Adaptive Ranking and Slate Composition
tags: [rag, llm, pattern]
summary: Score a candidate pool with weight profiles that shift by how specific the request is (vague → vibe/context carry the weight, specific → time/location/format do), rank deterministically with bounded penalties, then compose a five-slot slate by role — Best Match, Strong Fit, Safe Pick, Adjacent Fit, Discovery Pick — where exploration slots scale down with specificity instead of being a fixed 1-in-5; ranking creates trust, composition creates taste.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/diskoe/docs/notion/scoring.md
  - data/raw/claude-docs/playground/docs/notion/scoring.md
  - data/raw/claude-docs/diskoe/docs/notion/dis-38-ranking-helper.md
  - data/raw/claude-docs/playground/docs/notion/dis-38-ranking-helper.md
  - data/raw/claude-docs/diskoe/docs/notion/dis-46-top5-composition.md
  - data/raw/claude-docs/playground/docs/notion/dis-46-top5-composition.md
  - data/raw/claude-docs/diskoe/docs/notion/top-5-composition-v1-superseded.md
  - data/raw/claude-docs/playground/docs/notion/top-5-composition-v1-superseded.md
  - data/raw/claude-docs/diskoe/docs/notion/taxonomy.md
  - data/raw/claude-docs/playground/docs/notion/taxonomy.md
  - data/raw/claude-docs/akira/docs/research/2026-09-25-dis392-s4-reputation-signal.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-25-dis392-s4-reputation-signal.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-25-dis392-s4-reputation-signal.md
  - data/raw/claude-docs/akira/docs/research/2026-10-09-notion-stable-places-rotation.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-stable-places-rotation.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-stable-places-rotation.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b27-sensitivity-sweeps.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
---

# Specificity-Adaptive Ranking and Slate Composition

A design for turning a structured request (time, place, format, vibe, companions,
budget, accessibility) plus an enriched catalogue into **exactly five** recommendations.
From the diskoe product specs (scoring, ranking helper, top-5 composition, taxonomy),
2026-08/09. The serving path is deliberately deterministic — a `WHERE` clause plus
in-memory scoring over at most ~1,000 rows — because all the model work happened at
enrichment time (see [[Offline Annotation over Online Inference]]).

## Hard filters before scoring

Anything that violates a stated constraint is removed before any score is computed:
date/time window, district, price ceiling, format exclusions, and accessibility. The
accessibility rule is the one worth copying: when `barrier_free_required` is set, an
item whose accessibility is **unknown is not eligible** — unknown is treated as a fail,
not a maybe, because the cost of a wrong "yes" is borne entirely by the user.

## Specificity drives the weight profile

Request specificity is a points model over how many dimensions the user pinned: 0–2
points = low, 3–5 = medium, 6+ = high, with named overrides (a hard time window alone
bumps a request to medium). Each level has its own weight profile, every profile summing
to 1.00:

- as specificity rises, **time-fit, location-fit and format-match gain weight**;
- as specificity falls, **vibe-match and context-fit (companions, mood, occasion) gain
  weight**, because a vague request is a request for taste, not for constraint
  satisfaction.

A single global weight vector gets one of the two regimes wrong.

## Ranking: bounded additive adjustments, deterministic ties

```
final_score = clamp(base
                    + discovery_boost      (≤ +0.05)
                    − friction_penalty     (up to −0.10; booking, travel, queue)
                    − uncertainty_penalty  (up to −0.08; sparse or flagged enrichment)
                    − constraint_edge      (up to −0.07; near a hard boundary, e.g. ends 20 min after the window)
                    , 0, 1)
```

Rules that fell out of writing this down:

- **Bounded adjustments.** Each penalty has a ceiling, so no single secondary signal can
  invert the primary ordering.
- **Deterministic tie-break** — `quality_trust_score` → `time_fit` → earlier start →
  `event_id`. The same request and pool must always yield the same ranking, which is
  what makes serves replayable (see [[Replayable Slate Ranker]]).
- **Signals that must not touch the score.** `diversity_potential_signal` is computed for
  composition and is explicitly forbidden from entering `final_score`. Mixing a
  set-level property into an item-level score is how "diversity" quietly becomes "worse
  top result".
- **`quality_trust_score` must not over-reward polished institutions.** A well-run venue
  with a complete listing is not thereby a better fit; trust is a tie-breaker and a
  mild prior, not a ranking axis.
- **Information completeness ≠ content quality.** A sparse listing lowers certainty (the
  uncertainty penalty), never fit. The same rule governs enrichment (see
  [[Graded-Uncertainty Enrichment Contract]]).

## Composition: roles, not ranks

> Ranking creates trust. Composition creates taste.

The top five by score is not the slate. Each slot has a **role** with a threshold:
Best Match, Strong Fit, Safe Pick, Adjacent Fit, Discovery Pick (and a Backup list).
Thresholds scale with specificity — a high-specificity request demands a higher
`Safe Pick` floor. Replacement rules keep taste from eating trust:

- A lower-ranked item may **replace** a higher-ranked one only within a score gap that
  shrinks with specificity (0.12 / 0.08 / 0.04 for low / medium / high); **never replace
  for diversity alone**.
- **Repetition limits** are hard for venue (never two slots at one venue) and soft for
  organizer/format.
- **Progressive pool expansion** (L1–L5: widen time, widen district, relax soft
  preferences…) runs when a role cannot be filled; "return fewer than five" is the
  explicit last resort, and expansion must *score without blocking* — expanded
  candidates compete on the same score, they are not auto-admitted.

### Why v1's fixed exploration slot was superseded

The first composition spec reserved an unconditional 1-in-5 "exploration" slot. The
revision made exploration **conditional on specificity**: low → one Adjacent plus one
Niche pick; medium → one Adjacent and zero-or-one Niche; high → at most one Adjacent *or*
Niche, and only within the hard constraints (never break date/time, type, price,
district, barrier-free). Reinstating a flat exploration slot would be a regression: it
spends a precious slot on a user who has just told you exactly what they want.

## Taxonomy separation that makes this scorable

The scorer only works because the taxonomy keeps axes apart: `format` (what it is) vs
`category` (what it is about) vs `vibe` (how it feels) vs `context` (who/when it suits)
vs `plan_role` (where it fits in an evening) vs `audience`; and `decision_signals`
(machine-read) vs display copy (human-read). "A tag should earn its place" — every tag
has to be read by a filter, a weight, or a slot rule, or it is deleted (the same
discipline as [[Every Column Names Its Reader]]).

## Reputation demotion: an operator flag, not a model axis

The "tourist-trap" case (a highly ranked venue locals avoid) was fixed in research on
the akira repo (2026-09-25) with the **smallest mechanism**: an **operator-set per-venue
reputation flag**, consumed by a small capped penalty in the existing capped-modifier
slot (the shape of `subtype_fit_penalty`, 0.06 cap). A null flag falls back to source
values, and the penalty is reason-tagged so it shows in the ranking explanation. The
whole modifier stack stays bounded (+0.05 / −0.31). Two findings shaped it:

- **Correct axis, wrong polarity.** `audience_fit` already distinguished `locals` from
  `visitors`, but `visitors` was only ever used as a bonus. The demotion signal was
  already there, wired one way.
- Automating reputation from review sites would be a new ingestion source, and it was
  blocked on the unbuilt legal-posture review. It wasn't needed to fix the case.

The sampling lane later mirrored the same flag (see
[[Relevance Is the Score, Enrichability Is the Gate]]).

As built (2026-09-25):

- The penalty cap of 0.08 is labelled a guess in code, to be revisited once measured.
- There is no waiver path. The emergency lever is `CAPS.reputation_penalty = 0`.
- The flag's audit columns were moved off the public venue table to an admin-only table
  (see [[RLS Gates Rows, Not Columns]]).
- The ranker version was bumped so logged results before and after stay distinguishable.

## Controlled rotation for evergreen inventory

Events rotate naturally because they expire, but stable places (restaurants, bars) don't.
A returning user with the same context would otherwise see the same five every time. The
product spec (May 2026) called the answer **controlled rotation: relevance first, but
avoid repetition**:

1. Apply hard constraints (district, dietary, open now, budget). They stay hard.
2. Score every match.
3. Build a qualified pool: the top 20, or everything above a minimum relevance
   (placeholder 70/100).
4. Apply history penalties and novelty boosts **only inside that pool**.
5. Select the final five.

Never shuffle: a new place may rise only if it still fits. Penalties are graded: shown
this session (small), opened but not acted on (stronger), shown 3+ times without a save
(stronger), dismissed (downrank). Previously saved places don't return as "new" unless
the context strongly fits. Logged-out users get session-storage rotation, and logged-in
users get a 7-day history. The penalty values were placeholders to be tuned from
analytics.

## See Also
- [[RAG Reranking]] — alternative-to (a learned reranker over passages vs. a deterministic rubric over catalogue rows)
- [[RAG Retrieval Strategies]] — related (hard filters as the retrieval stage of a two-stage pipeline)
- [[Replayable Slate Ranker]] — extends (the implementation shape that keeps this ranking replayable)
- [[Explore Slice for Position Bias]] — related (how exploration slots get their counterfactual)
- [[Offline Annotation over Online Inference]] — prerequisite-for
- [[Graded-Uncertainty Enrichment Contract]] — prerequisite-for (where the uncertainty penalty's inputs come from)
- [[Validated Concept vs Unmeasured System]] — related (the rubric was validated by hand before any of this was implemented)
- [[Relevance Is the Score, Enrichability Is the Gate]] — related (pre-enrichment sampling score that mirrors the reputation flag)
- [[No Evidence Ranks Below Confident Mismatch]] — extends (sparse evidence must not be penalised twice)
- [[Intake Option Separability via Reach Vectors]] — related (how distinct the intake requests really are)
- [[Constraint Tiers and Two-Phase Relaxation]] — prerequisite-for (how inputs are classified before scoring, and what relaxes when results run thin)
- [[Anchor-and-Guardrail Similar Items]] — related (the "more like this" layer beside the slate)
- [[Capped Tiered Tag Assignment]] — related (keeps the vibe tags this scorer reads sparse)
- [[Ranker Weight Sensitivity Sweep]] — extends (measures how load-bearing each profile weight is)
- [[Adversarially Independent Baseline Arm]] — alternative-to (the equal-weight floor the profiles must beat)
- [[RLS Gates Rows, Not Columns]] — related (where the flag audit trail had to move)
- [[Required Field as Exhaustive Site Finder]] — related (how the penalty reached every modifier literal)
