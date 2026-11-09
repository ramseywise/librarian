---
title: Multi-Agent Context
tags: [context, context-management, llm, agents, concept]
summary: Sub-agent isolation is the highest-cost context lever — a sub-agent burns 100k tokens and returns 2k, and the discarding of its window is the feature, not a side effect.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context-engineering--notes--10-tools-and-multi-agent.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--06-multi-agent-context.md
  - data/raw/papers/2026-11-07-context-engineering-multi-agent-systems-ch02-building-multi-agent-system-mcp.md
  - data/raw/papers/2026-11-07-context-engineering-multi-agent-systems-ch06-building-summarizer-agent-context-r.md
  - data/raw/papers/2026-11-07-context-engineering-multi-agent-systems-ch10-blueprint-production-ready-ai.md
  - data/raw/papers/2026-11-08-context-engineering-multi-agent-systems-appendix-a-context-engine-reference-guid.md
  - data/raw/papers/2026-11-06-yang-2025-docagent.md
---

# Multi-Agent Context

> Isolation is the highest-cost context lever. Use it when compression is not enough.

The **Isolate** lever of [[Context Engineering]] — last of the four, because it is the most
expensive.

## Sub-Agent Architectures

Specialized agents handle focused tasks with **clean context windows**, returning condensed
summaries to a lead coordinator.

**The economics are the point.** A sub-agent may burn 100k tokens exploring a codebase and
return a 2k-token summary. The orchestrator pays 2k for work that would have cost it 100k of
its own window — and, more importantly, would have left 98k of exploration debris polluting
the window it needs for synthesis.

```
Orchestrator (holds plan, stays small)
  ├── Sub-agent A: explore subsystem X  ->  2k summary  (spent 80k internally)
  ├── Sub-agent B: explore subsystem Y  ->  2k summary  (spent 60k internally)
  └── Sub-agent C: explore subsystem Z  ->  2k summary  (spent 90k internally)

Orchestrator window: ~6k of findings, not 230k of exploration.
```

**The sub-agent's window is discarded, not merged. That discarding is the feature.**

## Orchestrator-Holds-Plan

The settled default: the **orchestrator owns the plan and the synthesis**; sub-agents own
bounded investigations.

Sub-agents should not decide overall strategy, because each sees only its slice. An agent
that explored one subsystem will **over-weight that subsystem** — it has no basis for
comparison. Cross-cutting judgment requires the window that saw all the summaries.

### What a sub-agent receives

The prompt is the entire interface.

| Gets | Does not get |
|---|---|
| Its specific task, scoped and bounded | The full conversation history |
| The minimum context needed to do it | The overall plan |
| The expected return shape | The other sub-agents' findings |

**That last exclusion is what makes isolation work — and it is also the failure mode.**

## Costs

- **Lost shared context.** Sub-agents can't coordinate, may duplicate work, or reach
  contradictory conclusions from disjoint evidence.
- **Summary is lossy.** Whatever the sub-agent doesn't include is gone. If its judgment
  about relevance was wrong, **the orchestrator never learns what it missed.**
- **Prompt is the whole interface.** An under-specified sub-agent prompt yields an off-target
  investigation, discovered only after it has burned its budget.
- **Token multiplier.** Three sub-agents spending 80k each is 240k of real tokens for 6k of
  visible output. Cheap for the *orchestrator's window*, expensive in absolute spend.

> Try **Compress** before reaching for **Isolate**. Sub-agents are the right answer for
> genuinely parallel, genuinely separable investigation — not for work that a compaction
> would have handled. See [[Context Compaction]].

## Isolation as a Security Boundary

Isolation is also a **containment mechanism**. A sub-agent processing untrusted content —
scraped web pages, user uploads, third-party API responses — has a window that gets
discarded. An injection landing in that window cannot reach the orchestrator except through
the **summary**, which is a narrow, inspectable channel.

**This only holds if the summary is treated as data, not instructions.** A sub-agent summary
interpolated directly into an orchestrator prompt is itself an injection path. See
[[Prompt Injection]].

This is the same structure as the Dual-LLM pattern: a quarantined component reads untrusted
content but cannot act; a privileged component acts but never reads raw untrusted text.

### Skills plus open network access

A high-risk combination. Skills make procedures more capable; network access makes
exfiltration possible. Together they form a data-exfiltration path that is easy to introduce
and hard to retrofit against.

A defensible default posture:

- Skills: **allowed**
- Shell: **allowed**
- Network: **enabled only with a minimal allowlist**, per request, for narrowly scoped tasks

**Assume tool output is untrusted regardless of source.**

## Tool Integration Patterns

| Level | Pattern | Context implication |
|---|---|---|
| Sequential | A → B → C, each output feeds the next | Intermediate results pile up; clear after use ([[Context Compaction]]) |
| Parallel | Independent calls, results merged | Fast; summarise at the merge |
| Conditional | Model picks the tool from the situation | Tool descriptions must be distinct enough to choose between |
| Recursive | A tool call spawns its own loop (a sub-agent) | This is isolation |

Most production agents are conditional loops with occasional parallel batches. Pipelines
and DAGs are worth it only when the order is known in advance — and then they belong in
code, not in the model's decisions ([[Harness Orchestration]]).

