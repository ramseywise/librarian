---
title: Prompt Chaining
tags: [llm, agents, concept]
summary: Decomposing a complex task into a sequence of simpler prompts where each output feeds the next — the boundary case between prompting and harness engineering.
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
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
