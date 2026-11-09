---
title: Speech and Audio Generation and Recognition
tags: [multimodal, comparison]
summary: "A map of the speech and audio methods in the wiki by job: self-supervised speech encoders and ASR, neural codecs, generation of speech and sound, speech translation, and speech inputs to language models."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-chung-2021-w2v-bert.md
  - data/raw/papers/2026-11-07-defossez-2022-high-fidelity-neural-audio-compression.md
  - data/raw/papers/2026-11-07-gulati-2020-conformer.md
  - data/raw/papers/2026-11-07-hsu-2021-hubert.md
  - data/raw/papers/2026-11-07-huang-2023-make-audio.md
  - data/raw/papers/2026-11-07-wang-2023-neural-codec-language-models-zero.md
  - data/raw/papers/2026-11-07-zeghidour-2021-soundstream.md
  - data/raw/papers/2026-11-07-zellers-2022-merlot-reserve.md
  - data/raw/papers/2026-11-08-ardila-2019-common-voice.md
  - data/raw/papers/2026-11-08-communication-2023-seamlessm4t.md
  - data/raw/papers/2026-11-08-le-2023-voicebox.md
  - data/raw/papers/2026-11-08-park-2019-specaugment.md
  - data/raw/papers/2026-11-08-seamless-2023.md
  - data/raw/papers/2026-11-08-shu-2023-llasm.md
  - data/raw/papers/2026-11-08-team-2025-omnilingual-asr.md
  - data/raw/papers/2026-11-08-vyas-2023-audiobox.md
  - data/raw/pdfs/2016-09-12-wavenet.md
---

# Speech and Audio Generation and Recognition

The speech and audio papers in the wiki answer five different questions. Each per-method page holds its own setups, self-reported numbers and limits; this page only orders them. Figures from different papers use different test sets, so the table compares what each method does, not whose number is higher.

## By job

| Job | Methods | What each trains |
|---|---|---|
| Recognition encoders | [[Conformer Convolution-Augmented Transformer for ASR]], [[SpecAugment Spectrogram Augmentation]] | a block that mixes attention and convolution; an augmentation on log mel spectrograms |
| Self-supervised speech pretraining | [[HuBERT Masked Prediction of Hidden Units]], [[W2V-BERT Contrastive and Masked Speech Pretraining]] | masked prediction of offline k-means labels; contrastive and masked prediction losses together |
| Neural codecs (audio to discrete codes) | [[SoundStream Neural Audio Codec]], [[EnCodec Neural Audio Compression]] | an encoder, a residual vector quantizer and a decoder trained against adversaries |
| Speech and sound generation | [[VALL-E Neural Codec Language Model TTS]], [[Voicebox Flow-Matching Speech Infilling]], [[Audiobox Unified Audio Generation]], [[Make-An-Audio Text-to-Audio Latent Diffusion]], [[WaveNet — Autoregressive Audio Generation]] | codec-token language model; flow matching on Mel frames; flow matching on codec latents; latent diffusion on spectrograms; sample-by-sample waveform model |
| Translation and multilingual recognition | [[SeamlessM4T Multilingual Speech Translation]], [[Seamless Expressive and Streaming Translation]], [[Omnilingual ASR]] | one multitask model across many languages |
| Data | [[Common Voice Multilingual Speech Corpus]] | crowdsourced read speech with vote-based validation |

## Threads that connect them

- **Self-supervised encoders feed recognition and translation.** HuBERT and W2V-BERT both predict targets at masked frames and differ in where the targets come from (offline clusters versus a codebook trained jointly). SeamlessM4T builds a w2v-BERT 2.0 encoder, and Omnilingual ASR scales a wav2vec 2.0 encoder to 7B parameters.
- **Codecs turn audio into tokens.** EnCodec extends SoundStream; VALL-E uses EnCodec codes as its language-model vocabulary and Audiobox runs flow matching on EnCodec latents. The EnCodec paper itself evaluates reconstruction quality only, not use of the codes as tokens for language models.
- **Autoregressive versus non-autoregressive generation.** VALL-E predicts the first quantizer autoregressively and the rest non-autoregressively; Voicebox is non-autoregressive throughout and infills masked frames, so different tasks become different masks. Its paper reports speed that depends on the number of ODE evaluations.
- **Diffusion and flow matching for sound.** Make-An-Audio generates spectrogram latents with classifier-free guided diffusion; Audiobox adds description and voice-prompt control on a flow-matching model.
- **Cascades versus direct models.** SeamlessM4T reports direct models beating cascades on automatic S2TT and S2ST metrics while human S2ST ratings for X-eng favour the cascade, linked by its authors to truncation in longer inputs.

## Speech into language models and video models

LLaSM (arXiv 2308.15930) feeds Whisper audio embeddings through a modal adaptor into Chinese-LLAMA2-7B so the model follows spoken instructions without an ASR step. Training first updates only the adaptor on public ASR data, then updates the adaptor and the LLM on instructions voiced with TTS. It releases LLaSM-Audio-Instructions, 199k conversations and 508k samples (428k English, 80k Chinese) (self-reported), voiced with Azure TTS from text of WizardLM, ShareGPT and GPT-4-LLM. It follows the two-stage recipe of [[LLaVA Visual Instruction Tuning]]. The authors call it the largest dataset of its kind, with no comparison shown. Section 4 gives only example conversations, with no WER, benchmark or baseline; the training hyperparameters and adaptor design are not given, the speech inputs are synthetic, and outputs are text only.

[[MERLOT Reserve Audio-Video-Text Pretraining]] adds audio to video-language pretraining and reports gains on TVQA and Kinetics-600 from audio input.

## Limits

- The papers use different languages, datasets and metrics (WER, CER, MUSHRA, ViSQOL, BLEU variants, FAD), so no ranking across rows is claimed here.
- Most results are self-reported, single runs without seeds, and several papers do not release code or weights.

## See Also
- [[W2V-BERT Contrastive and Masked Speech Pretraining]] — instance-of
- [[HuBERT Masked Prediction of Hidden Units]] — instance-of
- [[Conformer Convolution-Augmented Transformer for ASR]] — instance-of
- [[SpecAugment Spectrogram Augmentation]] — instance-of
- [[SoundStream Neural Audio Codec]] — instance-of
- [[EnCodec Neural Audio Compression]] — instance-of
- [[VALL-E Neural Codec Language Model TTS]] — instance-of
- [[Voicebox Flow-Matching Speech Infilling]] — instance-of
- [[Audiobox Unified Audio Generation]] — instance-of
- [[Make-An-Audio Text-to-Audio Latent Diffusion]] — instance-of
- [[SeamlessM4T Multilingual Speech Translation]] — instance-of
- [[Seamless Expressive and Streaming Translation]] — instance-of
- [[Omnilingual ASR]] — instance-of
- [[Common Voice Multilingual Speech Corpus]] — instance-of
- [[MERLOT Reserve Audio-Video-Text Pretraining]] — related
- [[WaveNet — Autoregressive Audio Generation]] — prerequisite-for
- [[Real-Time Multimodal Agents]] — related
- [[Voice Agent Paradigms]] — related
