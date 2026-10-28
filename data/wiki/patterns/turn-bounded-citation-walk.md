---
title: Turn-Bounded Citation Walk
tags: [langgraph, rag, pattern]
summary: A response formatter that walks message history backwards collecting tool-call citations must stop at the most recent human message — without that boundary a prior turn's web-search sources leak into an unrelated current answer, a bug that passes every single-turn test.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/listen-wiseer/docs/CHANGELOG.md
---

# Turn-Bounded Citation Walk

Found in review of listen-wiseer's Phase 8 (agentic web search). `format_response` built
`agent_response.sources` by walking the LangGraph message list backwards and collecting
citations from web-search tool outputs. The loop had **no turn boundary**: on a
multi-turn thread it kept walking past the current user message into earlier turns and
attached a previous question's citations to the current, unrelated answer.

## Why it survives testing

Every single-turn test passes — there is nothing earlier to leak. The defect only appears
when a session has a prior turn that called the same tool, which is exactly the shape a
conversational agent has in production and almost never in a unit fixture. It was caught
by a review pass, not by the 18 new tests added in the same phase.

## The fix

Stop the backward walk at the most recent `HumanMessage`. Anything older belongs to a
previous turn's answer and has already been cited there. Six regression tests pin the
boundary.

## Generalization

Any accumulator that reads from a shared, append-only message history — citations, tool
outputs, confidence tiers, "sources used" footers — needs an explicit notion of *the
current turn*. The history is one list; turns are a structure you impose on it. The same
class of bug appears when a confidence gate reads the latest tool output without checking
it belongs to this turn.

## See Also
- [[Listen-Wiseer Project]] — instance-of
- [[CRAG Retry Logic]] — related (the confidence gate the same phase wired into validation)
- [[Context Failure Modes]] — related (stale context contaminating the current answer)
- [[HistoryCondenser]] — related (another component that must respect turn structure when editing history)
