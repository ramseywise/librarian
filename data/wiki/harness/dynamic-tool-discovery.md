---
title: Dynamic Tool Discovery
tags: [llm, agents, mcp, pattern]
summary: "Eagerly loading every tool schema can spend ~30% of a window before the first message — three lighter alternatives (retrieval pre-filter, proactive discovery via a tool_search meta-tool, skills as a greppable catalog) and the KV-cache rule for where a newly loaded schema goes."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
---

# Dynamic Tool Discovery

## The Cost of Eager Loading

Li (*AI Agents in Depth*, ch. 4) measures five typical MCP servers at **~55K tokens of tool
definitions — roughly 30% of a 200K window — before the first user message.** Selection
accuracy also degrades as the candidate set grows (it falls off past roughly a hundred
tools), so every resident tool spends a shared budget. That is the quantitative case for
subtraction in [[Tool Design as Harness Surface]].

## Three Alternatives, Heaviest to Lightest

1. **Retrieval pre-filter.** Embed tool descriptions; inject the top-k for the user's query.
   *Limitation:* it matches **once**, against the opening request. "Debug the file" can turn
   into a cross-domain tool chain nobody predicted.
2. **Proactive discovery.** The agent declares a capability gap mid-task; the system matches
   and injects tools. Two-level matching (server first, then tool), as in MCP-Zero, reports
   ~98% fewer tokens than full injection across ~2,800 tools; dynamic discovery is reported to
   have lifted a frontier model from 49% to 74% on a vendor tool-selection eval. The
   production form is a **resident `tool_search` meta-tool** (deferred loading of MCP
   tools). When nothing scores above threshold, return an explicit **"not found"**, so the
   agent rephrases, improvises with basic tools, or builds one.
3. **Skills.** A thin resident catalog read with ordinary file tools — no embedding index to
   maintain. A folder of tool descriptions the agent greps is reported to cut tokens by
   ~47%; another design keeps MCP out of the core entirely behind a single ~200-token proxy
   tool. See [[SKILL.md Pattern]].

> **MCP solves interoperability. Skills solve choice overload.** Complementary, not rivals.

## The KV-Cache Rule for Dynamic Tools

**Never insert a newly loaded schema into the static prefix** — that invalidates the whole
cache. Append it at the end of the context *on the turn it is discovered*, then leave it
pinned where it landed, where it becomes ordinary cached history. Cache invalidation then
comes only from TTL expiry or from modifying, removing, or reordering tools already loaded.
The cost: weaker models handle schemas that appear mid-trajectory poorly. See
[[Prefix Caching]].

The same "append at the end, never mutate the prefix" rule governs the environment status
bar in [[Harness Anatomy]].

## See Also
- [[Tool Design as Harness Surface]] — extends (tool discovery at scale)
- [[MCP Protocol]] — complements (runtime discovery at the protocol level)
- [[Prefix Caching]] — depends-on
- [[Skill Authoring Discipline]] — complements
- [[Tool Design as Context Engineering]] — extends
