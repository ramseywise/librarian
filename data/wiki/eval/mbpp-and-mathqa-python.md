---
title: MBPP and MathQA-Python
tags: [eval, code, benchmark]
summary: "Austin et al. release MBPP (974 crowd-sourced short Python problems with three asserts each) and MathQA-Python (23,914 problems), and show that few-shot sampling, fine-tuning and prompt choices move solve rates for models from 244M to 137B parameters (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-austin-2021-program-synthesis-large-language-models.md
  - data/raw/papers/2026-11-07-nijkamp-2022-codegen.md
  - data/raw/papers/2026-11-07-li-2023-starcoder.md
  - data/raw/papers/2026-11-07-hui-2024-qwen2-5-coder-technical-report.md
  - data/raw/papers/2026-11-06-zhang-2023-unifying-perspectives-nlp-software-engineering.md
---

# MBPP and MathQA-Python

Austin et al. (arXiv 2108.07732) ask how well general-purpose language models synthesize short Python programs from natural language. The models are dense decoder-only Transformers from 244M to 137B parameters trained on web documents, dialog and Wikipedia, with no dedicated code files. Two datasets come with the paper:

- **MBPP**: 974 crowd-sourced problems, of which 426 were hand-edited. The prompt gives three assert statements; the program is executed against them. The paper's 500 test problems are the usual evaluation set, with 374 available for fine-tuning.
- **MathQA-Python**: 23,914 problems derived from MathQA.

The extraction describes MBPP as designed to be more literal than the competition problems in APPS (see [[Repository-Level Coding Benchmarks]] for later code benchmarks).

## What the paper found (self-reported)

Setup: 137B model, few-shot, unless stated.

- 59.6% of MBPP problems solved with 80 samples (3 asserts in the prompt, T=0.5).
- Fine-tuning on 374 problems improves most model sizes by roughly 10 points.
- On MathQA-DSL (1883 test tasks) the fine-tuned 137B reaches 83.8%; few-shot, the 137B gets 33.4% on MathQA-Python.
- Prompt examples matter: giving only the function name solves 43.2% against 58.4% with 3 examples, and one assert versus three differs by only 3 problems. Ensembling prompt seeds raises 59.6% to 66.4%.
- Sampling: a low temperature is best for a single try, a higher one wins once 10 samples are allowed, and beam search does worst because it loops.
- On 100 problems present in both the original and edited sets, hand-editing took the few-shot solve rate from 63% up to 79%.
- With hand-written adversarial tests on 50 sampled test problems the apparent solve rate falls from 66% to 58%, which the authors read as roughly 12% of counted solutions being wrong.
- Four turns of one-sentence human feedback raise problems solved from 30% to over 65% (50 edited problems).
- Few-shot execution prediction never exceeds 29% accuracy for any prompt type.
- Pre-training overlap was low: 32 of 974 problems (3.3%) had over half their lines found in the pre-training data.

## MBPP as a later benchmark

Other code-model papers report on it without the paper's few-shot setup:

- CodeGen-Mono 16.1B is evaluated on sanitized MBPP with n=100 at temperature 0.8.
- StarCoder reports 52.7% pass@1 (n=200, temperature 0.2).
- Qwen2.5-Coder base 32B scores 83.0 on MBPP and 68.2 on MBPP+; its other settings are not stated.
- Code Llama uses 3-shot greedy decoding for MBPP pass@1 and the 70B Python model has the highest MBPP pass@1 in that family.

The metric is pass@k as defined in [[HumanEval and pass@k]].

## Limits

- The programs are short and simple, and the ones models solve are the shortest and simplest.
- A task is often solved by only one or two of the 80 samples, so scores rely on many draws plus automatic checking.
- Which few-shot examples are chosen changes results noticeably (Fig 6).
- The human-feedback experiment covers only 50 problems and is preliminary, and the MathQA explanation findings are anecdotal.
- The fine-tuning optimizer, schedule, seeds and layer and width sizes are not given. The models received no safety treatment, and neither weights nor pre-training data are available.
- The later numbers above state different setups (CodeGen's sanitized MBPP at n=100, StarCoder's n=200 at temperature 0.2, Code Llama's 3-shot greedy, Qwen2.5-Coder's unstated settings), so they should not be set against the 59.6%; Zhang et al.'s survey likewise collects MBPP 3-shot figures from each model's own paper rather than a common harness.

## See Also

- [[HumanEval and pass@k]] — related (the concurrent benchmark)
- [[EvalPlus and HumanEval+]] — related
- [[InterCode]] — related (reuses MBPP)
- [[Code LLM Training Recipes]] — related (models scored on it)
