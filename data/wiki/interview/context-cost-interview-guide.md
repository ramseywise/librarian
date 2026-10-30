---
title: Context Engineering and Cost Interview Study Guide
tags: [interview, context, reference]
summary: Exam-prep reference for context and cost questions — context rot as the root problem, the five context layers sorted by frequency/stability/enforcement, compaction retention priorities, prefix vs semantic caching, skill descriptions as routing logic, the rank-ordered cost/latency levers, and reporting cost per successful task.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--5-context-cost--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--5-context-cost--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--context-engineering-cost.md
  - data/raw/repos/sisyphus/interviewing--guides--5-context-cost--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--5-context-cost--00-overview.md
---

# Context Engineering and Cost Interview Study Guide

"Context engineering" has replaced "prompt engineering" as the interview keyword. The root
problem to name first is **context rot**: attention degrades as the window fills, so more
context is not better context ([[Why Context Is Finite]]).

## The five context layers

Organise any answer by sorting information on **usage frequency, stability, and enforcement
requirement** — keep the active context small and retrieve the rest on demand:

1. **Persistent instructions** — identity, invariants, safety constraints. Short, stable,
   always loaded.
2. **On-demand knowledge** — skills and long references under progressive disclosure: only
   name + "what and when" stay visible ([[SKILL.md Pattern]]).
3. **Runtime injection** — date, tenant, permissions, task status; assembled per turn, never
   baked into the system prompt.
4. **Long-term memory** — a compact index plus retrievable topic files, editable and
   auditable so wrong memories can be removed.
5. **Deterministic system layer** — what the model must *never* get wrong does not belong in
   context at all: hooks, validators, permissions, schemas. "The model may ignore an
   instruction; a code-level control won't."

The full anatomy is [[Context Anatomy]].

## Compaction

Pipeline: prune irrelevant → replace bulky tool outputs → extract structured task state →
summarise older reasoning → keep recent messages verbatim. **Retention priority** when
compacting: architectural decisions (never summarise away) → modified files → verification
pass/fail → open TODOs and rollback notes → tool outputs (drop, keep conclusions). Related
mechanics: summarisation nodes on a small model, tool-call offloading (head + tail in
context, full output on disk), and trimming items before the latest compaction point. See
[[Context Compaction]].

## Prefix vs semantic caching — distinguish them

**Prefix caching** reuses the prefill KV state when a new prompt shares a byte-identical
prefix ([[Prefix Caching]]). Consequences to recite: static content first, dynamic last; a
per-turn timestamp in the "static" region silently kills the cache; hits save roughly 90% of
input cost with proportional TTFT; TTLs are minutes; verify via the cache-read token field,
don't assume. Architectural consequence: **one agent with a stable prefix caches better than
N agents each with their own context** — a real argument for skills-based single agents over
multi-agent topologies.

**Semantic caching** caches *answers* keyed by query similarity, with a threshold to tune
against serving a wrong cached answer ([[Semantic Cache for RAG Agents]]). Interviewers
conflate the two deliberately.

## Skill descriptions are routing logic

Write them as when-to-use / when-not-to / success criteria in about ten tokens; add negative
examples to cut misfires; put templates inside the skill (free when unused); tell the model
explicitly to use the skill when determinism matters.

## Cost/latency levers, rank-ordered

1. Prefix caching (free if ordering is right)
2. Model routing — small model for classify/rewrite/grade, large for synthesis
3. Streaming (perceived latency; also needed inside serverless timeouts)
4. Semantic cache for paraphrase traffic
5. Compaction and tool-output offloading
6. Output-length discipline and structured outputs (decode tokens cost more than prefill — [[LLM Inference Economics]])
7. Batch/offline jobs for non-interactive work

**Report cost per successful task, not per call.** An agent that retries three times and
still fails is cheap per call and unbounded per outcome. Track per step → per conversation →
per successful task and quote the last; it is the only figure that moves with quality as well
as spend.

## Question bank (answer sketches)

- *"Token bill doubled."* — cache hit rate first (ordering regression?), then per-route token
  histograms (agent circling), tool-output bloat, model-routing drift; fix in lever order.
- *"System prompt is 8K and growing."* — split by the five layers and measure cache hit rate
  before and after.
- *"Where does retrieved context go?"* — after the static prefix (caching), next to the
  question (recency), under a token budget with a summarisation fallback.

## Follow-ups on long-running context (answer sketches)

*Provisional:* condensed from the reference answers to the chapter questions in *AI Agents in Depth* (Li), which the book itself flags as AI-drafted with light human review. Treat these as answer shapes to check, not settled claims.

- *Sliding window makes the agent repeat tool calls; full history explodes.* Append only; at ~80% of
  the window compress old tool results once; persist large outputs to disk with a summary; isolate
  intermediate work in sub-agents. This keeps the cached prefix intact.
- *Reasoning content across hundreds of tool calls.* Keep recent reasoning in full and roll older
  reasoning into a structured status (goal, confirmed facts, ruled-out paths, to-dos) once, at a fixed
  point ([[Reasoning State Pass-Back]]). Stripping prior reasoning is cheap and cache-friendly but loses the long-range plan; for agents,
  reasoning is state.
- *148K characters compressed to 2K — irreversible loss?* Yes, so pair lossy compression with lossless
  indexing: a source reference per fact, raw outputs on disk, verbatim retention of decisions, dates,
  names and IDs.
- *The status summary itself is wrong.* The model trusts it unconditionally ([[Agent Status Bar]]). Maintain it in code, never
  by an LLM counting history; track its accuracy; feed it only from real observations.
- *Twenty queued events (tool results, user messages, alerts).* Route urgent ones separately as
  interrupts, truncate long tool results to head + tail + file path, end the context with per-type
  counts and an instruction to answer each.
- *Many authors on one system prompt.* Prompts as reviewed code, benchmark before/after, enforced
  structure, fragments labelled cacheable vs cache-breaking, bloat split out into Skills.
- *Where to inject a loaded Skill.* System prompt: strongest adherence, breaks the cache. Mid-context as
  a file read: cache-safe, weaker adherence. End of context: good adherence, recomputed every call.
- *Large, changing tool set — maximise cache hits.* A small frozen core of tools in fixed order in the
  static prefix, a generic executor, capabilities delivered as Skills; sub-agents share the parent's
  prefix ([[Prefix Caching]], [[Cache-Stable Context Layout]]).

## See Also
- [[Context Anatomy]] — prerequisite-for (the layer model in depth)
- [[Prefix Caching]] — prerequisite-for (the mechanism behind lever 1)
- [[Context Compaction]] — extends
- [[Agents Interview Study Guide]] — related (harness and long-horizon side)
- [[System Design Interview Study Guide]] — related (cost trade-offs in the design round)
