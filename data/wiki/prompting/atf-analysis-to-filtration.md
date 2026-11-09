---
title: ATF Analysis-to-Filtration Prompting
tags: [prompting, pattern]
summary: "ATF has the model list the irrelevant clauses in a problem, rewrite the question without them, then reason on the filtered text; on GSMIR (GSM8K plus one irrelevant sentence) it lifted chain-of-thought accuracy on GPT-3.5-Turbo from 50.2 to 74.9 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-jiang-2024-enhancing-robustness-large-language-models.md
---

# ATF Analysis-to-Filtration Prompting

The paper (arXiv v2, May 2025) asks why an irrelevant detail in a problem costs LLMs reasoning accuracy, and whether prompting can reduce the damage. Its hypothesis is that models can identify irrelevant information but do not exclude it themselves, so filtering it explicitly before reasoning should recover accuracy.

## GSMIR dataset

GSMIR inserts one thematically related irrelevant sentence into each of 500 GSM8K problems. It builds on an earlier distractor dataset (GSMIC) by making the distractors more topical. GSM8K-SLC is the comparison without the sentence.

## Mechanism

ATF runs in three steps. An LLM-generated analysis demonstration lists the irrelevant clauses; a filtration prompt rewrites the question without them; ordinary prompting then runs on the filtered question. It can be combined with SP, chain of thought (COT), zero-shot COT (0-COT) and least-to-most prompting (LTM).

## Findings (self-reported)

All on GPT-3.5-Turbo (the 16k variant for the error analysis) over 500 problems.

- With the irrelevant sentence, COT accuracy fell from 77.8 to 55.2, and SP accuracy fell from 29.4 to 18.5.
- ATF raised COT accuracy on the GSMIR set, 50.2 up to 74.9, the biggest gain (10 demonstrations). LTM with ATF reached 69.9, 3.5 points under the 73.4 on original questions.
- Of COT errors attributed to irrelevant information, 70.3% (378 of 538) were cases where the model had identified the irrelevant information. For SP it was 76.3% (232 of 304). The authors read this as identify-but-not-exclude.
- Instructed prompting (telling the model to ignore irrelevant information) lowered accuracy in the example given: COT with IP 48.4 against COT 50.2.
- ATF barely helped SP, moving it from 14.9 to 18.1, which the authors attribute to SP errors being mostly computational. ATF-Shuffle recognition of irrelevant information was 79.6.
- ATF missed the irrelevant information in 421 GSMIR problems, and about half or more of those held weak irrelevant information, meaning information that does not change the model's ability to reach the right answer.

## Limits

- One irrelevant sentence per problem, though the authors concede real data has several. Only GPT-3.5-Turbo and its 16k variant; the problems are all arithmetic word problems, and no decoding settings, temperature or seeds are given.
- Internal inconsistencies: error counts of 304 and 538 exceed the 500 problems, unexplained, and the claim that instructed prompting lowers accuracy conflicts with the 0-COT with IP row (58.9 against 52.0 for 0-COT).

## See Also
- [[Context Failure Modes]] — prerequisite-for (distraction from irrelevant context)
- [[Chain of Thought]] — related (the baseline ATF wraps)
- [[Prompt Chaining]] — related (analysis, filter, then answer is a three-step chain)
- [[Prompt Injection]] — related (both are failures to disregard text in the input)
