---
title: "Lexical Diversity: Types, Tokens and Conditional Frequency Counts"
tags: [data-science, concept]
summary: "Counting tokens against types, and counts split by genre or language with a conditional frequency distribution, with the normalisation steps that change the count and the caveats on raw counts."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nlp-with-python-ch01-language-processing-python.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch02-accessing-text-corpora-lexical.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch03-processing-raw-text.md
---

# Lexical Diversity: Types, Tokens and Conditional Frequency Counts

A **token** is a sequence of characters treated as a group; a **word type** is a word's spelling independent of its occurrences. **Lexical diversity** is `len(text) / len(set(text))`: tokens divided by types, i.e. mean uses per type. The NLTK book reports tokens and types separately and normalises before counting types.

## What normalising does to a type count

Setup: Moby Dick (NLTK text1), 260,819 tokens including punctuation. Case-sensitive, it has 19,317 types. Lowercasing every token gives 17,231, and lowercasing while keeping only alphabetic tokens gives 16,948. Genesis (text3) has 44,764 tokens and 2,789 types, so about 16 uses per type. On chapter 2's count (tokens per type, types lowercased), diversity ranges from 5 for Blake's poems to 79 for the King James Bible across 18 Gutenberg texts, with sentence length and diversity varying by author but not word length. The Chat Corpus scores 7.42 against Genesis at 16.05. Brown Corpus genres range from 4.3 (humor, 21,695 tokens) to 8.3 (fiction: romance, 70,022 tokens). In Moby Dick, nearly half the text is its 50 commonest tokens, mostly function words and punctuation, while about 9,000 words appear only once (hapaxes).

Bird, Klein and Loper advise setting aside both the commonest words and the hapaxes when hunting for characteristic words, for instance with a combined word-length and frequency filter.

## Conditional frequency distributions

A **conditional frequency distribution** keeps one frequency distribution per condition and is built from (condition, event) pairs. The Brown Corpus gives 1,161,192 events over 15 genre conditions. Counts of six modal verbs by genre show *will* most frequent in news and *could* in romance. In the UDHR translations, words up to five letters long are roughly 80% of the Ibibio text, 60% of the German and 25% of the Inuktitut.

Stop words are 34% of Reuters tokens (content fraction 0.66), tokens lowercased before lookup. The chapter's wordlist is a 2,400-entry list, and the current NLTK English list is about 180 words, so the 0.66 would not reproduce.

## Limits

- Counts are raw, not normalised by genre or corpus size, with no significance testing; the modal-verb comparison depends on genre size.
- The authors say the Gutenberg average word length of about 4 is really 3, because the character count included spaces.
- Single-run counts on small, dated sample corpora with no baselines; Python 2 and NLTK 2 APIs (`FreqDist.keys()`, `inc`).
- Chapter 1 does not print its authors or year; the book is dated 2009.

## See Also
- [[Text Preprocessing and the Stop-Word Negation Trap]] — related (normalisation steps)
- [[Bag of Words, n-grams and TF-IDF]] — related
