---
title: Dynamic Tool Discovery
tags: [llm, agents, mcp, pattern]
summary: "Eagerly loading every tool schema can spend ~30% of a window before the first message — three lighter alternatives (retrieval pre-filter, proactive discovery via a tool_search meta-tool, skills as a greppable catalog) and the KV-cache rule for where a newly loaded schema goes."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
  - data/raw/papers/2026-11-06-lumer-2025-tool-agent-retrieval.md
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

## Joint Tool and Agent Index (Tool-to-Agent Retrieval)

When tools belong to agents or MCP servers, retrieving tools alone drops what the owner holds (authentication, parameter inference, access policy), and routing to agents first hides fine-grained tools. Tool-to-Agent Retrieval (Lumer et al., 2025) indexes tools together with their owning agents, retrieves the top N entries with BM25 plus dense search, maps each tool hit to its owner through metadata, and deduplicates until K unique agents are found. Queries are decomposed into steps and retrieved per step. All numbers are the authors' (self-reported), on LiveMCPBench (70 servers, 527 tools, 95 questions), retrieving the correct agent:

- Recall@5 0.83 against 0.70 for MCP-Zero, 0.74 for ScaleMCP, 0.56 for a query-retrieval baseline and 0.20 for BM25; nDCG@5 0.46 against 0.41, 0.40, 0.32 and 0.14.
- Across eight embedding models Recall@5 ran 0.80 to 0.87 against 0.65 to 0.74 for MCP-Zero; 39.13% of top-K items came from the agent corpus.

## Limits

- One benchmark, no intervals, no ablation of tool-only against agent-only against joint, and no end-to-end task success, latency or token saving, though token cost motivates the work. Its per-model table compares against MCP-Zero only, and its Recall@5 column averages about 0.85 against Table 1's 0.83 (the extraction notes this as its own computation, unexplained by the paper). The extraction notes that the abstract and the contributions list assign the 19.4% and 17.7% gains to opposite metrics. The authors also wrote ScaleMCP, so some baselines are their own.

## See Also
- [[Tool Design as Harness Surface]] — extends (tool discovery at scale)
- [[MCP Protocol]] — related (runtime discovery at the protocol level)
- [[Prefix Caching]] — prerequisite-for
- [[Skill Authoring Discipline]] — related
- [[Tool Design as Context Engineering]] — related
- [[SkillWeaver Compositional Skill Routing]] — instance-of (routing over a skill library)
- [[AnyTool]] — instance-of (hierarchical retrieval over a large API pool)
- [[Alita]] — related (creating a tool when none is found)
- [[UPRISE Universal Prompt Retrieval]] — related (retrieving demonstrations, not tools, with a trained retriever)
- [[OpenDev Terminal Coding Agent]] — related (lazy MCP discovery)
