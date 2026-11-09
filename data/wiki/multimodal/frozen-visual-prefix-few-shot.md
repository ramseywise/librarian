---
title: Frozen Visual Prefix Few-Shot Learning
tags: [multimodal, concept]
summary: "Frozen trains only a vision encoder, through a frozen 7B language model, to emit a two-token visual prefix on Conceptual Captions, then prompts with interleaved images and text for few-shot VQA and classification (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-tsimpoukelli-2021-multimodal-few-shot-learning-frozen.md
---

# Frozen Visual Prefix Few-Shot Learning

Tsimpoukelli et al. (2021) ask whether a text-only language model that stays frozen can gain a trained vision front-end, with its in-context few-shot ability carrying over to multimodal tasks. The extraction describes the method as image-conditional prefix tuning.

## Mechanism

- The 7B GPT-2-style LM is frozen. A visual encoder (NF-ResNet-50) followed by a linear map produces two prefix tokens for every image.
- Only the vision side is trained. It learns from a captioning loss on Conceptual Captions, and gradients pass back through the frozen LM.
- When tested, the prompt interleaves images with text, covering VQA, OKVQA and few-shot classification. **Task induction** is explanatory text placed before the example sequence; **inner-shots** are the exemplars per category shown in a classification episode.

## Results (self-reported)

- On the VQAv2 validation set, using greedy open-ended decoding with the 7B frozen LM trained only for captioning, Frozen gets 38.2% given four in-context examples; training on the whole VQAv2 set gets 48.4% (self-reported).
- A variant that fine-tunes the LM generalises worse at 4 shots on VQAv2; a variant trained from scratch scores 0.0 at every shot count (self-reported).
- On OKVQA, performance scales with LM size when the 7B model is compared with a 400M one (self-reported).
- On 2-way open-ended miniImageNet, a task adapted so that labels are nonsense words, the extraction leaves the 2-way result blank, so no figure is given here; 5-way is near chance at a best of 22.3% against 20% (self-reported).
- Curated qualitative samples needed about five seeds to avoid repetition or irrelevant output.

## Limits

- On every task it sits well below the leading results; the extraction notes the authors call it a proof of concept and a baseline.
- The 5-way miniImageNet result is not significantly above chance.
- No seeds or variance for quantitative results; training steps, warmup, precision and encoder pretraining are not stated; the evaluation sets had not yet been made public when the preprint appeared.

## See Also
- [[Vision-Language Model Architectures]] — related
- [[Flamingo Gated Cross-Attention VLM]] — extends
- [[BLIP-2 Q-Former Bridging]] — extends
- [[Vision-Language Model Training Families]] — related
- [[PICa GPT-3 Knowledge VQA]] — alternative-to
