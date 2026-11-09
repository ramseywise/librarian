---
title: SeamlessM4T Multilingual Speech Translation
tags: [multimodal, method]
summary: "SeamlessM4T is one multitask UnitY model for S2ST, S2TT, T2ST, T2TT and ASR across up to 100 languages, built on w2v-BERT 2.0 pretraining, an NLLB text model and mined SeamlessAlign data."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-communication-2023-seamlessm4t.md
---

# SeamlessM4T Multilingual Speech Translation

The question is whether one model can translate speech and text for up to 100 languages over S2ST, S2TT, T2ST, T2TT and ASR tasks, matching or exceeding cascades. The hypothesis is that a direct multitask model, resting on self-supervised speech pretraining, the NLLB multilingual text model and mined speech alignments, can narrow the distance to strong cascades.

## Mechanism

UnitY is a two-pass framework: it writes text first and then predicts discrete acoustic units. Training has three stages. In stage 1 an X2T model (a w2v-BERT 2.0 Conformer speech encoder, a length adaptor, and a text encoder-decoder derived from NLLB) learns S2TT from X into English and English ASR. Stage 2 adds S2TT from English into X plus ASR for other languages. In stage 3 X2T is frozen and a text-to-unit model with 6+6 layers is fine-tuned on 121K hours of S2ST data, alongside a multilingual HiFi-GAN unit vocoder. w2v-BERT 2.0 extends [[W2V-BERT Contrastive and Masked Speech Pretraining]] with product-quantization codebooks and an RPQ masked prediction loss, and was pretrained on 1 million hours. SeamlessAlign holds roughly 470,000 hours of speech-translation pairs aligned automatically, for 37 languages, mined from 4M hours of raw audio with a Sonar margin threshold of 1.15 (k=16). Sonar is a shared fixed-size embedding space covering 200 text languages and 37 speech languages. Blaser 2.0 is a modality-agnostic quality metric. The Large model has 2,326M parameters and Medium 1,151M.

## Results

- On Fleurs X-eng, Large improves on the previous direct S2TT result by 4.2 BLEU (self-reported) and on the strongest cascade (Whisper-Large-v2 with NLLB-3.3B) by 1.3 BLEU, while the bigger cascade leads on eng-X. Setup: Fleurs test, S2TT, 81 X-eng directions and 88 eng-X directions.
- X-eng S2ST is 2.6 ASR-BLEU above the best 3-stage cascade (self-reported). Setup: Fleurs, Whisper-Medium scorer.
- Fleurs ASR word error is lower by 45% than Whisper-Large-v2, over 77 languages both cover (self-reported).
- Human XSTS for X-eng S2ST ends up below the Whisper-Large-v2 plus YourTTS cascade although the automatic metrics rank Large higher; annotators flagged audio problems in 206 Large outputs against 22 for the cascade. A manual check of 50 items found that about half of the sampled Large items cut off the end of the translation, and S2ST XSTS drops past about 8 s of source audio (self-reported).
- Added toxicity for X-eng S2TT is 63% below Whisper-Large-v2 (0.11% against 0.31%) (self-reported). Setup: Fleurs, detection by word list.
- With no gender cue the model favours the masculine form by around 10%, and it holds up about 3% worse on feminine source speech (self-reported).
- Ablation BLEU peaked after adding 400 h of top-ranked mined S2TT data for each direction, and 600 h did worse (self-reported). Setup: a 14-language ablation set, Fleurs dev.

## Limits

- The paper does not report final-model hyperparameters, hardware, compute or seeds. It is a research model, not meant for production, long-form translation or specialised domains.
- Human evaluation spans 24 languages of high and middle resource and is described as preliminary; toxicity and gender checks use word lists, with 81-84% false positives among Fleurs detections.
- Mining reaches only 37 languages, and expressivity, prosody and streaming are out of scope. On CoVoST 2 X-eng it trails AudioPaLM by 3.7 BLEU.
- The paper's numbers disagree with each other in places: the CVSS gain (58% / 50% / 14 points), and the robustness to noise and speakers (38% and 49% in the abstract, but 49.4% plus 33.3% and 42.2% in the body).

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[Seamless Expressive and Streaming Translation]] — extends (v2, expressive and streaming variants)
- [[Omnilingual ASR]] — related (compares on S2TT and shares the wav2vec 2.0 line)
- [[W2V-BERT Contrastive and Masked Speech Pretraining]] — prerequisite-for
