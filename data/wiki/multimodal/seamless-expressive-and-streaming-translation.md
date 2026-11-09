---
title: Seamless Expressive and Streaming Translation
tags: [multimodal, system]
summary: "The Seamless family adds SeamlessM4T v2, expressive speech translation with a prosody-aware generator, and EMMA-based streaming translation, plus red teaming and watermarking."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-seamless-2023.md
---

# Seamless Expressive and Streaming Translation

The question is whether one family of models can translate speech among many languages, keep the speaker's vocal style and prosody, and stream with low latency.

## Mechanism

SeamlessM4T v2 is a multitask S2ST model of 2.3B parameters: a w2v-BERT 2.0 encoder, an NLLB text model and UnitY2, a non-autoregressive text-to-unit decoder. SeamlessExpressive adds Prosody UnitY2 and PRETSSEL, an expressive acoustic model. SeamlessStreaming fine-tunes v2 in two stages using EMMA monotonic attention, and Seamless joins streaming with PRETSSEL. The release also includes SeamlessAlign grown by 114,800 hours to cover 76 languages, the MuTox and MinTox tools for red-teaming and toxicity, the SeamlessWM watermark and the AutoPCP expressivity metric.

## Results

- In the teacher T2U ablation over 32 languages, the non-autoregressive decoder with character input and non-reduced units gets 13.41 ASR-WER, where the best autoregressive decoder gets 20.79 (self-reported).
- On Fleurs X-eng S2ST, v2 reaches 22.2 ASR-BLEU, and under noise it improves on Whisper-Large-v2 for X-eng S2TT by 53.2% on average (self-reported).
- On mExpresso X-eng the best expressive model gets 39.00 ASR-BLEU and an AutoPCP of 3.18, while the plain model gets 2.16 AutoPCP (self-reported).
- PRETSSEL (65M parameters) is cheaper to run than Unit Voicebox (329M), but adding it lowers MOS sound quality and clarity (self-reported).
- Per item, AutoPCP correlates with human PCP at 0.49 on average (self-reported).
- Streaming speech output at t_EMMA 0.5 gives up 7.6 ASR-BLEU compared with offline on X-eng; the relative S2TT BLEU loss grows as resource level falls, reaching 31.4% for zero-shot languages (self-reported). Setup: Fleurs, 101 source languages.

## Limits

- Only automatic evaluation was run for the unified Seamless model; human PCP for eng-X is incomplete, and the X-eng PCP leaves out cmn and fra.
- Time pressure meant the expressive models were trained without filtering for semantic and prosodic quality, and joint training lowers VSim and AutoPCP.
- Against offline decoding, streaming gives up 10-31% of BLEU, most in zero-shot languages, where it also over-generates.
- Expressive covers 5 non-English languages and drops phrase-level rate and pause preservation. Gender overgeneralization is not improved over v1, and T2TT chrF drops 1.6.
- Red-team prompts were not the same across models, so the toxicity results do not line up directly.
- Hyperparameters, hardware and seeds are not stated; models are research-only and the PDF gives no arXiv id.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[SeamlessM4T Multilingual Speech Translation]] — prerequisite-for (the first release this extends)
- [[Voicebox Flow-Matching Speech Infilling]] — prerequisite-for (Unit Voicebox is used for vocal-style conversion data)
