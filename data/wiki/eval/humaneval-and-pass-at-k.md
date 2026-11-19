---
title: HumanEval and pass@k
tags: [eval, code, benchmark]
summary: "HumanEval is 164 hand-written Python function problems scored by unit tests, and pass@k is an unbiased estimator of the chance that at least one of k samples passes; Codex introduced HumanEval and the unbiased estimator, and later code models report against them."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-chen-2021-evaluating-large-language-models-trained.md
  - data/raw/papers/2026-11-07-nijkamp-2022-codegen.md
  - data/raw/papers/2026-11-07-li-2023-starcoder.md
  - data/raw/papers/2026-11-07-hui-2024-qwen2-5-coder-technical-report.md
  - data/raw/papers/2026-11-06-zhang-2023-unifying-perspectives-nlp-software-engineering.md
  - data/raw/papers/2026-11-08-fan-2023-large-language-models-software-engineering.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch06-reasoning.md
  - data/raw/papers/2026-11-08-xu-2022-systematic-evaluation-large-language-models.md
---

# HumanEval and pass@k

Chen et al. (Codex paper, arXiv 2107.03374) built HumanEval to measure whether a model writes functionally correct function bodies from docstrings. Each of the 164 hand-written problems has a function signature, a docstring, a body and several unit tests (7.7 on average). The paper pairs it with a sandbox for running untrusted generated code.

## pass@k

The model generates k samples per problem. A problem is solved when at least one sample clears every unit test; the score is the share of problems solved. The paper credits the metric's origin to SPoC ([[SPoC Pseudocode-to-Code]]).

The naive estimate 1-(1-p_hat)^k, computed from the single-sample pass rate, is biased and underestimates pass@k. The unbiased estimator draws n samples per problem (n=200 in the paper), counts the c correct ones, and averages over problems the quantity one minus the ratio of two binomial coefficients, C(n-c, k) over C(n, k). The paper's reference implementation returns 1.0 whenever n-c < k and otherwise a running product over `np.arange(n-c+1, n+1)`.

The paper reports that the best sampling temperature rises with k: for a 679M Codex model the best temperature is 0.2 at pass@1 and 0.8 at pass@100. Later papers therefore choose the temperature per k (CodeGen takes the best of 0.2, 0.6 and 0.8 for each k), which the CodeGen extraction lists as a limit.

BLEU is not a substitute: the Codex paper finds that correct and incorrect Codex-12B samples have heavily overlapping BLEU distributions ([[Eval Metric Interpretation Pitfalls]]).

## Reference numbers (self-reported by each paper)

Setup: HumanEval pass@1 unless stated; sampling settings differ by paper.

| Model | pass@1 | Setup |
|---|---|---|
| GPT-3 | 0% | Codex paper |
| GPT-J-6B | 11.6% | Codex paper, best over temperatures 0.2 and 0.8 (its headline bullet says 11.4%) |
| Codex-12B | 28.8% | Codex paper; pass@10 46.81, pass@100 72.31 (Table 1) |
| Codex-S-12B | 37.7% | Codex paper |
| PolyCoder 2.7B | 5.59% | Xu et al.; the best of four temperatures (0.2 to 0.8), with top-p 0.95 and 100 samples drawn per prompt; that paper reports 6.41% for GPT-Neo 2.7B and 11.62% for GPT-J 6B |
| CodeGen-Mono 16.1B | 29.28 | n=200, best of three temperatures, top-p 0.95 |
| StarCoderBase 15.5B | 30.4% | n=200, temperature 0.2 |
| StarCoder 15.5B | 33.6% | n=200, temperature 0.2; 40.8% with a file-name prefix prompt at temperature 0.1 |
| Qwen2.5-Coder-32B base | 65.9 | base model; HumanEval variant and sampling not stated |
| Qwen2.5-Coder-32B-Instruct | 92.7 | EvalPlus HumanEval (stated for the Instruct models); GPT-4o-2024-08-06 listed at 92.1; sampling not stated |

