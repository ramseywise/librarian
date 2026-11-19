---
title: Verifier Reranking for Math Word Problems
tags: [llm, reasoning-and-planning, pattern]
summary: "Cobbe et al. (2021) introduce GSM8K and train a separate verifier on final-answer correctness to pick the best of 100 sampled solutions; a 6B verifier slightly beats a finetuned 175B generator, roughly a 30x model-size gain (self-reported), at the cost of false positives and over-search."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-cobbe-2021-training-verifiers-solve-math-word.md
---

# Verifier Reranking for Math Word Problems

Cobbe et al. (2021) ask whether training a verifier to rank sampled solutions improves multi-step grade-school maths beyond finetuning a generator. They hypothesise that checking a solution is easier than producing one and keeps options open, so verifiers should gain more from extra data and model size. All numbers below are self-reported.

## Dataset

GSM8K: 8.5K grade school math questions with natural-language solutions, annotated with calculator calls. Re-solving a subset suggests fewer than 2% of problems contain breaking errors (the extraction also quotes a 1.7% estimate). Repairing calculator bugs lifted verification test performance by roughly 1% with the full training set.

## Method

1. Finetune GPT-3 models as generators on GSM8K.
2. Sample 100 completions per training problem and label each by final-answer correctness.
3. Train a verifier on those labels; it starts from the generator's weights and adds a scalar value head, with the language-modelling loss kept in training. Token-level verifiers outperformed solution-level ones.
4. At test time, sample 100 completions at T=0.7 and return the verifier's top-ranked one.

## Results

- On the full GSM8K training set, a 6B generator with a 6B verifier edges past a finetuned 175B model; the authors equate that boost with a 30x larger model, and say verifiers scale better with data. Setup: 100 completions per test problem.
- Small training sets give verification no benefit; it pays off only once the data is large enough.
- Verifier test performance rises with the number of completions up to 400 and then declines. For majority voting among the best-ranked completions, the best pool is the top 3-5 out of 100 samples, and about the top 30 out of 3,200.
- Finetuning a 6B model to emit the answer without intermediate steps drops accuracy drastically. The authors' naive log-linear extrapolation puts finetuning alone at about 10^16 parameters for 80% (a claim).
- More finetuning epochs sharply worsen test@100 (solved at least once in 100 samples at T=0.7) while test@1 keeps improving, so the generator that produced verifier training data got 2 epochs.
- A larger generator matters more than a larger verifier. The joint LM loss helps, and dropout (0.2) acts as a strong regulariser for both finetuning and verification.

## Relation to later practice

Since the verifier is trained on final-answer labels, it can be read as an outcome-level signal in the sense of [[Outcome vs Process Reward Models]] (an inference, not the paper's wording). [[Minerva Quantitative Reasoning]] compares majority voting, as in [[Self-Consistency]], against log-likelihood reranking on MATH.

## Limits

- Verifier labels come from final-answer correctness only, so flawed reasoning that reaches the right answer produces false positives.
- Sampling more candidates eventually turns up adversarial solutions that deceive the verifier.
- Calculator implementation bugs make the reported numbers a slight underestimate (under 1% in most experiments). The dataset may hold subtle errors beyond the breaking-error estimate.
- The 175B verification result is a single run, and absolute accuracy figures appear only in figures. Example solutions in the appendix were slightly cherry-picked.

## See Also
- [[Outcome vs Process Reward Models]] — prerequisite-for
- [[Self-Consistency]] — alternative-to
- [[MATH Dataset]] — related (the harder dataset the paper cites as motivation)
- [[Math Word Problem Benchmarks]] — related
- [[GSM-Symbolic]] — related (a later variation of GSM8K)
