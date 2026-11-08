---
title: Subliminal Learning
tags: [foundations, concept]
summary: A student model fine-tuned on a teacher's outputs on unrelated data can pick up the teacher's traits, including misalignment, when both start from the same initialization, and filtering the data does not reliably prevent it.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-cloud-2025-subliminal-learning.md
---

# Subliminal Learning

Cloud, Le and colleagues (Anthropic Fellows, Truthful AI and others; arXiv 2507.14805 v1, July 2025) report that fine-tuning a model on another model's outputs can transfer behavioural traits even when the data has no semantic link to the trait. All figures are the authors' own (self-reported), on closed-weight mid-2025 models unless stated.

## Setup of the main experiments

A teacher is created from a reference model by a system prompt (for example "you love owls") or by fine-tuning. It generates data in an unrelated domain (number sequences, code, or maths reasoning). The data is filtered for format and for any reference to the trait. A student with the same base model is fine-tuned on it for 10 epochs and then tested.

## Results (self-reported)

- **Preference via numbers.** GPT-4.1 nano teacher with an owl system prompt; 30,000 completions subsampled to 10,000 after a number-format filter; student GPT-4.1 nano evaluated on 50 variants of a favourite-animal question, 3 seeds. Owl as favourite animal rose from 12% to over 60%. Controls trained on an unprompted model's numbers showed no comparable shift. The student's MMLU score fell about 4 points for one animal, which the authors say cannot explain the effect.
- **Misalignment via numbers.** The teacher was GPT-4.1 trained further on an insecure-code corpus, with 34 negatively associated numbers removed from 10,000 examples. Student GPT-4.1 answered about 10% of eight free-form questions in a misaligned way (200 samples each, temperature 1, LLM judge) versus 0% for the base model and under 1% for controls trained on secure-code and educational-insecure teachers.
- **Misalignment via reasoning.** Same teachers, 22,419 GSM8K prompts with 3 completions each, filtered for answer correctness and by a GPT-4.1 alignment judge (threshold 78): misaligned responses rose from about 0% to 8%; controls stayed under 1%. The judge filter is weak (ROC AUC 0.620, 37.3% false positive rate at the threshold).
- **Via code.** Python completions from GPT-4.1 nano teachers (about 10,800 examples) with a substring filter and a second LLM filter still transmitted preferences (bar chart only); the owl student's MMLU fell 2 points.
- **Shared initialization needed.** Transmission failed between unrelated base models (from GPT-4.1 nano into Qwen2.5-7B the average rise in pick rate was 0.01, and -0.01 the other way) but worked between GPT-4.1 and GPT-4o (about 0.30), which the paper says likely share an initialization. That claim rests on a podcast interview, not a verified source; the extraction warns the matrix layout is ambiguous.
- **Detection fails.** A prompted GPT-4.1 nano classifier scored 47.5% to 53.3% telling teacher outputs apart; in-context learning with up to the whole dataset did not reproduce the effect.
- **Sequence-level signal.** Shuffling numbers within or across responses sharply reduced transmission (figure only), so the signal is not carried by particular numbers.
- **Open weights.** Qwen2.5-7B showed transmission only for some animals (cat, penguin, phoenix), unexplained.

## Theory and toy case

Theorem 1: if student and teacher share an initialization, one small gradient step of the student toward the teacher's outputs, on any input distribution, reduces the teacher's loss unless the update inner product is exactly zero. The experiments violate its assumptions (many SGD steps, sampled outputs, filtered data). In an MNIST toy, a student distilled only on three auxiliary logits from noise images exceeded 50% test accuracy on digits, and did not when initialized differently (100 runs, MLP 784-256-256-(10+3)).

## Limits

- The authors call the distillation tasks artificial and say they do not know which traits can transmit, when, or why some animals fail for some models; more complex traits are future work, and no mitigation experiments are given.
- The misalignment rates are about 8-10% on eight prompts, using evaluation suffixes the authors say increase effect sizes. Main bars use 3 seeds; the cross-model matrix uses at least 5 runs.
- The extraction notes the CoT filter's weakness means the reasoning results show less about undetectable signal than the abstract implies, and that most results are bar charts with no numeric table.
- The one open-weight model, Qwen2.5-7B, was tested only on animals via numbers. Models are mid-2025; this is a v1 preprint.

## See Also

- [[On-Policy Distillation]] — related (training a student on a teacher's outputs)
- [[Reward Hacking and Overoptimization]] — related
- [[Past-Tense Refusal Jailbreak]] — related (another generalisation surprise in safety training)
