---
title: Measuring Fixed Context Overhead
tags: [context-management, context, reference]
summary: "The fixed token cost of a coding-agent session can be read directly from its transcript: cache_creation_input_tokens on the first assistant turn of a cold session (cache_read == 0). Comparing that figure with the byte count of the repo-controlled prefix splits overhead into a configurable part and a harness floor. In one measurement the declared content was only about half the observed figure."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-44-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-44-research.md
  - data/raw/claude-docs/guacamayo/docs/plans/GUA-44-plan.md
  - data/raw/repos/guacamayo/.claude--docs--plans--GUA-44-plan.md
---

# Measuring Fixed Context Overhead

A one-time audit from guacamayo (GUA-44): how many tokens does every session pay before
any work starts, and how much of that can the repo actually control?

## The proxy

On a fresh session's **first assistant turn**, nothing can be read from a warm cache.
The whole fixed prefix (harness system prompt, tool schemas, global and repo `CLAUDE.md`,
rules, skill listing) is written to cache as one block, before the agent has read any
file. So `usage.cache_creation_input_tokens` on that turn is the fixed overhead. The
data already sits in every session transcript, so no new instrumentation is needed.

Hygiene rules for the sample:
- **Require `cache_read_input_tokens == 0` on turn 1.** A nonzero value means the session
  resumed from a warm cache and understates the prefix.
- **Exclude sessions whose first user message is long** (e.g. >200 tokens). A pasted spec
  inflates the reading.
- Sample 10–20 fresh sessions per repo and report median and range.

## What it found

| Measure | Value |
|---|---|
| Observed first-turn cache write, 19 sessions in one repo | 15k–23k tokens, mean ~19.7k |
| Cross-repo, most recent session each | ~20k / ~23k / ~33k |
| Declared on-disk prefix (global + repo CLAUDE.md, rules, skill frontmatter), bytes ÷ 4 | ~8.5k tokens |

The declared content is roughly **half** the observed figure. By elimination, the rest is
the harness's own base prompt plus the JSON schemas for every tool, including connected
MCP servers. None of that lives in a file the repo controls, so editing `CLAUDE.md` or
skills cannot reduce it. **The gap between the two numbers is the finding.** It tells you
how much of the budget is configurable before you start trimming instructions. The
gap attribution is medium confidence: bytes ÷ 4 is untested against the real tokenizer,
and the higher repo's extra ~10k was not decomposed (bigger CLAUDE.md, more skills, more
MCP tools).

## Recording a one-time measurement

The audit did not build a recurring pipeline. It added one row to the dashboard's
existing "signal coverage" table, marked *one-time, not tracked live*, following the
table's precedent rows for non-continuous signals. The natural extension point if it
ever becomes live is a nullable column on the session fact store.

## See Also
- [[Context Anatomy]] — extends (measures the stable layers that table describes)
- [[Prefix Caching]] — prerequisite-for (the cache-write and cache-read usage fields this reads)
- [[Why Context Is Finite]] — related (the fixed prefix is budget unavailable to the task)
- [[Rate Metrics Measure the Logger]] — related (the same session-fact dashboard and its regime caveats)
