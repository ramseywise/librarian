---
title: Assembled, Not Generated Replies
tags: [llm, prompting, pattern]
summary: The user-facing answer line and the spoken line are assembled from the parsed request and the actual result list by templates, never written by a model — so the reply can only state what the system did, is free, and needs no grounding check.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/kiez/docs/assistant.md
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-voice-assistant.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-voice-assistant.md
  - data/raw/claude-docs/kiez/docs/plans/2026-10-16-itineraries.md
  - data/raw/repos/kiez/.claude--docs--plans--2026-10-16-itineraries.md
---

# Assembled, Not Generated Replies

The kiez assistant uses a model (optionally) to *understand* a request and never to
*answer* it. The answer line — "8 places for *live music* in Kreuzberg, tonight." — is
assembled from the parsed request and the count of results:

> That keeps it truthful (it can only state what the system did) and free.

The two properties come from the same decision. A templated sentence over the parse and
the result list cannot assert anything the system did not do, so there is nothing to
ground-check; and it costs no tokens, so it can run on every request including the ones
the rules parser handled without a model.

## The same rule for voice

With hands-free on, each answer is read out with the browser's speech synthesis. The
spoken line is likewise assembled from the reply — the count, the first three results in a
fixed phrasing, and what to say next — "never written by a model". It is built where the
final ranked list is known (the web app), since the parsing service never sees ranked
venues. Three follow-ups ("more", a pick such as "the second one", "thanks") are answered
from the last list without a new request; anything else is a new request.

## What the reply does say honestly

When a search is retried without the free-text query, or without the time window, the
assembled answer says so ("No events listed for …"). A retry that silently widened the
search would make the templated line untrue; the template carries the retry state instead.

## When this applies

Any surface where the reply is a *report on a deterministic result* — a count, a list, a
viewport, a fallback that was taken. The model's job ends at the structured parse
([[Dual Parser with Shared Shape]]); the words shown to the person are the system's own.

## Voice plan: escalate only by measured failure

The voice plan keeps the first step free (browser speech recognition and synthesis) and
names the decision rule for paying: record recognition failures per turn, turns per
session, and latency; **if recognition is the failure, move to server STT; if latency or
voice quality is, consider a realtime voice model.** Voice barge-in was not built —
recognition during playback would transcribe the device's own voice; a stop control cuts
the answer short instead. If a realtime voice model is ever added, it is a tool-calling
front with one tool (`ask(text)` → the assistant endpoint) and is told to read the
assembled spoken line and nothing else, so the no-generated-answers rule survives the
upgrade.

## See Also
- [[Dual Parser with Shared Shape]] — prerequisite-for
- [[Grounding Claim Methodology]] — alternative-to (measure grounding after generation vs. make generation impossible to un-ground)
- [[Structured Output]] — related
- [[Kiez Project]] — instance-of
- [[Itinerary as Anchored Slot Composition]] — extends (multi-stop plans assembled by rules; the model only parses)
