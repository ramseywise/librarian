---
title: "Word Segmentation by Objective and Simulated Annealing"
tags: [data-science, pattern]
summary: "Segmenting unspaced text as a search: score a boundary bit string by lexicon size plus word count, then flip bits with a cooling schedule to find a low-scoring split."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nlp-with-python-ch03-processing-raw-text.md
---

# Word Segmentation by Objective and Simulated Annealing

The NLTK book's chapter 3 treats tokenisation, sentence splitting and word segmentation as instances of one **segmentation** problem. For text with no spaces, it annotates each character with a Boolean word-break. A text of length n can break in only n-1 places, so the bit string is one character shorter than the text.

## The objective

Following a Brent and Cartwright (1995) style objective, a segmentation scores `text_size + lexicon_size`: the number of words, plus the length in characters of the space-joined unique words. Smaller is better. On the toy text "doyouseethekittyseethedoggydoyoulikethekittylikethedoggy", three hand-made segmentations score 46, 47 and 63.

## The search

**Simulated annealing** is a heuristic that approximates the best value of a function across a large discrete search space. Here it starts at a temperature equal to the number of bits and, for each of 5,000 iterations at a temperature, flips a number of bits equal to the rounded temperature. It keeps the best-scoring guess and divides the temperature by the cooling rate 1.2 until it falls to 0.5. On the toy text the objective drops from 60 to 42, and the returned split has ten pieces, including the chunks "doyou", "thekitty" and "thedoggy". The output varies between runs because the search is stochastic.

## Where it sits among tokenisers

The same chapter's advice for ordinary text is to tokenise with a regular expression or `nltk.word_tokenize`, with `regexp_tokenize` and the verbose `(?x)` flag for readability, and to evaluate a tokenizer against gold-standard tokens, for example from the Penn Treebank sample. It also advises segmenting into sentences before words when only a character stream exists, using Punkt, whose output on quoted speech split one logical sentence into several strings.

## Limits

- The segmentation example is a toy: 4 utterances and 55 characters, a single unseeded stochastic run.
- The objective and cooling settings are shown on that one text, with no comparison against another segmenter.
- Python 2 and NLTK 2 code; the Punkt model path and the `nltk.word_tokenize` behaviour have since changed.
- The chapter has no treatment of subword tokenisation such as BPE or WordPiece, used by modern language-model pipelines.

## See Also
- [[Text Preprocessing and the Stop-Word Negation Trap]] — prerequisite-for
