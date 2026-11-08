---
title: Output Length Confounds Reference Metrics
tags: [eval, concept]
summary: "On open-ended long-context tasks, L-Eval found n-gram scores track answer length rather than human judgement: Claude-100k's NQ F1 rose from 9.84 to 57.76 once the prompt stated the expected length, and the length instruction lifted ROUGE-L's Kendall tau with human rankings from 0.5 to 0.8 (self-reported), so check answer lengths before comparing systems."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-an-2023-l-eval.md
---

# Output Length Confounds Reference Metrics

A reference-based metric compares a model's answer with a gold answer. L-Eval (An et al., arXiv
2307.11088, 2023), a long-context benchmark of 20 sub-tasks over 508 documents of 3k–200k
tokens, found that on its open-ended tasks these scores follow the length of the answer, and
built its evaluation design around that.

## The evidence

- **One model, two prompts.** On the NQ subset (Table 2), Claude-100k scored F1 9.84 with its
  answers on average 135 words longer than the reference. With a length instruction added to
  the prompt the excess fell to about 1 word and F1 rose to 57.76 (self-reported).
- **Agreement with humans.** Without the length instruction, the paper reports that the
  automatic metrics other than the GPT-4 judge do not track human scores.

## The fix: a length instruction

L-Eval adds the expected length to the prompt ("answer in about N words"). Against human
rankings of 7 systems on 85 questions, the authors report that ROUGE-L's Kendall tau rose from
0.5 to 0.8 with the instruction, and that the GPT-4 judge's reached 1 (self-reported). Two
cautions apply:

- Stating the reference's word count tells the model how detailed an answer is wanted, which
  is part of the answer's shape. Report scores with and without it.
- Seven systems is a small sample for a rank correlation.

## Other findings worth keeping

- **Closed-ended tasks** (multiple choice, exact answers) avoid the problem; L-Eval keeps 7 of
  them beside 13 open-ended ones and scores them by exact-match accuracy.
- **Retrieval vs full context:** a 4k-window model with retrieval scored about 49.7 against
  60.7 for full context on the closed tasks, so retrieval is not a free substitute for a long
  window ([[Long-Context Prompting]]).
- The same commercial model was used to filter the data and was then evaluated, a
  self-selection risk to note when reading its scores.

## Practical rule

Before comparing two systems on a free-text metric, check their mean answer lengths. If they
differ a lot, either constrain the length in the prompt or normalise, and say which you did
([[Eval Metric Interpretation Pitfalls]]).

## Limits

The agreement figures are a rank correlation over 7 systems, not over individual answers, with
small question sets (85 and 96) and no inter-annotator agreement reported; the paper states
only two tau values in its text. The length instruction changes the answers as well as their
scores: Claude's average human rating rose from 3.08 to 4.04 with it. The judge sees only the
reference answer, never the document, and one of the evaluated models also filtered the data.
The authors themselves say almost every metric they tried, the GPT-4 judge included, shows bias.

## See Also
- [[Eval Metric Interpretation Pitfalls]] — prerequisite-for
- [[LLM Judge Biases]] — related
- [[Long-Context Prompting]] — related
- [[Benchmark Prompt Format Sensitivity]] — related (another prompt detail that moves scores)
