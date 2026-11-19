---
title: "Semi-Supervised Sequence Learning: LM-LSTM and SA-LSTM"
tags: [llm, pretraining-and-data, concept]
summary: "Dai and Le initialise a supervised LSTM classifier from an LSTM pretrained either as a next-step language model or as a sequence autoencoder, reaching 7.24% IMDB error where a randomly initialised LSTM got 13.50%."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-dai-2015-semi-supervised-sequence-learning.md
---

# Semi-Supervised Sequence Learning: LM-LSTM and SA-LSTM

Dai and Le ask whether pretraining an LSTM on unlabeled sequences stabilises and improves later supervised LSTM text classification. They propose that the sequence autoencoder, able to memorise its input and offering short gradient paths, makes a stable and useful starting point, and that more unlabeled data should generalise better; the memorisation and shortcut reasoning is not tested.

## Method

The LSTM is pretrained in one of two ways. **LM-LSTM** is a next-step recurrent language model. **SA-LSTM** is a sequence autoencoder whose encoder and decoder share weights: it reads the whole document and then reproduces it. The embeddings and LSTM weights then seed a classifier that predicts the label from its final timestep and is tuned end to end, stopping early. Other terms: **linear label gain** puts the label at every timestep and raises the prediction weights linearly from 0 to 1; **joint training** trains the supervised task together with the autoencoder. See [[LSTM: Constant Error Carousel and Gated Memory Cells]].

## Results (self-reported)

IMDB setup: 25,000 labeled and 50,000 unlabeled training documents, 25,000 test documents, a 15% slice of labeled training held out for validation, and a 1,024-unit LSTM over a 512-unit embedding:

| Initialisation | Test error |
|---|---|
| Randomly initialised, tuned LSTM | 13.50% |
| word2vec only | 10.00% |
| Joint training with SA | 14.70% |
| Linear label gain | 9.17% |
| LM-LSTM | 7.64% (Table 2; the text says 8.98%) |
| SA-LSTM | 7.24%, below Paragraph Vectors at 7.42% |

- With no pretraining, a tuned LSTM topped out near 86.5% IMDB accuracy and grew unstable as hidden units or backpropagation steps increased (512 hidden units, truncation 400).
- Rotten Tomatoes (80/10/10 split): SA-LSTM pretrained on 7.9 million Amazon movie reviews gets 16.7% error; pretraining on IMDB unlabeled data 18.6%; word2vec Google News vectors 20.5%; SA-LSTM without extra unlabeled data equals a tuned LSTM at 20.3%; an LSTM with word2vec trained on the Amazon reviews 23.3%. The 16.7% ranks second behind RNTN at 14.6%, which used 215,154 extra labeled phrases.
- 20 Newsgroups: LM-LSTM scores 15.3% error and SA-LSTM 15.6%, against 18.0% for a plain LSTM and 17.1% for SVM+BoW; linear gain without pretraining collapses to 71.6%.
- Character-level DBpedia (560K train, 14 classes): a 3-layer SA-LSTM with linear gain gets 1.19%, versus 1.73% for a large ConvNet; plain character LSTM 13.64%; linear gain alone 1.32%; plain SA-LSTM 2.34% against LM-LSTM 1.50%.
- CIFAR-10 (rows as input, 400 units, L2 loss): a 2-layer LM-LSTM reaches 18.0%, compared with 21.1% for Convolution DBNs and 26.0% for a 2-layer LSTM without pretraining; 2-layer SA-LSTM gives no gain (25.1%).

## Limits

- The paper names no optimiser, learning rate, schedule or hardware and gives no seeds; results are single runs without variance. Settings were tuned separately per dataset on validation sets, and dropout varies a lot between tasks.
- For LM-LSTM on IMDB, the running text says 8.98% error while Table 2 says 7.64%.
- On Rotten Tomatoes the Amazon-data gain mixes together domain similarity and sheer data volume, and no curve shows how results scale with the amount of unlabeled data.
- Neither pretraining objective dominates: LM-LSTM is better on 20 Newsgroups, on DBpedia without gain, and on CIFAR-10; the authors' account in terms of short-term objectives is only a hypothesis.
- Only supervised classification is evaluated; on CIFAR-10 the result trails state-of-the-art convnets, as the authors concede. No code or weights are released.

## See Also
- [[LSTM: Constant Error Carousel and Gated Memory Cells]] — prerequisite-for
- [[ULMFiT: Universal Language Model Fine-Tuning]] — extends
- [[ELMo and TagLM: Contextual Embeddings from Bidirectional LMs]] — related
