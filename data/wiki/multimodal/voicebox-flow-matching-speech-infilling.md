---
title: Voicebox Flow-Matching Speech Infilling
tags: [multimodal, method]
summary: "Voicebox is a non-autoregressive flow-matching model trained to infill masked Mel frames given a phone transcript, so zero-shot TTS, denoising and editing become different context masks."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-le-2023-voicebox.md
---

# Voicebox Flow-Matching Speech Infilling

The question is whether one non-autoregressive speech model, trained at scale to infill masked speech given text, can do many speech generation tasks in context and outperform systems built for single tasks. The hypothesis is that scale plus a flexible infilling objective trained with flow matching lets speech models handle tasks they were not trained on, as language models do.

## Mechanism

Voicebox is a continuous normalizing flow trained with flow matching on an optimal-transport path. It fills in masked 80-dimensional Mel frames from the audio around them and a phone transcript aligned per frame, while a separate duration model, either regression or flow matching, sets lengths. Zero-shot TTS, denoising, editing, style transfer and diverse sampling differ only in which context mask is used at inference. Guidance in the style of classifier-free guidance is extended to the flow by mixing the conditioned and unconditioned vector fields with a weight alpha, and the number of ODE function evaluations (NFE) trades quality for speed.

## Results

- On zero-shot English TTS it beats VALL-E on WER and speaker similarity; the contribution list gives 5.9% to 1.9% WER and 0.580 to 0.681 similarity (self-reported). Setup: filtered LibriSpeech test-clean (4-10 s), a 3 s prompt from a different sentence, NFE 32, HuBERT-L ASR; VALL-E numbers copied from its paper.
- At NFE 2 without guidance it is about 20 times faster than VALL-E for 10 s of audio, but at NFE 64 it is only slightly slower (self-reported). Setup: VALL-E is the authors' reimplementation.
- For zero-shot TTS across six languages, WER falls and similarity rises against YourTTS on English, French and Portuguese (self-reported). Setup: filtered MLS test sets, 3 s context, Whisper large-v2 WER.
- An ASR model trained solely on 281K synthetic utterances lands within about 0.4 (one test condition) and 1.7 (another) absolute WER of one trained on real recordings (self-reported). Setup: RNN-T Conformer; the real-data baseline uses 960 h.
- Flow matching with the OT path trains faster than diffusion-path variants and gives good results at 8 NFEs (self-reported). Setup: a reduced configuration with 1K h of data and a smaller model.
- More training data improves WER and similarity monotonically from 60 h to 60,000 h (self-reported). Setup: reduced setup.

## Limits

- Training covers read audiobook speech in at most six languages; conversational speech with laughter or backchannels may not transfer.
- Depends on a phonemizer and forced aligner; there is no independent control of voice versus emotion.
- VALL-E was not available, so its numbers are copied and the latency comparison uses a reimplementation.
- The paper releases no data, code or weights, and gives neither GPU type nor wall-clock time.
- A lower WER need not mean better quality (regression duration lowers WER partly through being more regular), and with English prompts the cross-lingual WER rises as the prompt grows because English dominates the multilingual data.
- The venue is given as a preprint under review.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[VALL-E Neural Codec Language Model TTS]] — alternative-to (autoregressive codec-token approach to the same task)
- [[Audiobox Unified Audio Generation]] — extends (builds on Voicebox's infilling objective)
- [[Seamless Expressive and Streaming Translation]] — related (uses Unit Voicebox for vocal-style conversion data)
- [[Classifier-Free Diffusion Guidance]] — prerequisite-for (the guidance form extended to flow matching)
