---
title: Itinerary as Anchored Slot Composition
tags: [patterns, llm, decision]
summary: "An evening plan is built as anchor + slot template + per-slot fill + exact composition at request time — the model only parses the request, because benchmarks show LLMs alone satisfy itinerary constraints in under 10% of cases and place stops more than twice as far apart as humans — while pre-built area lists and similarity graphs are rejected as the primary design and kept only where they help."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-itineraries.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-itineraries.md
---

# Itinerary as Anchored Slot Composition

A plan in the kiez city-discovery app for "plan my evening around <event or place>": a
2–4 stop walk where every stop is open at its time and within a walk of the previous one,
served and logged like any other ranked slate, with no new model spend. Status: planned,
not built — the value here is the decision and its evidence.

## Three designs, one primary

| Design | Verdict |
|---|---|
| **Pre-built by area** ("the Kreuzberg evening") | Rejected. The map already answers "what is here"; precomputed lists go stale as events change daily and ignore *when* — an evening around a 20:00 concert differs from one around a 22:00 club night two streets away. 42% of visible venues had no district, so area cells would be partial anyway. |
| **Themes** (coffee walk, night out) | Kept as **slot templates, not stored lists**: a theme is a sequence of slots (role, kinds, facet boosts, minutes, max walk) — rules as data, filled from the live catalogue at request time. |
| **Similarity / relation graph** around an anchor | Kept for **alternatives within a slot** ("swap the dinner"), not for building the sequence. A learned transition graph needs visit sequences the system does not have yet; the interaction log will produce them. |

## Why the model does not pick stops

- On the TravelPlanner benchmark GPT-4 met all constraints in 0.6% of cases, o1-preview in
  about 10%; a real-world benchmark measured LLM plans at 17 km average distance between
  stops against 7.3 km in human plans.
- The hybrids that work (ITINERA, a NAACL 2025 solver hybrid at 93.9%) let the model read
  the request and let clustering or a solver choose and order stops — the shape the
  assistant already had ([[Dual Parser with Shared Shape]] parses; rules search;
  [[Assembled, Not Generated Replies]] speaks).
- Formally it is the **Orienteering Problem with time windows**. With ≤4 slots and K ≤ 5
  candidates per slot, exact enumeration over the K^slots product is cheap — no heuristic.

## The shape

`parse → anchor → template → fill → compose → serve → reply`

- **Anchor** is an event (fixes a time window, the strongest anchor), a venue, or a point.
- **Fill** per slot: venues within the slot's walk bound of the *previous stop*, open at the
  slot's instant, matching kinds (facets as boost, since enrichment is sparse), ranked by the
  existing ranker with the previous stop as the proximity reference. Top K kept as
  alternatives.
- **Compose**: best path = sum of stop scores − walk penalty, no kind twice, every stop
  open at its time.
- **Spatial compactness is a hard pre-filter, not a score** — following the cluster-then-plan
  systems; here the cluster is "within ~800 m of the previous stop".
- **An unfillable slot is dropped and the reply says so** ("Nothing open for dinner within a
  walk; starting at the concert"), as an empty shelf names its reason.
- Venues with no opening hours count as `no_data`, allowed and scored 0.5, as the ranker
  already does.

## Measured, not passed/failed

Feasibility is four continuous 0..1 scores (open-at-time share, walk-within-bound share,
time-ordered, kind diversity), after TripCraft's separate temporal/spatial/ordering/persona
scoring. The eval gate threshold is set from the first measured run over 50 real anchors,
not before. Saved itineraries, a "popular evenings" shelf, and a learned kind-transition
table each wait for measured opens and directions — each its own plan.

## Explicitly not in scope

Model-chosen stops or model-written text; transit routing (straight-line walk bound until
measured distances say otherwise); multi-day plans; server-stored personal itineraries.

## See Also
- [[Dual Parser with Shared Shape]] — prerequisite-for (the parse the anchor and template come from)
- [[Assembled, Not Generated Replies]] — extends (stops and times are reported, never generated)
- [[Replayable Slate Ranker]] — extends (an itinerary is one more logged slate; fill reuses the ranker)
- [[Kiez Project]] — instance-of
- [[Open POI Data Sources]] — related (opening-hours coverage bounds the open-at-time check)
