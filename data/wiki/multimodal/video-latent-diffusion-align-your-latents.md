---
title: "Video Latent Diffusion (Align Your Latents)"
tags: [multimodal, video, concept]
summary: "Video LDM turns a pretrained image latent diffusion model into a video generator by freezing the spatial layers and training only inserted temporal layers, a video-fine-tuned decoder and a video-aware upsampler."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-blattmann-2023-align-your-latents.md
---

# Video Latent Diffusion (Align Your Latents)

Blattmann and colleagues ask whether adding temporal layers to a pretrained image LDM, and training just those, is enough to get a high-resolution video generator. Numbers are self-reported.

## Mechanism

- The spatial layers of an image LDM (or Stable Diffusion) are frozen. Temporal attention and 3D-convolution residual layers are interleaved with them and trained on encoded video. A learned alpha merges the spatial and temporal paths: z' = alpha z + (1 - alpha) z'.
- The first-stage decoder is also given temporal layers, plus a patch discriminator that works on video.
- A cascade of models gives long, high-resolution output: prediction models (0, 1 or 2 context frames), interpolation models (T to 4T, then 4T to 16T) and a 4x video-aware upsampler. **Context guidance** applies classifier-free guidance to the conditioning on context frames.
- The trained temporal layers can be combined with other image checkpoints, DreamBooth for example.

## Findings

- Fine-tuning the decoder on video brings reconstruction FVD on driving videos down, 390.88 to 32.94, with FID rising from 7.61 to 9.17 (RDS, 128x256, 2,048 examples). WebVid improves under the same fine-tuning (35.82 to 18.66), as does Mountain Biking (73.78 to 25.55). Adding an image discriminator worsens FVD (51.01 against 32.94).
- Against Long Video GAN on RDS 128x256, unconditional: FVD 389 against 478 and FID 31.6 against 53.5. With day/night and crowdedness conditioning FVD falls to 356 while FID goes up to 51.9. In a rater study the conditional model was preferred 62.03% to 31.65% (100 videos of 4 s, each pair judged by 4 MTurk raters).
- On Mountain Biking the Video LDM wins on FID (7.73 against 21.1) and human preference (54.2 against 42.2) but loses on FVD (118 against 85.3).
- Fine-tuning the pixel-space 4x upsampler on video drops FVD from 165.98 to 45.39 (FID 19.71 against 19.85).
- Ablations on a smaller Video LDM (RDS 128x256): image pretraining matters (FVD 1155.10 without against 534.17); 3D-conv plus attention beats attention-only (534.17 against 704.41 at equal trainable parameters); context guidance brings FVD to 508.82 but costs FID (54.16 against 48.26). Training the temporal layers does little harm to image quality (FID 47.00 at alpha = 1; 48.26 otherwise).
- Zero-shot UCF-101, model built on SD 2.1, 10k samples: IS 33.45, FVD 550.61, where FVD lags Make-A-Video (367.23) and IS is a little higher (33.00). A model built on SD 1.4 scores worse (IS 29.49, FVD 656.49). Zero-shot MSR-VTT CLIPSIM is 0.2929 against Make-A-Video 0.3049 and CogVideo 0.2631.
- The text-to-video LDM built on SD has about 3.1B parameters in total with about 2.2B of them trained, compared with 11.6B for Imagen Video. Videos of up to 5 minutes were validated on driving data.

## Limits

- The authors state the models are unfit for productisation; the training data are scraped from the internet for research use only.
- Generated videos can still be told apart from real ones; the authors flag the risk of deceptive realism.
- Long text-to-video generation that is convolutional in time is fragile, and text-to-video prediction models are left to future work.
- Make-A-Video, a concurrent work, scores better than this text-to-video model on UCF-101 FVD and on MSR-VTT CLIPSIM.
- Fine-tuning the spatial layers on WebVid costs a little image quality; the authors also accept that FVD is unreliable.
- RDS is an in-house dataset, so outsiders cannot reproduce the headline results; seeds and optimiser are not given.

## See Also

- [[Latent Diffusion Models]] — prerequisite-for
- [[Video Diffusion Models]] — alternative-to
- [[AnimateDiff Motion Module]] — related (network inflation practice, per its extraction)
- [[Cascaded Diffusion Models]] — prerequisite-for
- [[Diffusion and GAN Image Generation]] — prerequisite-for
