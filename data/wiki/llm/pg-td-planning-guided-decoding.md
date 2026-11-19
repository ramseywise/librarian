---
title: Planning-Guided Transformer Decoding (PG-TD)
tags: [llm, reasoning-and-planning, pattern]
summary: "PG-TD runs a Monte-Carlo tree search over tokens, scoring each node by completing the program with beam search and measuring its pass rate on public tests; with Codex it raised APPS introductory pass rate from 33.26 to 59.14 on 100 problems, though sampling and filtering catches up at larger budgets (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-zhang-2023-planning-large-language-models-code.md
---

# Planning-Guided Transformer Decoding (PG-TD)

Zhang and colleagues (ICLR 2023) ask whether a planning algorithm integrated with a pretrained code transformer can beat conventional beam search and the sampling-plus-filtering scheme. Their hypothesis is that public-test pass rate works better as a lookahead reward inside decoding than as a filter applied after programs are finished, and that it needs fewer samples.

## Mechanism

PG-TD runs a Monte-Carlo-tree-search-style search over tokens. No weights change at decode time, and it needs no grammar knowledge.

- **Selection:** P-UCB, with the transformer's next-token probability as a weight.
- **Expansion:** add the top-k next tokens.
- **Evaluation:** finish the program with transformer beam search, then score the result by its pass rate on the public tests.
- **Backup:** propagate the maximum reward up the tree.

Two caches (tree structure and sequence) share information between beam search and tree search. The baseline **Sampling + Filtering (S+F)** samples many complete programs, runs public tests and returns the one with the best pass rate. Outputs can also be used to fine-tune the model, using the reward-weighted loss from [[CodeRL Unit-Test Actor-Critic]].

## Results (self-reported)

Setup: APPS introductory unless stated, 256 transformer generations, public tests as the reward.

- GPT-2 1.5B: PG-TD leads beam search, S+F and the SMCG-TD baseline on pass rate (beam search 11.95). With GPT-Neo it gets 29.27% against 27.71% for S+F. On CodeContests (165 problems) with GPT-2: 24.05% against 20.40%.
- Strict accuracy is not always better: S+F matches or beats PG-TD on APPS introductory with GPT-2 (13.80 against 13.10).
- Codex (code-davinci-002) on the first 100 introductory problems only: strict accuracy goes 14 to 31 and pass rate 33.26 to 59.14, measured against beam search. On the same subset GPT-2 1.5B goes from 11.65 to 36.42.
- Using Codex-generated tests (prompt from [[CodeT Generated-Test Reranking]]) on a HumanEval subset, PG-TD reaches 74.53% strict accuracy against 26.82% for beam search. Run against the human sample solutions, those tests accept them in 72.56% of cases.
- One public test case already gives 23.27 pass rate against 13.61 for beam search (first 500 problems); three give 33.02.
- Changing the reward changes the output: a length-penalty reward shortens code (248.42 down to 190.73) at pass rate 22.82 versus 23.14, and a comment-encouraging reward lifts comment lines per program from 0.68 to 3.11.
- Compilation errors fall to 1.93% (from 5.58%) and runtime errors to 19.5% (from 32.95%). Using both caches, time falls to 1312.27 s from 2206.38 s. After fine-tuning GPT-2 2.7B on PG-TD solutions, beam search reaches pass rate 16.54, versus 14.32 for the original model and 15.24 when the extra data comes from S+F.

## Limits

- It needs test cases; the authors say auto-generated tests partly address that.
- It costs more compute than beam search because it runs beam search many times.
- At 512 generations the gap to S+F narrows (28.27 against 27.33), and S+F is ahead on pass@100 (28.3 against 27.3).
- Backbones are APPS-finetuned GPT-2 and GPT-Neo from 2022; Codex was run on a 100-problem subset only because of API limits, and is now deprecated.
- Seeds, variance and significance tests are absent; the public and private test split is the authors' own even split of APPS test cases, not an official one.
- Sequence caching with more than one beam may underestimate values.

## See Also
- [[CodeT Generated-Test Reranking]] — alternative-to (tests as a filter, not a search reward)
- [[AlphaCode Sample, Filter and Cluster]] — alternative-to
- [[APPS Coding Challenge Benchmark]] — prerequisite-for
- [[Self-Evaluation Guided Beam Search]] — related
