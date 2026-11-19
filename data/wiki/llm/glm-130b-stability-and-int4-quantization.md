---
title: GLM-130B Stability Recipe and INT4 Quantization
tags: [llm, pretraining-and-data, concept]
summary: "Zeng et al. (2022) train GLM-130B, an open bilingual 130B bidirectional blank-infilling model, with DeepNorm and embedding gradient shrink for stability, 5% multi-task instruction pre-training, and weight-only INT4 quantization for inference on 4 RTX 3090 GPUs (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zeng-2022-glm-130b.md
---

# GLM-130B Stability Recipe and INT4 Quantization

GLM-130B is a 130B-parameter, 70-layer bidirectional GLM trained by autoregressive blank infilling with two mask types: [MASK] fills short blanks, while [gMASK] fills one long blank of random length at the end of a sequence that has a prefix as context. Training used 400B tokens of English and Chinese text and ran about 60 days on 96 DGX-A100 40G nodes. The authors hypothesise that this backbone, a small slice of instruction-style pre-training data, DeepNorm and embedding gradient shrink together let a 130B model match or beat GPT-3 175B. Everything below is self-reported.

## The three named mechanisms

- **Embedding Layer Gradient Shrink (EGS).** The embedding output is mixed with a gradient-detached copy of itself, weighted alpha for the live path and 1 - alpha for the detached one, with alpha = 0.1, so only a tenth of the gradient reaches the embedding layer. In a 40B-scale test and in the final run this removed most loss spikes, leaving three divergences late in the final run. Training used FP16 mixed precision.
- **DeepNorm Post-LN.** The residual branch is rescaled before normalisation: LayerNorm applied to alpha times the input plus the sublayer output, with alpha equal to the square root of 2N.
- **Multi-task Instruction Pre-training (MIP).** Prompted instruction datasets (74 of them) make up 5% of training tokens. A 10B English-only ablation compared GLM unidirectional, GLM bidirectional and GLM+MIP bidirectional: the bidirectional objective explains 73% of the LAMBADA improvement and 90% of the MMLU improvement, while MIP mainly helps on text-similarity and coreference tasks, while WiC, ReCoRD and HellaSwag can get worse. Since many NLI datasets sit inside MIP, the authors keep fixed-label tasks out of their headline zero-shot claims.

Other design points: RoPE and GeGLU lowered test perplexity on a 110M GLM-Base from 24.58 to 22.31 (ALiBi 24.14, RoPE 22.95; 50G mixed corpus), with the GeGLU feed-forward dimension reduced to 8/3 of the hidden size. A 3D parallel layout chosen for the hardware (tensor parallel 4, pipeline parallel 8, PipeDream-Flush schedule) fixes the 70-layer shape; with global batch 4224 and re-materialisation it reached 43.3% hardware and 32.5% model FLOPs utilisation, with a pipeline bubble share of 3.8%.

## INT4 weight-only quantization

Weights are quantized to INT4 with absmax and no post-training, while activations stay in FP16. Memory drops to half of INT8, about 70GB, which lets four RTX 3090 or eight RTX 2080 Ti cards serve the model. Accuracy fell 0.74 points on LAMBADA and was unchanged on MMLU (+0.05), still above GPT-3. Outliers appear in roughly 30% of GLM-130B's hidden dimensions, versus 0.1% in GPT-style models (a figure from Dettmers et al.), so the authors quantize weights alone rather than apply [[LLM.int8 Outlier-Aware Quantization]]. Under absmax INT4, BLOOM-176B falls on LAMBADA from 64.37% to 34.83% (column-wise absmax) while GLM-130B drops from 80.21 to 79.47 (row-wise). In 16-bit decoding on eight A100 80G, GLM-130B is 7.0x to 8.4x quicker than BLOOM-176B run through HF Transformers (FasterTransformer against PyTorch).

## Results

- LAMBADA zero-shot 80.2%, above GPT-3 and PaLM 540B. MMLU 5-shot 44.8 against 43.9 for GPT-3 175B (GPT-3 number from the MMLU paper). Pile BPB 0.634 against 0.742 for GPT-3 and 0.650 for Jurassic-1.
- BIG-bench-lite zero-shot 13.31 against 4.35 for GPT-3 and 8.05 for PaLM 540B, but few-shot grows less (15.12 at 3-shot against 13.18 for GPT-3). The authors attribute this to bidirectionality and zero-shot-only MIP.
- Chinese: 24.26% better than ERNIE Titan 3.0 (260B parameters) across 7 CLUE datasets zero-shot and by 12.75% across 5 FewCLUE datasets (dev sets, English prompts and verbalizers).
- Weak spots: Natural Questions closed-book 11.7 EM against 14.6 (GPT-3) and 21.2 (PaLM), which the authors blame on seeing only about 200B English tokens; the unidirectional variant trails GPT-3 on GEM generation (WebNLG ROUGE-2 25.3 unidirectional, 38.5 bidirectional, 29.9 GPT-3, 1-shot).
- CrowS-Pairs overall bias score 65.8 against 67.2 for GPT-3 and 69.5 for OPT-175B (pseudo-log-likelihood). Pre-training emitted 257.01 t CO2 from 442.4 MWh, against about 500 t estimated for GPT-3.

## Limits

- The few-shot cause (bidirectionality, zero-shot-only MIP) is conjectured and untested; ablations were done at 10B, not 130B.
- MIP spans 74 datasets, so the authors flag their SuperGLUE and NLI results as not truly zero-shot.
- The model saw just 400B tokens, roughly 200B of them English, and the authors accept it is under-trained.
- Evaluation covers part of CLUE and FewCLUE and 24 of the 150 BIG-bench tasks; Pile BPB covers 18 of 22 subsets against numbers copied from Jurassic-1 and GPT-3.
- The authors could not run OPT-175B themselves, and most GPT-3 figures come from the literature.
- No seeds or confidence intervals. The BLOOM speed-up reflects BF16 and the HF implementation, not only architecture.
- Bias benchmarks are English-centric; Chinese biases are not tested. Explanations of why GLM quantizes to INT4 and what the outliers mean are speculative.

## See Also

- [[Open Pretrained Model Reports Comparison]] — alternative-to (open 100B-class models: BLOOM, OPT)
- [[GPT-3 and Few-Shot In-Context Learning]] — related (the comparison model)
- [[LLM.int8 Outlier-Aware Quantization]] — alternative-to
- [[Transformer Architecture]] — prerequisite-for
