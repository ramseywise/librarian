---
title: "W2V-BERT Contrastive and Masked Speech Pretraining"
tags: [multimodal, method]
summary: "W2V-BERT trains wav2vec 2.0's contrastive task and a masked prediction task over the quantizer's token IDs together, end to end, for self-supervised speech pretraining."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-chung-2021-w2v-bert.md
---

# W2V-BERT Contrastive and Masked Speech Pretraining

W2V-BERT asks whether a BERT-like masked objective over learned discrete speech units can be optimised in the same run as the wav2vec 2.0 contrastive objective, and whether the combination improves ASR over contrastive-only pretraining. The stated hypothesis is that the contrastive task produces a discriminative codebook whose token IDs make good targets for masking, which avoids the repeated re-clustering rounds of [[HuBERT Masked Prediction of Hidden Units]].

## Mechanism

Three parts are pre-trained jointly on unlabeled speech: a conformer feature encoder; a contrastive module made of a quantizer and a conformer stack; and a masked-prediction module, a conformer stack with a softmax over the quantizer's token IDs. The combined loss is Lp = beta*Lc + gamma*Lm, with beta and gamma both 1 and the contrastive loss Lc = Lw + alpha*Ld with alpha 0.1. For downstream use the encoder is fine-tuned under an LSTM sequence-transducer decoder, on LibriSpeech or on an internal Voice Search set. The encoder block is the [[Conformer Convolution-Augmented Transformer for ASR]].

## Results

- Dropping the contrastive module makes every model collapse: masked loss near 0, accuracy 100%, diversity loss near 1 (24 conformer layers). The extraction notes that the explanation for the collapse rests on training curves and is a hypothesis, not a controlled test.
- Contrastive module depth: test-other WER 4.6 with 8 contrastive layers versus 5.1 with 2, 4.6 with 12 and 5.0 with 24 (self-reported). Setup: LibriSpeech 100hr, 24 layers in total, no self-training or LM.
- Voice Search: an untuned w2v-Conformer-XL does not beat a supervised 100M Conformer (10.8 vs 10.7 WER); a tuned contrastive baseline used 3 stacked frames instead of a 4x conv stride (self-reported). Setup: 34.3k hours of voice-search pretraining, 1k hours fine-tuning, about 12k test utterances, all 600M XL models.
- The abstract claims a Voice Search improvement of more than 30% over an internal wav2vec 2.0 model (self-reported).

## Limits

- Voice Search pretraining and test data are internal, and the paper states no code or weights; the low-resource Libri-Light splits (10min, 1hr, 10hr) were not run.
- Baselines come from published numbers rather than reruns.
- The wav2vec 2.0 and w2v-BERT systems compared differ in model size and in language-model size.
- Single runs with no seeds or significance tests; no compute or total pretraining steps are stated. English only.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[HuBERT Masked Prediction of Hidden Units]] — alternative-to (offline-cluster targets instead of an end-to-end codebook)
- [[Conformer Convolution-Augmented Transformer for ASR]] — prerequisite-for (the building block)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for
- [[SeamlessM4T Multilingual Speech Translation]] — extends (w2v-BERT 2.0 is its speech encoder pretraining)
