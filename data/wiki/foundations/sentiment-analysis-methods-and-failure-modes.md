---
title: "Sentiment Analysis Methods and Failure Modes"
tags: [foundations, comparison]
summary: "Lexicons reach about 70 percent with no labels, TF-IDF bigrams plus a linear model about 90 percent, and sequence models overfit without more data; a maxlen mismatch at inference silently costs 11 points."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--06-sentiment-analysis.md
---

# Sentiment Analysis Methods and Failure Modes

Sentiment is binary or graded polarity; finer forms are aspect-based (battery good, screen poor) and emotion detection. Three generations of method were compared on a balanced 25,000/25,000 movie-review split. The tell on every method is whether negation survives (see [[Text Preprocessing and the Stop-Word Negation Trap]]).

## 1. Lexicons (no labels)

A lexicon maps words to polarity scores and aggregates them. Accuracy on 1,500 reviews, with the conventional threshold and with a threshold tuned on train:

| Lexicon | Conventional | Tuned on train |
|---|---|---|
| TextBlob (polarity, modifier and negation handling) | 0.761 | 0.759 |
| AFINN (integer word scores, summed) | 0.710 | 0.735 |
| VADER (rules for negation, intensifiers, caps, emoji) | 0.697 | 0.714 |
| SentiWordNet (first synset only, naive sense choice) | 0.613 | 0.658 |

A dictionary gets about 70% right against 50% for a coin. Failures: domain vocabulary ("unpredictable" is good for a thriller, bad for a car), sarcasm, and sad plots described approvingly. The threshold is a parameter: picking it by looking at test accuracy tunes on the test set, so tune it on train. VADER is the lexicon for short informal text with no labels.

## 2. Supervised sparse models

With labels the recipe from [[Linear Text Classifiers and the TF-IDF Baseline]] applies directly. TF-IDF 1-2-grams with logistic regression reached 0.906 test accuracy in 9 seconds; counts with logistic regression 0.898; a linear SVM via SGD 0.902. That is thirty points above lexicons. Bigrams earn their cost here: unigrams 44,797 features and 0.883, bigrams 436,597 features and 0.906.

Dense features lose: averaged word2vec (200-d) with a small dense net reached 0.831 (published figures on a larger split: 0.882 for 512-d, 0.860 for 300-d pretrained). Averaging throws away order and negation scope; see [[Word Embeddings and Similarity Measures]].

## 3. Sequence models

On a 6,000-review subset (vocabulary 10,000, length 120, 4 epochs), validation accuracy: pooled embeddings 0.80, CNN 0.794, LSTM 0.782, SimpleRNN 0.592. Training accuracy was 0.94 to 0.97 for the sequence models: memorised. The CNN and LSTM validation losses had turned upward, the pooled learned bag of words overfit least, and SimpleRNN was barely above chance (vanishing gradients at 120 tokens). These had a fifth of the linear model's data, so compare them with each other, not with it. A reported LSTM on 35,000 reviews reached 0.88 and TF-IDF still beat it. Use early stopping on validation loss. A pretrained transformer off the shelf is the next thing to measure against the linear model before training anything.

## The inference-length bug

An LSTM trained on length-120 sequences was fed length-20 padded inputs. It runs without error because recurrent layers accept any length. Four hand-written reviews barely moved (for instance 0.989 to 0.992) because they fit in 20 tokens, so a spot check passes. On 2,500 real held-out reviews accuracy fell from 0.782 to 0.672: the model saw only each opening. Silent train/serve skew shows up only if accuracy is measured through the serving path. Use identical preprocessing, ideally inside the model as one code path.

## Pitfalls
- Start with TF-IDF 1-2-grams plus logistic regression: seconds to train, explainable, and it won the comparison.
- Comparing models on different data amounts.
- Pair a score with per-class topics: see [[What Drives Sentiment: LIME, Per-Class Topics and Log-Odds]].

## See Also
- [[What Drives Sentiment: LIME, Per-Class Topics and Log-Odds]] — extends
- [[Linear Text Classifiers and the TF-IDF Baseline]] — prerequisite-for
- [[Text Preprocessing and the Stop-Word Negation Trap]] — prerequisite-for
- [[Semantic Analysis, WordNet and Lexical Ambiguity]] — related (SentiWordNet scores WordNet synsets)
