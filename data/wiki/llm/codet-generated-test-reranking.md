---
title: CodeT Generated-Test Reranking
tags: [llm, reasoning-and-planning, pattern]
summary: "CodeT has the same pretrained model write many solutions and many assert-style tests, runs every solution on every test, and picks from the consensus set scoring highest on solutions times tests passed; it lifted code-davinci-002 HumanEval pass@1 from 47.0 to 65.8 (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-chen-2022-codet.md
  - data/raw/papers/2026-11-08-fan-2023-large-language-models-software-engineering.md
---

# CodeT Generated-Test Reranking

Chen and colleagues (ICLR 2023) ask how to pick the correct program from many language-model samples without human-written tests. Their hypothesis, in the spirit of RANSAC: correct solutions pass more generated tests and coincide with more of the other solutions, whereas wrong ones scatter and seldom coincide by accident.

## Mechanism

1. Sample N solutions and M assert-style tests from the same pretrained model, zero-shot, adding an instruction to the prompt that asks for tests.
2. Execute every solution on every test.
3. Group solutions that pass exactly the same tests into a **consensus set** (solutions Sx with the tests Sy they all pass).
4. Score each set by **dual execution agreement**: f = |Sx| x |Sy|; the implementation uses sqrt(|Sx|) x |Sy|.
5. Output a solution drawn from the best-scoring set.

There is no training: it is inference-time reranking.

## Results (self-reported)

Setup: code-davinci-002, zero-shot, temperature 0.8, 100 samples and 100 generated test samples per problem, pass@1, unless stated.

- HumanEval (164 problems, example inputs and outputs removed from prompts): 47.0 to 65.8. MBPP sanitized (427 problems): 58.1 to 67.7. With code-cushman-001, HumanEval goes from 33.5 to 44.5.
- CodeT pass@2 on HumanEval (75.1) is close to the baseline's pass@10 (74.9).
- The earlier record on HumanEval pass@1 was 42.7, from a trained ranker (Inala et al.); the two setups are not identical.
- Open models gain too: INCODER-6B gains 13.1 on MBPP pass@1, and across INCODER-6B and CODEGEN-MONO-16B on both HumanEval and MBPP the gains span 4.2 to 13.1.
- APPS introductory pass@1 rises from 27.2 to 34.6 (50 samples), but competition-level gains are only 1.8 to 2.2. CodeContests (165 problems, 1,000 samples) goes from 0.7 to 2.1.
- Replicating AlphaCode's clustering with CodeT's test inputs gives 55.1 against 65.8 ([[AlphaCode Sample, Filter and Cluster]]).
- Ablations: counting only solutions (like [[Self-Consistency]]) gives 55.9 and counting only tests gives 58.4, both below the joint score. With only 10 generated tests per problem, pass@1 still gains 9.5; pass@1 grows from 56.5 (sampling number 10, limit 1) to 65.8 (sampling number 100, limit 5).
- Tests transfer between models: INCODER-6B gains 6.2 and CODEGEN 11.0 on HumanEval pass@1 when code-davinci-002 writes the tests in place of their own. Codex tests average 391.1 per problem with 95.7 statement coverage; CODEGEN's average 55.6 with 78.2.
- Leaving the example inputs and outputs in the HumanEval prompt inflates CodeT to 74.8 because the model copies real tests.

## Related use

[[Planning-Guided Transformer Decoding (PG-TD)]] borrows CodeT's prompt design for auto-generated test cases. A software-engineering survey (Fan et al.) lists combining LLMs with search, test generation or rankers among its recommended practices.

## Limits

- Only executable code qualifies, and writing tests costs extra compute that the paper does not quantify.
- Hard problems (APPS competition, CodeContests) see small gains since the generated tests are poor; a one-shot filter variant is slightly worse than baseline on CodeContests (9.6 against 9.9).
- It assumes incorrect solutions rarely agree. It fails on ambiguous specifications, uncovered corner cases or misread problems: with code-cushman-001, 53 of 164 HumanEval problems had a correct solution outside the top consensus set, and about 20% of those were due to ambiguity, corner cases or missing imports.
- Single run, no variance or significance; numbers differ from original HumanEval because examples were removed.
- The Codex models are deprecated, so the runs cannot be reproduced through the API.

## See Also
- [[AlphaCode Sample, Filter and Cluster]] — alternative-to
- [[Self-Consistency]] — related (agreement ranking; the solutions-only ablation)
- [[Planning-Guided Transformer Decoding (PG-TD)]] — related (borrows the test-generation prompt)
- [[HumanEval and pass@k]] — prerequisite-for
- [[CodeRL Unit-Test Actor-Critic]] — related
- [[LIBRO LLM Bug-Reproducing Tests]] — related
