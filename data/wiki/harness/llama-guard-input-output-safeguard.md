---
title: Llama Guard
tags: [harness, concept]
summary: "Llama Guard is a Llama2-7b model instruction-tuned to label user prompts or model responses safe or unsafe against a taxonomy supplied in the prompt, so the taxonomy can be changed by prompting or light fine-tuning (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-inan-2023-llama-guard.md
---

# Llama Guard

Inan, Upasani, Chi et al. (2023, arXiv 2312.06674) ask whether an instruction-tuned LLM can act as an input-output safeguard that classifies user prompts and model responses separately against a configurable taxonomy. They hypothesise that a model fine-tuned with the guidelines in its input performs on its own taxonomy and can be moved to other taxonomies by zero-shot or few-shot prompting, or by more fine-tuning.

## Mechanism

A Llama2-7b model is tuned to answer safe or unsafe and to name any violated category codes. Its input prompt bundles the guidelines, the task type (prompt or response), the conversation and the answer format. Rewording the instruction toggles between **prompt classification** (judging user messages) and **response classification** (judging agent messages), which are two moderation tasks served by a single model. The training set has 13,997 annotated prompt/response pairs from a red team, derived from Anthropic harmlessness prompts, and uses an augmentation that drops categories. The final verdict is the maximum of the per-category scores (Eq. 1). Training ran for roughly one epoch, 500 steps, on 8xA100 80GB at sequence length 4096.

## Results (self-reported, AUPRC unless stated)

- On the authors' own test set for prompts, Llama Guard prompted zero-shot with its target taxonomy scores above the OpenAI and Perspective APIs.
- On ToxicChat, prompted zero-shot with the ToxicChat taxonomy and never trained on it, it outscores every baseline, at 0.626. Plain Llama2-7b zero-shot gave only malformed outputs and counts as 0.
- On the OpenAI Mod dataset, zero-shot with the OpenAI taxonomy, it lands slightly under the OpenAI API, which was trained for that data. Few-shot prompting (the taxonomy description plus two to four worked examples for each category) puts it above the API.
- Fine-tuning on ToxicChat at 10, 20, 50 and 100% of the training data (values read off Fig 3): beginning from Llama Guard, about 20% of the data matches Llama2-7b trained on all of it.
- By category on the own test set, the OpenAI Mod API has low prompt AUPRC for Guns and Illegal Weapons.
- The appendix gives precision, recall and F1 at threshold 0.5 against GPT-4 for prompts and responses on the own test set.

## Terms

**1-vs-all** means one prediction task per category with only that category positive. **1-vs-benign** is the same but drops positives from other categories, leaving only benign negatives.

## Limits

- Its common-sense knowledge is bounded by its training and pretraining data, so some judgements will be wrong.
- The tuning data and most of the pretraining data are in English; other languages come with no guarantee.
- Policy coverage is not claimed to be complete, and all labels come from one in-house red team.
- Prompt injection may work against it, and used as a chat model it can emit unsafe language since it has no chat safety tuning.
- The extraction notes: the own test set shares taxonomy and data process with training, making the 0.945 figure a ceiling; baselines evaluated off-policy use 1-vs-benign, which may flatter them.
- Azure and GPT-4 yield no AUPRC, so the main comparison leaves them out.
- The extraction notes: no optimizer, schedule, seeds or exact prompt wording are stated, and variance is not reported.
- The extraction notes: the setup is dated: six categories from 2023 on a Llama2-7b base.

## See Also
- [[Execution Boundaries and Guardrails]] — prerequisite-for
- [[Input Guardrails Pipeline]] — related (a guard model is one stage such a pipeline can use)
- [[Constitutional Classifiers]] — alternative-to (a trained input-output classifier approach)
- [[Jailbreak Rapid Response]] — related (adapts an input guard after seeing attacks)
- [[Prompt Injection]] — related
