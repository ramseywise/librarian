---
title: Reflection in Pre-Training
tags: [foundations, concept]
summary: "A study of OLMo-2 checkpoints reports that self-correction behaviour already appears during plain pre-training and grows with pre-training compute, measured by injecting errors into chains of thought and appending 'Wait,'; it argues against reflection being a product of RL alone."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ai-2025-rethinking-reflection-pre-training.md
---

# Reflection in Pre-Training

Essential AI (arXiv 2504.04022, preprint) tests whether models reflect on mistakes before any RL or post-training. The measurement has two settings. **Situational reflection** gives the model a chain of thought that a frontier model has corrupted with a small error, ends it with "Wait,", and checks whether the model catches the error. **Self-reflection** takes the checkpoint's own wrong chains and appends "Wait,". A classifier (DeepSeek-V3 with a few exemplars) labels whether a response contains explicit reflection tokens; an answer that is right without them counts as implicit reflection. Six tasks were used (BBH, two CruxEval variants, GSM8K, GSM8K-Platinum, TriviaQA). The trigger comes from budget-forcing work on sequential test-time scaling, and the paper contests the R1 claim that reflection emerges from RL interaction.

## Results (self-reported; OLMo-2 stage-1 checkpoints unless noted)

- OLMo-2-7B at 198B tokens already shows reflection across maths, code, verbal and logical tasks; the abstract claims that at 4T tokens the 7B model self-corrects across all six self-reflection tasks.
- Across 40 checkpoints and 6 datasets, 231 of 240 pairs showed at least one situational reflection and 154 of 240 at least one self-reflection; the mean Pearson correlation of accuracy with log pre-training compute was 0.76.
- In the situational setting, accuracy correlated with log compute at 0.84 on GSM8K and GSM8K-Platinum (mean of three runs); implicit accuracy was flat except on TriviaQA.
- Self-reflection accuracy correlated weakly with compute (0.09 to 0.69) while the explicit-reflection rate correlated at 0.49 to 0.88. About 64.2% of attempts showed some self-correction.
- On OLMo-2-32B checkpoints (GSM8K-Platinum, adversarial), more training compute meant fewer test-time tokens needed for the same accuracy; Qwen2.5 from 0.5B to 72B showed the same direction with parameter count only.
- The classifier had precision 0.95 to 1.00 and recall 0.61 to 0.76 on the three datasets checked, so reflection is likely under-reported.

## Limits

- Self-reflection sets keep only questions every checkpoint of that size failed, which the authors say makes them hard by design.
- How pre-trained reflection becomes post-training reasoning is left open, and the data that produces it was not identified. No RL or post-trained model was run, so it does not show that RL adds nothing.
- Pearson r mixes model size and token count; OLMo-2 checkpoints are pre-anneal; the classifier was checked against labels on just three of the six datasets; adversarial chains are synthetic.
- Compute is the 6nt estimate only; each result averages three runs, and the text gives no spread; one checkpoint was excluded as an outlier.
- Internal inconsistency noted by the extraction: the abstract speaks of six self-reflection tasks, while the body reports self-reflection in only 154 of 240 pairs.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Prompting Reasoning Models]] — related
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Reflexion]] — related (prompted reflection after feedback)
