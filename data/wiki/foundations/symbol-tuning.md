---
title: Symbol Tuning
tags: [foundations, pattern]
summary: Finetuning on in-context input-label pairs whose labels are replaced by arbitrary symbols and whose instructions are removed, so the model must infer the task from exemplars; helps most when prompts carry no meaningful labels.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wei-2023-symbol-tuning-improves-context-learning.md
---

# Symbol Tuning

Symbol tuning finetunes a model on in-context classification examples in which the natural-language labels are swapped for arbitrary symbols (integers, character strings, words; about 30k symbols) and instructions are dropped. The model can only succeed by reading the input-label mapping from the exemplars. Setup in the paper: 22 classification datasets with 2 to 10 exemplars per class; Flan-PaLM at 8B, 62B and 540B plus a continued-training 62B variant.

## Reported results (self-reported)

Evaluation covers 11 tasks unseen in tuning, with four exemplars per class and no more than 100 test examples per task, under four settings that cross instruction presence with relevant-label presence.

- Gains are +0.8 to +4.2 points with relevant labels and +5.5 to +15.5 without. For 540B in the hardest setting (no labels, no instruction): 58.1 to 63.6; with instruction and no labels: 70.7 to 80.0 (random guessing 42.4).
- Symbol-tuned 8B beat untuned 62B, and symbol-tuned 62B beat untuned 540B in the no-label settings, which the authors equate to roughly 10 times less inference compute.
- Flan-PaLM-8B got worse when labels were meaningful (-6.3 and -7.3).
- Algorithmic transfer with no algorithmic tuning data: on BIG-Bench list functions the gains are +18.2 at 8B, +11.1 at 62B, +15.5 for the 62B variant and +3.6 at 540B; simple Turing concepts gain +15.3 at 8B, +14.1 and +4.7 on the larger models.
- On six binary tasks with flipped labels, symbol tuning adds 26.5 points at 8B, 33.7 at 62B and 34.0 at 540B, though the authors say average accuracy is not significantly above random.
- Cheap: most change within the first 1k to 2k steps (1k steps about 16 minutes for 8B on 64 TPUv4 chips, 6 hours for 540B on 512).
- A 16% share of symbol data in the tuning mix already shifts in-context behaviour, while flipped-label ability keeps growing as the share rises. Tuning on few datasets helps no-label settings and hurts relevant-label ones. A control with continued instruction tuning for equal steps gave little or negative change.
- Large models moved about 1 point on MMLU with five demonstrations and on BIG-Bench Hard with three; zero-shot MMLU dropped by at most 1.7.

## Limits

- The extraction skimmed appendices B to E and made no claims from per-task tables or prompts. Venue is not printed; treat as a preprint.
- Only Flan-PaLM family models, classification tasks and at most 100 eval examples per task; the large gains shrink with scale on algorithmic tasks.
- Small models can be hurt, and the authors attribute that to overfitting or treating all labels as arbitrary without testing it. The exemplar-count figure has no printed numbers.

## See Also

- [[Flipped-Label In-Context Learning]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
- [[Implicit Weight-Patch Theory of In-Context Learning]] — related
- [[Post-Training for Agents]] — related
