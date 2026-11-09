---
title: RepoCoder Iterative Retrieval-Generation
tags: [rag, pattern]
summary: "RepoCoder uses the model's own previous completion to build the next retrieval query over a repository, iterating retrieve-then-generate with frozen components; on its RepoEval benchmark two iterations beat single-pass retrieval and in-file completion, with no way to choose the iteration count (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhang-2023-repocoder.md
---

# RepoCoder Iterative Retrieval-Generation

Zhang and colleagues (EMNLP 2023) ask how a code language model can draw on the rest of a repository to finish partial code, given that the partial code is itself a weak retrieval query. The hypothesis is that building each new query from the model's own previous completion narrows the gap between what is retrieved against and what must be written.

## Mechanism

No training; both retriever and code model are frozen.

1. A Jaccard retriever over tokens, applied to a sliding window of repository code, fetches snippets, querying with the final lines of the partial code.
2. The code model completes.
3. Later iterations query with the previous prediction's first Ss lines appended to the last (Sw minus Ss) lines of the partial code, and retrieval and generation repeat.

Baselines are **In-File completion** (the prompt holds only the unfinished code) and the **Oracle** (a single retrieval that uses the true first Ss lines instead of a prediction), which serves as an upper bound. The paper also contributes **RepoEval**: line completion (1600 samples, 8 repos), API invocation completion (1600 samples) and function body completion (373 samples, 6 repos, scored by unit tests).

## Results

Self-reported. Setup: Python repos from 2022, GPT-3.5-Turbo unless stated, Sw=20, Ss=10, K=10 for line and API (Sw=50 and up to 500 output tokens for function bodies). The extraction records most scores as labels without values, so only the stated figures appear.

- On line completion, two iterations beat In-File and also single-retrieval RAG, and the paper states an absolute gain over In-File above 10 percent EM and 8 percent ES across the four models on the line and API sets. In-File EM for line completion is 40.56 with GPT-3.5-Turbo; with a UniXcoder dense retriever (line completion, Oracle setup, iteration 2) the score is 56.25, which the paper presents as comparable to the sparse retriever's results.
- Function bodies: iteration 2 matches the Oracle and doubles the In-File pass rate.
- On line completion, CodeGen-Mono-350M at iteration 2 performs about as well as GPT-3.5-Turbo with In-File.
- Recall of the ground-truth API invocation examples goes up between iterations 1 and 2 (1046 eligible API samples); the GT-Code variant, which retrieves snippets containing the true call, is compared against iteration 2's 55.07 EM.
- Iterations are not monotone: for API completion with GPT-3.5-Turbo, going from the third to the fourth iteration adds 10 correct completions but drops 14 (794 to 790).

## Limits

- Little gain when a repository has few duplicated code lines. No method is given for choosing the iteration count and there is no stopping criterion; a later iteration can miss cases an earlier one got right.
- Latency from extra rounds is not measured. Prompt templates, other retrievers and stronger code models are unexplored; baselines are only In-File and Oracle.
- EM undercounts correct completions. Python only, single run, no variance.

## See Also
- [[Repository-Level Coding Benchmarks]] — related
- [[Code Retrieval: Structural Index and Agentic Search]] — related
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[FLARE Forward-Looking Active Retrieval]] — alternative-to (also forms the next query from the model's own output)
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
