---
title: LIBRO LLM Bug-Reproducing Tests
tags: [prompting, pattern]
summary: "LIBRO prompts Codex with a bug report, samples many tests, runs them on the buggy program, clusters failures and ranks them, showing a test only when the largest failure cluster is large enough; on Defects4J it reproduced 251 of 750 bugs (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-kang-2023-large-language-models-few-shot.md
---

# LIBRO LLM Bug-Reproducing Tests

Kang, Yoon and Yoo (2023) ask whether an LLM prompted with a bug report can generate tests that reproduce general (non-crash) bugs, and whether post-processing can say when to trust them. A **BRT** (bug-reproducing test) fails because of the bug in the report; a **FIB** test compiles and fails in the buggy program.

## Pipeline

1. Write a Markdown prompt out of the bug report, with example report-and-test pairs added if wanted.
2. Sample tests from Codex at temperature 0.7.
3. Insert each test into the existing test class most similar in wording, then fix imports.
4. Run on the buggy program and cluster the failing tests by failure output.
5. Rank by match to the report, cluster size and test length; output is shown only when the biggest cluster of failures passes a size threshold.

## Results (self-reported)

Unless stated otherwise: Defects4J 2.0, code-davinci-002 sampled at temperature 0.7, 50 samples per bug, and two handpicked examples.

- 251 of 750 Defects4J bugs reproduced; 10 of the 31 bugs in the post-cutoff GHRB set under the same default setting.
- Top-1 ranked test reproduces 149 bugs against 116 for random ranking (threshold 1, 350 selected bugs).
- A threshold of 1 selects 350 of the 570 FIB bugs, of which 219 are reproduced (precision 0.63, recall 0.87). A threshold of 10 gives precision 0.84 and recall 0.42.
- n=10 samples per bug: no example reproduces 124, two examples a median of 173. A within-project example does worse than a generic one because Codex copies it. Stack traces help crash bugs (84 against 69 reproduced, one example).
- The count of reproduced bugs rises logarithmically as more tests are generated and shows no plateau (1000 resamples from 50 tests per bug).
- 91 more unique bugs than EvoCrash on the 60-bug JCrashPack and Defects4J overlap (19 crash bugs).
- One run of 50 tests lasts 444 s overall, with 292 s spent querying the API (i7-7700).
- Repository analysis motivating the task: the median ratio of tests added by issue-linked commits to the current suite size is 28.4% (300 Java repositories). Separately, in generated tests 81% of tokens come from code snippets in the report, where snippets exist. Among 40 failures checked by hand, the commonest cause is missing helper definitions (13).

## Limits

- Codex has probably been trained on the Defects4J projects, and GHRB contains just 31 bugs.
- Findings might not hold for other languages, or for projects that differ from what the model was trained on.
- Tests needing external files or unusual infrastructure fail (Checkstyle 0 of 13, Closure 2 of 172).
- The model, code-davinci-002, was available only in closed beta and has been retired.
- Beyond resampling there is no variance or significance testing; ablations use n=10 where the default is n=50.

## See Also

- [[Code Generation Prompting]] — prerequisite-for
- [[CodeT Generated-Test Reranking]] — related (joint test and code generation)
- [[HumanEval and pass@k]] — related (the Codex sampling setup)
- [[Few-Shot Prompting]] — related (report-test example pairs in the prompt)
