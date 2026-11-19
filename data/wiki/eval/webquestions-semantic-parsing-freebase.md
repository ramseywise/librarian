---
title: WEBQUESTIONS and Semantic Parsing on Freebase
tags: [eval, language-tasks, benchmark]
summary: "Berant et al. train a Freebase semantic parser from question-answer pairs alone, using an alignment lexicon and a bridging operation, and release WEBQUESTIONS (5,810 examples); the full system scored 31.4% on its test set (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-berant-2013-semantic-parsing-freebase-question-answer.md
---

# WEBQUESTIONS and Semantic Parsing on Freebase

Berant and colleagues (EMNLP 2013) ask whether question-answer pairs alone, with no annotated logical forms, can train a parser able to handle the thousands of Freebase predicates. They hypothesise that coarse text-to-knowledge-base alignment, plus an operation that builds predicates from neighbouring ones, shrinks the predicate space enough to learn from answers.

## Method

The parser, SEMPRE, is a beam-based bottom-up parser over lambda-DCS logical forms, scored by a log-linear model. Training maximises the log-likelihood of derivations whose **denotation** matches the gold answer; a denotation is what a logical form evaluates to over the knowledge base, a set of entities or entity pairs.

- **Alignment lexicon:** ReVerb triples extracted from ClueWeb09 and linked to Freebase give a coarse phrase-to-predicate lexicon.
- **Bridging:** creates a binary predicate from the adjacent predicates (neighbouring unaries or event variables) instead of from the words.
- Features cover part of speech, rule counts and denotation size, soft-encoding composition rules.

## The dataset

WEBQUESTIONS was built by sending 100K Google Suggest questions to Mechanical Turk at $0.03 per question; 6,642 received identical annotations from two or more workers, and 5,810 examples (4,525 word types) are released. The extraction does not explain the gap. The Freebase dump (2013-06-09) has 41M non-numeric entities, 19K properties and 596M assertions. The paper also evaluates on FREE917 (Cai and Yates).

## Results (self-reported)

- WEBQUESTIONS test (35% held out): full system 31.4%; removing bridging, denotation and alignment features gives 26.9%.
- Development set, average of three random splits: alignment alone 30.6% on WEBQUESTIONS, bridging alone 21.2%, combined 32.9%. On FREE917, bridging alone gives 66.9 against 38.0 for alignment, combined 71.3.
- Without denotation features the dev scores fall to 28.0 on WEBQUESTIONS (from 32.9) and 58.6 on FREE917 (from 71.3); without part-of-speech features WEBQUESTIONS dev is 28.9.
- Adding lexicalised features gives the best WEBQUESTIONS dev (36.4) but overfits on small FREE917.
- On FREE917 (30% held out, with a manual entity lexicon of 1,100 entries) the system trained on answers only outperforms Cai and Yates, whose system learned from logical forms.

## Limits

- Gold answers come only from the entity's Freebase page, which makes some of them imprecise or partial.
- WEBQUESTIONS accuracy (31.4%) sits well under FREE917's (62%). The authors blame disambiguating among 41M entities, bridging errors when many binaries fit, and verbs taken from subordinate clauses.
- FREE917's manual lexicon simplifies entity disambiguation; questions are structurally simple.
- The paper does not give the learning rate, AdaGrad step size, regularisation or hardware.

## See Also
- [[GrailQA Three Levels of KBQA Generalization]] — related (another Freebase question set)
- [[WikiSQL and Seq2SQL]] — related
