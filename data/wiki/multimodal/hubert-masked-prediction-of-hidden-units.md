---
title: HuBERT Masked Prediction of Hidden Units
tags: [multimodal, method]
summary: "HuBERT predicts offline k-means cluster labels for masked speech frames, with the loss on masked frames only and the cluster targets refined over iterations."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-hsu-2021-hubert.md
---

# HuBERT Masked Prediction of Hidden Units

HuBERT targets self-supervised speech representation learning, where one utterance holds several sound units, no sound-unit lexicon is available and there is no segmentation. The hypothesis is that predicting cluster labels only at masked frames tolerates weak clusters, and that consistent targets matter more than correct ones.

## Mechanism

Offline k-means supplies one label per frame, first from MFCC features and later from an intermediate layer of an earlier HuBERT model. A wav2vec 2.0-like convolution-plus-transformer network predicts the labels of masked frames through a softmax over cosine similarities. The loss is L = alpha*Lm + (1 - alpha)*Lu over masked and unmasked frames. For ASR the pretrained models are fine-tuned with CTC. Cluster quality is scored with PNMI, the phone-normalized mutual information (the percentage of uncertainty about the phone label removed by observing the k-means label).

## Results

- Masked-only loss (alpha=1) gives 17.86 dev-other WER, while loss on unmasked frames only (alpha=0) gives 96.37 (self-reported). Setup: a BASE model pretrained for 100k steps on MFCC k-means with 100 clusters, then fine-tuned on 10h of Libri-light and decoded with an n-gram LM.
- Iterating the teacher raises PNMI from 0.276 to 0.637 to 0.704 and lowers WER from 18.40 to 11.91 to 10.75 (self-reported). Setup: BASE model, 100k pretraining steps, 500 clusters, 10h fine-tuning, n-gram LM decoding.
- Combining three k-means runs of 100 clusters each yields 16.73 WER, against 17.86 for one run (self-reported). Setup: the same 100k-step BASE ablation.
- X-LARGE reaches 1.8 WER on test-clean and 2.9 on test-other (self-reported). Setup: pretraining on Libri-light 60k, fine-tuning on 960h of LibriSpeech, Transformer LM decoding.
- With 10 minutes of labels, X-LARGE reaches 4.6 / 6.8 and LARGE 4.7 / 7.6, against 4.8 / 8.2 for wav2vec 2.0 LARGE (self-reported). Setup: 10-minute split, Libri-light 60k pretraining, Transformer LM.
- Training 100k BASE steps takes about 9.5 hours on 32 GPUs (self-reported).

## Limits

- Only English ASR is tested; the paper leaves generation tasks for later work.
- The k-means then re-clustering pipeline runs in several phases, and the authors say they plan a single-phase version.
- It lags methods that combine pretraining with self-training.
- Ablations are single runs at 100k steps with no seeds; GPU type, precision, weight decay and decoding hyperparameters are not stated.

## See Also
- [[Speech and Audio Generation and Recognition]] — related (the family hub)
- [[W2V-BERT Contrastive and Masked Speech Pretraining]] — alternative-to (end-to-end codebook instead of offline re-clustering)
- [[Contrastive Self-Supervised Pretraining]] — prerequisite-for
- [[Real-Time Multimodal Agents]] — related (HuBERT units appear as speech-decoder targets in LLaMA-Omni)
