# Technical Strategy for Evolving the Virtual Assistant from PoC to v1

**Source:** https://app.notion.com/p/367f148b3ab780fbbae6ecc81829dd4a
**Last edited:** 2026-06-02
**Status:** Awaiting ADR
**Type:** ARD

## Summary

Classic "build fast vs. build right" dilemma. PoC is solid but TypeScript + ADK has limitations for GenAI ecosystem (evaluations, observability, multi-model support, multi-agent routing). Recommends **phased Python migration** rather than a massive architectural leap.

---

## Proposed Strategy: The Phased Transition

Rather than changing both programming language AND orchestration paradigm simultaneously, embrace smaller iterative steps. Reuse single-agent pattern for MVP before evolving to multi-agent LangGraph for v1.

### Phase 1: Current PoC (TypeScript ADK)
- **Architecture:** Single-agent, large prompt handling orchestration + tool usage
- **Limitations:** Bottlenecked by TS reviews, lacks out-of-the-box evaluations, poor multi-model support, difficult to instrument for deep observability

### Phase 2: MVP (Python ADK Stepping Stone)
- **Architecture:** Migrate ADK TypeScript → Python, **keep single-agent architecture**. Split large prompts into skills/tools but delay complex multi-agent router.
- **Tool strategy:** Wrap existing TS tools in an MCP server, or migrate tools to Python and wrap in MCP server — new Python brain calls them without rewriting business logic
- **Justification:** Syntactic translation rather than fundamental redesign. Immediately solves MVP pain points (native Python eval sets, Langfuse observability, bypass TS review bottlenecks) without LangGraph learning curve

### Phase 3: v1 Target (Python LangGraph)
- **Architecture:** Evolve Python ADK foundation into LangGraph orchestration
- **Justification:** Core logic, tools, and evals already stabilized in Python → safely introduce multi-agent router pattern and graph-based state machine

---

## The "Double Migration" Tradeoff

Two smaller migrations (TS ADK → Python ADK → Python LangGraph) instead of one giant leap. Highly strategic: migrating Python ADK → LangGraph later will be significantly easier because all integrations, prompts, and evals will already be in Python.

---

## When TS Cost Exceeds Python

The cost of staying in TypeScript exceeds Python when you need to:
- Move to multi-agent or state-machine architecture (LangGraph handles natively; TS ADK requires custom orchestration)
- Implement LLM-as-a-judge or functional eval sets (Python: ragas, pytest, native ADK evals)
- Switch models away from Gemini family
- Integrate deep observability (Langfuse auto-instrumentation vastly superior in Python)

---

## BFF Pattern — Frontend/Backend Contract

**Key decision:** Keep TypeScript as a **BFF (Backend For Frontend)** + UI router. Strip of "agentic" responsibilities. New Python brain becomes the AI reasoning layer.

**Generative UI contracts:** Extract into strict, language-agnostic JSON schema (JSON Schema or OpenAPI). Frontend only expects a specific JSON payload to render components — doesn't care whether TS/Python ADK or LangGraph generated it.

---

## MCP Strategy

**For MVP (TS ADK):** No MCP needed — direct API integrations are functional. Adding MCP would be unnecessary overhead.

**For Phase 2 (Python ADK):** Three options:
1. **Move all tools to Python** — rewrite integrations natively in Python
2. **TS MCP server** — wrap existing TS tool logic; Python agent calls functional tools we already built. Maximizes reuse of TS investments while transitioning orchestration to Python
3. **Python MCP server** — build tool registry natively in Python via MCP

**Recommendation:** For Phase 2, TS MCP server is the most strategic "bridge" — decouples AI reasoning (Python) from existing business logic (TS).

---

## Main Risks

- **Risk of postponing migration (staying in TS too long):** MVP becomes successful, product demands new features, trapped maintaining unscalable TS monolith because "don't have time to rewrite"
- **Risk of migrating too early (directly to LangGraph now):** Delay getting product to users, burn budget on infra setup, lose momentum of current working PoC. Mitigated by Phase 2 Python ADK stepping stone

---

## Strategic Recommendation

**Strangler Fig / TS BFF pattern + phased Python migration:**
- MVP: Migrate core ADK reasoning to Python (unlock native evals + observability), retain single-agent architecture
- Strictly define Generative UI JSON contracts; convert TS app into BFF + UI router with TS-based MCP server
- Post-MVP: Complex agentic workflows, multi-model requirements, advanced orchestration → trigger LangGraph transition (Phase 3)
