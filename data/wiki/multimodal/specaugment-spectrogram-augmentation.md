---
title: SpecAugment Spectrogram Augmentation
tags: [multimodal, method]
summary: "SpecAugment applies time warping, frequency masking and time masking to the log mel spectrogram during training, turning ASR overfitting into underfitting."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-park-2019-specaugment.md
---

# SpecAugment Spectrogram Augmentation

The question is whether a cheap augmentation applied straight to the log mel spectrogram can let end-to-end ASR networks overtake hybrid systems on LibriSpeech and Switchboard. The hypothesis is that if features survive time deformation and the loss of some frequency bands or short speech stretches, the network learns more useful features and overfits less.

## Mechanism

Three deformations act online on the log mel spectrogram, which is treated like an image: time warping, frequency masking and time masking. LAS encoder-decoder networks learn under long ramp-hold-decay schedules for the learning rate, and some results add shallow fusion with an RNN LM. The authors state that augmentation turns overfitting into underfitting, so larger networks and longer schedules pay off.

## Results

- LAS-6-1280 reaches 6.8% test-other without LM and 5.8% with LM fusion, which the paper presents as 22% relative better than the best earlier hybrid (self-reported). Setup: LibriSpeech 960h, the long schedule L (about 24 days), policy LD, and the checkpoint with the best dev-other score.
- Without SpecAugment, the same model reaches 12.5% test-other and uses no LM (self-reported).
- Test-clean is 2.8% without LM and 2.5% with LM (self-reported).
- On Switchboard/CallHome the model reaches 7.2/14.6 without LM and 6.8/14.1 with LM, where the strongest earlier hybrid scores 8.3/17.3 (self-reported). Setup: 300h of Switchboard, LAS-6-1280, policy SM, schedule L.
- Holding the network at LAS-4-1024 on schedule B, test-other improves from 13.4 to 9.2 (self-reported). Setup: no LM, policy LD.
- Ablation (LAS-4-1024, schedule B, no LM): leaving out time warping costs just 0.1 on test-other (10.1 against 10.0), while leaving out frequency masking costs 1.0 and leaving out time masking costs 0.9 (self-reported).

## Limits

- Single runs without seeds or confidence intervals; the 0.1 time-warp difference is within plausible noise.
- Policies are hand-made with no search, and label smoothing makes training unstable when augmentation is combined with a decaying learning rate.
- Compute is heavy: the best models took about 24 days on 32 TPU chips. Only LAS was tried, on English speech, with no noisy or far-field test.
- Switchboard has no dev set, so the checkpoint is taken at schedule end; fusion parameters do not transfer between networks.
- Optimizer, parameter counts and code are not stated.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[Conformer Convolution-Augmented Transformer for ASR]] — related (trained with SpecAugment)
