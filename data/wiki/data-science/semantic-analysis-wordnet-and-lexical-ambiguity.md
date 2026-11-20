---
title: "Semantic Analysis, WordNet and Lexical Ambiguity"
tags: [data-science, nlp, concept]
summary: "WordNet organises senses into synsets with is-a and part-of links, Lesk disambiguates by definition overlap and fails without it, and logic-based semantics evaluates assertions."
updated: 2026-11-20
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--05-semantic-analysis-and-ner.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch07-semantic-sentiment-analysis.md
  - data/raw/papers/2026-11-08-text-analytics-with-python-ch01-natural-language-basics.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch02-accessing-text-corpora-lexical.md
---

# Semantic Analysis, WordNet and Lexical Ambiguity

Meaning from structure rather than from distance (contrast [[Word Embeddings and Similarity Measures]]).

## WordNet

A lexical database that groups words into **synsets** (synonyms sharing one sense) linked by relations. One spelling can have many synsets: "bank" has 18 (10 noun, 8 verb).

| Relation | Meaning | Example |
|---|---|---|
| Synonym / antonym | Same / opposite sense | large and small |
| Hypernym / hyponym | Is-a (general / specific) | tree is a woody plant |
| Holonym / meronym | Part-of / has-part (member, part, substance) | tree has-part trunk; has-substance heartwood |
| Entailment | Verb A implies verb B | walk entails step; eat entails chew |
| Homonyms | Same spelling, different sense | bank (river) and bank (money) |

Because synsets form an is-a tree, distance between senses is measurable: lion and tiger share the hypernym "big cat"; path similarity (1 over 1 plus the shortest is-a path) gives 0.33 for lion and tiger, 0.2 for cat and dog, 0.07 for lion and tree. Lasting uses: lemmatisation, query expansion with synonyms and hypernyms, and a hand-built taxonomy, an early knowledge graph.

## Lesk disambiguation

Lesk picks the sense whose dictionary definition overlaps most with the context words. It got both senses of "lead" and the river bank right, then labelled a bank raising interest rates as a flight manoeuvre: with no definition overlap it has nothing to go on. It is a weak baseline; contextual embeddings disambiguate implicitly and much better, since a static vector blends all senses (see [[Word Embeddings and Similarity Measures]]).

## Figures from a 2016 textbook

Sarkar's chapter 7 reports WordNet as containing more than 155,000 words spread over upwards of 117,000 synsets (version not stated). With NLTK, `tree.n.01` has 180 direct hyponyms. Path similarity over five synsets (tree, lion, tiger, cat, dog) ranks lion and tiger closest at 0.33, with tree against the others between 0.07 and 0.13. Lesk, run through `nltk.wsd.lesk` on five hand-picked sentences, picked the correct sense in every example shown, covering fruit in two sentences and lead as a metal, an actor and a verb; the extraction notes that no failure case is shown.

Chapter 1 of the same book names the word relations by shared spelling, sound and relatedness of meaning (homonym, homograph, homophone, heteronym, heterograph, polyseme, capitonym) and defines the hyponym as the specific subclass word and the hypernym as the generic superclass word. It also lists corpora: the Brown Corpus (15 categories through NLTK, texts from 500 sources), NLTK's Reuters corpus (about 90 categories over 10,788 news articles), the British National Corpus (over 100 million words), and the Google N-gram corpus (over a trillion words, n-grams up to 5) (reported).

## WordNet figures from the NLTK book

Chapter 2 of Bird, Klein and Loper reports WordNet 3.0 (the NLTK copy of that era) as holding 155,287 words and 117,659 synsets. The noun `car` is spread over five synsets, whereas `motorcar` and `automobile` each map to a single one. The first `car` synset reaches `entity.n.01` by two separate hypernym routes, since its parent `wheeled_vehicle.n.01` counts as both vehicle and container. Minimum depth rises as concepts narrow, from 0 for entity through 8 (vertebrate) and 13 (whale) to 14 for baleen_whale. Path similarity drops from 0.25 (right whale versus minke whale) to 0.0435 (right whale versus novel), a score in [0, 1] that is -1 when no path exists; the authors say such numbers "won't mean much". They advise it for matching a search for "vehicle" to documents about limousines, and `lowest_common_hypernyms` and `min_depth` for judging how close two synsets are.

## Logic-based semantic representations

Before statistical NLP, meaning was written in logic. A resolution prover can show that "the dog does not jump over the fox" follows from a rule (if x jumps over y then y does not jump over x) plus the event "the fox jumps over the dog", while failing to prove the opposite. A small model (a domain of entities plus a valuation of predicates) evaluates quantified expressions: "someone studies" true, "everyone studies" false in a two-person domain. Practical descendants are triples, knowledge graphs and constrained output schemas; LLMs now do the extraction step. Extraction itself is [[Named Entity Recognition and Sequence Tagging]].

## Limits

- The textbook's Lesk examples are all cases it gets right, and its code is Python 2 with NLTK of 2016.
- The chapter 1 survey has no experiments; its application descriptions are dated.
- The NLTK book's counts disagree: WordNet is given as 155,287 words in the text but its Table 2-2 says 145k. Its WordNet attributes are properties in NLTK 2 and methods in NLTK 3, and path-similarity scores come with the authors' own caveat that they mean little.

## See Also
- [[Named Entity Recognition and Sequence Tagging]] — related
- [[Word Embeddings and Similarity Measures]] — alternative-to
- [[Feature Structures, Unification and SEM Features]] — extends
