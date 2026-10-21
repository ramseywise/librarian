---
title: Dual Parser with Shared Shape
tags: [llm, prompting, pattern]
summary: A model parser and a rules parser that emit the identical structured shape, with the rules path as the default and the model path gated behind a spend flag and used only when it returns something valid — so the system works with no model at all, degrades to the same behaviour on failure or timeout, and every value the model emits is filtered against the same fixed vocabularies the rules use.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/kiez/docs/assistant.md
  - data/raw/claude-docs/kiez/docs/graphs.md
  - data/raw/repos/nonprofit-success-ai/CLAUDE.md
  - data/raw/repos/nonprofit-success-ai/README.md
---

# Dual Parser with Shared Shape

The kiez assistant turns a typed or spoken request ("somewhere with live music in
Kreuzberg tonight") into a search. Two parsers produce the same shape:

| Parser | When | How |
|---|---|---|
| **model** | spend is allowed *and* a key is set | structured output into a typed parse model, prompt version logged with the serve; every kind, facet and area outside the tag lists is dropped |
| **rules** | otherwise, or when the model call fails or returns nothing valid | the same word lists (English and German) for kinds, facets, areas and times; whatever is left minus filler words becomes the free-text query |

The shape is `{query, kinds, facets, genres, area, when, nearMe, itinerary}`, every
enumerable field drawn from a fixed vocabulary that the rest of the system already uses.

## What the shared shape buys

- **The model is optional.** The product runs with no model at all, which is the default
  posture while spend is off; the model is an upgrade to the parse, not a dependency.
- **Failure is a downgrade, not an error.** A model call that fails, times out or returns
  nothing valid falls back to the rules path and the request still completes.
- **The model cannot widen the vocabulary.** Because its output is filtered against the
  same tag lists, an invented kind or area is dropped rather than searched for. A free
  boolean (`itinerary`) is kept only as a boolean.
- **Everything downstream is parser-agnostic.** Search, ranking, logging and the reply
  consume the shape; the serve log records which parser produced it, so behaviour can be
  compared across the two paths.

## The same idea at service level

The web route is the single entrypoint. With a service URL set it forwards the request to
a LangGraph service that parses, searches events and logs; when the URL is unset *or the
service does not answer within 15 s*, the web app answers alone with the same parsers and
rules. The web path keeps no session memory while the service path remembers up to six
turns (a follow-up that names only a time, area or genre inherits the previous turn's
kinds, facets and query) — a documented difference, not an accident.

## Deliberately few questions back

There is no intake questionnaire. The one clarifying question ("What kind of music?") is
asked only when a music request names no genre, has not already been clarified, there are
at least six events to choose between, and at least two genre options are actually on
offer. Each option is sent back as a new message with the genre word prepended, so it is
parsed like anything typed.

## See Also
- [[Assembled, Not Generated Replies]] — extends (the reply side of the same cost/truthfulness posture)
- [[Structured Output]] — related (the model path's output contract)
- [[Spend Gate Before the Model Call]] — related (the same spend switch, on the pipeline side)
- [[Kiez Project]] — instance-of
- [[Itinerary as Anchored Slot Composition]] — prerequisite-for (the parse supplies the anchor and template)
- [[Server-Derived Autonomy Tier]] — related (a deterministic fallback required on every agent path in a roster)
- [[Gated Weighted Composite Score]] — alternative-to (a deterministic engine that is the implementation, not a stand-in)
