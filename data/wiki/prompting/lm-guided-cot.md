---
title: LM-Guided Chain-of-Thought
tags: [prompting, pattern]
summary: "A small fine-tuned LM (FLAN-T5 80M) writes the rationale and a frozen larger LM (FLAN-T5 XXL 11B) answers; distilled rationales beat plain CoT on 2WikiMultiHopQA by about 10% EM/F1, while the RL stage adds only tenths of a point (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-lee-2024-can-small-language-models-help.md
---

# LM-Guided Chain-of-Thought

Lee, Yang, Tran et al. (preprint, 2024) test whether splitting chain-of-thought across two models helps a frozen black-box model on multi-hop question answering. The small model produces the rationale; the large model sees the question plus that rationale and predicts the answer.

## Method

A FLAN-T5 small model (80M) is first instruction-tuned on rationales from a large LM that were filtered (rationale distillation, KD). It is then refined with PPO using two rewards: rationale-quality aspects scored by classifiers (eight aspects) and a task reward taken from the answers of a frozen FLAN-T5 XXL (11B). At test time the small model's rationale is inserted into the large model's prompt. Evaluation is on HotpotQA and 2WikiMultiHopQA with hand-filtered hard eval sets of 1000 correct plus 1000 incorrect examples.

## Results

All numbers are the paper's own (self-reported).

- On the hard 2WikiMultiHopQA eval set, with a small FLAN-T5 writing the rationale and the XXL model answering, against CoT prompting with XXL: KD improves EM and F1 by roughly 10%.
- Original CoT with FLAN-T5 XXL scores below standard prompting on 2Wiki EM.
- HotpotQA hard set: KD with self-consistency is the best setting on F1 but ties standard prompting at 0.714.
- RL adds little: on 2Wiki the aspect-reward variant gets EM 0.507 against 0.506 for KD, and some RL variants fall below KD. Picking the top-ranked rationale by quality lowers task performance a little.
- A logistic-regression reward classifier matches humans better than FLAN-T5 XXL self-evaluation on coherence, consistency and logicality (10 held-out of 100 annotated examples). Agreement between the three annotators was moderate.

## Limits

- One model family (FLAN-T5) and one task type (multi-hop QA); wider use is untested.
- Reward classifiers were trained on 100 labels and tested on 10.
- The hard eval sets are hand-filtered, so the absolute numbers do not reflect accuracy on the natural data mix.
- No seeds, variance or significance tests; RL gains are tenths of a point, and the authors do not explain why ranking lowers performance.
- The 11B model is not a model above 100B parameters, and CoT hurting at that size matches reports of weak reasoning under 50B.

## See Also
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Multimodal Chain-of-Thought]] — related (two-stage rationale then answer)
- [[Self-Consistency]] — prerequisite-for
- [[Compositionality Gap]] — related
