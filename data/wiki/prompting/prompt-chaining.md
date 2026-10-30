---
title: Prompt Chaining
tags: [prompting, llm, agents, concept]
summary: Decomposing a complex task into simpler prompts with fixed I/O contracts — trading a general/weak prompt for strong single-job steps wired as a pipeline or (by default) a DAG; the boundary case between prompting and harness engineering.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
---

# Prompt Chaining

## The Technique

Break a complex multi-step task into a sequence of smaller prompts, where the output of
one becomes the input of the next. Each link is simpler, individually testable, and
debuggable in isolation — when the chain produces a bad result you can identify which step
degraded rather than re-prompting the whole thing.

## Why It Beats One Large Prompt

A single prompt asking for five things tends to do all five mediocrely: attention is split,
and a failure anywhere contaminates the whole output. Five chained prompts each get the
model's full attention on one objective, and each can be evaluated against its own
criterion.

The cost is latency (serial round-trips) and token overhead (re-supplying context at each
link).

## Generality vs Strength

A single general prompt trades **strength for generality**: it attempts anything but
executes multi-step work poorly. Pushed at a multi-step job (scrape stores → invent a
product idea per store → email the owner), one agent degrades predictably: the system
prompt grows until it distracts, there is no clean way to process work items one at a
time, and a failed step has no correction mechanism — a system-prompt instruction is only
a suggestion. Splitting buys strength back.

The canonical two-step example is **document QA**: prompt 1 extracts relevant quotes into
`<quotes>` (or says none were found); prompt 2 answers from quotes plus document. XML at
the hand-off makes parsing trivial ([[Structured Output]]).

## Building a Workflow

1. Define the goal. 2. Specify ordered tasks with tools, inputs and outputs. 3. Implement
each in isolation. 4. Connect and adjust. 5. Optimize quality, latency, cost.

- **I/O contracts matter more than internals.** A step's prompt can change freely; changing
  its input or output schema forces neighbours to change.
- **First question per task: does it need an LLM?** Plain code for scraping and writes, a
  small classifier for pure classification; mix model sizes by difficulty.

| Implementation | How | Use for |
|---|---|---|
| Templated prompt | Prefix and suffix bracket the output so the completion is exactly the body | Generation |
| Forced tool call | Tool whose parameters are the output schema, forced via `tool_choice` | Extraction ([[Tool Definitions as Prompts]]) |
| Two-step with scratch work | Brainstorm with CoT, then write up only the winner | Keeping reasoning out of stored output |

If extraction fails: is the source hard even for a human (clean it)? Is the schema too big
(split it across calls)? If quality is still short: force a planning pass (`tool_choice:
"none"` for one turn), task-level [[Reflexion]] with a validator or judge, conversational
sub-agents (assistant plus user-proxy) last, and human-in-the-loop for irreversible actions.

## Topologies

| Topology | Trade-off |
|---|---|
| Pipeline A → B → C | Simplest; information not passed along is lost downstream, creating odd couplings |
| **DAG** | **Default** — each task gets what it needs directly; simple dependency reasoning |
| Cyclic | Must carry failure context back, handle retried items everywhere, cap attempts — **prefer hiding a retry loop inside a task** |

Batch for known item sets, streaming for open-ended arrivals. Brainstorm steps need
explicit diversity pressure (a run produced many near-identical ideas) and a feasibility
check. For routing, parallelization, orchestrator–workers and evaluator–optimizer see
[[Agentic Workflow Patterns]]; parallel voting is [[Self-Consistency]]. **Start with a
workflow**; move to agentic routing only when fixed topologies can't express the problem.

## Operating a Workflow

Evaluate per task before end-to-end; collect each task's real I/O as the offline test set
and optimizer training data ([[DSPy]]); run it as a regression harness before every prompt
change ([[Evaluating Prompts]]); sample production traffic for drift and A/B competing
task implementations.

## The Boundary to Harness Engineering

**When prompt chains become stateful and conditional, you have crossed into harness
territory.** A fixed linear chain is prompt engineering. Once the chain branches on
intermediate results, retries failed links, or loops until a condition holds, it is a
control flow — and that belongs to the harness/loop layer.

This is the natural escalation path: chaining is the gateway from prompt engineering to
agent architecture.

## See Also
- [[Loop Detection and the Two-Retry Rule]] <!-- auto-linked -->
- [[Iterative Harness Simplification]] <!-- auto-linked -->
- [[Harness Engineering]] <!-- auto-linked -->
- [[Prompt Templates and Variables]] <!-- auto-linked -->
- [[Structured Output]] <!-- auto-linked -->
- [[XML Prompt Structuring]] <!-- auto-linked -->
- [[Prompt Engineering]] — part-of
- [[Context Engineering]] — extends
- [[Agentic Workflow Patterns]] — extends
- [[DSPy]] — prerequisite-for
- [[Stateful Objects of Discourse]] — extends
- [[Prompting Reasoning Models]] — alternative-to
