---
title: Cache-Stable Context Layout
tags: [context, context-management, infra, pattern]
summary: "Once prompt caching carries real money, byte-stability of the prefix becomes an architectural constraint — the usual cache breakers (timestamps, per-request config, reordered tools, sliding windows, per-request few-shot) and the three design moves that keep the key stable (cache-boundary ordering, byte-aligned sub-agents, frozen tool-result replacements)."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--02-context-anatomy.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--05-compression-compaction.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--04-retrieval.md
---

# Cache-Stable Context Layout

[[Prefix Caching]] hits only on a byte-identical prefix; [[Context Anatomy]] gives the
basic rule (stable before dynamic). This page covers what breaks the prefix in practice
and how cache-key consistency ends up shaping design decisions that look unrelated.

**The stakes.** In a course-cited production incident, adding `Current time: {{now}}` to
the system prompt of a ~100k-conversations/day agent took time-to-first-token from 0.5 s
to 3–5 s and nearly doubled the bill.

## Patterns That Break the Cache (or the Model)

| Pattern | What breaks | Fix |
|---|---|---|
| Timestamp in the system prompt | Prefix changes every request | Append time as a late message, or offer a clock tool |
| Per-request user config (quota, balance) | Same | A state channel at the end ([[Agent Status Bar]]) |
| Reordering tools by usage frequency | Hundreds of tokens per tool re-prefilled | Fixed tool order; accuracy barely changes |
| Sliding-window history | Prefix shifts *and* old tool results vanish, so the agent re-runs calls and loops | Compaction, not truncation ([[Context Compaction]]) |
| Flattening messages into `USER: … ASSISTANT: …` text | The real damage is leaving the trained format: ignored tool results, repeated actions | Use the API's structured roles |
| Per-request "most relevant" few-shot examples | Examples sit early, so every swap breaks the prefix | A fixed example set per task type |

Note the sliding-window row: truncating history is not just cache-hostile, it causes
behavioural loops, because the agent no longer sees that a call already ran.

## Economics in Brief

Cached reads cost roughly **one-tenth** of fresh prefill across the major providers.
Anthropic requires explicit `cache_control` breakpoints, a minimum length (~1024 tokens)
and has a ~5-minute TTL; OpenAI caches prefixes automatically. KV cache works *within* a
request inside the engine; prompt cache works *across* requests at the API layer — both
need the prefix byte-stable. Vendors also expose **explicit** caches (a named cache object
with a TTL, e.g. Gemini context caching) that suit "upload a corpus once, ask many
questions" sessions — a cheap alternative to RAG when the corpus fits in the window.

**"Cache-friendly" means write once, benefit repeatedly — not zero cost.** The first
insertion still pays a cache write.

## Caching as an Architectural Constraint

Claude Code illustrates three design moves driven by cache-key consistency:

1. **Order by cache boundary first, meaning second.** A marker splits globally cacheable
   content from per-user/per-session content. Every binary runtime condition placed
   *before* the marker doubles the number of cache-key variants (N conditions → 2^N), so
   prompt fragments are tagged *cacheable* or *cache-breaking*.
2. **Sub-agents are byte-aligned with the parent** — same prompt, tools, model config and
   message prefix — so side queries hit the parent's cache.
3. **Tool-result replacements are frozen at first use.** When a large output is swapped
   for a preview, that exact string is persisted and reused after a session restore, so
   the replayed history stays byte-identical.

**Design this in from the start; retrofitting cache consistency is expensive.**

## Where Skill Content Lands

Progressive disclosure of skills (see [[Context Anatomy]]) poses the same trade-off:

| Placement | Cache | Instruction-following |
|---|---|---|
| Append to the system prompt | Breaks the prefix on every load | Strongest — system position is heavily trained |
| Read as an ordinary file (mid-context tool result) | Untouched | Model-dependent; often treated as reference, not orders |
| Metadata resident, full skill via a dedicated Skill tool | Write once, then cached | Good — routing and execution are separate steps |

Write the skill description as a **routing rule, not a feature summary**: "Use when … / Do
not use when …", with negative examples. Explicit exclusions are what make routing precise.

## See Also
- [[Prefix Caching]] — extends
- [[Context Anatomy]] — extends (stable-before-dynamic, made operational)
- [[Context Window Budgeting]] — prerequisite-for (the cost side of the budget)
- [[Agent Status Bar]] — prerequisite-for (where per-request state goes instead)
- [[Reasoning State Pass-Back]] — extends (the other way message formatting changes behaviour)
- [[Measuring Fixed Context Overhead]] — extends
