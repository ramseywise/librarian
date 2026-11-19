---
title: "Text Preprocessing and the Stop-Word Negation Trap"
tags: [data-science, pattern]
summary: "Each text-cleaning step decides what a later model can see; default stop-word lists delete negations and flip sentiment, and the order of steps matters."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--01-text-representation.md
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--README.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch01-analyzing-text-data-deep-learning.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch01-natural-language-basics.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch02-python-refresher.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch03-processing-understanding-text.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch03-processing-raw-text.md
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

Part-of-speech tags (Penn Treebank tags such as NN, VBZ), shallow parsing (noun-phrase chunks), dependency parsing (head to dependent arcs such as `nsubj`, `dobj`) and constituency parsing (phrase-structure trees, which need a separate Java server in the toolkit used) feed later rule-based work. Tagger and chunker mechanics, with the textbook's scores, are in [[N-gram Taggers, Backoff and Brill Transformation Rules]] and [[NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers]]. They power rule-based extraction in [[Named Entity Recognition and Sequence Tagging]] and keyphrase chunking in [[Topic Models and Extractive Summarisation]].

## Worked cases from a 2016 textbook

Sarkar's chapter 3 (Python 2 and NLTK) runs each step on small examples. The extraction gives these setups:

- **Repeated characters.** A regex that strips one repeated letter per pass, applied until nothing changes, ends 'finalllyyy' at 'finaly'. Adding a WordNet lookup before each pass stops at 'finally' after three passes.
- **Edit-distance spelling correction.** Norvig's corrector, run against the word counts of his big.txt file, returns 'finally' for 'fianlly' among distance-2 candidates that also include faintly, finely and frankly. The book's version treats case literally until it is wrapped, and a word missing from big.txt is beyond its reach. 'the' is the most frequent word in that file, at 80,030 occurrences.
- **Stemmers disagree.** Porter gives 'strang' and 'lie' for 'strange' and 'lying'; Lancaster leaves both unchanged. The author advises choosing a stemmer by trial and error.
- **The lemmatiser needs the part of speech.** With the noun tag, WordNet's lemmatiser returns 'ate' and 'men' unchanged.
- **Sentence splitting.** NLTK's Punkt splitter cut Alice in Wonderland (144,395 characters) into 1,625 sentences.
- **Order of cleaning.** The author leaves the timing of special-character stripping (before or after tokenising) to the task, and says to keep apostrophes when contractions will be expanded. Expansion uses a contraction map that keeps one expansion per contraction.

Chapter 2 of the same book shows an encoding trap: under Python 2, the regex `\w+` on the unicode string u'H\u00e8llo' splits it into two tokens unless `re.UNICODE` is passed. The extraction notes that Python 3 string patterns are Unicode-aware by default. The Raieli and Iuculano chapter lists segmentation, lowercasing, lemmatisation and stemming as the normalisation operations and advises lowercasing and normalising before tokenising. Sarkar's chapter 1 advises cleaning noisy terms before turning each document into a vector of word weights.

## Stemmers, lemmatiser and regexes in the NLTK book

Setup for these examples: one 38-token Monty Python sentence in an NLTK 2 / Python 2 session, from chapter 3 of Bird, Klein and Loper's *Natural Language Processing with Python*. The Porter stemmer maps "lying" to "lie", while Lancaster leaves it unchanged. Both over-stem other words (Porter gives "DENNI" and "ceremoni", Lancaster gives "pow" and "som"). The WordNet lemmatiser, called with no part of speech, turns "women" into "woman" but leaves "lying", "distributing" and "derives" alone. A hand-written suffix-stripping regex over-strips further: "basi" for basis, "i" for is, and the non-words "distribut" and "deriv". Greedy `.*` splits "processes" as ('processe', 's'), while non-greedy `.*?` gives ('process', 'es').

The authors advise tokenising with a regular expression or `nltk.word_tokenize` rather than splitting on whitespace, and writing the pattern with the verbose `(?x)` flag. Their verbose pattern leaves abbreviations (U.S.A.), hyphenated compounds, currency amounts ($12.40) and ellipses intact as single tokens, while `\W+` splitting breaks "won't" into "won" and "t". They advise Porter for indexing over word variants and the lemmatiser when valid lemmas are wanted, and assert, with no data, that mapping numbers and acronyms to special tokens shrinks the vocabulary and helps language modelling. The same chapter covers segmentation in [[Word Segmentation by Objective and Simulated Annealing]]. The stemmer and lemmatiser outputs come from one sentence, with no accuracy or retrieval measurement, and the chapter has no subword tokenisation.

## Pitfalls

- **Different preprocessing at inference.** A model trained on lemmas and served raw text degrades with no error. This is train/serve skew: the world has not moved, but serving computes features differently. Use one function, or put the step inside the model as a layer.
- **Fitting any vocabulary on all the data** leaks the test set; see [[Bag of Words, n-grams and TF-IDF]] and [[Tabular ML Leakage Taxonomy]].
- **Over-cleaning for neural models**, as above.

## Limits

- The textbook code is Python 2 with NLTK 3.1 to 3.2.1 and does not run unmodified today.
- It tests no normalisation step against a downstream task, so its advice on which steps to use is asserted, not measured.
- The textbook says to avoid NLTK 3.2.0, whose `pos_tag()` had problems.

## See Also
- [[Bag of Words, n-grams and TF-IDF]] — extends
- [[Tabular ML Leakage Taxonomy]] — related (fitting transforms outside the training fold)
- [[Sentiment Analysis Methods and Failure Modes]] — related (negation is the signal there)
- [[Word Segmentation by Objective and Simulated Annealing]] — extends
- [[Lexical Diversity: Types, Tokens and Conditional Frequency Counts]] — extends
- [[Chart Parsing, PCFGs and Structural Ambiguity]] — extends
