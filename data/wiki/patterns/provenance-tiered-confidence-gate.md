---
title: Provenance-Tiered Confidence Gate
tags: [rag, pattern]
summary: "When retrieval has no rerank score (web search, API fallbacks), derive answer confidence from *which source actually answered* — direct answer, raw results, fallback, nothing — collapse tiers that drive no different behaviour, and let only the bottom tier trigger an honest non-answer, with structured sources carried beside the text rather than trusted to inline citation."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase8-rag-rightsize-agentic-search.md
  - data/raw/claude-docs/listen-wiseer/docs/reviews/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--reviews--phase8-rag-rightsize-agentic-search.md
---

# Provenance-Tiered Confidence Gate

The classic [[CRAG Retry Logic]] gate reads `max(relevance_score)` from a reranker. A
search-backed tool has no reranker and no score — but it still has a perfectly good
confidence signal: **the provenance of what came back.** Found while replacing a single
web-search call with an agentic search step in listen-wiseer (Phase 8).

## The ladder

Drafted with four tiers, keyed on what the search provider returned:

| Provenance | Tier |
|---|---|
| Provider returned a direct synthesized `answer` field | high |
| Only raw `results` (snippets, URLs) | medium |
| Fell through to an encyclopedia page-summary fallback | medium-low |
| Nothing found anywhere | low |

It shipped with **three**. The fallback-success tier collapsed into `medium` because no
code path behaved differently for it — only `low` (literally no text found) triggers the
honest "couldn't find relevant information" reply, and that happens naturally rather than
needing a separate check. **A tier that no reader branches on is decoration** — the same
test as [[Confidence That Is Not a Probability]], applied at design time instead of audit
time. This ladder is explicitly a status lookup, not a probability, and is honest about it:
its only consumer is a branch.

## How it is wired

- The tool returns `(content, artifact)` (LangChain `response_format="content_and_artifact"`),
  with `artifact = {"sources": [...], "confidence": tier}`. The text goes to the model; the
  artifact rides on the `ToolMessage` where the model cannot rewrite it.
- The post-tool validation node reads `artifact["confidence"]` to decide whether a
  corrective retry is worth issuing, alongside its existing string-based error-signal check.
- The response formatter reads `artifact["sources"]` into a structured `sources` field on
  the final response — **populated from tool metadata, independent of whether the LLM
  remembered to cite inline.** (That same formatter then needed a [[Turn-Bounded Citation Walk]].)
- Complexity scoring and query decomposition that already existed (and were being
  computed and discarded) now decide when to fan out to parallel sub-queries; a
  synthesis call merges multi-hit results.

## Borrowed from a reference graph — selectively

The reference CRAG-style graph this was modelled on turned out to wire *no* corrective
loop in production: its `should_continue_crag()` signal was defined but unused. What was
live and worth copying was smaller — (1) refuse to answer when confidence is low *and* no
documents came back, and (2) a structured `sources` list extracted from document metadata.
Read the wired graph, not the module list, before borrowing a pattern
([[Write-Only Fields and the Reader Map]]).

## Known coupling cost

Review flagged that the generic all-tools validation node now duck-types one tool pair's
artifact shape (`{"confidence": ...}`). Accepted as a deliberate choice; the trigger to
introduce a shared typed artifact schema is a third tool adopting `content_and_artifact`
with a different shape ([[Named-Trigger Deferral]]).

## See Also
- [[CRAG Retry Logic]] — alternative-to (score-based gate when a reranker exists)
- [[Confidence That Is Not a Probability]] — instance-of (a status-lookup confidence with a real reader)
- [[Turn-Bounded Citation Walk]] — related (the citation path this artifact feeds)
- [[Write-Only Fields and the Reader Map]] — related (tier collapse and the unwired CRAG signal)
- [[Listen-Wiseer Project]] — instance-of
