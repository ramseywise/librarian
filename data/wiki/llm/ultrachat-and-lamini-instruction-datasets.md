---
title: UltraChat and LaMini Instruction Datasets
tags: [llm, pretraining-and-data, concept]
summary: "Two 2023 scale-oriented ChatGPT-generated instruction sets: UltraChat (1.5M multi-turn dialogues built by simulating the user, training UltraLM-13B) and LaMini (2.58M single-turn pairs distilled into 61M to 7B models); both papers report results that depend on GPT-4 or small human evaluations (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ding-2023-enhancing-chat-language-models-scaling.md
  - data/raw/papers/2026-11-07-wu-2024-lamini-lm.md
---

# UltraChat and LaMini Instruction Datasets

Both are large datasets generated with ChatGPT (gpt-3.5-turbo); see also [[Self-Instruct and Unnatural Instructions]]. Every figure below is self-reported.

## UltraChat

The question is whether a bigger, more diverse and higher-quality set of synthetic multi-turn conversations, produced with no human queries, gives a stronger open-source chat model. Opening lines are generated in three sectors: questions about the world, creation and writing, and assistance on C4 materials. Two ChatGPT API instances then act as user and assistant for 3 to 7 rounds, and the dialogues are filtered. UltraLM is LLaMA-13B finetuned on the result, with loss taken on responses only. The authors name role confounding as the obstacle for the simulated user: seeing only the dialogue history, it tends to slip into the assistant's role and coherence drops.

- Size and length: 1.5M multi-turn dialogues, averaging 1467.4 tokens each, the longest among the instruction datasets in Table 4 (SODA averages 231.8).
- Diversity: Table 4 gives MTLD 0.702, below SODA at 0.797, even though the body text calls UltraChat more diverse than earlier sets.
- Human check: two annotators scored 500 dialogues on a 0, 0.5 or 1 scale; the overall helpfulness score was 0.960, and the third sector was weakest at 0.893.
- Vicuna-style comparison: on a curated set of 831 questions (the Vicuna benchmark plus 300 GPT-4-written ones, each answer rated 1 to 10 by GPT-4), UltraLM-13B averages 9.00, ahead of WizardLM at 8.95 and Vicuna at 8.78. Head to head with Vicuna-13B it wins 39.1, ties 30.2 and loses 30.7.
- AlpacaEval (805 instructions, GPT-4 as judge): UltraLM beats Text-Davinci-003 in 76.09% of comparisons.
- Four knowledge benchmarks (ARC-Challenge, HellaSwag, MMLU, TruthfulQA, lm-evaluation-harness): base LLaMA-13B averages 55.98, WizardLM-13B 60.19 and UltraLM 60.95, although UltraLM trails WizardLM-13B and Vicuna on MMLU.
- On the 218-example Evol-Instruct test set, UltraLM reaches 102.8% of WizardLM-13B's total score, falling to 79.3% for math, its weakest category.
- Prompting UltraLM with a helpful, detailed system prompt wins 49.1% and loses 18.9% against the same model without it.

## LaMini

The question is whether sequence-level distillation, in which a teacher's generated outputs become the student's training targets, can let many small models rival larger instruction-tuned ones when trained on a large gpt-3.5-turbo instruction set. Instructions come from existing prompt sets (self-instruct, P3, FLAN, Alpaca) and from new gpt-3.5-turbo instructions guided either by examples or by Wikipedia topics; gpt-3.5-turbo then writes a brief reply to each. The result is 2.58M pairs, about 50 times Alpaca's size. Seventeen models ranging from 61M to 7B parameters, cover six families (LLaMA, GPT-J, GPT-Neo, Cerebras-GPT, GPT-2 and T5), each trained with full finetuning.

- Fifteen NLP tasks (zero-shot, micro-average): LaMini-Flan-T5-248M matches LLaMA-7B, and LaMini-LLaMA-7B tops both LLaMA-7B and Alpaca-7B.
- Subset ablation (52K random examples per subset, only T5 and GPT-2 models): self-instruct-style subsets yield small benchmark gains while P3 and FLAN-derived subsets yield clearly larger ones; in human evaluation the self-instruct-style subsets matter more.
- The authors claim encoder-decoder LaMini models outperform decoder-only ones, mostly under 500M parameters. In human ratings of 114 user-oriented instructions a considerable gap to gpt-3.5-turbo persists.
- Hallucination probe of 40 questions built to induce it: LaMini-LLaMA-7B was wrong on 12 and Alpaca-7B on all 40; LaMini-GPT-124M was wrong on every one.
- Toxicity on 1K RealToxicityPrompts prompts: LaMini-Flan-T5-77M gave 46 toxic outputs where Flan-T5-small gave 25, while LaMini-LLaMA-7B gave 71 where LLaMA-7B gave 138. The paper concludes that tuning raised toxicity for the encoder-decoder models and lowered it for decoder-only ones.
- The complete dataset scores highest on lexical diversity (MATTR, window 50), and topic guidance increases it. Eight experts rated 400 examples per subset and judged most pairs good, finding more errors in the topic-guided and P3/FLAN-derived responses. Coding, math and logical reasoning remain poor.

## Limits

- UltraChat: the judging leans on GPT-4, whose possible bias the authors acknowledge; hyperparameters go unreported; the sectors and the user simulation are not ablated against model quality; the data is English only with no explicit reasoning content or math problems, and UltraLM is weak at math; HellaSwag barely improves; annotator agreement is low (kappa 0.358) and hard-to-verify dialogues could be skipped; ChatGPT's hallucinations and biases carry over; baselines predate 23 June 2023.
- LaMini: only the models listed were tried; the data is single-turn; gpt-3.5-turbo's hallucination and toxicity carry over; there are no seeds, variance or significance tests, and optimiser, schedule and decoding settings go unstated; the human evaluation covers 114 prompts with one rater each; the subset ablation uses 52K examples on T5 and GPT-2 with no human-evaluation table; the 40-question hallucination probe is small and the toxicity check relies on a closed moderation API that may since have changed; LLaMA-7B and GPT-J had only 2.5 epochs.
- The LaMini extraction omits the values for the 52K D_ALL result, so that comparison is left out here. The extraction dates the LaMini paper 2024, and UltraChat's comparison set dates from mid-2023.

## See Also
- [[Self-Instruct and Unnatural Instructions]] — prerequisite-for
- [[Evol-Instruct (WizardLM and WizardCoder)]] — related (the WizardLM baseline for UltraLM)
- [[Synthetic Instruction Data: Curation and Verification]] — related
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — related (LaMini draws on P3 and FLAN prompts)
