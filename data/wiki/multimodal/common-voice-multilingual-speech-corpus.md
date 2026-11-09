---
title: Common Voice Multilingual Speech Corpus
tags: [multimodal, benchmark]
summary: "Common Voice is a crowdsourced, CC0 multilingual read-speech corpus with vote-based validation and speaker-disjoint splits, evaluated with DeepSpeech transfer learning from English."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-ardila-2019-common-voice.md
---

# Common Voice Multilingual Speech Corpus

The question is whether a crowdsourced, openly licensed multilingual speech corpus can be built, and whether it can drive end-to-end ASR research for languages with little data. The hypothesis tested is that reusing layers of a pre-trained English DeepSpeech model lowers character error rate (CER) on target languages.

## Construction

Contributors read prompted sentences, and other contributors vote each clip valid or invalid. The train, dev and test splits are speaker-disjoint, so no training speaker appears at test time. The paper says it sized test and dev for 99% confidence and a 1% margin of error relative to the training set. The corpus is released under CC0. In the ASR experiment DeepSpeech v0.3.0 starts from an English model, copies 0 to 5 of its layers for each target language, and is fine-tuned there; CER, the Levenshtein distance between reference and decoded characters, is the score.

## Results

- For most of the 12 target languages, the best final model came from copying four English layers (self-reported). Setup: Table 3 and Fig 5, internal splits from Feb 2019.
- Chuvash shows the largest CER drop from 4 copied layers compared with training from scratch (self-reported). Setup: 1,023 training clips, 5 training speakers.
- Slovenian also improves with 4 layers (self-reported). Setup: 728 train clips.
- German, the largest language, gains almost nothing from transfer (self-reported). Setup: 65,745 training clips, best at 3 layers.

## Limits

- CER was picked over WER as less tied to a language; WER can mislead where words are not separated by whitespace.
- The experiments use an internal version from Feb 2019, and its splits differ from the official releases. A few training sets have very few speakers (Tatar 3, Slovenian 3).
- Each setting was run once, with no seeds or significance tests, and the headline gain has a large standard deviation.
- Only DeepSpeech v0.3.0 and CER were used: there is no WER, and no breakdown by noise, accent or demographics.
- Validation relies on crowd votes (2 votes), and early bugs in voting left some clips with over 3 votes. Prompts are read speech, not spontaneous.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[Omnilingual ASR]] — related (Common Voice 22 is one of its evaluation sets)
