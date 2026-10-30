---
title: Cited-Minus-Read Grounding Check
tags: [rag, eval, pattern]
summary: Make a chat agent cite pages in a fixed parseable marker, then compute ungrounded = cited − pages successfully read in this answer; a search excerpt does not count as a reading, prior turns carry text only so the model must re-read before citing, and a cited id never lights up the UI unless the tools actually returned it.
updated: 2026-10-30
sources:
  - data/raw/repos/librarian/.claude--docs--plans--2026-10-28-chat-agent-improvements.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-10-30-frontend-audit-fixes.md
---

# Cited-Minus-Read Grounding Check

Found while upgrading the librarian graph UI's chat agent (an Anthropic tool-use loop with
`search_wiki` and `read_page`). Its only grounding control was a prompt line, "never
invent content". Nothing checked that a page the answer attributed a claim to had been
read. The fix turns grounding into a set difference computed after the loop.

## Mechanism

1. **A citation form that cannot collide.** Answers cite `[page:<page-id>]`, where the id
   is the kebab-case filename stem `search_wiki` returns. double-bracket wikilinks were
   rejected: they are keyed by title and already appear inside the page bodies the agent
   quotes, so a quoted link would parse as a citation. `[page:` occurs nowhere in the wiki.
2. **Two sets per answer.** `cited` is parsed from all streamed text. `pages_read` is the
   ids whose `read_page` call *succeeded in this answer*.
   `ungrounded = cited − pages_read`.
3. **An excerpt is not a reading.** A page that appeared only as a 200-character search
   excerpt and was then cited counts as ungrounded.
4. **Surface it, do not trust it.** A `grounding` event (`cited`, `pages_read`,
   `ungrounded`) streams before the final highlight. The UI shows a one-line sources list
   and, in a warning colour, "cited but not read".
5. **Hallucinated ids never reach the graph.** The highlight set comes only from pages
   that search or read returned, filtered to ids that exist on disk. Cited ids are never
   added to it.

## Why multi-turn has to be text-only

Follow-up questions get the prior turns as text only: tool blocks never cross the wire.
So the model cannot see pages it read in earlier turns, and the system prompt tells it to
re-read before citing. That constraint is what keeps "read in *this* answer" well defined.
If tool results carried over, a page read three turns ago would count as grounded for a
claim made now. This is the same turn-boundary bug as [[Turn-Bounded Citation Walk]],
reached from the other side.

History is trimmed by the agent rather than the API, so the eval harness and any later
caller get the same bounds: last 10 messages, then oldest-first while over 24k characters,
then a leading assistant turn is dropped so the transcript opens on `user`. A validator
rejects any history that does not alternate strictly user/assistant ending on
`assistant`. The client sends completed pairs only, so an errored or aborted reply drops
its pair and the invariant holds by construction.

## What it feeds

- **Per-answer telemetry**: one JSON line per answer (`turns`, `tool_calls`,
  `pages_read`, `cited`, `ungrounded`, `latency_ms`, `stop_reason`, `source` = chat or
  eval). It mirrors the retrieval log's writer: it never raises, and it resolves the log
  path at call time so the test fixture that isolates one log isolates both. Answer text
  is not logged.
- **An answer eval that reuses the UI path**: deterministic `read_recall` and
  `cited_recall` (expected source pages ∩ read or cited), `grounded` (no ungrounded
  citations), plus an opt-in, billable LLM judge whose parse failures are excluded from
  the mean rather than scored 0. It is report-only until a baseline exists
  ([[UNGATED Metric Convention]]).
- **Injectable client**: the loop takes `client=None` and falls back to the env-built
  one, so tests drive the full loop with a fake streaming client and never call the API.

A later UI change renders each `[page:id]` marker as a chip that focuses the graph node.
The grounding line is kept alongside it.

## See Also
- [[Quoted Span as Proof of Reading]] — alternative-to (the same "did it actually read it?" check for review findings, done by string match)
- [[Turn-Bounded Citation Walk]] — extends (the cross-turn citation leak, closed by keeping tool results out of history)
- [[Librarian Graph Explorer]]
- [[UNGATED Metric Convention]]
