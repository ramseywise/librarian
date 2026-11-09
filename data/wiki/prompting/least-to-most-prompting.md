---
title: Least-to-Most Prompting
tags: [prompting, pattern]
summary: Two-stage few-shot prompting that first lists easier subproblems and then solves them in order, feeding earlier answers forward; large gains on length generalisation, small ones on GSM8K.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-zhou-2022-least-most-prompting-enables-complex.md
---

# Least-to-Most Prompting

Least-to-most prompting splits reasoning into two prompts. A decomposition prompt, shown a few worked examples, lists the subproblems of a new question. A solving prompt then answers them one at a time, with each prompt including the answers already obtained. The aim is easy-to-hard generalisation: solving problems harder than the exemplars. No training is involved. The main model was code-davinci-002; text-davinci-002, code-davinci-001 and a 540B model were also tried. Baselines used the same exemplars in standard and chain-of-thought form.

## Reported results (all self-reported)

| Task and setup | Least-to-most | Chain-of-thought |
|---|---|---|
| SCAN length split, code-davinci-002 (standard prompting 16.7) | 99.7 | 16.2 |
| Last-letter concatenation, 12 words, 2-shot, 500 lists | 74.0 | 31.8 |
| Same task, 4 words | 94.0 | 84.2 |
| Same task, 8 words | 83.0 | 50.2 |
| GSM8K overall, 1-shot with a 2-step exemplar | 62.39 | 60.87 |
| GSM8K problems needing at least 5 steps, 1-shot | 45.23 | 39.07 |
| GSM8K 2-step problems, 1-shot | 74.53 | 76.68 |
| GSM8K, engineered multi-example prompts | 68.01 | 68.613 |
| DROP non-football numerical, code-davinci-002 | 82.45 | 74.77 |
| DROP football, code-davinci-002 | 73.42 | 59.56 |

Standard few-shot prompting scored 0.0 at every list length from 4 to 12 words. A 2-shot least-to-most prompt (123 tokens) beat an 8-shot CoT prompt (573 tokens) at 12 words, 74.0 against 38.4. On SCAN with text-davinci-002 on 100 commands, least-to-most scored 76.0 against 0.0 for CoT. In the paper's failure analysis, of 13 code-davinci-002 SCAN errors, 6 misread repeats after "around" and 7 read "after" as "and"; of 20 DROP failures, 4 were wrong decompositions, 13 wrong solving and 3 wrong labels.

## Limits

- The authors report that a decomposition prompt written for math did not work for commonsense questions, and that generalising decomposition is hard even within one domain.
- GSM8K gains are small overall and absent with engineered prompts; the gain concentrates in problems with five or more steps. The authors say hand-written correct decompositions let nearly all GSM8K problems be solved, so decomposition is the bottleneck (no number given).
- Strong last-letter and SCAN results are attributed by the authors to decomposition being easy there.
- Performance depends on the model: code-davinci-001 was far weaker (19.6 against 96 on four-word last-letter, 4-shot). No open models, decoding settings, seeds or intervals; GPT-3 variant sizes and the DROP test size for code-davinci-002 are not stated.
- Per-split SCAN numbers other than the length split are not printed.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Decomposed Prompting (DecomP)]] — alternative-to (modular handlers per sub-task)
- [[Self-Ask Prompting]] — alternative-to (question decomposition inside one pass)
- [[Hypotheses-to-Theories (HtT)]] — extends (uses it as a base prompt)
- [[Compositionality Gap]] — related
