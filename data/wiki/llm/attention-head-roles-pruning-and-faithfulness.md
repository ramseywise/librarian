---
title: Attention Head Roles, Pruning and Faithfulness
tags: [llm, interpretability-and-safety, concept]
summary: "Three 2019 analyses of attention: Clark et al. find BERT heads that match some syntactic relations and coreference, Voita et al. prune most heads of a translation encoder with Hard Concrete gates, and Jain and Wallace find attention weights often disagree with gradient and leave-one-out importance (all self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-clark-2019-what-does-bert-look.md
  - data/raw/papers/2026-11-08-voita-2019-analyzing-multi-head-self-attention.md
  - data/raw/papers/2026-11-07-jain-2019-attention-not-explanation.md
---

# Attention Head Roles, Pruning and Faithfulness

Three papers ask what attention heads contain and whether attention weights explain a model's predictions. Figures are the authors' own (self-reported).

## What BERT heads attend to (Clark et al.)

The authors extracted attention maps from frozen BERT-base on 1,000 Wikipedia segments (up to 128 tokens). They used surface statistics, single heads as classifiers needing no training, and small trained probes.

- More than half the attention in layers 6-10 lands on [SEP]. The gradient of the masked-LM loss with respect to this attention shrinks from layer 5 onward, and the authors read it as a no-op (their speculation; nothing was intervened on). Final-layer [CLS] attention is very diffuse.
- Individual heads fit some relations on WSJ Stanford Dependencies. Head 8-11 finds a determiner's noun (94.3% accuracy); head 9-6 connects prepositions to their objects at 76.3% where a fixed offset gets 34.6%. Syntax overall is not handled by any one head: the top head, 7-6, gets 34.5 UAS, near a right-branching baseline.
- Head 5-4 reaches 65% on coreference (CoNLL-2012, cut to 128 tokens), over ten points beyond matching head words.
- A probe that takes every head's attention map plus fixed GloVe vectors gets 77 UAS on PTB dev. A structural probe on BERT's vectors gets a similar score, though the setups are not directly comparable.

## Pruning heads of a translation encoder (Voita et al.)

Transformer-base models translated English into Russian, German and French. Heads were ranked by layer-wise relevance propagation, and head roles were scored against CoreNLP parses. Pruning attached a stochastic gate to each head, with the Hard Concrete relaxation of an L0 penalty, while fine-tuning a converged model. Trained gates end up almost entirely open or closed.

- EN-RU WMT (2.5m): removing 38 of 48 encoder heads costs 0.15 BLEU. EN-RU OpenSubtitles (6m): leaving 4 of 48 loses 0.25 BLEU.
- Roles found: positional heads (their top attention falls on one relative position at least 90% of the time), syntactic heads (on WMT the best dobj head scores 78%, where a positional baseline gets 41%) and a layer-1 head pointing at rare words. A 17-head encoder still holds heads for every role identified.
- With gates on all three attention types, encoder self-attention is pruned first and decoder-encoder attention matters most.
- A sparse architecture trained from scratch does worse than the pruned one (5/9/12 heads on WMT: 28.90 pruned, 28.41 from scratch).

## Attention as explanation (Jain and Wallace)

Encoders (BiLSTM, CNN, average of embeddings) with additive or scaled dot-product attention were trained on classification, QA and NLI data.

- For BiLSTM encoders, attention correlates only weakly with gradient or leave-one-out importance; the average encoder correlates more. Gradient and leave-one-out agree with each other better than either does with attention.
- Shuffling the attention moved a negative-review sentiment output by a median of 0.006. Adversarially optimised attention, far from the original, gave equivalent predictions for many instances (epsilon 0.01 for classification, 0.05 for QA). Diabetes positive class is an exception.

## Limits

- Clark et al.: BERT-base only, a single run, no significance tests. Each relation's best head is picked on the data used to score it. The authors decline to claim that single heads capture dependency structure overall, give no probe hyperparameters, and say they examine what attention stores rather than what drives predictions.
- Voita et al.: translation into three languages with a Transformer-base encoder-decoder; only four dependency relations; BLEU alone, no variance or seeds; the result applies to trained models.
- Jain and Wallace: Kendall tau across all tokens may be lowered by irrelevant features; gradients and leave-one-out are not ground truth; adversarial attention shows other heatmaps exist without showing the model would produce them; no transformers or seq2seq; seeds and training settings are missing. The authors allow that a "sufficient" explanation may be reasonable.

## See Also
- [[Transformer Architecture]] — prerequisite-for
- [[Edge Probing and Layer Localisation in BERT]] — related (layer-level probing of the same encoder)
- [[Integrated Gradients]] — related (gradient-based feature importance)
- [[Efficient Attention Approximations]] — related
