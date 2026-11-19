---
title: "Skip-Thought Vectors"
tags: [llm, pretraining-and-data, concept]
summary: "A GRU encoder is trained to reconstruct the previous and next sentence from a sentence vector, then frozen as a feature extractor; a linear map from word2vec space expands its vocabulary from 20,000 to 930,911 words."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-kiros-2015-skip-thought-vectors.md
---

# Skip-Thought Vectors

Kiros and colleagues look for a training task and loss that would give an encoder general-purpose sentence representations without any supervised task in view. They propose lifting skip-gram from words to sentences (encode one sentence, predict the sentences next to it), expecting vectors that transfer to many tasks under just a linear model.

## Mechanism

- A GRU encoder turns a sentence into one vector. Two decoders (GRUs conditioned on that vector) generate the sentence before and the sentence after. BookCorpus is the training text, and the encoder is frozen once training ends.
- **Vocabulary expansion.** A linear regression maps CBOW word2vec space to the encoder's embedding space, so words outside the 20,000-word training vocabulary can be encoded (930,911 words after expansion, multiword entries removed). See [[Word2vec: CBOW, Skip-gram and Negative Sampling]].
- Eight tasks are evaluated with simple linear models (logistic regression, or a linear embedding for ranking); sentence pairs are represented by the product and absolute difference of the two vectors.

## Results (self-reported)

- SICK relatedness: the combine-skip model alone reaches Pearson r 0.8584, beating all SemEval 2014 submissions; adding COCO image-sentence features lifts it to 0.8655, close to the dependency Tree-LSTM's 0.8676.
- MSRP paraphrase: combine-skip alone 73.0% accuracy, above RAE+DP (72.6) with no hand-crafted features; with basic pairwise features 75.8% accuracy and 83.0 F1 against 77.4 / 84.1 for the best system.
- COCO image annotation (1,000-image test, linear embeddings): R@1 33.8 against 41.0 for m-RNN, R@10 82.1 against 83.5, median rank 3.
- Classification (logistic regression on frozen vectors; 10-fold cross-validation, with TREC's own split), combine-skip scores: MR 76.5 and CR 80.1, SUBJ 93.6, then MPQA 87.1 and TREC 92.2. That is roughly level with bag-of-words baselines and below task-tuned supervised models. Adding bigram naive Bayes features takes MR to 80.4.
- Training took about two weeks per skip-thought model.

## Limits

- On sentiment-style classification the authors admit that representations trained for the task do better than skip-thoughts.
- Only linear evaluators were tried, so any gain from non-linear ones is unknown.
- Small structural edits to a sentence can break the model (their Table 5 pairs "tricks" with a person-tricking variant).
- The paper gives no seeds, learning rate, hardware, ablations or significance tests, and the encoder's release is only promised.
- The authors list deeper encoders and decoders, wider context, paragraph-level encoding and convnet encoders as untried.
- Dated: GRU encoder-decoder with 2015 baselines.

## See Also
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — prerequisite-for
- [[Sentence Embeddings as Features for Classical ML]] — related
- [[Frozen vs Fine-Tuned Sentence Encoders]] — related (the frozen-feature setup)
