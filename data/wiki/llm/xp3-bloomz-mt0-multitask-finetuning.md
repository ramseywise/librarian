---
title: XP3, BLOOMZ and mT0
tags: [llm, fine-tuning, concept]
summary: "Muennighoff et al. (2023) finetune BLOOM and mT5 on xP3, a 46-language and code prompted mixture, and find zero-shot gains on tasks and languages not intentionally seen, but no HumanEval gain at 176B and a drop on English prompts when machine-translated prompts are added (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-muennighoff-2023-crosslingual-generalization-through-multitask-finetuning.md
---

# XP3, BLOOMZ and mT0

The paper tests whether multitask prompted finetuning of multilingual models yields zero-shot ability on new tasks and in non-English languages, including ones the model was never deliberately shown. xP3 mixes supervised datasets covering 46 languages and code, all with English prompts; xP3mt swaps in machine-translated prompts for monolingual datasets. Two base families are finetuned: decoder-only BLOOM from 560M to 176B and encoder-decoder mT5 from 300M to 13B, on English P3, xP3 and xP3mt, with loss on target tokens only and per-token length normalisation. This follows the recipe in [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]]. Zero-shot evaluation covers XNLI, XCOPA, XStoryCloze, XWinograd and HumanEval, scored by rank classification over 5 randomly drawn PromptSource prompts. Every figure is self-reported.

## Results

- XNLI language-average accuracy goes from 33.6 for BLOOM to 55.3 for BLOOMZ trained on xP3, and mT0-13B gets 57.7 (zero-shot, English prompts, 176B BLOOM models).
- English-only P3 training (BLOOMZ-P3) gives 80.5 on XCOPA and XStoryCloze sentence completion against 52.9 for BLOOM (176B, languages present in pretraining).
- Averaged over languages with English prompts and the median of 5 prompts, mT0-13B beats the 176B BLOOMZ on XWinograd.
- mTk-Instruct-13B trails same-size mT0 by a wide margin on XNLI. mT0-13B also beats English-only T0-11B on English held-out tasks, which the paper credits to the extra tasks and prompts in xP3.
- xP3-trained models handle XNLI in languages not deliberately included, such as Thai at 0.006% of the corpus (language ID on a random 1% ROOTS sample). A Levenshtein check on Thai, Turkish and Greek found label differences of just a few edits, which the paper takes to make shallow cues an unlikely explanation.
- Machine-translated prompts (xP3mt) lift 176B XNLI accuracy for human-translated prompts, 41.13 to 45.55, but cut English-prompt accuracy from 53.58 to 49.74. Plain BLOOMZ scores 52.99 on English prompts and 37.56 on machine-translated ones.
- On HumanEval, BLOOMZ gets 12.06% pass@1 against 15.52% for BLOOM (176B; top_p 0.95, 200 samples per problem, best of temperatures 0.2, 0.6 and 0.8). BLOOMZ-P3, trained without code data, gets 6.13%.
- BLOOMZ outputs on HumanEval average 144 characters against 247 for BLOOM. Forcing at least 768 generated tokens raises English-French MultiEURLEX BLEU by about 9 points (BLOOMZ-7.1B, median over 3 prompts per direction).
- Upweighting long tasks by dropping loss normalization lowers NLU validation accuracy by 10% (7.1B ablation). Bias-only (BitFit) finetuning trails full finetuning by 15 absolute points on held-out tasks (BLOOMZ-7.1B).
- The final BLOOMZ-176B saw 2.09 billion finetuning tokens (early stopped) and mT0-13B saw 1.29 billion; the ablations used 13 billion.
- Finetuned BLOOM models score better in languages that each exceed 10% of pretraining (English, Spanish, French); XWinograd does not follow the trend.

## Limits

- Reproducing the work needs the released code, since the paper omits optimizer, learning rate, batch size and step count; there are no error bars or repeated seeds.
- xP3 has 46 languages though mT5 saw 101. xP3x, with 277 languages, was released but nothing was finetuned on it. Languages seen only in finetuning were not studied (mT0 scored 0.00 on HumanEval).
- Short finetuning targets bias outputs toward brevity and hurt generative tasks; a forced minimum length at inference works around it.
- The unseen languages are not strictly unseen, since ROOTS holds a little of them.
- Prompts join input and target with a space, so a decoder-only model might extend the input before answering.
- The base models are suboptimal in compute allocation, data and objective, and held-out scoring uses untuned prompts, and BLOOM zero-shot sits near chance (0.50 or 0.33 depending on the task).

## See Also
- [[Multitask Prompted Instruction Tuning (FLAN, T0, Super-NaturalInstructions, MetaICL)]] — prerequisite-for
- [[Flan-PaLM Instruction Finetuning Scaling]] — related (another instruction-finetuning scale study, English-centred)
- [[XGLM Multilingual Few-Shot Language Models]] — related
- [[Multilingual Pretraining: XLM, XLM-R, mBART and mT5]] — prerequisite-for (mT5 base)
- [[Open Pretrained Model Reports Comparison]] — related
