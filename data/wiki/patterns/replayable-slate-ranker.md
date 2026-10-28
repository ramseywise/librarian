---
title: Replayable Slate Ranker
tags: [foundations, pattern]
summary: A ranker built as pure functions — no database, clock or randomness of its own, every input (time, viewport, session history, seed) passed in — so a logged serve can be replayed exactly; signals in [0,1] so weights read as shares, impression fatigue, greedy MMR with a per-kind cap, judgement-chosen starting weights behind a version string, and one serves row written before the response.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/kiez/docs/ranking.md
  - data/raw/claude-docs/kiez/docs/assistant.md
---

# Replayable Slate Ranker

The kiez ranker turns a pool of candidate venues into one short ordered list for every
surface (feed, map list, assistant). Its defining property is that it is a set of **pure
functions**: everything it needs — the time, the viewport, the session's history, a seed
— is passed in, so a logged serve can be replayed. Ties break on venue id; the same input
and seed always give the same slate.

## Pipeline

```
candidates (at most 300)
  -> drop: dismissed in this session
  -> signals: relevance, quality, proximity, timeliness   (each in [0, 1])
  -> base score: weighted sum
  -> fatigue: base x 1 / (1 + unopened impressions / 4)
  -> taste: base x (1 + 0.5 x taste)                      (multiplier, not a weight)
  -> diversity: greedy MMR with a per-kind cap
  -> explore: if flagged, seeded shuffle of the selected set
  -> slate: at most `size` items, each with its score and signals
```

## Design choices worth keeping

- **All signals in [0,1]** so the weights read directly as shares of the score; when a
  signal is unavailable (no query → no relevance) its weight moves to the others rather
  than scoring zero.
- **Quality is recomputable by a reader**: the mean of three plain checks (evidence
  score, has a current summary, has a licensed image), not a learned score.
- **Timeliness** is the larger of *open now* (from opening hours, evaluated in the venue's
  local wall-clock time so the server timezone is irrelevant) and *something on soon*
  (banded by hours until the next visible event).
- **Fatigue, not suppression.** Each impression without an engagement multiplies the
  score by `1/(1+n/4)`; once the session engages, fatigue stops applying. A *dismiss*
  removes the venue outright — showing it again is a bug.
- **Diversity** is greedy maximal marginal relevance (`0.7·score − 0.3·max similarity`,
  similarity = half same-kind, half Jaccard over facet values) plus a **kind cap**: no
  kind fills more than `ceil(size/3)` places while other kinds remain, lifted when only
  one kind is left so a filtered list still fills.
- **Weights are starting values, chosen by judgement, not measured** — stated in the
  doc — to be tuned once explore-slice data exists ([[Explore Slice for Position Bias]]).
  Any weight or rule change bumps `RANKER_VERSION`.
- **Taste** (from venues the visitor saved) multiplies rather than adds, is built per
  request from a browser-held list, and is never stored server side — only its count is
  logged.
- **Bounded lists, no pagination.** Slate sizes are fixed per surface; the feed uses
  bounded shelves with an explicit "show others" so that every card is a logged
  impression.

## Logging is part of the ranker contract

Every slate writes one `serves` row *in the same request, before the response*: session,
surface, the request as received, ranker version, the explore flag, and
`items = [{venue_id, position, score, signals}]` with `position` as shown after any
shuffle. The client then logs impressions and engagements against that serve id. No IP,
account or fingerprint — the session id is a random browser-held value. Because inputs
and version are logged and the functions are pure, any served slate can be regenerated.

## Tests that follow from purity

Bounded size, no duplicate venue, dismissed never appear, the kind cap holds when
alternatives exist and lifts when they do not, same input and seed give the same slate,
and the explore shuffle changes order only when flagged and never changes the set.

## See Also
- [[Explore Slice for Position Bias]] — extends (how the judgement-chosen weights get measured)
- [[Kiez Project]] — instance-of
- [[Track2Vec Playlist Co-Occurrence Embeddings]] — related (a learned signal that could feed such a ranker)
- [[Experiment Tracking Schemas]] — related (version-stamped logging that makes a run reproducible)
- [[RAG Reranking]] — alternative-to (reranking retrieved passages rather than slating items for a feed)
- [[Specificity-Adaptive Ranking and Slate Composition]] — instance-of (the scoring and composition rules such a ranker implements)
- [[Frozen Ranking Baseline from a Pure Ranker]] — extends (purity makes the offline baseline a composition of existing pieces)
- [[Foreign Rows in a Shared Log Table]] — prerequisite-for (a second surface logging into the result-set table)
