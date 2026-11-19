---
title: "Feature Structures, Unification and SEM Features"
tags: [data-science, concept]
summary: "Feature structures replace atomic grammar categories so agreement is shared across a production, and a SEM feature carries a meaning built during parsing, from SQL strings to logic with quantifier scope."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-nlp-with-python-ch09-building-feature-based-grammars.md
  - data/raw/papers/2026-11-08-nlp-with-python-ch10-analyzing-meaning-sentences.md
---

# Feature Structures, Unification and SEM Features

The NLTK book's chapter 9 extends a context-free grammar (see [[Chart Parsing, PCFGs and Structural Ambiguity]]) by replacing atomic categories (S, NP, V) with a **feature structure**: a dictionary-like set of attribute-value pairs. The motivation given is to stop atomic categories from multiplying massively, since singular and plural, and person, become feature values within one production.

## Unification

**Unification** combines what two feature structures say, or fails. It returns `None` when one path holds two distinct atoms (`A='a'` against `A='b'`); unifying with a structure it subsumes gives back the more specific of the two. **Subsumption** is the partial order in which a more general structure subsumes a less general one. When two paths share one value (**re-entrancy**), specialising one specialises the other at once. Bird, Klein and Loper advise using variables over feature values so that subject-verb agreement is a property of one production, putting fixed values in the lexicon and requiring each phrase's values to unify with its children's, and handling unbounded dependencies with slash categories, where A/B marks a gap of type B inside A.

## A SEM feature carries meaning

Chapter 10 builds a meaning alongside the parse. With a grammar whose SEM values are assembled by string concatenation, "What cities are located in China" becomes a SQL query selecting City from city_table where Country is "china", over the Chat-80 city table (Athens at 1368 thousand, data from at least the 1980s).

Beyond SQL, the chapter builds meanings compositionally with the lambda-calculus. Three results are claims or worked examples:
- "Everybody admires someone" reads two ways in first-order logic: each person may admire someone different, or one person is admired by all.
- A syntax-driven translation yields only the first scoping of "Every girl chases a dog", while **Cooper storage**, which stores quantifiers and retrieves them in any order, generates every ordering.
- A discourse representation structure (referents plus conditions) lets "Angus owns a dog" bind the pronoun in "It bit Irene".

Checking a representation is done by evaluating it in a model and asking Prover9 for entailment. When a proof fails, Mace4 builds a countermodel. Given the premises that there is a woman whom every man loves, that Adam is a man and that Eve is a woman, Mace4 finds a model where Adam and Eve are the same individual and the loved woman is a second one, so "Adam loves Eve" does not follow.

## Limits

- Both chapters are formal-linguistics tutorials with toy grammars; nothing is scored on a corpus or benchmark.
- The SQL grammar was written by hand for a single table with a small vocabulary; the chapter itself says this restricted-domain approach needs a theory of meaning to generalise.
- Logic handles consistency and entailment; lexical meaning, vagueness and world knowledge fall outside it.
- The chapters do not relate feature grammars to statistical or neural parsing, and Python 2 and NLTK 2 APIs are used. Prover9 and Mace4 are external binaries.

## See Also
- [[Semantic Analysis, WordNet and Lexical Ambiguity]] — related (logic-based semantic representations)
