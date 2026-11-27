---
title: "Collocations and Pointwise Mutual Information"
tags: [data-science, nlp, concept]
summary: "PMI scores word pairs by how much more often they co-occur than chance; it overrates rare pairs, so it needs a minimum count, while raw frequency surfaces only common pairs."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--03-topic-models-and-summarization.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch05-text-summarization.md
---

# Collocations and Pointwise Mutual Information

Pairs like "new york" or "serial killer" mean more together than apart. Finding them is the principled way to choose which n-grams to keep (see [[Bag of Words, n-grams and TF-IDF]]) and to merge phrases into single tokens before [[Topic Models and Extractive Summarisation]].

## PMI

Pointwise mutual information is log of p(x, y) divided by p(x) p(y): how much more often two words co-occur than independence predicts.

- **Failure mode:** it overrates rare pairs. A pair seen once between two words each seen once scores the maximum. Fix: set a minimum count.
- **The opposite failure:** raw frequency favours common pairs. With stop words kept it returns "of the" and "in the".

## Measured on 4,799 film descriptions

| Ranking | Top results |
|---|---|
| PMI, no filter | one-off name pairs such as 'abortionist vera', 'abu ghraib' |
| PMI, count at least 10 | 'mild mannered', 'hong kong', 'alter ego', 'las vegas', 'post apocalyptic' |
| Raw frequency, stop words removed | 'new york', 'year old', 'high school', 'true story' |

The two filtered rankings answer different questions: PMI with a floor finds distinctive phrases, raw frequency finds common ones. At corpus scale, `gensim.models.Phrases` does the same and rewrites `new_york` as one token (the source's setup used `min_count=20, threshold=20`).

## Tag-based keyphrases

An alternative: chunk noun phrases with a part-of-speech grammar (adjectives followed by nouns), then weight each phrase by TF-IDF across the corpus. This surfaces "family groups" or "asian elephant" instead of the single words. The grammar is short and works on one article: on a 29-sentence text the top-weighted phrase was the subject itself ("elephants", 3.23). See [[Text Preprocessing and the Stop-Word Negation Trap]] for the tagging layer.

## The same checks in a textbook run

Sarkar's chapter 5 repeats the contrast on Alice in Wonderland (NLTK Gutenberg text, lemmatising off). Raw-frequency bigrams are dominated by speech tags, with the top bigram occurring 123 times. PMI collocations from NLTK's bigram and trigram finders with no frequency filter surface obscure pairs seen once, not meaningful phrases.

For tag-based keyphrases, the chapter treats each of 9 sentences of an elephants text as a document and chunks noun phrases with the grammar `NP: {<DT>? <JJ>* <NN.*>+}`. Phrases confined to one sentence all tie at a TF-IDF weight of 0.707, which puts them above repeated phrases such as "elephants". That is a different setup from the 29-sentence article above, where the subject phrase ranked first. The author advises tagging parts of speech on text that has not been normalised first, when chunking noun phrases.

## Limits

- Sarkar's chapter 5 reports no quantitative evaluation: each method is judged by reading its output.
- The examples are toy data (one short text and one 9-sentence passage).
- The code is Python 2 and uses dated APIs.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — related (which n-grams to keep)
- [[Topic Models and Extractive Summarisation]] — related (phrase merging before topic models)
- [[NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers]] — related (the chunking layer under keyphrase chunks)
