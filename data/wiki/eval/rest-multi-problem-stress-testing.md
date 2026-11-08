---
title: REST Multi-Problem Stress Testing
tags: [eval, pattern]
summary: "Concatenate s consecutive benchmark questions into one prompt and score each; on MATH500 a 1.6-point gap between two distilled 7B and 32B reasoning models became 22.22 points under stress, and DeepSeek-R1's AIME24 accuracy fell from 81.66 to 52.49 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-pan-2025-rest.md
---

# REST Multi-Problem Stress Testing

REST (Pan et al., Tsinghua and Shanghai AI Laboratory, arXiv 2507.10541, 2025 preprint) makes a
benchmark that is close to saturated harder without any new questions being written. A prompt joins s
successive questions together (indexing wraps around, so the number of prompts stays N); s is called the
**stress level**. The authors report sharp accuracy losses for many reasoning models, and say that models
with equal single-question scores come apart under stress. The abstract questions the idea that LLMs
are able to solve several problems at once.

## Setup

The headline figures come from Tab. 1, covering 34 reasoning models (1.5B to 671B parameters),
with a 32K output-token cap, OpenCompass, and rule-based `\boxed{}` answer extraction. The "stress" score is
the mean accuracy across stress levels greater than 1; for AIME24, AIME25 and AMC23 each score averages 8 sampling runs.

## Results (self-reported)

- **Drops.** DeepSeek-R1 on AIME24 falls from 81.66 (single question) to 52.49 (stress, levels 2 to 5),
  which the text reports as a 29.17% drop; that figure equals the fall in accuracy points, not a relative
  drop. For AIME25 the fall is 68.75 to 37.17, reported as 31.58% and again equal to the point difference.
- **Discrimination.** MATH500 at levels 3, 5, 7 and 9: R1-Distill-Qwen-7B moves from 93.0 to 66.75,
  while R1-Distill-Qwen-32B moves from 94.6 to 88.97. The single-question gap of 1.6 points widens to 22.22.
- **Post-training does not carry over.** The R1-7B base scores 93.0 single and 66.75 stress on MATH500.
  AReaL-boba-RL-7B starts higher (95.0) but lands at 60.77 under stress; OpenThinker2-7B goes 93.8 to 83.30.
  Both AReaL and Light-R1-7B-DS (stress 61.73) finish below that base. Looking at s=9 alone,
  those two get 38.07 and 39.11 while R1-7B gets 49.42.
- **Ranking flip.** On MATH500 with a single question, R1-Distill-Qwen-1.5B (83.40) is ahead of
  Qwen2.5-Math-1.5B-Instruct (73.00); under stress the order reverses (42.47 against 53.94).
- **Shorter reasoning helps.** At s=9 on MATH500, Efficient-R1-7B (alpha 0.2) reaches 66.02 where R1-7B
  reaches 49.42, despite lower single-question accuracy (88.20 against 93.00), a margin of 16.60.
  L1-Qwen-1.5B-Max is 44.71 points ahead of R1-1.5B at s=9.
- **Easy tasks barely move.** On GSM8K the losses are 0.43% (R1-7B) and 0.04% (R1-32B), stated in the
  text. In a separate run (Tab. 5), lifting the output cap from 32K to 128K makes almost no difference
  (R1-7B on AIME24: 16.53 then 16.17).
- **Error analysis (AIME24, Fig. 5; ordering and token results from Figs. 6 to 8).** For DeepSeek-R1, omitted questions and reasoning errors together explain
  42.00% of the degradation; for Light-R1-7B, endless repetition and truncated output together explain
  48.90%. The four models analysed had no format violations. Accuracy declines the later a question
  sits in the prompt, putting easy questions first beats hard first, and the strong models spend fewer
  reasoning tokens on the opening question.

## Limits

- The paper's dates disagree: the arXiv v2 listing says 16 July 2025 and its footer 15 July 2025.
- The authors acknowledge the extra evaluation cost from longer reasoning, and that recent models may be absent.
- Math, GPQA and LiveCodeBench runs used reasoning models only; models without reasoning appear just as
  reference points.
- Nothing here shows that a stress score tracks quality in real deployments with several issues at
  once; the tutoring and support scenarios serve only as motivation. The abstract mentions contamination,
  yet no experiment on it is run.
- Question position and difficulty are entangled, since the difficulty ordering takes R1-7B's failure rate as its proxy.
- Rule-based answer extraction undercounts: for R1-7B on MATH500 it gives 66.75, whereas an extractor
  built on gemma-3-27b-it gives 70.59.
- Each benchmark got its own stress levels, so scores cannot be compared across benchmarks. The models are
  from early to mid 2025.

## See Also
- [[Functional Benchmarks and the Reasoning Gap]] — alternative-to (a regenerated-instances route to a harder, fresher benchmark)
- [[GSM-Symbolic]] — alternative-to (perturbs one question; REST stacks several)
- [[Eval Suite Maintenance]] — related (a saturated suite)
- [[Prompting Reasoning Models]] — related (the failure modes of reasoning models)
