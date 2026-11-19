---
title: ODEX Open-Domain Execution-Based Code Evaluation
tags: [eval, code, benchmark]
summary: "ODEX has 945 natural-language-to-Python problems over 79 libraries with 1,707 human-written tests in four languages; Codex pass@1 is much lower on library-using (open-domain) problems, and one random test overstates pass@1 when a problem has three or more tests (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-wang-2023-execution-based-evaluation-open-domain.md
  - data/raw/papers/2026-11-08-fan-2023-large-language-models-software-engineering.md
---

# ODEX Open-Domain Execution-Based Code Evaluation

Wang and colleagues note that earlier execution benchmarks are closed-domain, so models could behave differently when queries involve libraries. ODEX is their open-domain set. In it, **open domain** means the code calls any library (standard or third-party) and closed domain means it calls none.

## Construction

Annotators took 945 pairs from CoNaLa and MCoNaLa (StackOverflow), turned each snippet into a function with its imports, and wrote tests of three kinds: mock, bounding and specialised equality. The set covers 79 libraries, 1,707 tests (average 1.8 per problem, against 7.7 for HumanEval and 13.2 for APPS) and four natural languages (439 English, 90 Spanish, 164 Japanese, 252 Russian problems); Library use appears in 53.4% of the problems. Annotators' canonical solutions pass all tests.

## Results (self-reported)

Setup: pass@k with a zero-shot docstring prompt, no fine-tuning, top-p 0.95 sampling at temperature 0.8 and a 512-token cap.

- On English, code-davinci-002 scores 47.15 pass@1. CodeGen-6.1B-mono gets 34.49 against 33.62 for davinci-001, matching it at pass@1 but not at pass@10 (43.05 against 67.43).
- For davinci-002 the pass@1 shortfall on open-domain problems varies by language: 4.34 points for Spanish up to 38.57 for Japanese. Moving from C1 to D1 to D2 does not always shrink it; it grows in English and Japanese. For CodeGen the shortfall narrows as models grow, by about 6.3 points on English between 2.7B and 6.1B. StarCoder 16B shows 37.00 open against 53.11 closed on English.
- By library, davinci-002 manages around 50% pass@1 for common ones like random and math but below 10% for matplotlib and tensorflow. Among 60 inspected examples, 16 of the 26 open-domain failures (61.5%) never used the required libraries.
- Putting one test case in the prompt helps clearly; more adds little.
- Scoring with one random test instead of all barely changes the full-set English pass@1 (48.31 against 47.15), but on problems with three or more tests it overstates it: English 60.7 against 52.7, Spanish 64.7 against 47.1.
- Execution-free metrics (BLEU, ROUGE-L, METEOR, ChrF, CodeBLEU) order the Codex models differently, and BLEU hardly distinguishes passing from failing samples.

## Related evidence on weak tests

A software-engineering survey (Fan et al.) cites EvalPlus as showing that thin test suites let false positives through; its figure and setup are on [[EvalPlus and HumanEval+]].

## Limits

- Executing open-domain code and tests needs a safety inspection.
- Language coverage is bounded by StackOverflow forums; the set is small, and the authors urge significance testing.
- StackOverflow posts may overlap with closed models' training data; edits and a StarCoder and SantaCoder check mitigate this.
- With 1.8 tests per problem, the argument that tests suffice rests on the one-versus-all ablation.
- Models are 2022-era Codex and CodeGen.

## See Also
- [[HumanEval and pass@k]] — prerequisite-for
- [[DS-1000]] — related (another library-using execution benchmark)
- [[EvalPlus and HumanEval+]] — related
- [[APPS Coding Challenge Benchmark]] — related
