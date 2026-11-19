---
title: "N-gram Taggers, Backoff and Brill Transformation Rules"
tags: [data-science, pattern]
summary: "A part-of-speech tagger built from a default tag, suffix rules, unigram and bigram lookups chained by backoff, with Brill rules as a compact alternative; the held-out split decides which numbers mean anything."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nlp-with-python-ch05-categorizing-tagging-words.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch06-learning-classify-text.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch03-processing-understanding-text.md
---

# N-gram Taggers, Backoff and Brill Transformation Rules

Bird, Klein and Loper's NLTK book builds a part-of-speech tagger in stages, each scored on the Brown corpus news category. A **unigram tagger** gives each word its most likely tag. An **n-gram tagger** also conditions on the tags of the n-1 preceding tokens. **Backoff** means that when the specialised model cannot assign a tag, a more general one answers instead.

## The ladder and what each rung scored

| Tagger | Accuracy | Evaluated on |
|---|---|---|
| Default, every token NN | 0.1309 | same sentences it was chosen from |
| Regexp, 8 suffix and number patterns, catch-all NN | 0.2033 | all news sentences, nothing trained |
| Lookup of the 100 most frequent words, no backoff | 0.4558 | the data the table was built from |
| Unigram, trained and tested on all sentences | 93.5% | train equals test, so overstated |
| Unigram, 90/10 split (first 4,160 sentences train) | 81.2% | held-out 10% |
| Bigram, no backoff | 10.3% | held-out 10% |
| Bigram, backing off to unigram, then default NN | 84.5% | held-out 10% |

The bigram tagger alone falls to 10.3% because one unseen word yields `None`, and every later tag in the sentence then has a `None` context. Chaining `DefaultTagger('NN')`, `UnigramTagger(backoff=t0)` and `BigramTagger(backoff=t1)` gives the 84.5%, the best figure in the chapter. In the Brown news training data, roughly one trigram context in twenty (the word and the two tags before it) had more than one tag seen, which the authors present as a bound on n-gram taggers.

## Advice from the chapter

Bird, Klein and Loper advise:
- start from a default baseline, since it sets the floor;
- train and test on separate data;
- tag one sentence at a time, since context should not cross sentence boundaries;
- keep n at 3 or lower, because larger contexts meet the sparse data problem (a context in the data to be tagged that never appeared in training);
- replace low-frequency words with UNK so context can still tag unseen words;
- tabulate gold tags against predicted tags in a confusion matrix, to spot tags worth merging or handling separately. On Brown editorial, the Section 5.4 unigram tagger labels 1.6% of words NN where JJ was correct, and 1.5% NN where NNS was correct.

## Brill tagging

A Brill tagger guesses a tag for each word, then fixes mistakes with rules of the form "replace T1 with T2 in context C". A rule's score is the errors it corrects minus the correct tags it breaks. On a demo of 80 training sentences, 6,555 candidate rules were found, and the top rule, NN to VB when the previous tag is TO, scored 12 (13 tags corrected, 1 broken). The authors assert, without data, that Brill models are a small fraction of an n-gram tagger's size, and recommend them where a small, readable model is wanted. No Brill accuracy is reported.

## Tagging as classification

Chapter 6 recasts tagging as per-word classification. A decision tree on the 100 most common 1 to 3 character suffixes reaches 62.7% on Brown news, with the first 10% of tagged words held out. A naive Bayes classifier using suffixes 1 to 3 plus the previous word reaches 78.9%. A consecutive (greedy sequence) tagger that also feeds in the previously predicted tag reaches 79.8%. An exhaustive hidden Markov search would face 30^10, about 600 trillion, labelings for a 10-word sentence under a 30-tag set. The splits differ by run: the consecutive tagger holds out 10% of sentences, while the decision tree and naive Bayes runs hold out the first 10% of tagged words, so the figures are not directly comparable with each other or with the table.

## The same chain in Text Analytics with Python

Sarkar's chapter 3 (Python 2, NLTK) builds the same kind of chain by hand. A helper takes a list of tagger classes and builds each with the previous result as its backoff, so the first class listed is the last resort. Setup for every score here: NLTK `treebank` tagged sentences, the first 3,500 for training and the rest for testing, accuracy from `tagger.evaluate`, one run.

| Tagger | Result |
|---|---|
| Default tagger, every token NN | 14.5% |
| Regex tagger | better than the default baseline (figure not given) |
| Unigram alone | 86%, but unseen words stay untagged (`None`) |
| Bigram or trigram alone | collapse, since training n-grams rarely recur in test text |
| Unigram, bigram and trigram chained by backoff to a regex tagger | 91% |
| Classifier-based tagger (Naive Bayes) | the most accurate of those built; figure not given |

The extraction gives two reasons for the chain: a unigram tagger leaves unseen words untagged, and bigram and trigram taggers rarely see their training n-grams again in test text. The author advises the chain over single n-gram taggers, and the classifier-based tagger over both. The default-tagger figure (14.5%) is on a different corpus and split from the Brown figure above (0.1309), so the two are not comparable.

## Limits

- Default, regexp and lookup accuracies are scored on the sentences used to build them; only the unigram, bigram and backoff rows use the 90/10 split.
- One split of one Brown category, no variance or cross-validation.
- No accuracy for the Brill tagger, trigram backoff or the UNK approach; they are left as exercises.
- Chapter 6 runs are single runs with no seed, and the positional split takes the first 10%.
- The Text Analytics section is Python 2 with NLTK 3.1 to 3.2.1 and will not run unmodified today; its scores are single runs on a small treebank sample with no variance.
- Python 2 and NLTK 2 code (`simplify_tags`, `FreqDist.keys()` sorted by frequency, the old Brill demo API); the book predates HMM, CRF and neural taggers.

## See Also
- [[Named Entity Recognition and Sequence Tagging]] — extends (tag-per-token labelling with sequence features)
- [[Train, Validation and Test Discipline]] — prerequisite-for
- [[NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers]] — extends