## Orchestration and Coordination

| Pattern | Good for | Watch out for |
|---|---|---|
| Orchestrator–workers | Research, broad search | The default |
| Pipeline (fixed specialist stages) | Repeatable draft → review → edit | Errors propagate forward |
| Debate / critique with a judge | Reducing single-model blind spots on judgement calls | Cost; agents converge on confident wrong answers |
| Shared blackboard | Long-running collaborative tasks | Write conflicts — needs schema and ownership ([[Structured Context and Schemas]]) |

**Emergence is a failure mode to monitor, not a feature to design for:** in LLM systems it
mostly shows up as agents duplicating work, echoing each other or drifting off-task
([[Context Field Theory (Speculative)]] covers the claims to the contrary).

### Inter-Agent Messages Are Context

Every hand-off is a prompt someone else will read. Give messages a schema (task,
constraints, evidence, return shape), keep them self-contained, and log them. Agents that
share no context make conflicting decisions — **pass the decisions, not just the task**
([[Shared Context Brief]]).

## A worked context engine from a 2025 book

Chapters 2, 6 and 10 and Appendix A of Context Engineering for Multi-Agent Systems describe one running example, an engine in which agents hand each other context as structured messages. The extraction notes that none of it is evaluated: the chapters give design description, a few single runs and hypothetical numbers.

- **Chapter 2 (orchestrator, researcher, writer).** The orchestrator only delegates and chains outputs; each agent has one narrow role through its system prompt. A validator agent fact-checks the writer, with the revision loop capped at two writing attempts and the validator's feedback appended to the writer's next prompt. A retry wrapper repeats a failed call up to 3 times, waiting 5 seconds between tries, and gives back None if all fail. The book's "MCP" message is just a Python dict (protocol version, sender, content, metadata) that stands in for JSON-RPC and is not the Model Context Protocol itself. The validator checks only that the dict has the four keys, and the pass decision is a substring test on the reply.
- **Chapter 6 (summarizer).** A summarizer agent run before the writer cut its input from 253 to 110 tokens (56.5%) in one example, a single paragraph and a single run. Adding it broke the writer because the researcher emits facts and the summarizer a summary, so the writer was patched to accept both. Speed and quality gains are asserted, not measured.
- **Chapter 10 (production).** Practices include enqueueing requests and returning a trace id, structured logs carrying that id, token counts before a call with a summarizer for inputs over a budget, sanitising retrieved chunks at ingestion and again at runtime, and moderating the goal before the task queue and the output before storage. The 40-50% token saving and the 85% time saving for contract review are labelled hypothetical.
- **Appendix A (reference).** A planner emits a JSON plan with step-output placeholders that an executor resolves. A registry hands each agent only its dependencies, and the researcher retrieves the top three chunks. Chunk size 400 and overlap 50 tokens are example values.

Limits and inconsistencies: the chapter 2 notebook shows one console run on one topic against a hard-coded database. The model name differs between listings (gpt-5 in one, gpt-4 in another). Retry settings differ between chapter 2 (3 tries) and the appendix (up to six with exponential backoff). Business-value claims (return on investment, trust, a knowledge moat) are assertions without evidence.

## Dependency-Ordered Documentation Agents

DocAgent, a 2025 code-documentation system, orders work by dependency so each component is documented using only the docs of what it directly depends on, not an ever-growing transitive context. A navigator builds a dependency graph, condenses cycles, and sorts topologically, so callees are documented first and methods before their class; a Reader, Searcher, Writer and Verifier run under an Orchestrator. On 366 components from 9 Python repos with a GPT-4o judge, a random-order ablation lowered helpfulness from 3.88 to 3.44 and the existence ratio from 94.64% to 86.75% (self-reported). Gains depended on the backbone (3.88 against 2.95 for a single-shot chat baseline with one model; 2.35 against 2.16 with a 34B open model).

Limits: one small Python set, no repeats or variance; the extraction notes that table count columns do not reproduce the reported ratios and that prose values (3.69, 2.39) differ from table values (3.88, 2.35); context budgeting is done by truncation.

## See Also
- [[Memory as Context]] <!-- auto-linked -->
- [[Shared Context Brief]] <!-- auto-linked -->
- [[Why Context Is Finite]] <!-- auto-linked -->
- [[Context Engineering]] — related (part of)
- [[Tool Design as Context Engineering]] — related
- [[Context Compaction]] — alternative-to
- [[Prompt Injection]] — related (mitigates)
- [[Cognitive Tools]] — extends (verifier sub-calls as bounded isolation)
- [[Harness Orchestration]] — extends
- [[Context Window Budgeting]] — related
- [[Task Decomposition Patterns]] — instance-of (spatial isolation via worktrees)
- [[Protocol-Driven Multi-Agent Collaboration]] — instance-of (externalized plan state and isolation)
- [[Agent Primitives Latent Composition]] — related (KV-cache messages between agents)
- [[Diversity Collapse in Multi-Agent Ideation]] — related
- [[LatentMAS and RecursiveMAS Latent Handoff]] — instance-of (latent handoff)
