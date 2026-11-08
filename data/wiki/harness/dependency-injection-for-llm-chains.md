---
title: Dependency Injection for LLM Chains
tags: [harness, pattern]
summary: "Pass each step of an LLM chain in as a function argument whose default is the real call, so one step can be tested against a mock while the others run and so a model swap touches one function; Lakshmanan and Hapke present it as the alternative to vibe-checking a nondeterministic pipeline."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lakshmanan-hapke-genai-design-patterns-ch06-improving-reliability.md
  - data/raw/papers/2026-11-06-lakshmanan-hapke-genai-design-patterns-ch10-composable-agentic-workflows.md
---

# Dependency Injection for LLM Chains

The problem the authors name: LLM steps are nondeterministic, hosted models change on schedules the caller does not control, and long detailed prompts are brittle across models. Portable client libraries do not make prompts portable. Their remedy (Pattern 19 in Generative AI Design Patterns, O'Reilly 2025) is ordinary dependency injection: every step is a function with a fixed signature, and the chain takes the steps as parameters.

## Mechanism

- A chain such as critique then improve is written as `improvement_chain(text, critique_fn=critique, improve_fn=improve)`, with the real LLM functions as defaults.
- A test passes a mock for one step (for example a canned critique) and calls the real other step, so only one nondeterministic component varies at a time.
- Assertions check structure, not wording: the critique has at least four suggested improvements, the chosen change appears in that list, and a line-diff check keeps the edited lines inside a small range. An LLM judge can add softer checks. The tests run before every deployment or commit; the authors frame this explicitly as the replacement for vibe checking.
- In the composable-workflow chapter the same idea underwrites independent testing and swapping of each agent in the workflow.

## Caveats

- Hand-written mocks get harder to keep faithful as the steps interact more; external tools can be mocked the same way.
- At the time of writing (2025) the authors say no GenAI framework supports this natively, with one framework coming close for prompts and tools but not for whole agents. That statement is likely dated.
- Assertions are disabled under Python's `-O` flag in production. The book gives no measured effect and no example beyond one small text-improvement chain.

## Limits

The source is a book chapter whose examples are single illustrative runs with no benchmark or ablation, so this page records a design pattern and its stated rationale, not evidence that it reduces defects.

## See Also
- [[Prompt Optimization]] — related (rerunning an optimiser after a model swap relies on the same swappable steps)
- [[Tool Design as Harness Surface]] — related
