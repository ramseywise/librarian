---
title: Prefix Caching
tags: [llm, context-management, infra, concept]
summary: Claude's automatic KV cache reuse for repeated prompt prefixes — cuts latency and cost by 90% for static system prompts and long tool schemas.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/support-agents/invocation-flow.md
  - data/raw/claude-docs/playground/docs/archived/librarian-stack-audit.md
  - data/raw/claude-docs/project-g/docs/support-agents/invocation-flow.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b49-prompt-cache.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b49-prompt-cache.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b63-spend-observability.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b63-spend-observability.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b63-spend-observability.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b63-spend-observability.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--context-management.md
---

# Prefix Caching

Claude (Sonnet and above) automatically caches the KV representations of prompt prefixes across calls. When a new request shares a long prefix with a recent request, the cached KV state is reused — the model only processes the novel suffix.

## What It Saves

| Without cache | With cache (prefix hit) |
|---|---|
| Full prompt processed each call | Only suffix processed |
| ~100% token cost per call | ~10% of prefix token cost |
| Full TTFT latency | Reduced TTFT proportional to prefix length |

Cache TTL: 5 minutes. Prefix must be byte-identical to hit.

## Where It Applies

**High-value targets** (long, static, repeated):
- System prompts (agent instructions, persona, rules)
- Tool/skill schemas in the tools field
- Long document contexts injected at the start of a conversation

**Does not apply** to dynamic content appended per turn (user messages, tool results).

## ADK Implication

In ADK, `static_instruction` (a string) is eligible for prefix caching. `instruction=callable` (a function called per turn) is NOT — the callable injects dynamic content, breaking the byte-identical requirement.

This is why the three [[ADK Context Engineering]] skill-loading strategies differ:
- `live_mcp` (all schemas in system prompt from turn 1) → cache-eligible
- `dynamic_skill_mcp` (injects via function_response) → not cache-eligible

## LangGraph Implication

Prompt templates with a static system block at the top cache aggressively. Vary only the suffix (user query + retrieved context). Keep retrieved chunks AFTER the system prompt, not before.

## Monitoring Cache Hits

Anthropic API responses include `cache_read_input_tokens` and `cache_creation_input_tokens` in usage stats. A healthy prefix-caching setup should show `cache_read_input_tokens > 0` on all calls after the first.

## Design Goal: Minimize LLM Calls + Cache Aggressively

The [client] ADK POC (April 2026) explicitly set "minimize LLM calls + optimize for prefix caching at scale" as top design goals. This directly influenced the choice of **Agent with Skills & Compaction** over multi-agent topologies — a single agent with a stable prefix caches better than N agents each with their own context. See [[Multi-Agent Orchestration Patterns]].

## Gemini `cachedContent` for the system instruction

A production TypeScript support agent caches its ~4,000-token system instruction plus its
tool schemas as a Gemini `cachedContent` resource. The cache has a 1-hour TTL and is
refreshed proactively 5 minutes before it expires, as a module-level singleton. When the
cache is active, `system_instruction` and `tools` must be **stripped** from the request:
Gemini rejects a request that carries them alongside a `cachedContent` reference. At volume
this is the main per-call cost lever, because the system instruction is the dominant token
cost per turn.

## OpenAI's 1,024-Token Threshold: Where the Dynamic Slots Sit (akira, 2026-08)

OpenAI caches prompt prefixes automatically, but only once the identical prefix reaches
**1,024 tokens**. An enrichment pipeline had three templates, each about 85% static text
(rule block and vocabulary lists). Even so, the per-event slots (title, venue, content
JSON) were interpolated about **11% of the way in**. The cacheable prefix was only about 340
tokens, so nothing was ever cached.

- **Move every dynamic slot to the end.** The static prefix grows to about 85% of the
  template (~3,200–3,800 tokens), above the threshold, which is worth roughly 50–60% off
  input cost. "Static text" is not enough on its own: what matters is the position of the
  *first* byte that varies.
- **Minify the dynamic payload.** Switching `JSON.stringify(content, null, 2)` to plain
  `JSON.stringify(content)` cuts the uncached tail.
- **Verify the prefix is byte-identical across events** rather than assuming it.
- **Surface `cachedTokens`, then make sure something reads it.** The plan threaded the
  provider's cache-read count through the result type. A retroactive review found it was
  computed and never read, because the spend ledger's `record()` signature had no field for
  it and dropped it at the call site. That needed a follow-up plan. A cache-hit metric that
  nothing reads proves no more than having no metric.
- The regression gate named for the reorder was a fixture eval that never calls the model.
  See [[Fixture Eval Blind to the Swapped Component]].

## See Also
- [[ADK Context Engineering]]
- [[Multi-Agent Orchestration Patterns]]
- [[Production Hardening Patterns]]
- [[LangGraph CRAG Pipeline]]
- [[LLM Fundamentals Interview Study Guide]] — prerequisite-for
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Context Compaction]] — extends (compaction invalidates the cached prefix from the compaction point forward)
- [[Context Anatomy]] — extends (stable-before-dynamic ordering as the prefix-match precondition)
- [[Offline Annotation over Online Inference]] — instance-of (a static taxonomy prefix as ~97% of enrichment input tokens)
- [[Fixture Eval Blind to the Swapped Component]] — related (the gate that could not detect a regression from the prompt reorder)
- [[Measuring Fixed Context Overhead]] — extends (first-turn cache write as a fixed-overhead proxy)
