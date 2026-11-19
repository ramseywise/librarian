---
title: "Chart Parsing, PCFGs and Structural Ambiguity"
tags: [data-science, concept]
summary: "Why parsers need a chart and probabilities: attachment ambiguity multiplies parses with the Catalan numbers, backtracking recursive descent loops on left recursion, and a PCFG ranks parses by the product of production probabilities."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nlp-with-python-ch08-analyzing-sentence-structure.md
  - data/raw/papers/2026-11-08-loper-2002-nltk.md
---

# Chart Parsing, PCFGs and Structural Ambiguity

A context-free grammar is a set of rewrite rules, each with a single non-terminal as its left side (A -> alpha), and a **constituent** is a group of words that behaves as one unit and can be swapped for another unit of the same category. The NLTK book's chapter 8 motivates grammars with **structural ambiguity**: "I shot an elephant in my pajamas" has more than one analysis because the prepositional phrase can attach in more than one place.

## Ambiguity grows fast

For sentences with ambiguous attachment, the number of parses follows the Catalan sequence (1, 2, 5, 14, 42, ...) and reaches 208,012 at length 23, which the book gives as the average Penn Treebank WSJ sentence length. Setup: strings of repeated "fish" at lengths 3, 5, 7 and up. For length 50 the text claims over 10^12 parses (the extraction prints "1012" for the power of ten). The book concludes that candidate parses should be ranked, not enumerated.

## Parsers walked through

- **Recursive descent** never terminates on left-recursive rules such as NP -> NP PP, explores structures that cannot match the input, and constructs again subtrees that backtracking threw away.
- The well-formed substring table, used as a toy chart parser, only recognises a sentence, needs binary rules and works wastefully bottom-up. In the book's run, one of two VP readings landed in cell (2,8) and the second was lost.
- Bird, Klein and Loper advise chart parsing (dynamic programming that stores intermediate constituents) over backtracking for anything beyond demonstrations. Loper and Bird's 2002 toolkit paper describes chart parsing as a flexible algorithm whose chart data structure records hypotheses about constituents.
- Shift-reduce and left-corner parsers are also covered, with no scores.

## Probabilistic CFGs

A PCFG gives each parse the product of its production probabilities, and productions sharing a left-hand side must sum to one (the sample VP rules are 0.4, 0.3 and 0.3). With the book's hand-written grammar, `ViterbiParser` returns a parse of "Jack saw telescopes" with probability 0.064. Dependency grammar is the alternative the book describes: arcs from each word to a head, with a projectivity test, meaning the arcs can sit above the words and never cross. It suits tasks that want grammatical functions such as subject and object directly. The book's Penn Treebank sample is a 10% sample, which it suggests searching to learn, for instance, what verbs accept a sentence as complement.

## Limits

- No parser is scored for accuracy or speed; grammars are toy-sized.
- One hand-written PCFG; no induction of probabilities from a treebank is shown.
- Python 2 and NLTK 2 APIs (`nbest_parse`, `.node`).
- The chapter is older than neural dependency and constituency parsers, so it is silent on how current parsers rank candidates.

## See Also
- [[Feature Structures, Unification and SEM Features]] — extends (grammar with feature-valued categories)
- [[NP Chunking with IOB Tags: Regexp, N-gram and Classifier Chunkers]] — alternative-to (shallow structure without a full parse)
