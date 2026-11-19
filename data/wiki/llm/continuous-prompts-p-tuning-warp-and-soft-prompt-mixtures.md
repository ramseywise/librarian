---
title: "Continuous Prompts: P-Tuning, WARP and Soft-Prompt Mixtures"
tags: [llm, fine-tuning, concept]
summary: "Three 2021 methods that train continuous prompt vectors against a masked or pretrained LM: P-tuning (prompt encoder plus discrete prompt), WARP (prompt and verbalizer embeddings on a frozen MLM) and Qin and Eisner's mixtures of soft prompts for knowledge probing (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-liu-2023-gpt-understands-too.md
  - data/raw/papers/2026-11-08-hambardzumyan-2021-warp.md
  - data/raw/papers/2026-11-08-qin-2021-learning-how-ask.md
---

# Continuous Prompts: P-Tuning, WARP and Soft-Prompt Mixtures

All three methods swap hand-written or mined prompt words for vectors trained by backpropagation on the task loss. They are contemporaries of prefix-tuning and prompt tuning ([[Prefix-Tuning and Prompt Tuning]]) and start from cloze-style prompts like those in [[LM-BFF and PET Prompt-Based Fine-Tuning]] and [[LPAQA Prompt Mining and Ensembling]].

## P-tuning (Liu et al.)

The template interleaves ordinary prompt words with trainable pseudo-token embeddings [P_i]. A small prompt encoder f (an LSTM, an MLP or the identity) turns them into input vectors h_i, so that the prompt vectors depend on one another. The LM stays frozen on LAMA and is tuned jointly on SuperGLUE. The authors' hypothesis is that trainable prompt input can cancel out the sensitivity of results to small edits of a discrete prompt.

Results (self-reported):
- LAMA, frozen BERT-base-cased, relation P17: editing one word of a manual prompt makes P@1 drop sharply, while P-tuning stays between 57.8 and 58.1. The standard deviation over manual prompts shrinks from 10.1 to 0.46.
- LAMA-34k with BERT-large: P@1 rises from 43.3% (best discrete baseline) to 50.6%. LAMA-29k with MegatronLM 11B: 64.2 against 23.1 for the manual prompt.
- Few-shot SuperGLUE (FewGLUE, ALBERT-xxLarge, mean of 4 runs on different splits): P-tuning 71.81, PET-FT 70.74, Prompt Tuning 58.56. On BoolQ the spread across patterns is 3.52 for P-tuning and 5.68 for PET-FT.
- Fully-supervised SuperGLUE dev: GPT2-medium 75.6 for P-tuning, 74.9 for PET-FT, 63.1 for CLS-FT; BERT-large 74.6, 73.1 and 72.5. Benefit is slight or nil on resource-rich tasks (WiC, MultiRC) and bigger on low-resource ones.
- Ablations, few-shot CB with ALBERT: 4 continuous tokens average 86.76 and 8 tokens 78.40. MLP and LSTM encoders both work; the identity encoder is unstable (F1 67.27 against 84.24 for the MLP).
- Adding continuous prompts to LM-BFF's three best discrete prompts on RoBERTa-Large helps unevenly: SST-2 92.78 against 92.89, MNLI 58.70 against 57.53, MRPC 69.49 against 68.26.

## WARP (Hambardzumyan et al.)

The name stands for Word-level Adversarial ReProgramming. Trainable prompt embeddings [P_1..P_K] go before, between and after the input sentences next to a [MASK] token. At the mask, the MLM head's output (before its decoder) is projected through trainable verbalizer embeddings [V_1..V_C], with a cross-entropy loss, while all other model weights stay frozen.

Results (self-reported):
- Frozen roberta-large reaches a GLUE test average of 81.6 using fewer than 25K trainable parameters, ahead of every leaderboard entry that trains up to 25M. On dev, WARP_20 averages 84.8 against 88.9 for full fine-tuning.
- Few-shot (albert-xxlarge-v2, 32 examples, ensemble of 20 runs, SuperGLUE test): on CB it is better than GPT-3 and PET but behind iPET; on RTE WARP_init scores 69.1, GPT-3 69.0, iPET 70.8.
- One prompt token gives 93.8% on SST-2 dev, against 91.2% for AutoPrompt. The dev average climbs steadily from 72.4 with no prompt tokens to 82.1 with eight.
- Starting from a manual prompt helps small datasets: RTE dev 80.1 with WARP_init against 72.9 with WARP_8.
- Each epoch runs 2.5 to 3 times faster than fine-tuning at equal batch size.

## Mixtures of soft prompts (Qin and Eisner)

With the LM frozen, each relation gets several cloze prompts, made of token vectors initialised from mined prompts or at random, plus mixture weights. Training minimises the mixture's log-loss on the predicted distribution over (x, y) pairs. A "deeply perturbed" variant adds a perturbation at every layer, and another variant makes the weights data-dependent. Tests use T-REx, Google-RE and ConceptNet against LAMA, LPAQA and AutoPrompt prompts.

- On T-REx original with BERT-large-cased, a soft-prompt mixture outperforms the AutoPrompt-style and LPAQA baselines, and random initialisation is almost as good as mined initialisation.
- ConceptNet, BERT-large, random init: 14.5 P@1 against 0.1 for the LAMA prompt.
- Most of the gain comes from tuning token vectors; tuning only the mixture weights adds little, and data-dependent weights made little difference.
- Tuning every layer yields small extra gains but clearly hurts RoBERTa-base.
- When train and test share no y values, soft prompts still beat LPAQA. One prompt trains in a few minutes.

## Limits

- P-tuning: fully-supervised SuperGLUE figures are single numbers without variance, and the authors grant that discrete prompts differ little there. The few-shot edge over PET is about one point while per-task standard deviations are several points, and P-tuning loses on RTE. ReCoRD is left out. Compute, seeds for the supervised runs, encoder size and the token count per task are unstated. Scope is NLU with small encoders or GPT-2-scale models (MegatronLM 11B only on LAMA), with no generation or modern LLMs. The Prompt Tuning comparison runs on ALBERT, where that method is weak.
- P-tuning's LAMA gains combine learned prompts with training on relation triples, so higher P@1 partly reflects fitting rather than elicited pretrained knowledge (the authors do not discuss this).
- WARP: CoLA is weak (53.9 test); learned tokens cannot be read; few-shot results trail iPET, which has 20000 unlabeled examples; GLUE test is 6.5 points under fully fine-tuned RoBERTa; only encoder classification and regression are tested (an autoregressive extension is footnoted); GLUE seeds are not reported.
- Qin and Eisner: answers must be a single token in cloze relation tasks (BART results are not comparable); learning rate, seeds, hardware and parameter counts are missing; soft prompts are uninterpretable; the claim that the method is cheaper than fine-tuning is presumed, not measured.

## See Also

- [[Prefix-Tuning and Prompt Tuning]] — related (concurrent continuous-prompt methods)
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for
- [[LAMA Knowledge Probe]] — prerequisite-for
- [[LPAQA Prompt Mining and Ensembling]] — prerequisite-for
- [[LM-BFF and PET Prompt-Based Fine-Tuning]] — prerequisite-for
- [[Prompt-Based Learning Survey Typology]] — related
