---
title: UL2 Mixture of Denoisers
tags: [foundations, concept]
summary: "UL2 pre-trains one model on a mixture of three denoising objectives (regular, sequential, extreme) tagged with mode tokens, arguing the objective matters more than encoder-decoder versus decoder-only; the paper reports gains over T5 and GPT-like baselines and a 20B model (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-tay-2022-ul2.md
---

# UL2 Mixture of Denoisers

Tay, Dehghani, Tran et al. (ICLR 2023) ask whether a single pre-training recipe can serve supervised, few-shot and generation tasks whatever the architecture. Their hypothesis is that diverse denoising objectives, plus mode tokens, trade off better than span corruption (T5) or causal language modelling alone.

## Mechanism

Seven span-corruption denoisers are mixed, each prefixed with a mode token on C4 data:

- **R-Denoiser** (regular): standard span corruption, spans of 2 to 5 tokens, about 15% of tokens masked.
- **S-Denoiser** (sequential): targets do not depend on future information, which is prefix language modelling.
- **X-Denoiser** (extreme): long spans of 12 or more tokens, or corruption of 30% or more.

**Mode switching** adds a paradigm token ([R], [S], [X]) in pre-training and at downstream time to bind behaviour to one of the pre-training modes. The ablations compare causal LM, prefix LM, span corruption (T5), span corruption plus LM, and UniLM objectives, using decoder-only and encoder-decoder backbones of about 167M and 335M. Scaling follows, to 1B parameters on 0.5T tokens and to 20B on 1T tokens.

## Results

All numbers are the paper's own (self-reported); ablations are single runs.

- 335M encoder-decoder, 32B tokens of C4: UL2 beats the T5 span-corruption baseline on a normalised overall gain across 9 of 9 tasks. The UL2 decoder-only model is the only decoder to beat the T5 encoder-decoder overall (167M decoder against 335M encoder-decoder).
- Mode tokens matter for generation: one-shot XSum, encoder-decoder on 7B tokens, [R] gives Rouge 13.5/1.5/11.1 and [X] gives 8.9/0.9/7.6; SuperGLUE hardly moves.
- A modest share of S-denoisers (around 20%) works best, while 50% does harm.
- For the 1B encoder-decoder trained on 0.5T tokens, one-shot XSum is well ahead of T5, which scores 8.9 / 0.8 / 7.8.
- For the best UL2 20B checkpoint, zero-shot SuperGLUE average is above GPT-3 175B (61.2); zero-shot MMLU above T0 and LM-adapted T5-XXL.
- UL2 20B with chain-of-thought prompts from Wei et al.: five commonsense sets average 37.8 standard, 48.1 with CoT and 52.2 with self-consistency; arithmetic with calculator plus self-consistency reaches 36.0 against 13.5 standard.
- Flan-UL2 20B averages 49.1 across MMLU and BBH direct and CoT, against 49.9 for Flan-PaLM 62B; CoT still scores below direct.
- Authors' opinions: encoder-only models are deprecated, and causal LM is the worst objective of those tried, so train at least with prefix LM or UniLM.

## Limits

- The 20B run had no monitoring, saw loss spikes and got no mitigation; the authors expect the results to understate the method.
- Ablations are single runs at 167M and 335M, 32B tokens; no seeds or variance. The encoder-decoder has about twice the parameters of the decoder at matched compute, which may favour it.
- State-of-the-art comparisons date to 15 April 2022; checkpoints were trained on TPUv4.
- Finetuning details and few-shot prompts are missing from the extraction, and the claim that the mixture enables CoT at 20B is not tested.
- These are pre-instruction-tuning, C4-only in-context results. The authors note a slight conflict with a masking-rate study (Wettig et al.) on high corruption.

## See Also
- [[Chain-of-Thought Prompting]] — related (CoT results at 20B)
- [[Self-Consistency]] — related
- [[Mixture-of-Transformers]] — related
- [[PEGASUS Gap-Sentence Pretraining]] — related (another pre-training objective study)
- [[PaLI and PaLI-X Jointly Scaled VLMs]] — related
