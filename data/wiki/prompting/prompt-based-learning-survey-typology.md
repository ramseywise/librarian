---
title: Prompt-Based Learning Survey Typology
tags: [prompting, reference]
summary: "Liu et al.'s 2021 survey gives prompting a common notation (template, input and answer slots, answer mapping) and sorts the field into five tuning strategies and the axes of prompt engineering, answer engineering and multi-prompt learning; findings are as of mid-2021 and quoted from cited work."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-liu-2022-pre-train-prompt-predict.md
---

# Prompt-Based Learning Survey Typology

Liu et al. (arXiv July 2021; ACM Computing Surveys 2023) describe prompt-based learning formally and organise it along its design dimensions. The survey runs no experiments of its own; everything below is reported from cited work.

## Notation

In **prompt-based learning** the LM models text probability directly. A **template** is a string with an input slot [X] and an answer slot [Z]; the input x becomes a prompt x' whose slots are empty, and the LM supplies [Z] by searching the answer space Z, z_hat = search over z in Z of P(f_fill(x', z); theta). An answer mapping turns the searched answer into the output y, and several answers may map to one class. A **verbalizer** maps a label to a single answer token. A **cloze prompt** leaves a slot inside the text to be filled; a **prefix prompt** has the input entirely before z. **Prompt engineering** is building the prompting function f_prompt(x) that works best downstream.

## Dimensions of the typology

- The prompt shape follows the model: prefix prompts suit generation and left-to-right LMs, while cloze prompts suit masked LMs, and models that reconstruct the full text can take either.
- **Discrete (hard)** prompts are text strings; **continuous (soft)** prompts live in the embedding space with their own tunable parameters.
- **Prompt augmentation** (demonstration learning) adds a few answered prompts; **in-context learning** is tuning-free prompting combined with prompt augmentation. **Prompt ensembling** uses several unanswered prompts at inference.
- **Five tuning strategies**, in order: promptless fine-tuning; tuning-free prompting, where the LM is frozen and nothing in the prompt is trained; fixed-LM prompt tuning, where only prompt parameters are trained; fixed-prompt LM tuning, where the LM is trained under a fixed prompt; and prompt plus LM fine-tuning, which trains both.
- Zero-shot, few-shot and full-data mean zero, very few and reasonably many training examples.

## Practices the survey lists

- Pick few-shot examples that lie close to the input in embedding space instead of at random; the order of demonstrations matters, and permutations can be scored, for instance by entropy.
- Combine prompts by voting, by averaging their probabilities, or by weighting them by accuracy, which steadies results and lowers the cost of prompt engineering.
- Correct few-shot output using an input with no content (for example the string N/A), which strips out label, recency and token bias.
- Allow several surface forms per label, since surface forms compete for probability mass.
- Split a prompt into parts for token or span prediction such as NER, and compose prompts for tasks that relate spans.

## Reported findings

- Across classification tasks, a prompt is on average worth hundreds of labelled examples (Scao and Rush; not rerun).
- Which few-shot examples are chosen can move performance from close to state of the art down to close to a random guess (Lu et al.).
- Prompts selected on a larger validation set carry over between models of similar size, but prompts selected true-few-shot do not, and carry-over across very different sizes is poor (Perez et al.).
- Relation extraction has far more labels than binary sentiment, so engineering its answers is harder.
- In the survey's own meta-analysis of the works in its tables (a hand-collected sample), papers on prompting surged in 2021, and attention moved away from discrete prompt search toward continuous; template search is far more studied than answer search.

## Limits

- No experiments of its own, and findings are as of mid-2021: before ChatGPT, instruction tuning, RLHF, chain-of-thought and tool use; GPT-3 at 175B is the largest model discussed.
- Heavy focus on cloze prompts, masked LMs and classification and probing tasks.
- The authors concede few or no systematic comparisons across pre-trained LMs and tuning strategies, and little theory.
- Internal inconsistency: Sec 8.5 reports that Jiang et al. found QA probabilities weak predictors of correctness, yet Sec 10.9 says the same work saw them well calibrated.
- The meta-analysis counts only papers in its own tables. Prompts built using annotated data can be argued not to be truly zero-shot (Perez et al.).

## See Also

- [[Prompt Engineering]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
- [[Contextual Calibration]] — instance-of (the calibration recipe the survey recommends)
- [[LPAQA Prompt Mining and Ensembling]] — instance-of
- [[True Few-Shot Prompt Selection]] — instance-of
- [[LM-BFF and PET Prompt-Based Fine-Tuning]] — instance-of (the survey lists PET as a fixed-prompt LM tuning example)
- [[Prefix-Tuning and Prompt Tuning]] — related (soft prompts, fixed-LM prompt tuning)
