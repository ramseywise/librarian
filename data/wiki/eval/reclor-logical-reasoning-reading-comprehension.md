---
title: ReClor Logical Reasoning Reading Comprehension
tags: [eval, reference]
summary: "ReClor is 6,138 GMAT and LSAT logical reasoning questions with an EASY split (solvable from the options alone) and a HARD split; fine-tuned models scored about 75% on EASY and about 30% on HARD in the authors' runs, showing biased options can inflate scores (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-yu-2020-reclor.md
---

# ReClor Logical Reasoning Reading Comprehension

Yu, Jiang, Dong et al. (ICLR 2020) built a reading comprehension dataset from exam logical reasoning questions, and split its test set to show whether models reason or exploit answer-option biases.

## Construction

6,138 GMAT and LSAT questions with four options (after deleting one wrong option), split 4,638 train, 500 validation and 1,000 test. The **EASY set** is the test items that a model seeing only the options gets right under all four random seeds, pooled over five base models (GPT and GPT-2 alongside BERT-base, XLNet-base and RoBERTa-base); the **HARD set** is the rest. That gives 440 EASY and 560 HARD items. Guessing right under four seeds has a 0.39% chance (25% each). Correct options run a little longer than wrong ones (23.06 words against 21.82 on average).

## Results

All numbers are the paper's own (self-reported), on the test set with input of context, question and answer unless stated.

- BERT, XLNet, RoBERTa, GPT and GPT-2 fine-tuned on ReClor only: about 75% on EASY and about 30% on HARD.
- RoBERTa-large fine-tuned on RACE first and then ReClor: 65.1% overall, above graduate students at 63.0%; on HARD it scores 54.3% (40.0% without RACE) against 57.1% for the students. XLNet-large without RACE: 56.0 overall, 75.7 EASY, 40.5 HARD. BERT-large: 54.5 with RACE, 49.8 without.
- Ten graduate students on 100 sampled test questions: 63.0 overall, 57.1 EASY and 67.2 HARD.
- Options only: RoBERTa-large scores 43.2 overall, 69.5 on EASY and 22.5 on HARD. Adding the question gives little; adding the context gives a large gain.
- On HARD, models score lower on strengthen, weaken and role questions, and higher on conclusion, main-point and match-structure types.

## Limits

- The human EASY and HARD gap (57.1 against 67.2) comes from 10 students on 100 questions, which the authors attribute to the small sample.
- The extraction notes that the split is defined by 2019-era option-only models, so it depends on the models chosen.
- No LLM prompting or few-shot results; no variance across seeds for the input ablation.

## See Also
- [[RuleTaker]] — related (another test of logical reasoning with fine-tuned encoders)
- [[Functional Benchmarks and the Reasoning Gap]] — related
- [[Math Word Problem Benchmarks]] — related (a similar shortcut finding)
