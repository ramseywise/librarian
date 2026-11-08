---
title: CALM Composition to Augment LLMs
tags: [foundations, pattern]
summary: "CALM joins a frozen large anchor model to a frozen smaller specialist through learned projections and cross-attention over every fourth layer; the authors report gains on low-resource translation, maths and code over the anchor without the forgetting seen after further pre-training, and a synthetic task neither model can do alone (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-bansal-2024-llm-augmented-llms.md
---

# CALM Composition to Augment LLMs

Bansal et al. (Google Research and DeepMind; arXiv 2401.02412, the PDF prints no venue, so a conference listing is unconfirmed) compose two frozen models: an anchor (PaLM2-S or XS) and a smaller augmenting model (PaLM2-XXS further trained on a domain). A linear projection maps the augmenting model's hidden states to the anchor's width, and a cross-attention block, with the anchor's layer as query and the projected states as key and value, is added residually at every fourth layer of the augmenting model. Only the projections and cross-attention are trained, on a small slice of the domain data. Decoding re-runs both models on the growing sequence. The authors' worked arithmetic (a BERT example, not measured on PaLM2) gives about 1.5% added parameters.

## Results (self-reported)

Setup: PaLM2 models only; CALM trained on about 5-7% of each domain's data; the further-pre-trained anchor is a skyline.
- FLORES-200 translation into English, five-shot: average chrF1 46.1 for CALM against 41.7 for the anchor and 37.2 for the augmenting model; further pre-training the anchor reached 48.2. CALM beat the anchor on 175 of 192 languages, with the largest gains on the lowest-resource ones.
- GSM8K in 25 machine-translated low-resource languages: 25.0 against 22.5 for the anchor; further pre-training gave 22.6, which the authors read as forgetting. High-resource languages: 31.8 against 28.0 (further pre-training 25.6).
- Code: HumanEval pass@1 22.5 against 16.4 for the anchor, but the further-pre-trained code model scored 24.3, and on MBPP 32.2 against 43.0. On code-to-text it kept anchor performance while the code-trained anchor fell from 30.4 to 18.9.
- Synthetic key-value arithmetic: 84.3% against 0.7% and 0.0% for the two models alone, with training on 20% of keys.
- Ablations at equal added parameters: CALM beat LoRA (HumanEval 22.5 against 18.3), so the specialist, not the extra parameters, carries the gain (self-reported).

## Limits

- Closed PaLM2 models only, sizes and mixes not stated; one augmenting model; no multi-seed or deviation figures. Needs weights, intermediate activations and backpropagation through the anchor, so it cannot compose API models.
- The low-resource maths set is machine-translated (back-translation overlap about 55-83); gains there are 1.15-1.70 points. The qualitative examples are admitted cherry-picked. The cost figure is an assumed linear estimate.
- The extraction notes that the abstract's "40% relative" code gain and "on par with fully fine-tuned" claim are only partly supported: the code-pre-trained model wins on HumanEval and MBPP. The "13%" abstract figure also could not be traced to a table, and Table 5 labels are scrambled in the extraction.
- Motivation about skewed code and low-resource data in pre-training is asserted, not measured.

## See Also
- [[Post-Training for Agents]] — related
- [[MoE Expert Offloading]] — related
- [[Compiling Workflows into Weights]] — alternative-to
