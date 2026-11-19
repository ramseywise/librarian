---
title: Minerva Quantitative Reasoning
tags: [llm, pretraining-and-data, reference]
summary: "Minerva is PaLM 8B/62B/540B continued-trained on 38.5B tokens of arXiv and math web pages and evaluated with chain-of-thought prompts and majority voting; 540B with 64-sample voting reaches 50.3% on MATH (self-reported), with a measured false-positive rate that grows with problem difficulty."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-lewkowycz-2022-solving-quantitative-reasoning-problems-language.md
---

# Minerva Quantitative Reasoning

Lewkowycz et al. (2022) ask whether a model given further training on mathematical and scientific text can answer college-level quantitative questions in natural-language steps, without calculators or other tools. Minerva takes PaLM decoder-only models (8B, 62B, 540B) and trains them further with the autoregressive objective on 38.5B tokens of math web pages and arXiv, plus a little general text, in a dataset that keeps mathematical notation. Evaluation uses few-shot chain-of-thought prompts with either greedy decoding or **maj1@k** (sample k answers per problem and keep the most frequent one), with final answers checked by SymPy equivalence. See [[Continued Pretraining for Domain Adaptation]] for the general technique.

## Results (all self-reported)

| Benchmark and setup | Result |
|---|---|
| MATH, 4-shot, 540B, maj1@k with k=64 | 50.3% (prior SOTA 6.9%) |
| MATH, 540B greedy | 33.6% (PaLM 540B 8.8%) |
| MATH, 62B greedy / maj1@k k=256 | 27.6% / 43.4% |
| MATH, 8B greedy | 14.1% (PaLM 8B 1.5%) |
| GSM8k, 540B maj1@k k=40, no calculator, Wei et al. prompt | 78.5% (published SOTA 74.4%) |
| MMLU-STEM, 540B maj1@k k=16 | 75.0% (Chinchilla 54.9%) |
| OCWCourses (272 undergraduate STEM problems), 540B k=64 | 30.8%; greedy 17.6% |
| National Math Exam in Poland, May 2022 | 62B 57%, 540B 65% |

Other findings:

- For Minerva 62B on MATH, majority voting outperformed reranking by log-likelihood (scored by exact string match: 23.8% for log-likelihood 1@k, 21.8% pass1 at T=0.6, 26.5% pass1 at T=0). Voting levels off sooner than pass@k, reaching 97% of its large-k accuracy by k=64 on MATH and k=16 on GSM8k.
- The continued training is what helps: few-shot MATH for the 8B model rises from 1.5% to 14.1%. Finetuning Minerva 8B on the MATH training set adds nothing (13.4, 12.9, 13.0%), whereas PaLM 8B improves to 4.4-5.6%.
- The 540B model saw only 26B tokens of continued training, against 164B for the 8B and 109B for the 62B, so it is highly undertrained relative to them and is still best.
- Among 201 samples where the 62B succeeded and the 8B failed (restricted to a confident majority, top answer with at least 15% of votes), 82 of the 8B failures were reasoning errors and 70 were calculation errors.
- On plain arithmetic the 540B model exceeds 80% for 10-digit addition and 20% for 18-digit addition.

## False positives

Because only the final answer is checked, a wrong derivation can score as correct. In a manual inspection of 100 random MATH questions (20 per level) with 62B zero-temperature answers, the estimated false-positive rate is 8% on average and 30% at level 5. 62B pass@256 on MATH is 84.5%, but about 30% of samples that fail majority vote yet pass at pass@k are false positives, so the corrected estimate is above 68%. The same final-answer-only labelling is the weakness named in [[Verifier Reranking for Math Word Problems]].

## Limits

- The model's reasoning cannot be checked automatically, and false positives rise with difficulty.
- No calculator or Python tools; little control over which capabilities the model acquires.
- Compared with the 8B and 62B, the 540B model is undertrained. No ablation removes LaTeX from the training text.
- Single runs, no seeds or intervals. Contamination was examined only through BLEU on 100 MATH problems.
- The extraction gives no setup for the Polish exam beyond the exam name and date.

## See Also
- [[MATH Dataset]] — prerequisite-for (the main benchmark)
- [[Math Word Problem Benchmarks]] — related
- [[Self-Consistency]] — prerequisite-for (maj1@k is majority voting)
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Verifier Reranking for Math Word Problems]] — related (GSM8k's source)
- [[MMLU, C-Eval and CMMLU Knowledge Exams]] — related (MMLU-STEM)
