---
title: Emergent Analogical Reasoning in GPT-3
tags: [llm, reasoning-and-planning, concept]
summary: "Webb, Holyoak and Lu test text-davinci-003 zero-shot on four analogy families against human data; it beat UCLA undergraduates on Digit Matrices and letter strings but trailed on story analogies, with the mechanism unidentified (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-webb-2023-emergent-analogical-reasoning-large-language.md
---

# Emergent Analogical Reasoning in GPT-3

Webb, Holyoak and Lu (Nature Human Behaviour 2023) ask whether an LLM trained only to predict the next token can handle analogy problems with no examples at a human level. The main model is text-davinci-003 (the supplement adds davinci, code-davinci-002 and text-davinci-002); human baselines are new data from UCLA undergraduates on four task families.

## Tasks and results (self-reported)

- **Digit Matrices**: a new text version of Raven-style problems, designed to be novel to both people and models (40 instances of each of 32 subtypes; 40 human participants). GPT-3 outscored people in the generative and 8-choice versions (mean log-probability scoring); its subtype accuracy tracks human accuracy only moderately.
- **Letter-string analogies** (sampled at temperature 0 after a short instruction to complete the pattern; 57 human participants): GPT-3 outscored people overall with a similar pattern of errors across 41 subtypes. Its accuracy drops faster than humans' as the number of required generalisations grows. Without the prompt the correlation with human performance falls but persists.
- **Four-term verbal analogies** (Jones et al., 120 problems, 241 human participants, choice by log-probability): greater semantic distance hurts GPT-3 as it hurts people.
- **Story analogies** (72 comparisons, forced choice, 54 human participants): GPT-3 does worse than people overall; it beats chance on near analogies but not far ones. Fifteen of the 54 students picked the analogous story every time.
- **Qualitative probes**: on the radiation problem GPT-3 produced the convergence solution only once it had seen the analogous story, and it lost the solution when distractor stories intervened unless it was told to think back to earlier ones. In the gumball physical task it could map the analogy but did not exploit it, which the authors put down to weak physical reasoning (single uncurated playground sessions).
- **Preliminary GPT-4** on the same 72 story problems through the ChatGPT web interface: close to perfect on near analogies and more robust on far ones.

## Limits

- The main text uses text-davinci-003 only; GPT-4 was tried just on story analogies because API access was missing.
- Digit Matrices are pseudo-symbolic, not visual. Each test is self-contained, so long-term retrieval of analogs is not examined.
- Letter-string accuracy dropped when the prompt or sentence format was removed, so results are format-sensitive.
- Contamination was assessed only by asking the model to reproduce memorised items (Supp S3); it is not excluded for letter strings, verbal and SAT analogies or the radiation problem.
- Per-condition accuracies appear only in figures, the human sample is college students doing online tasks, and the mechanism behind GPT-3's success is not identified. The paper does not itself take up later challenges to the emergent-reasoning reading.

## See Also

- [[LLM Reasoning Surveys and the Can-LLMs-Reason Debate]] — related
- [[Analogical Prompting]] — related
- [[Early GPT-4 Probing and Planning Limits (Sparks of AGI)]] — related
- [[Foundation Models: Homogenization and Emergence]] — related (the emergence framing)
