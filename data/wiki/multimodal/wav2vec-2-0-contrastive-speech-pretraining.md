---
title: wav2vec 2.0 Contrastive Speech Pretraining
tags: [multimodal, speech-and-audio, concept]
summary: "wav2vec 2.0 masks spans of CNN latents, builds contexts with a Transformer and picks the true product-quantized latent among 100 distractors, then fine-tunes with CTC; 10 minutes of labels give 4.8/8.2 WER with a Transformer LM."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-baevski-2020-wav2vec-2-0.md
---

# wav2vec 2.0 Contrastive Speech Pretraining

Baevski et al. ask whether speech representations learned from audio without transcripts, followed by fine-tuning on a small amount of labelled data, can equal or surpass semi-supervised speech recognition. They expect that a model which has absorbed the structure of speech needs few labelled examples to adapt.

## Method

A CNN feature encoder turns raw audio into latents, spans of which are masked before a Transformer builds contextual representations. The contrastive task is to pick the true Gumbel-softmax product-quantized latent for a masked step out of 100 distractors, with an added diversity loss: L = Lm + alpha*Ld, where Lm is the negative log of exp(sim(c_t,q_t)/kappa) over the sum of the same quantity across candidates. The quantizer is trained jointly with this task. Afterwards the model is fine-tuned on labelled data with CTC and a SpecAugment-like masking scheme.

## Results (self-reported; word error rate test-clean/test-other, Librispeech)

- Full 960h labelled: LARGE pretrained on LV-60k with a Transformer LM reaches 1.8/3.3. Trained from scratch with the same architecture it gets 2.1/4.6. A noisy-student system with an LSTM LM scores 1.7/3.4, still ahead of wav2vec 2.0 on test-clean.
- 10 minutes of labels (48 recordings), LARGE LV-60k with Transformer LM: 4.8/8.2; decoded with no LM, 40.2/38.7; with a 4-gram LM the dev/test others scores are 9.8/10.3 against 7.9/8.2 with the Transformer LM.
- 100h labelled, LARGE LV-60k, Transformer LM: 2.0/4.0, against 4.2/8.6 for noisy student (LS-860). With matched LS-960 pretraining the result is 2.3/5.0, which cuts relative error by 45% and 42% against iterative self-training. With 1h labelled, LS-960 gets 3.9/7.6, 7% and 12% better than noisy student trained on 100h, so it needs 100 times less labelled data. With 10h it gets 3.2/6.1, a relative reduction of 24% and 29%.
- TIMIT, LARGE LS-960, no LM: phone error 7.4 dev and 8.3 test, a 23%/29% relative reduction over vq-wav2vec.
- Ablations (BASE, LS-960, 250k updates, fine-tuning on train-10h for 60k updates, 3 seeds): quantizing only the targets while keeping continuous inputs works best at 7.97 average dev WER, versus 12.18 with both quantized. Continuous targets reach 8.58 and lift pretraining accuracy from 62% to 78.0%. Learning the discrete units jointly reduces WER by about one third relative to Discrete BERT, which quantizes separately.

## Limits

- Character-level CTC is paired with a word-level LM, and the authors say this delays LM feedback; they expect sequence-to-sequence models and word pieces to help. Combining with self-training is untried, though the authors think the two likely complement each other. Data is English only (Librispeech or LibriVox, TIMIT), so the multilingual claim is a hope from the broader-impact section; the ablations use a smaller setup (BASE, 250k updates, train-10h).
- Internal inconsistencies: the Section 5.1 text quotes 5.2/8.6 for the 10-minute LARGE LV-60k model but Table 1 lists 4.8/8.2; the ablation text gives p=0.065 as the baseline masking probability whereas the Table 5 label says p=0.075, and the main models in Section 4.2 use p=0.065.

## See Also
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for
- [[HuBERT Masked Prediction of Hidden Units]] — alternative-to
- [[W2V-BERT Contrastive and Masked Speech Pretraining]] — extends
- [[SpecAugment Spectrogram Augmentation]] — related
- [[Speech and Audio Generation and Recognition]] — related
- [[Contrastive Visual Representations: SimCLR, MoCo, CPC v2 and PIRL]] — related (the same contrastive-loss family on images)
