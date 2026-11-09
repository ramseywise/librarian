---
title: Conformer Convolution-Augmented Transformer for ASR
tags: [multimodal, method]
summary: "The Conformer encoder block sandwiches self-attention and a convolution module between two half-step feed-forward modules to model global and local dependencies in speech recognition."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-gulati-2020-conformer.md
---

# Conformer Convolution-Augmented Transformer for ASR

The question is how to join convolution and self-attention in one ASR encoder so that it captures both local and global structure with few parameters. The hypothesis is that both interactions matter, so a block holding the two beats a block with either alone.

## Mechanism

A Conformer block puts a multi-headed self-attention module and a convolution module between two feed-forward modules, uses half-step residual weights on the feed-forward modules, and ends in a layernorm. Self-attention uses relative positional encoding. In the paper's notation the block computes x~ = x + 1/2 FFN(x), then x' = x~ + MHSA(x~), then x'' = x' + Conv(x'), and outputs y = Layernorm(x'' + 1/2 FFN(x'')). The full encoder is a convolution subsampling stage and N such blocks, paired with a transducer decoder built on one LSTM layer. It is trained on LibriSpeech 960h at three sizes (10M, 30M, 118M), with ablations on the large model.

## Results

- Conformer(L), 118.8M parameters, reaches 2.1% test-clean WER with no LM (self-reported), and 3.9% test-other with a 3-layer LSTM LM by shallow fusion (self-reported).
- Conformer(S), 10M parameters, gets 2.7% / 6.3% test / test-other without LM (self-reported).
- Conformer(M), 30.7M parameters, scores 2.3 / 5.0 without LM against 2.4 / 5.6 for a 139M Transformer Transducer (self-reported).
- With the external LM, test-other improves 15% relative over the Transformer Transducer (4.6 to 3.9) (self-reported).
- Ablations on the large model without LM: taking out the convolution block raises test-other WER from 4.3 to 4.9; taking out relative positional embedding gives 5.6; swapping the paired macaron feed-forward modules for one feed-forward module gives 5.0 in one table and 4.5 in another (self-reported).
- More attention heads help up to 16, and kernel size 32 is best on dev WER (self-reported). Setup: large model, no LM.

## Limits

- Only LibriSpeech (read audiobooks) is used, so noisy, accented and conversational speech are untested; the model is scored as a full-context offline encoder and streaming is not studied.
- Runs are single, without seeds, and WER has one decimal place, so numerous ablation differences are just 0.1.
- Batch size, number of steps, hardware, compute and LM weight go unstated, and no code or weights are released.
- Ablations ran only on the large model, and two tables disagree on the single-feed-forward result (5.0 against 4.5).

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[W2V-BERT Contrastive and Masked Speech Pretraining]] — extends (uses Conformer as its building block)
- [[SpecAugment Spectrogram Augmentation]] — related (the Conformer paper trains with SpecAugment)
- [[Transformer Architecture]] — prerequisite-for
