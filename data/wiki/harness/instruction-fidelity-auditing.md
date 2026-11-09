---
title: Instruction Fidelity Auditing
tags: [harness, agents, pattern]
summary: "An auditor agent compares a handoff's output with the original instruction and returns pass or fail, with persistent anchors and a fractal reflection template as companions; a design from a pattern book with no measurements."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch06-explainability-compliance-agentic-patterns.md
  - data/raw/papers/2026-11-08-agentic-architectural-patterns-ch13-use-case-single-agent-loan-processing.md
---

# Instruction Fidelity Auditing

In a multi-agent chain the original instruction can drift as it is paraphrased across handoffs. Chapter 6 proposes three cooperating patterns.

## Mechanisms

- **Instruction Fidelity Auditing:** an auditor agent receives the original instruction and the latest output and returns a PASS or FAIL verdict. On FAIL the supervisor reverts to the previous state. Auditing every step costs too much, so it is applied only at high-risk handoffs.
- **Persistent Instruction Anchoring:** the instruction is stored as tagged anchors that are re-inserted into the context at each handoff, so later agents see the source text rather than a summary.
- **Fractal Chain-of-Thought:** the agent writes a thought, runs a self-correction check that ends in PASS or FAIL, then an action or revision, and repeats in a bounded loop. Variants add temporal re-grounding, a dynamic context window and reflection between agents.

The book advises combining two or three patterns rather than all of them. Chapter 13 applies the fractal prompt to a single loan-processing agent with a three-pass loop and a thinking budget.

## Limits

- No measurement of drift or of the auditor's error rate; the auditor is itself a model and can pass a faulty output.
- In chapter 13 the mock tools are lenient (the compliance tool always passes), success criteria are not enforced in code, a start function is undefined, and the text mentions an explainability output the code does not contain.

## See Also
- [[Verification Loops]] — related
- [[Self-Refine]] — related (a single-agent critique loop)
- [[Agentic Coordination Patterns Catalog]] — prerequisite-for
