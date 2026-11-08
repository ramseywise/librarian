---
title: GHOSTS Benchmark
tags: [eval, reference]
summary: "A set of 709 maths prompts in six subdatasets (proofs, graduate textbook exercises, integrals, olympiad problems, search-style queries) graded 1-5 by expert mathematicians with error codes; ChatGPT averaged 3.20 and 3.29 on two January 2023 versions and GPT-4 4.15 on a 170-prompt subset (self-reported), under a pass line of 3.5."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-frieder-2023-mathematical-capabilities-chatgpt.md
---

# GHOSTS Benchmark

GHOSTS (Frieder et al., arXiv 2301.13867, 2023, Oxford and Vienna) tests ChatGPT on maths
prompts that include proofs and graduate textbook exercises, where an answer is often a proof and cannot
be condensed to a number. It has 709 prompts in six subdatasets and 1,636 expert ratings in total
(709 plus 24 prompt-engineered prompts, on two ChatGPT versions, plus 170 on GPT-4).

## Contents and grading

Subdatasets: Grad-Text (130 prompts from graduate textbook exercises), Holes-in-Proofs
(162, textbook proofs with parts deleted), Olympiad (101, plus 24 prompt-engineered), Symbolic
Integration (100, converted by hand from another dataset's Polish notation), MATH (138, a random
sample) and Search-Engine-Aspects (78, expert-written queries). The authors wrote and graded
everything; raters range from master's degrees to professorships, with harder prompts going to
more senior people.

Ratings use a five-point scale: 1 means the question was not understood, 2 understood but
wholly wrong, 3 partly right, 4 mostly right and 5 fully right. Ratings 2 to 4 must carry an
error code and a 5 may not; codes cover missing information, wrong statements, wrong computation, several logic
errors (missing step, unsupported inference, circular reasoning and others) and broken
rules, with separate warning codes such as hallucination.

## Results (self-reported)

- ChatGPT, 9 January version: mean 3.20 (SD 1.23); 30 January version: 3.29 (SD 1.28).
  GPT-4, on the 170-prompt miniGHOSTS only: 4.15 (SD 1.12).
- Symbolic Integration averaged 2.51 for the January 9 version, against 3.50 for GPT-4 on a
  10-item subset. On MATH 29% of answers were perfect (GPT-4 70%). On Olympiad 75% were rated 2 and none
  received a 5. Reverse Definition Retrieval scored best at 4.30 (SD 1.14).
- The two ChatGPT versions had roughly the same number of grade-4 outputs although fewer than
  half of the prompts matched between them.
- miniGHOSTS draws ten prompts from every one of the 17 files, chosen so that mean and SD
  on the 30 January version match the file's, and then hand-picked for variety.
- Rephrasing about a fifth of the Olympiad prompts (step-by-step, or opening with "Prove
  that") reduced some error types, increased logic errors and left the mean almost unchanged.

## Limits

- Conceded by the authors: possible human error, incomplete checks, a size too small for
  fine-tuning, and no development/test split.
- No agreement statistic: only fewer than 10 samples per dataset got a second reviewer. Whether
  raters were blind to the model version is not shown. miniGHOSTS was tuned on one model,
  and GPT-4 never ran the full set, so its 4.15 covers different items from the 3.20 and 3.29.
- Contamination is argued (Polish notation, terse solutions, dialogue-style prompts) and not
  tested; Grad-Text comes from standard textbooks and is withheld for copyright.
- One sample per prompt through the web interface at unknown temperature; early-2023 models.

## See Also
- [[GSM-Symbolic]] — related (a later, automated maths robustness test)
- [[IMO-Bench]] — related (proof grading by experts, later and harder)
- [[Eval Error Bars and Sample Size]] — related
- [[Eval Contamination Defenses]] — related
