---
title: Omnilingual ASR
tags: [multimodal, system]
summary: "Omnilingual ASR scales a wav2vec 2.0 encoder to 7B parameters over 1,600+ languages and adds an LLM-style decoder that can transcribe unseen languages from a few in-context examples."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-team-2025-omnilingual-asr.md
---

# Omnilingual ASR

The question is whether one ASR system can handle more than 1,600 languages, including long-tail ones with scant data, and let communities add a language the model never saw by giving a few in-context examples. The hypothesis is that, since the corpus spans so many languages, a decoder trained with N speech-text context pairs from one language carries over to languages absent from training.

## Mechanism

The encoder is a wav2vec 2.0 model grown to 7B parameters, with 4.3M hours of unlabeled speech as its pretraining data. It is then fine-tuned on AllASR, a unified labeled corpus of 1,690 languages, using either a linear CTC head or a Transformer decoder of 1.2B parameters (LLM-ASR). The zero-shot variant places N context speech-text pairs in the decoder prompt and is trained on N+1 pairs from one language. Language and script conditioning and speech translation need only small changes. Languages are bucketed by labeled hours: high above 50, mid from 10 to 50, low below 10.

## Results

- In most of the FLEURS-81 languages the 7B LLM-ASR does better than Whisper large-v3, and on FLEURS-102 it edges out the best USM variant (self-reported). Setup: test CER; USM numbers are published values.
- On Common Voice 22, covering 76 languages, Whisper large-v3 has a test CER of 55.6 against 6.4 for the 7B LLM-ASR; on MLS-8, the high-resource set, Whisper stays ahead (self-reported).
- Most of the 1,570 evaluated languages reach CER of 10 or lower, but the low-resource bucket averages 18.0-18.6, and just 34-36% of its languages get under CER 10 (self-reported).
- Zero-shot with 10 context examples lowers CER on unseen languages; choosing the examples with SONAR beats choosing them at random (self-reported). Setup: 32 held-out languages.
- Across 13 languages in common, adding the Omnilingual and OMSF data lowers CER from 39.46 to 11.50 (self-reported).
- After the same CTC fine-tuning on FLEURS-102, the 7B encoder outperforms the XLS-R and MMS encoders (self-reported). OmniASR-LLM-7B scores 37.1 BLEU on CoVoST2 21-Eng.

## Limits

- Zero-shot quality falls short of fully trained systems and drops on some languages that were seen in training, which is why separate models are released for those.
- The zero-shot study held out 32 languages, half of them high-resource; unseen-language CER of 14.4 remains high, and the context examples were drawn at random from one dataset. Two of the selection methods read the target transcript, so they act as oracles.
- Dev and test sets are heterogeneous, and the authors caution against comparing across benchmarks.
- Detailed QA found a critical mismatch in about half of the commissioned transcripts; language-code validation covered 206 languages, of which 20 had wrong codes.
- No seeds, only confidence intervals across languages; GPU type and total compute are not stated. The authors note surveillance and moderation misuse risks.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[SeamlessM4T Multilingual Speech Translation]] — related (S2TT comparison and training data)
- [[Common Voice Multilingual Speech Corpus]] — prerequisite-for (a training and evaluation source)
