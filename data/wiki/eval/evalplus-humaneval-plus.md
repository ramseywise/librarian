---
title: EvalPlus and HumanEval+
tags: [eval, code, benchmark, conflict]
summary: "EvalPlus grows HumanEval's tests about 80x by mutating ChatGPT-written seed inputs and checking against re-implemented ground truths; across 26 LLMs pass@k falls by up to 19.3-28.9% and 18 of 164 original reference solutions turn out defective (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-liu-2023-your-code-generated-chatgpt-really.md
  - data/raw/papers/2026-11-08-fan-2023-large-language-models-software-engineering.md
---

# EvalPlus and HumanEval+

Liu et al. argue that the tests in HumanEval are few and weak, so wrong LLM-written code can pass. Their framework **EvalPlus** builds stronger tests, and the augmented benchmark is **HumanEval+**.

## Mechanism

1. ChatGPT writes roughly 30 seed inputs for each HumanEval task.
2. Type-aware mutation runs on the seeds under a budget of one hour, yielding about a thousand extra inputs.
3. Hand-written input contracts discard invalid inputs (83 of the 164 tasks have one).
4. Each LLM program is compared with a re-implemented reference solution (differential testing).
5. Optionally, a greedy set cover over branch coverage, mutants killed and other LLMs' samples killed shrinks the suite to HumanEval+-Mini.

Scoring uses unbiased pass@k; **pass@1\*** is pass@1 with greedy decoding.

## Results (self-reported)

Setup: 26 LLMs, HumanEval versus HumanEval+, 200 samples per temperature and the best temperature per k, unless stated.

- pass@k falls by up to 19.3-28.9% depending on k.
- Greedy pass@1\*: GPT-4 88.4 to 76.2; ChatGPT 73.2 to 63.4.
- On HumanEval+ pass@1\*, two open 34B CodeLlama fine-tunes overtake ChatGPT (Phind 67.1 and WizardCoder 64.6, ChatGPT 63.4), but not on plain HumanEval, where ChatGPT ties WizardCoder at 73.2 and Phind trails at 71.3. A ranking can therefore flip.
- Tests per task grow about 80-fold on HumanEval+. HumanEval+-Mini averages 16.1 tests per task (47x fewer) and shows nearly the same pass@1\* drop, per leave-one-out validation.
- Of the 164 original reference solutions, 18 (11%) are defective: five miss an edge case, ten have faulty logic and three are too slow.
- Small k favours a low sampling temperature and large k a higher one; the best temperatures stay mostly the same after augmentation.

## How a survey cites it

A software-engineering survey (Fan et al., mid-2023) reports a drop in HumanEval pass@k of up to 15% for 14 popular LLMs once generated tests are added including GPT-4 and ChatGPT, and treats it as evidence that original test suites give false positives. It recommends strengthened test suites, and reports that GPT-4's zero-shot HumanEval pass@1 was 67% in its technical report while a later leaderboard showed about 80%, so rankings go stale quickly. The 15% figure is below the 19.3-28.9% above (26 LLMs) and is flagged as an unresolved conflict.

## Limits

- Only HumanEval is augmented; the authors name MBPP and other benchmarks as future work.
- To save time and cost, GPT-4 ran greedy only and ChatGPT ran greedy plus temperature 0.8; CodeGen2-16B came from an unfinished checkpoint, greedy only.
- Suite reduction was checked on a subset of models.
- No seeds, intervals or significance tests appear, and it is unclear whether the quoted reductions are relative or absolute.
- The reference solutions were re-implemented by hand and not formally verified, which the authors list as future work.

## See Also
- [[AlphaCode Sample, Filter and Cluster]] — related (cited as a benchmark with the same weak-test limitation)
- [[PIE Performance-Improving Edits Benchmark]] — related
- [[InterCode]] — related
- [[ODEX Open-Domain Execution-Based Code Evaluation]] — related (one random test overstates pass@1 when a problem has three or more tests)
- [[HumanEval and pass@k]] — prerequisite-for
