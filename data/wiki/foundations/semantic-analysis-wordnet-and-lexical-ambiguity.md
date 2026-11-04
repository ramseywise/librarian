---
title: "Semantic Analysis, WordNet and Lexical Ambiguity"
tags: [foundations, concept]
summary: "WordNet organises senses into synsets with is-a and part-of links, Lesk disambiguates by definition overlap and fails without it, and logic-based semantics evaluates assertions."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--03-nlp--notes--05-semantic-analysis-and-ner.md
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

## Logic-based semantic representations

Before statistical NLP, meaning was written in logic. A resolution prover can show that "the dog does not jump over the fox" follows from a rule (if x jumps over y then y does not jump over x) plus the event "the fox jumps over the dog", while failing to prove the opposite. A small model (a domain of entities plus a valuation of predicates) evaluates quantified expressions: "someone studies" true, "everyone studies" false in a two-person domain. Practical descendants are triples, knowledge graphs and constrained output schemas; LLMs now do the extraction step. Extraction itself is [[Named Entity Recognition and Sequence Tagging]].

## See Also
- [[Named Entity Recognition and Sequence Tagging]] — related
- [[Word Embeddings and Similarity Measures]] — alternative-to
