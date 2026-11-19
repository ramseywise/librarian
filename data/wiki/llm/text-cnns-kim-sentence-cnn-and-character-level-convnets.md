---
title: "Text CNNs: Kim Sentence CNN and Character-level ConvNets"
tags: [llm, architecture, comparison]
summary: "A one-layer CNN over pretrained word2vec vectors (static, fine-tuned or two-channel) against a nine-layer ConvNet over raw characters: the word-vector CNN is strong with little tuning, while the character model overtakes n-gram baselines only on million-sample datasets."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-kim-2014-convolutional-neural-networks-sentence-classification.md
  - data/raw/papers/2026-11-08-zhang-2015-character-level-convolutional-networks-text.md
---

# Text CNNs: Kim Sentence CNN and Character-level ConvNets

Two convolutional classifiers sit at opposite ends of the input choice: pretrained word vectors (Kim, 2014) and one-hot characters (Zhang et al., 2015). The character paper uses Kim's model as a baseline.

## Kim's sentence CNN

One convolution layer with filters of width 3, 4 and 5 slides over the concatenated word vectors; max-over-time pooling keeps each feature map's largest value as that filter's feature (which copes with variable sentence length), followed by dropout and a softmax. There are four variants: random initialisation (rand), frozen word2vec (static), word2vec updated by backpropagation (non-static) and multichannel, which keeps two vector sets, applies every filter to both, and backpropagates into only one. Kim hoped the two-channel model would reduce overfitting. Kim describes pretrained vectors as universal feature extractors reusable across tasks. See [[Word2vec: CBOW, Skip-gram and Negative Sampling]].

Results (self-reported, 300-d word2vec, test accuracy on seven benchmarks):

- Static vectors lift MR accuracy about 5 points over random initialisation, and also help Subj and SST-2.
- Fine-tuning gives the best SST-1 of the four variants and beats static on TREC, but static is slightly ahead on CR and MPQA, so updating the vectors is not always a win.
- Multichannel wins on SST-2 and CR and is mixed on the rest. The static CNN ties DCNN on SST-2 at 86.8. Kim reports improving on the previous best results for 4 of the 7 tasks.
- Dropout added 2% to 4% relative performance consistently (stated without a table). In the original word2vec vectors the nearest neighbour of "good" is "bad"; after fine-tuning on SST-2 that is no longer true.
- A competing Max-TDNN with random initialisation gets 37.4% on SST-1 against 45.0% for Kim's CNN-rand; Kim attributes it to capacity (several filter widths and feature maps).

## Character-level ConvNet

A 9-layer temporal ConvNet (6 convolutional, 3 fully connected) reads 1,014 characters, each one-hot over a 70-symbol alphabet (any other character becomes an all-zero vector) and is trained from scratch per dataset. It is compared on eight new large datasets against bag-of-words and n-gram linear models, word2vec bag-of-means, word ConvNets and a word LSTM.

- The large model with thesaurus augmentation is best on Amazon Polarity (3.6M training samples); without it, it already beats the best n-gram model there.
- On the smallest set, AG News (120k), n-gram TF-IDF (error 7.64) is far better than the character model. The lookup-table word ConvNet is the best deep model on AG.
- Using a larger case-sensitive alphabet helps on Yelp Full (39.62 error with the 70-symbol alphabet) and hurts on Sogou (4.88). Bag-of-means is the worst model on every dataset. On DBPedia the character model is within a few tenths of word-based models.
- The authors say character ConvNets overtake traditional models only once datasets reach millions of samples, and that the pooling module let them train deeper than 6 layers.

## Limits

- Kim: the multichannel gains are inconsistent, and the author says regularising fine-tuning needs further work; no variance, seeds or significance tests; hyperparameters were tuned on the SST-2 dev set only and then reused; Kim cannot tell whether word2vec's edge over Collobert's Wikipedia vectors comes from the architecture or from its 100B-word corpus.
- Zhang: the authors found no direct evidence that the ConvNets cope better with misspellings and emoticons, and mark their case-sensitivity explanation as still to be validated; the bag-of-means result says nothing about other ways of using word2vec; classification only; single run per cell, no parameter count or training time.
- Sogou is handled through Pinyin, so its characters are romanised letters. The window is a fixed 1,014 characters.
- Static context-free vectors in Kim; both predate subword tokenisation and transformers. The character paper's extraction leaves several result lines without numbers.

## See Also
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — prerequisite-for
- [[NLP (Almost) from Scratch: Window Network and Sentence-Level Likelihood]] — prerequisite-for
- [[Choosing an Encoder vs CNN vs LSTM]] — related (a from-scratch comparison of the same model families)
- [[Neural Text Models vs TF-IDF]] — related
