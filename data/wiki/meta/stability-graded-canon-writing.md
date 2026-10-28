---
title: Stability-Graded Canon Writing
tags: [meta, llm, pattern]
summary: "When writing a conventions canon for agent design, rank gaps by the damage a wrong default does, write emerging topics at the level of their settled vocabulary (levers, taxonomy, threat model) rather than their churning specifics, promote project findings only after they survive three implementations, and wire the canon into every repo's Refs: line or it is never read."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-research-B-topic-canon.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-19-research-B-topic-canon.md
---

# Stability-Graded Canon Writing

A research pass surveyed four knowledge stores (global refs, a code-gen payload, a
playground repo's docs, and a readings folder) to define a topic canon for building
autonomous agents. Its durable output is less the topic list than four rules for *how* to
write such a canon so it neither ages badly nor goes unread.

## 1. Rank gaps by damage, not by size

Coverage gaps were ranked on one question — *how much damage does the absence do?* —
weighted by three factors:

- **Is a wrong default unrecoverable?** Security is the only gap whose failure mode is a
  breach rather than a bad result, so it ranked first despite being small.
- **Is the gap absent from every store**, or only thin in one?
- **How often is the topic touched?** Sandboxing was absent but rarely needed, so it sank
  to the "thin but recoverable" tier.

The resulting load-bearing tier was: agent security, context engineering and compaction,
tool design, MCP, and failure handling and recovery. MCP was the sharpest finding — zero
coverage across a 30-file code-gen payload that already emitted A2A, so the two-layer
stack was exactly half covered. "Not gaps" were listed explicitly (RAG, HITL, evaluation,
fine-tuning) so that nobody would invest there.

## 2. Write each topic at the level that has settled

Each topic was graded settled, settling, emerging, or contested, and the grade decides how
prescriptive the writing is:

| Status | Write | Do not write |
|---|---|---|
| Settling vocabulary, vendor-specific mechanics (context engineering) | the four levers: write, select, compress, isolate | a specific compaction ladder |
| Settled taxonomy, contested implementation (agent memory) | the episodic/semantic/procedural taxonomy | a backend prescription |
| Explicitly unstable standard (OTel GenAI conventions) | the span *shape*, with the doc dated | pinned attribute names (most `gen_ai.*` attributes carry Development stability badges and can change without a major version) |
| Out of the standard's scope (eval scoring in OTel) | a local eval schema now | nothing — don't wait for a standard |
| Unsettled, high stakes (injection defence) | the boundary and threat model: what has access to what | a defence recipe |
| Local invention that has held up (layered guardrails) | the convention, labelled as *ours* | a claim that it is an industry standard |
| Frontier (dynamic fan-out to hundreds of sub-agents) | — | anything canonical |

The rule is to write the part that will still be true in a year and date everything else.

## 3. Promote findings to conventions only after three implementations

Project repos hold findings: decisions and invariants, not command catalogues. A finding
becomes a convention once it has survived three independent implementations. A five-layer
safeguards model qualified because it held across ADK, LangGraph, and TypeScript builds.
Promotion also splits contract from instance. A grader *interface* and a gate *ladder
shape* were promoted. The grader implementations and per-gate thresholds stayed in the
project.

## 4. Make the canon load-bearing through the `Refs:` line

A new conventions file that no session loads is decorative. The mechanism proposed was a
`Refs:` line with three parts in every agent repo's `CLAUDE.md`:

```
Refs: python.md, logging.md                       # stack
      agent-architecture.md, agent-safety.md, ... # agent conventions (tooling-agnostic)
      langgraph.md                                # framework binding
```

Without that line the `agent-*` refs get written once and never read.

## See Also
- [[Friction Promotion Ladder]] — related (promotion by recurrence, applied to workflow rules)
- [[Documentation Boundary — Machine vs Human Docs]] — related (where conventions vs findings live)
- [[Capability Runtime-Coupling Tiers]] — related (the sibling capability-parity research pass)
- [[Context Engineering]] — related (the largest load-bearing gap)
