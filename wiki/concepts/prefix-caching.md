---
title: Prefix Caching
tags: [llm, context-management, infra, concept]
summary: Claude's automatic KV cache reuse for repeated prompt prefixes — cuts latency and cost by 90% for static system prompts and long tool schemas.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
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

## See Also
- [[ADK Context Engineering]]
- [[Production Hardening Patterns]]
- [[LangGraph CRAG Pipeline]]
