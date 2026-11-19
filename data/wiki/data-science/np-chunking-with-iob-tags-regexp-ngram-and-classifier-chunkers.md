---
title: "NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers"
tags: [data-science, pattern]
summary: "Noun-phrase chunking turned into token tagging with IOB labels, so a tag-pattern grammar, an n-gram tagger and a feature-based classifier can be scored on the same CoNLL-2000 split."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nlp-with-python-ch07-extracting-information-from-text.md
  - data/raw/papers/2026-11-08-loper-2002-nltk.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch03-processing-understanding-text.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch01-natural-language-basics.md
---

# NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers

Chunking segments and labels multi-token sequences, and chunks never overlap one another. In the NLTK book's information extraction pipeline it sits after part-of-speech tagging and before entity and relation recognition. **IOB tags** make it a tagging problem: B marks the first token of a chunk, I a token inside one, O a token outside any chunk. Ordinary taggers and classifiers then apply, and predictions are converted back to trees. **Chinking** is the inverse operation, removing a token sequence from a chunk.

## Scores on CoNLL-2000

Setup for every row: NP chunks only, the CoNLL-2000 corpus (WSJ text of about 270k words, labelled for NP, VP and PP chunks), test.txt as the test set. Data-driven rows train on train.txt. Each is a single run.

| Chunker | F | Note |
|---|---|---|
| Empty grammar, finds no chunks | 0 (IOB accuracy 43.4%) | most tokens are outside any NP |
| One-line regexp grammar `NP: {<[CDJNP].*>+}` over POS tags | 69.2% | no training |
| Unigram tagger, POS tag to IOB tag | 83.2% | |
| Bigram tagger | 84.5% | adds the previous POS tag |
| Classifier chunker, current POS tag only | 83.2% | maximum entropy, same as unigram |
| Classifier with POS, word, previous POS | 85.9% (IOB accuracy 94.2%) | against F 84.4% (IOB 93.6%) without the word |
| Adds lookahead, paired and tags-since-determiner features | 89.5% | |

The authors read the 0.6-point IOB gain from adding the word as about a 10% cut in error rate. The classifier chunker is a greedy left-to-right model that does not decode whole sequences, so an earlier IOB tag stays fixed.

## Method advice

Bird, Klein and Loper advise establishing a trivial baseline before training, and adding one feature at a time, re-scoring on the held-out set at each step. They also warn that a gazetteer alone is not enough for entity recognition, because location names collide with common words and other entity types (May, North). For relation extraction they take triples of an entity, the string between, and a second entity, filter them with a regular expression, and expect some false positives.

## The same ideas in Text Analytics with Python

Sarkar's chapter 3 scores a shallow parser (NP, ADJP, ADVP, PP and VP rules) and a tagger-style chunker with IOB accuracy. A **chink** is a token or run excluded from a chunk.

| Chunker | Data setup | IOB accuracy | Precision / recall / F |
|---|---|---|---|
| Hand-written regex grammar | `treebank_chunk`, first 4,000 sentences train, rest test | 54.5% | 25.0 / 52.5 / 33.9 |
| Tag chunker, bigrams falling back to unigrams, over POS tags | same split | 99.6% | 98.4 / 100.0 / 99.2 |
| Same chunker | `conll2000`, first 7,500 sentences train, 3,448 test | 66.8% | 77.7 / 45.4 / 57.3 |

The extraction notes that the author calls the 99.6% result excellent without pointing out that the split is small; the same chunker falls to 66.8% on the larger corpus. The chapter also shows a dependency parser and a probabilistic CFG parser on one sentence each, with no scores. In chapter 1, a dependency grammar links words with labelled, asymmetric arcs and does not depict word order, while a constituency grammar builds ordered phrases. The Viterbi PCFG parser failed on words outside its grammar until the sample sentence's words were added by hand.

## In the 2002 toolkit paper

Loper and Bird's NLTK paper shows the same idea at course scale: `ChunkRule('<NN.*>')` builds chunks from consecutive nouns. A student's brute-force cascade in a base-noun-phrase assignment grouped every tag sequence that fell inside a noun phrase in over half its occurrences. No accuracy is reported for it.

## Limits

- Each score is a single train/test run: no variance, seed or significance test is given; precision and recall count only exact chunk matches.
- Entity recognition appears only as gazetteer lookup and a pre-trained chunker, without an accuracy figure; relation extraction is shown by printed examples alone.
- The Text Analytics code is Python 2 with NLTK 3.1 to 3.2.1 and 2015 Stanford Parser jars; only tagging and chunking report scores, from one run each on a small treebank sample. Its dependency labels come from a 2016-era parser and vary by parser and training data.
- Text Analytics chapter 1 is internally inconsistent: it labels a dependency tree a DAG, and it describes dependency grammars as matching words one to one.
- Python 2 and NLTK 2 code (print statements, the megam trainer, old relation-extraction signatures).
- The 2002 paper's evaluation is anecdotal course experience, and it describes a Python and Tk toolkit of that date.

## See Also
- [[N-gram Taggers, Backoff and Brill Transformation Rules]] — prerequisite-for
- [[Named Entity Recognition and Sequence Tagging]] — related (BIO tagging of entities)
- [[Chart Parsing, PCFGs and Structural Ambiguity]] — alternative-to
