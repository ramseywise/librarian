---
title: Anchor-and-Guardrail Similar Items
tags: [rag, llm, pattern]
summary: A "more like this" layer where the opened item anchors similarity and the user's original search context guards against drift; it excludes the slate already seen, sorts by a combined related score rather than raw similarity, prefers one or two strong matches to three weak ones, hides itself when nothing qualifies, and returns reason codes for why it showed or didn't.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
---

# Anchor-and-Guardrail Similar Items

From the "similar events" spec of a discovery product whose main result is a fixed
five-item slate (repo diskoe, mirrored 2026-10-09 from a June 2026 product spec). The
principle: **the slate helps users decide; the similar-items layer helps them explore
nearby in taste, not necessarily nearby in location.**

## Two inputs with two jobs

- **The opened item is the anchor.** It defines what "similar" means.
- **The original search context is the guardrail.** A Friday-night, high-energy,
  with-friends search should not drift into Sunday-afternoon items merely because they
  share a category or organizer.

Without a search context (direct entry), the layer still works on anchor similarity
alone, but with a **stricter threshold** (0.70 vs 0.60), the relaxed fallback disabled,
and the section hidden unless matches are clearly relevant. Losing a guardrail should
raise the bar, not remove it.

## Rules that kept it honest

- **Exclude what the user already saw.** When a source slate exists, every item in it is
  excluded, so the detail page never repeats the decision set.
- **Vibe and context outrank format.** Priority: vibe, context fit, category, format, time
  window, price band, venue/organizer, quality. An experimental concert can be similar to
  an ambient listening session. Adjacent-vibe matches never outrank direct matches through
  adjacency alone.
- **Physical proximity is not similarity.** Location is at most a weak supporting
  signal, and "nearby alternatives" was deliberately rejected as a relationship type.
- **Sort by the related score, not raw similarity.** `final ≈ similarity × guardrail
  support × quality − friction/uncertainty`. A highly similar item can still be a poor
  recommendation.
- **Fewer is better than weak.** Up to 3; show 1–2 if that's all that qualifies; hide
  the section (no empty state) if none do. Never fill with generic items.
- **Light anti-duplication.** No more than two results sharing a venue, organizer or
  format unless the pool is sparse. Similarity still beats diversity here, unlike the
  main slate.
- **Hybrid candidate source.** Start from the main ranker's candidate list. Expand to the
  wider eligible pool only as a fallback, still under the guardrail.

## Explain the absence too

The layer returns runtime flags for why it did or didn't show (`returned_less_than_3`,
`fallback_expansion_used`, `hidden_due_to_low_quality`, `no_search_context_mode`,
`top5_exclusion_applied`), and per-result `relationship_type`, matched and weaker
dimensions, and reason codes. A hidden section with no reason is indistinguishable from
a bug.

## See Also
- [[Specificity-Adaptive Ranking and Slate Composition]] — extends (the main slate this layer sits beside; same controlled-rotation idea)
- [[Constraint Tiers and Two-Phase Relaxation]] — related (the search context it uses as a guardrail)
- [[RAG Reranking]] — alternative-to (learned relatedness vs. a transparent rule score)
