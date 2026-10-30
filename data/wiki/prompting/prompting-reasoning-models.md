---
title: Prompting Reasoning Models
tags: [prompting, llm, pattern]
summary: Reasoning models do chain-of-thought natively, so prompts shift from how to think to what to achieve — state goals and constraints, drop manual CoT (it can degrade instruction-following), escalate effort gradually against an eval, and never treat the visible thinking as a faithful audit trail.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--07-prompting-reasoning-models.md
---

# Prompting Reasoning Models

Reasoning models spend **test-time compute** on hidden or summarized thinking tokens
before answering. More thinking usually means better answers on hard tasks, at more
latency and cost — controlled by an **effort or budget** setting, not by prompt wording.
The [[Chain of Thought]] scaffolding written for standard models is redundant at best:
explicit step-by-step prompting has been shown to *degrade instruction-following* in
reasoning models (*The Pitfalls of Reasoning for Instruction Following*, 2025). Model
behaviour here moves fast; treat specifics as dated.

## Do / don't

| Do | Don't |
|---|---|
| State goal, constraints and output format at a high level | Prescribe the reasoning steps |
| General nudges for more effort ("consider several approaches") | Bolt on "Let's think step by step" |
| Delimit inputs; specify the format explicitly | Leave format to chance — formatting drift is common |
| Few-shot **only** for style/format the model gets wrong | Pad with examples by default |
| Ask it to verify its work before finishing | Trust reasoning because it was long |
| Explicit quality modifiers when you want ambition | Expect "above and beyond" unasked |

With extended thinking, high-level instructions beat prescriptive ones — read the thinking,
then steer. Few-shot examples may include thinking blocks to show reasoning *style*. In
agent loops, interleaved thinking between tool calls lets the model reflect on each result.

## Escalate gradually (hybrid models)

1. Thinking off; evaluate. A manual CoT prompt is a cheap middle step.
2. If failures look like reasoning failures, enable thinking at low effort.
3. Escalate to medium, then high, **only while eval scores keep improving** ([[Evaluating Prompts]]).
4. Use examples to fix style and format, not reasoning.

Optimize accuracy first, then latency and cost.

## Where they earn their cost

Put the reasoning model in the reasoning-heavy *module*, not the whole app: planners in
orchestrator–worker agents, agentic RAG routing, judges that must reason, large codebases
and scientific work, and writing prompts for other models ([[Prompt Optimization]]).
Simple extraction, classification and rewriting rarely need one.

## Failure modes

| Issue | Mitigation |
|---|---|
| Overthinking easy tasks, underthinking hard ones | Be specific; route only hard subtasks; tune effort |
| Mixed languages, repetition, format drift | Unambiguous instructions, explicit format, post-validation |
| Instruction-following degrades with explicit CoT | Drop manual CoT; curated examples; self-reflection |
| **Unfaithful reasoning** — visible CoT need not reflect what drove the answer (*Reasoning Models Don't Always Say What They Think*, 2025) | Don't use thinking text as an audit trail or sole safety monitor; evaluate outputs |
| Weaker tool calling in some open models | Test parallel and multi-step tool use explicitly |
| Sampling parameters fixed or rejected | Control with effort ([[Sampling Parameters]]) |

## Prompting deep-research agents

Runs are slow and expensive, so get the prompt right first time: give a plan and be
specific about scope, period and trusted sources; **answer its clarifying questions
thoroughly** (the cheapest steering point); supply precise keywords (they become search
queries); use clear task verbs (*compare*, *recommend*, *report*); specify the report
format; upload documents you already have; and verify the sources — citation errors,
domain bias, date sensitivity and paywalls are known weaknesses. Use deep research only
for multi-source, time-sensitive synthesis.

## What doesn't change

Still document completion; not psychic (smarter models don't fill missing context); easily
distracted, and more so when reasoning over everything; the rendered prompt must be
decipherable by a human; it must be led — on goals now rather than steps. Public
benchmark scores saturate and leak into training data, so they don't predict your task:
build your own eval.

## See Also
- [[Chain of Thought]] — supersedes (for reasoning-model endpoints, manual CoT is replaced by effort settings)
- [[Sampling Parameters]] — extends
- [[Evaluating Prompts]] — prerequisite-for
- [[Prompts as Document Completion]] — extends
