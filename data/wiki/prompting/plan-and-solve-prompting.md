---
title: Plan-and-Solve Prompting
tags: [prompting, concept]
summary: Zero-shot prompt (PS and PS+) that asks the model to devise a plan, extract variables and compute intermediate results before answering; reported on text-davinci-003 to beat Zero-shot-CoT on math sets with triggers tuned per dataset (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-wang-2023-plan-solve-prompting.md
---

# Plan-and-Solve Prompting

Plan-and-Solve (ACL 2023) targets three error types it finds in Zero-shot-CoT output: calculation errors, missing steps and semantic misunderstanding. The fix is a zero-shot trigger sentence that asks the model to plan first and then carry out the plan. PS+ adds instructions to extract the relevant variables and to compute intermediate results. Prompting is two-step on text-davinci-003: the trigger is appended after "Q: [X]. A:" to produce the reasoning, then an answer-extraction prompt is appended to read off the final answer.

## Results (self-reported)

All numbers use text-davinci-003 with greedy decoding at temperature 0, zero-shot, and report accuracy.

- Across six math datasets, PS+ averages 76.7%, Zero-shot-CoT 70.4% and PoT 73.5%. Plan-only PS averages 72.9%, which is 2.5 points over Zero-shot-CoT. The 8-shot Manual-CoT average is 77.6%.
- GSM8K (1,319 problems): PS+ 59.3 against 56.4, the smallest gain of the six. SVAMP: 75.7 against 69.9, with few-shot Manual-CoT higher at 80.3. MultiArith: 91.8 against 83.8, with PoT 92.2 and Manual-CoT 93.6.
- Last Letters: PS+ 75.2 against 70.6 for Manual-CoT. Coin Flip: 99.6 against 96.8 for Zero-shot-CoT, needing a task-specific trigger. PS+ also beats Zero-shot-CoT on CommonsenseQA and StrategyQA but stays below Manual-CoT on StrategyQA (71.2).
- Adding self-consistency (T=0.7, N=10) takes PS+ to 73.7% on GSM8K.
- Error analysis on 100 random GSM8K problems: PS+ gets 39 wrong against 46 for CoT and 43 for PS; missing-step errors fall to 7% from 12% and calculation errors to 5% from 7%, while semantic errors stay at 27%.
- On GSM8K, variable extraction alone does worse than Zero-shot-CoT (50.5 against 56.4), so the plan instruction carries weight.

## Limits

- The authors note prompt design takes effort and GPT-3 is sensitive to wording; semantic misunderstanding errors remain.
- The main paper uses only text-davinci-003, and trigger sentences are tuned for each dataset, so the PS+ numbers partly reflect choosing prompts on the test sets themselves.
- One greedy run per setting, with no variance or significance testing; the 100-problem error analysis is small and hand-labelled.
- Neither plan quality nor plan refinement is evaluated; the planning is decomposition within the text, not tool use or agentic search.

## See Also
- [[Zero-Shot Chain-of-Thought]] — prerequisite-for
- [[Chain of Thought]] — prerequisite-for
- [[Least-to-Most Prompting]] — alternative-to
- [[Task Decomposition Patterns]] — related
