---
title: Logits Masking and Grammar-Constrained Generation
tags: [prompting, pattern]
summary: "Two decode-time patterns from a design-patterns book: logits masking zeroes rule-violating continuations at sampling, grammar restricts output to a context-free syntax; try-and-try-again is only cheap when the failure rate is under about 10 percent."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch02-controlling-content-style.md
---

# Logits Masking and Grammar-Constrained Generation

Lakshmanan and Hapke (O'Reilly book chapter, dated June to July 2025) present five patterns for controlling the style, format and content of model output more robustly than prompting: Logits Masking, Grammar, Style Transfer, Reverse Neutralization and Content Optimization. This page covers the first two plus the retry arithmetic that motivates them; the chapter's examples are single anecdotal outputs.

## Why not retry

Regenerating until output passes style rules is acceptable only when the failure rate is under about 10 percent (the authors' claim). Under a geometric model of attempts: when only 30% of attempts succeed, about 3.3 tries are expected and mean latency rises 230% and the 99th percentile is 13 attempts; at 90% success, about 1.1 attempts, 10% more latency and a 99th percentile of 2 (worked examples).

## Logits Masking

Step in at the sampling stage and rule out any continuation that violates the constraints by setting its logit to -inf. It fits rules that change at run time, rely on logic, come from a database, or depend on what the user enters. In the chapter's example, a zero-shot Llama 3.2 product description contained three banned words; masking removed them (beam search with 10 beams). The idea matches invalid action masking in RL. It needs logit access: the chapter says that in June 2025 Claude models gave no logit access, whereas OpenAI, Google (Flash, not Pro) and Meta models did; a client round trip for each token adds delay, so the approach mostly suits models run locally.

## Grammar

Keep output within rules that a context-free grammar notation such as BNF can express. Since no token outside the grammar can be produced, a grammar missing `>` made a Llama 3.2 arithmetic example output two sums instead of a comparison. Cautions: runaway whitespace, extra refusals when structures are nested or long, and poor accuracy if the grammar is too tight. Practices listed: prefer provider-side structured outputs (a Pydantic schema) over BNF unless the rules go beyond data format; let a tight grammar include a fallback value like `Literal["Unknown"]`; state JSON explicitly in the prompt even in JSON mode; and confirm that a provider truly constrains decoding instead of running one more LLM call afterwards to fix the output (the chapter says LangGraph structured output was such a call as of June 2025).

## The other three patterns, briefly

- Style Transfer: few-shot (1 to 10 examples) or fine-tuning (about a hundred to thousands) from input-output pairs; enforcement is only implicit.
- Reverse Neutralization: fine-tune a model to restyle neutral-form output; the authors used 200 pairs on gpt-3.5-turbo, and a hundred to a thousand is typical.
- Content Optimization: preference tuning against an evaluator. DPO over 100 preference pairs finished in around 3 minutes using an L4 GPU and 8 vCPUs (Qwen2-0.5B-Instruct, default settings); results hinge on how good the evaluator is and on the data being in-distribution.

## Limits

- No repeated runs, metrics or baselines; provider support statements are dated June to July 2025.
- The chapter's Table 2-1 shows prompting for style is brittle across six models on one question (answers retrieved February 2025), which is a single sample.

## See Also
- [[Outlines Guided Generation]] — alternative-to (finite-state masking with a precomputed index)
- [[Ctrl-G HMM Logical Control]] — alternative-to
- [[Structured Output]] — prerequisite-for
- [[Direct Preference Optimization]] — related
