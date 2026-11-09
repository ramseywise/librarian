---
title: Make-An-Audio Text-to-Audio Latent Diffusion
tags: [multimodal, method]
summary: "Make-An-Audio generates audio with a spectrogram latent diffusion model conditioned on CLAP text embeddings, using distill-then-reprogram pseudo prompts to exploit audio without captions."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-huang-2023-make-audio.md
---

# Make-An-Audio Text-to-Audio Latent Diffusion

The question is how to get high-fidelity text-to-audio generation when text-audio pairs are scarce and raw waveforms are long, and whether the same model can also take audio, image or video as input. The hypothesis is that captions invented for audio without language labels, combined with latent diffusion on spectrograms conditioned through CLAP, beat earlier text-to-audio systems.

## Mechanism

A mel-spectrogram autoencoder compresses audio into a latent with 4 channels. A U-Net latent diffusion model generates latents, with a frozen CLAP text encoder feeding cross-attention and classifier-free guidance applied, and a HiFi-GAN vocoder turns the mel back into a waveform. Pseudo prompt enhancement (distill-then-reprogram) gets captions for unlabeled audio from captioning and retrieval experts, screened by CLAP score, then joins training examples online with sampled sound events (dynamic reprogramming: N in {0, 1, 2} concepts drawn from a database each time).

## Results

- On zero-shot Clotho the model's FID-Z is 17.38, against 24.97 for Diffsound (self-reported).
- CLAP score is 0.482, while reference audio has 0.526 and Diffsound 0.420 (self-reported). Setup: the AudioCaps validation set (494 samples, five captions each), a 332M model.
- A CLAP text encoder gives quality close to T5-Large with fewer parameters (332M against 563M); a CLIP text encoder gives worse FID (self-reported).
- Without pseudo prompt enhancement, zero-shot Clotho FID gets worse and AudioCaps FID moves from 5.15 to 5.37 (self-reported).
- 4 latent channels beat 32 and 128 on FID (self-reported).
- For video-to-audio the MOS-Q is 60.0 against 69.5 for reference audio; for image-to-audio the MOS-F is 78.0 against 76.4 (self-reported).

## Limits

- The authors concede that iterative sampling is slow, that latent diffusion needs a lot of compute, and that quality degrades with less training data.
- Diffsound is the only baseline (stated as the only publicly available text-to-audio model); AudioGen is not compared.
- The paper gives no MOS rater counts, sampler step count, guidance scale, batch size, optimizer or seeds.
- The visual-to-audio model is a variant trained on 110h of FSD50K.
- Internal inconsistencies: the text claims the highest CLAP score, yet Table 1 lists T5-Large at 0.486, higher than 0.482; the dataset table is cited as Table 5 while the statistics sit in Table 4.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[Audiobox Unified Audio Generation]] — alternative-to (flow matching for text-to-sound)
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for (guidance used at sampling)
- [[Denoising Diffusion Probabilistic Models]] — prerequisite-for
