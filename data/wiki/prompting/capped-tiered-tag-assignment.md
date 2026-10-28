---
title: Capped Tiered Tag Assignment
tags: [prompting, eval, pattern]
summary: An annotation rule for multi-label tags (moods, vibes) — the item's category defines a plausible range split into primary, secondary and situational tags, each item gets 1–3 (default 2) with at most one "stretch" tag, every tag needs concrete evidence, and under-tagging beats over-tagging because tag inflation makes filters and matching useless.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
---

# Capped Tiered Tag Assignment

From the mood-assignment rules of a discovery product's enrichment spec (repo diskoe,
mirrored 2026-10-09 from an April 2026 product page). The same rules served as manual
curation guidance and as an LLM prompt. The heuristic: **as few tags as possible, as many
as necessary.**

## The range is not the assignment

A category-to-tag table says which moods are *plausible* for, say, a film screening. It
does not say which ones a given screening gets. Inheriting the whole range is how every
item ends up tagged with everything.

Each category's range is tiered:

- **Primary**: usually fits. Start here; most items get at least one.
- **Secondary**: possible, only with clear evidence from the item itself.
- **Situational**: rare, only with strong, specific signals. Overuse destroys its meaning.

## Count caps

- Minimum 1, **default 2**, maximum 3. More than 3 is not allowed.
- A third tag only if it makes the profile sharper, not because it is also plausible.
- **At most one stretch tag** (a non-obvious secondary or any situational tag) per item.

## Evidence and anti-bloat

- A tag needs a concrete signal: title, description, format, venue type, time of day,
  performer, audience behaviour. The more specific the signal, the stronger the case.
- "Kind of fits" means no. When in doubt, under-tag.
- No aspirational tags: tag the likely real experience, not the marketing copy.
- Final check: would these tags help a user understand the item at a glance?

## Why the cap matters for retrieval

Tags exist to filter and match. If most items carry most tags, a mood filter returns
almost everything and similarity on tags stops discriminating. A cap trades recall at
annotation time for precision at serving time. It is the same discipline as "a tag
should earn its place" in the taxonomy (see
[[Specificity-Adaptive Ranking and Slate Composition]]), applied per item rather than per
vocabulary.

## See Also
- [[One Facet Per Fact]] — related (separating kinds of fact; this caps values within one facet)
- [[Graded-Uncertainty Enrichment Contract]] — related (the enrichment contract these rules fed)
- [[Every Column Names Its Reader]] — related (every tag must be read by something)
- [[Anchor-and-Guardrail Similar Items]] — prerequisite-for (vibe matching relies on sparse, primary-first tags)
