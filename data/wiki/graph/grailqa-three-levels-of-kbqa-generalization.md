---
title: GrailQA Three Levels of KBQA Generalization
tags: [graph, reference]
summary: "GrailQA is a 64K-question Freebase dataset that tests knowledge-base QA at three levels (i.i.d., compositional, zero-shot); the accompanying BERT ranking model scored 50.6 EM overall and its zero-shot results depended heavily on BERT (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-gu-2021-beyond-i-i-d.md
---

# GrailQA Three Levels of KBQA Generalization

Gu et al. (WWW 2021). The paper studies how knowledge-base question answering models generalise beyond the training distribution, and releases GrailQA.

## The three levels

- **I.I.D.**: every schema item a test question uses (relation, class or function) was seen in training, and the questions are drawn from the training distribution.
- **Compositional**: every schema item appears in training, but the specific logical form does not.
- **Zero-shot**: a test question uses one or more schema items that training never showed.

## Dataset and method

The dataset pairs 64,331 questions with logical forms, drawn over Freebase Commons from 4,969 canonical forms with 29,457 paraphrases. Logical forms are generated and checked, canonical questions are annotated, then crowd workers paraphrase them. Answers are S-expressions, a linearised set-based logical form. The authors' model is an LSTM sequence-to-sequence network over BERT encodings, used in two ways: as a generator (Transduction), or as a ranker over candidate logical forms enumerated near the linked entities (Ranking). Both prune the vocabulary to items within 2 hops of entities mentioned in the question.

## Results (self-reported)

- On the test split of 13,231 questions (half zero-shot, a quarter each i.i.d. and compositional), using the BERT-base ranker and an entity linker built from BERT NER plus FACC1 popularity, overall EM is 50.6 and F1 58.0 (self-reported); zero-shot EM 48.6 and F1 55.7, against EM 28.9 and F1 33.8 with GloVe.
- Transduction zero-shot EM was 25.7 with BERT against 3.0 without. Swapping BERT for GloVe cut Transduction F1 by 17.5% (compositional) and 26.2% (zero-shot), and Ranking F1 by 21.9% (zero-shot). On i.i.d. questions BERT and GloVe were similar, and GloVe Ranking had slightly higher EM (62.2 against 59.9).
- Vocabulary pruning raised Transduction overall EM from 26.6 to 33.3. Candidate generation for Ranking has 80% recall.
- The BERT entity linker scored F1 72.2 against 17.2 for Aqqu. In an error analysis of 100 wrong Ranking answers, 34% were coverage limits, 33% entity linking and 26% relation mis-classification.
- Further results: F1 of 25.0 on GraphQ, 3.5 above SPARQA; pretraining on GrailQA yielded 43% F1 on WebQuestions without in-domain data (assuming perfect entity linking). Among 100 sampled canonical forms, 5.6% held annotation errors.

## Limits

- Candidate enumeration for Ranking reaches about 80% of questions and allows at most 2 relations. Both Ranking and the QGG baseline break on superlatives and comparatives, which tend to have no topic entity. Entity linking is a large bottleneck, and the authors admit they do not know why BERT helps.
- Freebase is no longer updated, models are LSTM plus BERT-base with no LLM baselines, runs are single with no variance, and the data is English and Freebase Commons only.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Reasoning on Graphs]] — related
- [[Text-to-Cypher]] — related (logical-form generation against a graph)
