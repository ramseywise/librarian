---
title: SelfCheck Step Verification
tags: [prompting, pattern]
summary: "Checks each reasoning step with four independent LLM calls (extract target, collect context, regenerate, compare) and uses the confidence for weighted voting; on GSM8K with GPT-3.5 and 2 solutions it lifted accuracy 71.7 to 74.3 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-miao-2023-selfcheck.md
---

# SelfCheck Step Verification

SelfCheck (Miao, Teh, Rainforth) is zero-shot step-level checking. The motivation: asking a model whether a whole chain is right almost always gets "correct"; the paper's own MathQA ablation found a direct global check at 55.0% accuracy against 50.0% for guessing (100 questions, GPT-3.5).

## Mechanism

For each step, four separate calls with no shared context: target extraction (what the step is trying to do), information collection (which earlier facts it uses), step regeneration (redo the step without seeing the original), and comparison (supports, contradicts or unrelated). Step results are combined into a solution confidence, and answers are chosen by confidence-weighted voting instead of plain majority.

## Reported results

- GPT-3.5 generating and checking, 2 solutions per question: accuracy 71.7 to 74.3 on GSM8K, 59.2 to 64.6 on MathQA, 35.8 to 38.0 on a MATH subset (self-reported). The authors say gains come mainly when only one of the two solutions is correct.
- GPT-4 as generator, 500 questions per dataset: GPT-4 checking itself changed GSM8K by -0.2 and MATH by +3.4; a GPT-3.5 checker gave +1.0 and +1.0 (self-reported). The authors suggest different models decorrelate errors, a hypothesis they did not test.
- With 10 GPT-3.5 solutions, raising the confidence threshold lifted the share of correct solutions among those passed, for example 59.4% to 82.2% on MathQA (self-reported), at the price of rejecting some correct ones.

## Cost

About four calls per step, so checking a long chain multiplies cost well beyond the original generation.

## Limits

- Math datasets only; prompts were tuned on a few MathQA training samples and reused across models.
- Few-solution settings; gains on GPT-4 outputs are mixed and small on GSM8K.
- The 98% and 100% direct-check rates are quoted from an earlier paper, not measured here.

## See Also
- [[Verification Loops]] — prerequisite-for
- [[Chain-of-Verification]] — related (isolated verification questions on a draft)
- [[Outcome vs Process Reward Models]] — alternative-to (step scores from a trained model rather than prompted calls)
- [[Self-Consistency]] — prerequisite-for (swaps the majority vote for confidence weights)
- [[SelfCheckGPT]] — related (different method: sample agreement to flag hallucinated sentences)
