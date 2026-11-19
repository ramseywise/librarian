---
title: "FastText Subword Skip-gram"
tags: [llm, pretraining-and-data, concept]
summary: "FastText's skip-gram variant (sisg) scores a word as the sum of vectors for its hashed character n-grams, which gives vectors for unseen words and improves syntactic analogies and rare-word similarity but not semantic analogies."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-bojanowski-2017-enriching-word-vectors-subword-information.md
---

# FastText Subword Skip-gram

Bojanowski, Grave, Joulin and colleagues test whether building a word's vector from the vectors of its character n-grams captures morphology and yields better vectors for unseen words than keeping one vector per word. They expect gains for rare words, for morphologically rich languages and for small training sets. The model is called sisg (Subword Information Skip Gram).

## Mechanism

It is skip-gram with negative sampling where the score of a word w and a context c is s(w, c) = sum over g in G_w of z_g^T v_c. G_w holds the word's character n-grams of length 3 to 6, hashed, plus the word itself. A word never seen in training still gets a vector as the sum of its n-gram vectors; the variant sisg- uses a null vector for such words instead. Training was on Wikipedia in nine languages, compared with word2vec skip-gram and CBOW (see [[Word2vec: CBOW, Skip-gram and Negative Sampling]]) on similarity, analogy and language modelling.

## Results (self-reported)

- Word similarity: sisg beats skip-gram and CBOW on every similarity set except English WS353 (71 against 73 for CBOW), and summing n-grams for unseen words is never worse than using null vectors (German GUR350, Wikipedia dump, 300-d, five passes). On English rare words it beats both baselines.
- Syntactic analogies improve a lot: Czech accuracy goes from 55.0 for CBOW to 77.8. Semantic analogies do not improve, and German (66.5/66.8 down to 62.3) and Italian semantic accuracy degrade (n-gram range 3 to 6).
- Against morphology-based methods on the same German news data (WMT 2013), sisg scores 73 against 64 on GUR350 (Soricut and Och baseline).
- Small data: sisg on 5% of German Wikipedia beats CBOW on all of it on GUR350; on English rare words, sisg trained on 1% of Wikipedia scores 45 against CBOW's 43 on the whole corpus.
- Language modelling: initialising a 650-unit LSTM lookup (Russian, about 1M training tokens) from sisg vectors lowers perplexity against skip-gram vectors, most for Russian and Czech.
- Including n-grams longer than 2 matters: on English rare words range 3-6 gives 48 against 41 for range 2-2. Training runs about 1.5 times slower than the skip-gram baseline (English data, C++ code).

## Limits

- The authors concede there is no proper validation procedure for the n-gram range because of scarce test data; 3-6 was arbitrary.
- Results are single runs reported as integers, with no seeds, variance or significance tests.
- On German and Italian semantic analogies the subword vectors do worse.
- The paper does not give corpus token counts, hardware or total training time, and its qualitative tables and figures rely on hand-picked examples.
- Static word vectors with no context-dependent representation; superseded by contextual models.

## See Also
- [[Word2vec: CBOW, Skip-gram and Negative Sampling]] — prerequisite-for
- [[Word Embeddings and Similarity Measures]] — prerequisite-for
- [[GloVe Global Vectors]] — related (unseen words are not handled there)
