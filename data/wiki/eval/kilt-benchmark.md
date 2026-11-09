---
title: KILT Benchmark
tags: [eval, reference]
summary: "KILT maps 11 knowledge-intensive datasets across 5 tasks onto one 2019 Wikipedia snapshot with provenance, and its joint scores pay out only when the right page is ranked first; RAG-style baselines beat closed-book BART on most tasks except ELI5 (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-petroni-2021-kilt.md
---

# KILT Benchmark

Petroni and colleagues (2021) ask how knowledge-intensive tasks, namely checking facts, linking entities, filling slots, answering open-domain questions and holding dialogue, can all be evaluated against a single Wikipedia snapshot, letting retrieval and generation components be compared across tasks, with credit for naming the supporting evidence. Their hypothesis is that one shared dense index feeding a seq2seq model makes a strong general-purpose baseline.

## Design

- Eleven datasets spanning five tasks are mapped onto the 2019/08/01 Wikipedia snapshot of 5.9M articles, behind one JSONL interface. Mapping drops about 18 percent of dev and test instances in every task except entity linking (BLEU threshold 0.5); about 28 percent of the source articles hold knowledge the tasks need.
- **Provenance** is a set of Wikipedia text spans that contain evidence for an output. An annotation campaign extended it for NQ and others.
- **R-precision** is r over R: relevant pages among the top R retrieved, where R is the size of the provenance set.
- **KILT scores** are downstream metrics (accuracy, EM, F1, ROUGE-L) awarded only when R-precision is 1, so the gold provenance page must be ranked first. They are inspired by the FEVER score.
- Baselines: task-specific systems, closed-book BART and T5, BART with DPR, RAG, and retrievers including a multi-task DPR trained across tasks.

## Results

Self-reported, on KILT test sets, single runs.

- RAG and BART+DPR beat closed-book BART on FEVER accuracy (BART 78.93, BART+DPR 86.74), TriviaQA (BART 32.39, BART+DPR 58.55) and slot filling; ELI5 is the exception, where retrieval does not help ROUGE-L and closed-book BART beats RAG (RAG 14.05, BART+DPR 17.41).
- On entity linking the specialist BLINK is best; closed-book BART is strong on AIDA (BLINK 81.54, RAG 72.62).
- Retrieval: multi-task DPR improves page R-precision over single-dataset DPR on NQ, zsRE and T-REx; entity-centric retrieval wins the entity tasks; tf-idf beats the DPR variants on Wizard of Wikipedia retrieval.
- KILT scores fall steeply where provenance is hard: on ELI5 RAG can answer but cannot justify, HotpotQA KILT-EM is very low despite an EM of 26.97, and NQ KILT-EM is far below EM (44.39) for RAG.
- Mapping preserves quality: DPR on KILT NQ dev is close to the 41.5 its authors reported.

## Limits

- Provenance may not be exhaustive, since other pages can hold the evidence; annotator agreement is low (kappa 0.3 for NQ, 0.1 for ELI5). Provenance could also come from a different system than the one answering.
- In-knowledge-base only: unanswerable instances and the FEVER not-enough-info label are left out. Provenance is scored at page level, and R-precision of 1 usually needs the top page right.
- Single-run baselines with no hyperparameters, seeds or compute are reported; on NQ the test score is 3 to 4 points under dev. Evidence documents for TriviaQA and ELI5 are not guaranteed to hold evidence (estimated 79.7 percent for TriviaQA). Closed-book models cannot receive KILT scores.
- Dated: 2019 snapshot, BART and DPR era baselines, 2020 leaderboard.

## See Also
- [[RAG Evaluation]] — prerequisite-for
- [[Long-Form QA Evaluation Hurdles]] — related (built on the KILT ELI5 leaderboard)
- [[Wizard of Wikipedia]] — instance-of
- [[LAMA Knowledge Probe]] — prerequisite-for
- [[RA-DIT Dual Instruction Tuning]] — related
- [[2WikiMultiHopQA]] — related
