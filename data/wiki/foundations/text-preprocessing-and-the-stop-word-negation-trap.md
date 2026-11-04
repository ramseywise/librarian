---
title: "Text Preprocessing and the Stop-Word Negation Trap"
tags: [foundations, pattern]
summary: "Each text-cleaning step decides what a later model can see; default stop-word lists delete negations and flip sentiment, and the order of steps matters."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--01-text-representation.md
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--README.md
---

# Text Preprocessing and the Stop-Word Negation Trap

A model cannot read, so before any classifier, topic model or network sees a document, someone has decided how text becomes numbers. Those decisions set a ceiling on what can be learned. The standard chain is a menu, not a recipe: each step helps some tasks and destroys signal for others.

## The step chain and when to skip each

| Step | Example | Skip when |
|---|---|---|
| Strip markup | `<br />` in scraped reviews | Input is already clean |
| Remove accents | café to cafe | Non-English text |
| Expand contractions | can't to cannot | Subword tokenisers |
| Lower-case | | Case carries meaning (named entities) |
| Remove special characters and digits | | Numbers or emoji matter |
| Sentence and word tokenise | "Don't" becomes "Do", "n't" | |
| Remove stop words | the, is, and | Sentiment (keep negations) and neural models |
| Correct spelling and repeats | "finallllly" | Rarely worth it |
| Stem | jumping, jumps to jump | Real words are needed |
| Lemmatise | better to good (as an adjective) | Speed matters |

For neural models less preprocessing is usually better, because the model can learn what a step would have thrown away. Pretrained transformers expect the text their own tokeniser was built for, with case and punctuation intact. A [[Transformer Architecture]] fed text normalised as if for a linear model is a mismatch.

## The negation trap

Both the NLTK and scikit-learn default stop-word lists contain "not". Removing them turns "not good" into "good", the opposite claim. Check the list against the task. The sources show that "not a good film, not at all" keeps `not good film not` when negations are protected, but collapses to `good film` under the full list.

A second, subtler failure is order. If special characters are stripped before contractions are expanded, "weren't" becomes "weren t" and the negation vanishes even when "not" is safe in the stop list. In the worked example, "The brown foxes weren't jumping over the lazy dogs!" yields `brown fox jump lazy dog` without expansion and `brown fox not jump lazy dog` with it. Expand contractions first, then strip, then tokenise, then filter.

## Stemming versus lemmatisation

- A **stemmer** chops suffixes by rule: fast, may produce non-words. Porter turns "strange" into "strang" and "studies" into "studi"; Lancaster is more aggressive ("organization" becomes "org").
- A **lemmatiser** looks up the dictionary form using part of speech: slower, gives real words. Part of speech matters: "better" alone is read as an adverb and maps to "well", while as an adjective it maps to "good".
- Reported effect on a movie-review benchmark: lemmatisation gives a slightly better and smaller vocabulary, but the gain over plain tokens is small, and larger when training data is scarce.

## Linguistic structure beyond tokens

Part-of-speech tags (Penn Treebank tags such as NN, VBZ), shallow parsing (noun-phrase chunks), dependency parsing (head to dependent arcs such as `nsubj`, `dobj`) and constituency parsing (phrase-structure trees, which need a separate Java server in the toolkit used) feed later rule-based work. They power rule-based extraction in [[Named Entity Recognition and Sequence Tagging]] and keyphrase chunking in [[Topic Models and Extractive Summarisation]].

## Pitfalls

- **Different preprocessing at inference.** A model trained on lemmas and served raw text degrades with no error. This is train/serve skew: the world has not moved, but serving computes features differently. Use one function, or put the step inside the model as a layer.
- **Fitting any vocabulary on all the data** leaks the test set; see [[Bag of Words, n-grams and TF-IDF]] and [[Tabular ML Leakage Taxonomy]].
- **Over-cleaning for neural models**, as above.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — extends
- [[Tabular ML Leakage Taxonomy]] — related (fitting transforms outside the training fold)
- [[Sentiment Analysis Methods and Failure Modes]] — related (negation is the signal there)
