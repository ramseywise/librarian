---
title: DeBERTa Disentangled Attention
tags: [llm, architecture, pattern]
summary: "DeBERTa keeps masked-LM pretraining but gives each token separate content and relative-position vectors in attention and injects absolute positions only just before the output softmax through an enhanced mask decoder."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-he-2021-deberta.md
---

# DeBERTa Disentangled Attention

He et al. hypothesise that attention depends on both content and relative position, and that absolute positions work better when added late instead of at the input. Two changes to a BERT-style encoder follow.

## Mechanism

- **Disentangled attention:** each token has a content vector and a relative-position vector. The attention score sums content-to-content, content-to-position and position-to-content terms, scaled by sqrt(3d).
- **Enhanced mask decoder (EMD):** absolute positions enter right after all Transformer layers and before the softmax that predicts masked tokens.
- **Scale-invariant fine-tuning (SiFT):** a virtual-adversarial-training variant whose perturbations act on normalised word embeddings; used only for the 1.5B-parameter model on SuperGLUE.

## Reported results (self-reported)

- On the SuperGLUE test macro-average a single DeBERTa-1.5B with SiFT goes past the human baseline (results from 6 Jan 2021); the ensemble also tops the leaderboard above the human baseline.
- DeBERTa-large (24 layers, 1024 hidden) pretrained on 78GB for 1M steps at batch 2K beats RoBERTa-large (160GB, 500K steps at batch 8K) on MNLI-m dev, and its 9-task GLUE dev average is above the large versions of RoBERTa, XLNet and ELECTRA.
- Controlled base-size ablation (Wikipedia and BookCorpus, 1M steps, batch 256): DeBERTa-base beats a re-pretrained RoBERTa-base on RACE, and without the EMD RACE falls by 1.4 points (71.7 to 70.3).
- Cost: disentangled attention adds about 30% compute against BERT or RoBERTa and about 15% against XLNet (no fused kernel); the EMD adds about 3% for base and 2% for large.
- Sharing the position and content projections cuts DeBERTa-base from 134M to 120M parameters with near-identical MNLI (86.3/86.3).
- A DeBERTa-large variant pretrained with replaced token detection (160GB) matches the 1.5B model at a third of the parameters (MNLI 92.0 against 91.7).

## Limits

- The authors accept that the model remains well short of human language understanding and lacks compositional generalisation.
- SiFT was applied only to DeBERTa-1.5B on SuperGLUE; a fuller study is deferred.
- At large scale the comparisons mix data size and steps (78GB against 160GB); only the base-scale comparison on Wikipedia and BookCorpus is controlled.
- The T5 comparison uses test results and is not comparable with dev results.
- Precision, exact sequence length, total compute and token count are not stated.

## See Also
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for
- [[ELECTRA Replaced Token Detection]] — prerequisite-for (the objective used in its RTD variant)
- [[Transformer Architecture]] — prerequisite-for
