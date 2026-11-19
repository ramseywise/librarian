---
title: Adaptive Input Representations
tags: [llm, architecture, concept]
summary: "Baevski and Auli give frequent words larger input embeddings and rare words smaller ones, shrinking the dimension by a factor of 4 per frequency band, and compare it with word, BPE and character-CNN input layers in a decoder-only transformer language model."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-baevski-2018-adaptive-input-representations-neural-language.md
---

# Adaptive Input Representations

Baevski and Auli ask how a self-attentional language model should factorise its input and output layers (word, character CNN, sub-word or adaptive) for the best accuracy and speed. Their hypothesis: frequent words get larger embeddings and rare words smaller ones, the way adaptive softmax treats outputs, which curbs overfitting to rare words and lowers the parameter count while raising accuracy.

## Mechanism

- The vocabulary is ordered by frequency and split into clusters; the embedding dimension shrinks by a factor k = 4 per cluster and each is projected to a common dimension d.
- The input layer can be tied with an adaptive softmax output (ADP-T).
- Tail dropout is applied to the adaptive softmax.
- The model is a decoder-only transformer, compared under an identical architecture against fixed word, BPE and character-CNN input and output layers.

## Results (all self-reported, single runs)

- WikiText-103 (247M parameters, 3072-token training blocks, 2560 context at evaluation, 8 GPUs, 67 hours): 18.7 test perplexity, 10.5 better than the previous best. Billion Word (very large model, 1026M parameters, 64 GPUs, 145 hours): 23.02.
- WikiText-103, 512-token blocks, equal number of updates, 8-GPU machine: ADP-T is about 1 perplexity point better than a character CNN and takes 30 hours where the character CNN takes 70.
- Using 3072-token training blocks in place of 512 gives a WikiText-103 perplexity gain of almost 1.2 when no context is used at inference.
- Tail dropout 0.2 lowers WikiText-103 validation perplexity from 24.74 to 21.23 (adaptive softmax, 64-dimension input embeddings), below the full softmax at 23.87.
- Input plus output parameters fall 23%, and 61% when tied with an adaptive softmax, in the competitive Billion Word setup against fixed-size embeddings.

## Limits

- Document boundaries are ignored, left to future work.
- Tail dropout does not help on Billion Word, and a full softmax over 800K words is intractable, so there is no comparison.
- Single runs without seeds or significance. Baseline embedding sizes were tuned on validation under 16GB GPU memory limits, and band sizes were not tuned per band for dropout.

## See Also

- [[Transformer Architecture]] — prerequisite-for
- [[Transformer-XL Segment Recurrence]] — related (compares against it as a contemporary baseline)
- [[Pointer Sentinel Mixture Models and WikiText]] — related (WikiText-103 benchmark)
