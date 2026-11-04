---
title: "Neural Text Models vs TF-IDF"
tags: [foundations, comparison]
summary: "On 5,000 labelled reviews a TF-IDF bigram logistic regression (0.886) beat averaged embeddings (0.847), a text CNN (0.741) and a BiLSTM (0.716), because from-scratch embeddings overfit; truncation and sequence-loss choices also move scores, and generation and masked losses have their own traps."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--06-neural-text-models.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Neural Text Models vs TF-IDF

Start text work with [[Bag of Words, n-grams and TF-IDF]]; learned embeddings need pretraining on far more text than a small labelled set holds.

## The race (5,000 train, 5,000 test reviews, vocabulary 10,000, max length 250, embedding 16)

| Model | Parameters | Test |
|---|---|---|
| Average of embeddings | 160,034 | 0.847 |
| Text CNN (n-gram filters plus global max pool) | 170,626 | 0.741 |
| BiLSTM | 202,242 | 0.716 |
| TF-IDF bigrams + logistic regression | - | 0.886 |

Each neural model has more than 160,000 parameters for 5,000 examples; the CNN memorised training (0.998) while the BiLSTM was still learning. At 25,000 reviews the race was closer: about 0.87, 0.88 and 0.87-0.89 against about 0.90 for TF-IDF. Pretraining is what changed the picture; see [[Frozen vs Fine-Tuned Sentence Encoders]].

## Pipeline choices that move the score

- The vocabulary comes from training rows only; fitting it (or a scaler) on all data inflates scores that collapse on real text.
- Reviews are long (median 174 tokens, 90th percentile 454) and the verdict is often at the end: keeping the last 250 tokens gave test 0.857 against 0.847 for the first 250.
- Embedding dimension 4 gave 0.827 (less overfitting, less capacity); a max_length of 50 dropped the average model to 0.727 and TF-IDF to 0.752. Losing text hurts more than model choice.
- Recurrent layers must skip padding (mask or packed sequences). A bidirectional layer suits classification, not generation, since it uses the future at training time.

## Next-word generation

Trained on every prefix of every line (pre-padded so the target is the last column), an LSTM reached loss 0.59 against ln(2,693) = 7.90 for a uniform guess: mostly memorised. Greedy argmax loops; temperature 0.7 stays near known phrases and 1.5 loses grammar. A word-level vocabulary makes a huge output layer (hence character or subword tokens). See [[LSTM Forget-Gate Bias and Vanishing Gradients]] for sampling versus teacher forcing.

## Sequence regression: match the loss to the metric

Predicting airway pressure at each of 80 steps with an LSTM, scored only on the inspiratory steps: a masked loss matching the metric gave inspiratory MAE 0.248 against 0.274 for all-steps MAE, at the price of all-steps MAE 7.212 against 0.117, fine only because nobody scores those steps. Use group k-fold by breath so no sequence is in both train and validation (see [[Tabular ML Leakage Taxonomy]]); bidirectional is legitimate when the whole sequence is known at prediction time.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — prerequisite-for
- [[Frozen vs Fine-Tuned Sentence Encoders]] — extends
- [[Text Preprocessing and the Stop-Word Negation Trap]] — related
- [[Choosing an Encoder vs CNN vs LSTM]] — related
- [[Linear Text Classifiers and the TF-IDF Baseline]] — related
