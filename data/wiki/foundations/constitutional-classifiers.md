---
title: Constitutional Classifiers
tags: [foundations, infra, pattern]
summary: "Reference design for classifier guardrails — a natural-language constitution generates the synthetic training data, question and answer are judged together so coded requests are caught, and a near-free activation probe screens everything and escalates only suspicious traffic to a stronger classifier."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--03-agentic-foundations--agent-fundamentals.md
---

# Constitutional Classifiers

A classifier guardrail sits at the input and output positions of an agent's defence in
depth (see [[Agent Fundamentals]]). The constitutional-classifier design (Anthropic) has
three parts:

1. **A constitution generates the data.** Rules written in natural language are used to
   synthesise the classifier's training examples, so changing policy means editing text and
   regenerating, not re-labelling by hand — the same idea as [[Constitutional AI and RLAIF]]
   applied to a guard model rather than to the policy.
2. **Question and answer are judged together.** Judged alone, an innocuous-looking exchange
   can pass; judged as a pair, a request about "food flavourings" whose answer is a reagent
   list is recognisable as coded.
3. **Two-stage screening.** A near-free **activation probe** on the model's internals sees
   every conversation. Anything suspicious goes to a stronger classifier rather than straight
   to refusal. Because stage two catches stage one's false positives, stage one can be tuned
   to over-flag cheaply.

The two-stage shape is the general cost pattern for guardrails: a cheap high-recall screen
over all traffic, an expensive high-precision check over the flagged fraction. Classifiers
cover the input and output positions only; the execution position needs hard gates (see
[[Execution Boundaries and Guardrails]]).

## See Also
- [[Agent Fundamentals]] — instance-of (the classifier layer of agent guardrails)
- [[Constitutional AI and RLAIF]] — extends (a constitution as the source of training data, for a guard model)
- [[Input Guardrails Pipeline]] — alternative-to (rule- and model-based input screening)
- [[Execution Boundaries and Guardrails]] — extends (the execution-position controls classifiers do not cover)
