---
title: Constraint Tiers and Two-Phase Relaxation
tags: [rag, llm, pattern]
summary: Classify every search input as a hard constraint, a semi-hard constraint, a strong preference or a decision signal; when results run thin, soften internal scoring first and only then suggest user-facing filter changes, never auto-relax hard constraints (date, accessibility), and say so whenever close alternatives are shown.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-search-and-recommendation-specs.md
---

# Constraint Tiers and Two-Phase Relaxation

From the search and filter specs of a curated discovery product that returns five
results (repo diskoe, mirrored 2026-10-09 from May–Aug 2026 product pages). It answers
the question every filtered recommender hits: what to do when the user's filters leave
too few good results.

## Four tiers, not two

A filter UI tempts you to treat every input as a `WHERE` clause. The spec split them:

| Tier | Examples | Behaviour |
|---|---|---|
| **Hard** | date, start time (unless "any"), barrier-free | never broken, never silently relaxed |
| **Semi-hard** | district, price, indoor/outdoor *if the data is reliable*, near-me *if location quality is good* | respected, but may widen in controlled, **communicated** ways |
| **Strong preference** | mood, companions, event type, spontaneity | shape ranking and composition, never exclude |
| **Decision signal** | safe pick, niche, date-friendly, low effort | internal, used to give each slot a role and to explain it |

Three rules fell out of the split:

- **A constraint's tier depends on data quality.** Indoor/outdoor is only strict when the
  field is reliable. A hard filter on an unreliable field silently drops valid items.
- **Accessibility is hard because the cost of a wrong "yes" falls entirely on the user.**
  (The ranking spec goes further and treats unknown accessibility as a fail; see
  [[Specificity-Adaptive Ranking and Slate Composition]].)
- **Format is a preference, not a filter.** Demoting event type from hard to strong
  preference kept rare combinations ("chill" + "club") answerable: rank softer nightlife
  first instead of returning nothing. Derived signals like "visitor-friendly" come from
  the companion choice rather than becoming another filter.

The spec pages disagreed with each other on whether event type and price were hard. That
is the usual failure when tiers are written per page instead of in one table.

## Few results vs no results

- **Few results** (fewer than five strong results after hard constraints): keep the hard
  constraints, relax ranking and decision signals, add close alternatives, and **tell the
  user** ("Few exact matches. Showing close alternatives too.").
- **No results** (zero valid after hard constraints): do not relax anything silently. Say
  so and suggest the specific filters to change. An empty state should be a next step,
  not a dead end.

## Two-phase relaxation order

1. **Soften internally first**, in order: decision signals, event-type strength, mood
   strength, companion interpretation, spontaneity, indoor/outdoor (if data is weak),
   near-me radius.
2. **Then suggest to the user**, in order: district → citywide, start time → any time,
   price → another range, type → any, indoor/outdoor → any.
3. **Never auto-relax**: date and accessibility.

Internal softening is invisible and cheap, so it goes first. A change to what the user
asked for is visible, so it is offered, not applied.

## A loading state is not an explanation

The spec allowed a brief deliberate loading state ("Specific combo detected — we'll
search a little wider") but required that, if close alternatives were actually included,
a small explanation still appear above the results.

## See Also
- [[Specificity-Adaptive Ranking and Slate Composition]] — extends (the scorer and five-slot composer that consume these tiers)
- [[Anchor-and-Guardrail Similar Items]] — related (the detail-page layer that reuses the search context as a guardrail)
- [[Hide-Unknown Display Contract]] — related (the same "unknown is not a yes" posture on the display side)
