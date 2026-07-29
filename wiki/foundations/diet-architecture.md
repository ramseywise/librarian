---
title: DIET Architecture
tags: [foundations, concept]
summary: Dual Intent and Entity Transformer (Rasa, 2020) — a multi-task NLU architecture for joint intent classification and entity recognition that outperforms fine-tuned BERT while being 6x faster to train, using plug-and-play pre-trained embeddings with sparse features.
updated: 2026-07-19
sources:
  - raw/pdfs/2020-04-01-rasa-dual-intent-entity-transformer.md
---

# DIET Architecture

DIET (Dual Intent and Entity Transformer) is a multi-task architecture for two core NLU tasks: **intent classification** and **named entity recognition** (NER). Published by Rasa (Bunk et al., 2020).

## Architecture

### Featurization (Plug-and-Play)

Input tokens are featurized with any combination of:
- **Sparse features**: token-level one-hot encodings + character n-gram multi-hot encodings (n ≤ 5)
- **Dense features**: pre-trained word embeddings from ConveRT, BERT, or GloVe

A special `__CLS__` token is appended; when using ConveRT, its initial embedding is set to the sentence-level encoding (adding extra sentence context).

Sparse features pass through a fully connected layer (shared weights across positions) to match dense feature dimensions, then concatenate with dense features. Another FC layer projects to the transformer dimension (256).

### Transformer

2-layer transformer with **relative position attention** (Shaw et al., 2018). Encodes context across the complete sentence.

### Intent Classification (Dot-Product Loss)

The transformer output for `__CLS__` and intent labels are embedded into a shared semantic vector space (IR^20). Training maximizes dot-product similarity with the target intent and minimizes similarity with negative samples:

```
L_I = -<S_I+ - log(exp(S_I+) + sum(exp(S_I-)))>
```

At inference, dot-product similarity ranks all possible intent labels.

### Entity Recognition (CRF)

A Conditional Random Field (CRF) tagging layer on top of the transformer output sequence. Using BILOU tagging schema for strict span matching.

### Masked Language Model Objective

Additional training objective: predict randomly masked input tokens (15% selected; 70% masked, 10% random, 20% kept). Acts as regularizer and helps learn general text features. Improves performance ~1% absolute on both intents and entities when no pre-trained embeddings are used.

### Total Loss

```
L_total = L_intent + L_entity + L_mask
```

Architecture is configurable — any loss can be turned off.

## Key Findings

### No pre-trained embeddings needed
DIET with only sparse features (no pre-trained embeddings at all) outperforms state-of-the-art on NLU-Benchmark dataset, achieving 88.19% intent F1 and 85.12% entity F1.

### ConveRT > BERT for dialogue NLU
- ConveRT embeddings (trained on conversational data) outperform BERT embeddings (trained on prose)
- BERT requires fine-tuning before transfer to dialogue tasks; ConveRT works without fine-tuning
- Best model: sparse + ConveRT (no mask loss) = **90.18% intent F1, 86.04% entity F1**

### Beats fine-tuned BERT, 6x faster
Fine-tuned BERT inside DIET: 89.67% intent F1, 85.73% entity F1, **60 hours training**
Sparse + ConveRT: 90.18% intent F1, 86.04% entity F1, **10 hours training**

### Joint training helps entities, slightly hurts intents
Entity F1 drops from 86.04% to 82.57% when trained separately — strong correlation between intents and entities (e.g., `play_game` intent always co-occurs with `game_name` entity).

## Practical Implications

- **Modular > monolithic**: plug-and-play embedding architecture lets you swap representations without changing the model
- **Domain-matched embeddings matter more than model size**: ConveRT (conversational) beats BERT (prose) despite being smaller
- **Sparse features are surprisingly competitive**: character n-grams and one-hot encodings alone approach SOTA
- **Multi-task learning**: CRF for sequence labeling + dot-product loss for classification is a proven combination

## See Also
- [[Dialogue Transformers — TED Policy]] — extends (TED uses DIET for NLU in modular setup)
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Open-Domain Dialogue Systems]] — instance-of
- [[Transformer Architecture]] — prerequisite-for