Codex-12B with 100 samples solves 72.31% (Table 1), and Codex-S-12B reaches 77.5% within 100 samples. Picking the sample with the highest mean log-probability out of 100 gives 44.5% for Codex-S-12B, against 77.5% when the unit tests act as an oracle.

The EvalPlus variant of HumanEval is covered at [[EvalPlus and HumanEval+]]. One further Codex probe: given subtly buggy code in the prompt, the model produces worse completions than it otherwise could (30-problem subset, 3 in-context examples, temperature 0.2).

## How the benchmark has aged

Zhang et al.'s survey of code language models calls HumanEval near-saturated, adding that its leaderboard has been gamed almost to the maximum. Its benchmark tables size HumanEval at 164 Python problems, MBPP at 974 and SWE-bench at 2,294. In the survey, the SWE-agent system resolves only 12.5% of real GitHub issues in SWE-bench (citing Yang et al. 2024b). The Fan et al. software-engineering survey reports that Claude 2 and GPT-4 solve 4.8% and 1.7% of the 2,294 SWE-bench tasks, and that GPT-4's zero-shot HumanEval pass@1 was 67% in the GPT-4 report but about 80% on a leaderboard accessed 24 Aug 2023, so rankings date quickly. Both are secondary reports of other papers' numbers.

Xiao and Zhu's chapter on reasoning writes the estimator as the mean over N items of one minus C(Ns-Ci, k) over C(Ns, k), and pairs it with Cons@k, which scores the majority answer among N sampled reasoning paths against the ground truth ([[Self-Consistency]]).

## Limits

- The Codex paper describes HumanEval as small (164 problems), limited to Python and to standalone functions of roughly easy-interview difficulty, and reports no confidence intervals or seeds.
- The Codex paper gives three different pass@100 figures: 70.2% in the abstract, 77.5% (Codex-S) in the introduction and Fig 1, and 72.31% (Codex-12B) in Table 1. The alignment appendix says 158 problems where the main text says 164.
- The rows come from different papers with different temperature choices, sample counts and prompts; Zhang et al. say the same of their own Table 1, which collects HumanEval 0-shot and MBPP 3-shot numbers from each model's paper rather than a common harness (so rankings between rows are weak evidence). The Qwen2.5-Coder sampling settings are not stated.
- The Codex extraction gives GPT-J-6B as 11.4% in its headline bullet and 11.6% for the best-of-temperatures setup.
- CodeGen picks the best of three temperatures per k; StarCoder's own prompt-format result shows the score depends on the prompt (the file-name prefix hurts CodeGen-16B-Mono, 28.10%).
- StarCoder and Qwen2.5-Coder report single runs without seeds or variance.
- PolyCoder's paper picks the best temperature per metric on HumanEval itself, runs each result once with no seeds or variance, and says HumanEval covers Python only.

## See Also

- [[MBPP and MathQA-Python]] — related (the other benchmark these papers report beside HumanEval)
- [[EvalPlus and HumanEval+]] — extends
- [[SPoC Pseudocode-to-Code]] — prerequisite-for
- [[Self-Consistency]] — related (Cons@k scores its majority vote)
- [[Code LLM Training Recipes]] — related (models scored on it)
- [[Fill-in-the-Middle and Infilling Code Models]] — related (HumanEval turned into an infilling benchmark)
- [[CodeT Generated-Test Reranking]] — related
- [[ODEX Open-Domain Execution-Based Code Evaluation]] — related
- [[APPS Coding Challenge Benchmark]] — related
- [[CodeXGLUE Code Understanding and Generation Benchmark]] — related
- [[Textbook-Quality Data: phi-1 and phi-3]] — related (phi-1 headline result)
- [[Early GPT-4 Probing and Planning Limits (Sparks of AGI)]] — related
- [[PolyCoder Open Multilingual Code Model]] — related (evaluated with Pass@k)
