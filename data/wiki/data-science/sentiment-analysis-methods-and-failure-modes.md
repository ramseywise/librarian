---
title: "Sentiment Analysis Methods and Failure Modes"
tags: [data-science, comparison]
summary: "Lexicons reach about 70 percent with no labels, TF-IDF bigrams plus a linear model about 90 percent, and sequence models overfit without more data; a maxlen mismatch at inference silently costs 11 points."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--06-sentiment-analysis.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch07-semantic-sentiment-analysis.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch01-analyzing-text-data-deep-learning.md
  - data/raw/papers/2026-11-08-maas-2011-learning-word-vectors-sentiment-analysis.md
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

## A second comparison: 50,000 IMDb reviews and a GRU recipe

Sarkar's chapter 7 pools 50,000 IMDb reviews and takes the first 35,000 rows to train and the remaining 15,000 to test (7,510 positive, 7,490 negative). Text is lemmatised and the SVM is a hinge-loss `SGDClassifier` (200 iterations) on TF-IDF unigrams. No lexicon is trained.

| Model | Test accuracy | Notes |
|---|---|---|
| SVM on TF-IDF | 89% (F1 0.89) | the best of the four |
| Pattern lexicon, polarity at least 0.1 | 77% (F1 77%) | confusion matrix: 5,958 of 7,510 positive and 5,566 of 7,490 negative right |
| VADER, compound at least 0.1 | about 70% (F1 near 75%) | negative recall 0.54 |
| SentiWordNet (first synset, sum of positive minus negative over token count, threshold 0) | 59% | labelled 5,510 of 7,490 negative reviews positive; negative recall 0.26 |

According to the text, the lexicons recall many positives but with low precision. On eight fixed sample reviews the order flips: SentiWordNet got 8 of 8 right, Pattern 7 and the SVM and VADER 6 each, by the extraction's count from the printed predictions. The author advises reporting a full set of measures together (accuracy, precision, recall, F1, confusion matrix, per-class report), using lexicons when no labelled data exists, raising a skewed lexicon's threshold from 0 to 0.1 or higher, and not assuming the best model here is best elsewhere. Lexicon sizes it reports: AFINN-111 has 2,477 words and phrases and Bing Liu's has over 6,800; VADER keeps 7,500 of over 9,000 candidates, rated by ten raters. Pattern also returns a mood (indicative, imperative, conditional or subjunctive) and a modality score from 0 to 1, where above 0.5 means factual and below 0.5 means wishes and hopes.

Raieli and Iuculano's chapter ends in a GRU classifier on a binary movie-review set (average review 230 words). Setup: 300-d embeddings, 256 hidden units, 3 layers, 0.5 dropout, Adam with learning rate 0.001, binary cross-entropy, batches of 50, a vocabulary cut to the 1,000 most frequent words, and a stratified 80/20 train/test split with a tenth of train kept for validation. The text gives no accuracy figure, only plots. The authors prefer LSTM or GRU to a plain RNN against vanishing gradients, and call GRU lighter but more prone to overfitting.

## Sentiment-supervised word vectors and the IMDB benchmark (Maas et al., 2011; results self-reported)

Maas and colleagues test whether word vectors can capture semantic and sentiment similarity at once when trained on unlabelled documents together with documents carrying sentiment labels. A log-bilinear latent-mixture document model (word matrix R, biases b, per-document theta by MAP) is fitted jointly with a logistic-regression sentiment predictor applied to each word vector, alternating between the two. A document is represented as R times its bag-of-words vector and classified by a linear SVM, against LSA, LDA and several bag-of-words weightings.

- **Benchmark.** They release a 50,000-review IMDB set: balanced polarised reviews (positive score at least 7 of 10, negative at most 4, neutral excluded), at most 30 reviews per movie, 25,000 train and 25,000 test with disjoint movies. In the 2,000-review Pang and Lee set (PL04), 1,299 reviews have another review of the same movie, 249 of 406 movies with several reviews have a single polarity throughout, and about half the test reviews in the published random folds have a training review of the same movie and label.
- **IMDB test (linear SVM, 50-d vectors, 5,000-word vocabulary).** The full model trained on labelled data only gets 87.44, where LSA gets 83.96 and LDA 67.42. A delta-idf weighted bag of words reaches 88.23, leaving the best vector-plus-bag-of-words configuration (using 50,000 extra unlabelled reviews) only about 0.7 points ahead.
- **Other sets.** On PL04 (10-fold cross-validation) the best configuration reaches 88.90, below 90.20 for an appraisal-taxonomy method and above 87.15 for the Pang and Lee bag-of-words SVM. On subjectivity (10,000 sentences) the best combined model gets 88.58, short of Pang and Lee's bag-of-words SVM at 90.00.

## The inference-length bug

An LSTM trained on length-120 sequences was fed length-20 padded inputs. It runs without error because recurrent layers accept any length. Four hand-written reviews barely moved (for instance 0.989 to 0.992) because they fit in 20 tokens, so a spot check passes. On 2,500 real held-out reviews accuracy fell from 0.782 to 0.672: the model saw only each opening. Silent train/serve skew shows up only if accuracy is measured through the serving path. Use identical preprocessing, ideally inside the model as one code path.

## Pitfalls
- Start with TF-IDF 1-2-grams plus logistic regression: seconds to train, explainable, and it won the comparison.
- Comparing models on different data amounts.
- Pair a score with per-class topics: see [[What Drives Sentiment: LIME, Per-Class Topics and Log-Odds]].

## Limits

- The chapter 7 numbers are one split of one dataset with no seeds or repeated runs. The split takes the leading 35,000 rows of a pooled file, not the original 25,000/25,000 split used above, so these figures are not directly comparable with the table in section 1 or the supervised figures in section 2.
- Its lexicon thresholds (0.1 for VADER and Pattern) came from trying values against the test data, which makes the lexicon scores optimistic; the tuning-on-train advice above avoids this.
- The comparison has no neural or transformer model, and its code is Python 2 with older NLTK.
- Maas et al.: no variance, seeds or significance tests (the low-variance argument rests on the 25,000-example test set alone); the values of lambda, nu and SVM C, the iteration counts and the compute are missing, so the model cannot be rebuilt from the paper; the best vector results stay below the best published PL04 and subjectivity numbers; the vocabulary is capped at 5,000 words; the authors call their qualitative evidence an impressionistic look at a few cases; how many of the 50,000 unlabelled reviews are neutral is not reported; differences between the top IMDB rows are small (87.80 to 88.89).
- The GRU chapter is conceptual: epochs, seed and hardware are not specified, and its claims about LSTM memory and GRU against LSTM are asserted without citation.

## See Also
- [[What Drives Sentiment: LIME, Per-Class Topics and Log-Odds]] — extends
- [[Linear Text Classifiers and the TF-IDF Baseline]] — prerequisite-for
- [[Text Preprocessing and the Stop-Word Negation Trap]] — prerequisite-for
- [[Semantic Analysis, WordNet and Lexical Ambiguity]] — related (SentiWordNet scores WordNet synsets)
- [[Recursive Neural Tensor Network and the Stanford Sentiment Treebank]] — extends
- [[UDA: Unsupervised Data Augmentation]] — related
