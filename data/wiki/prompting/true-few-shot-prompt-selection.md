---
title: True Few-Shot Prompt Selection
tags: [prompting, concept]
summary: "Perez et al. separate true few-shot learning (no validation set) from tuned few-shot and show that cross-validation and MDL pick prompts and hyperparameters no better than near-random, so published few-shot results are overestimated (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-perez-2021-true-few-shot-learning-language.md
---

# True Few-Shot Prompt Selection

Perez, Kiela and Cho ask how well few-shot LMs do when prompts and hyperparameters must be chosen from the few training examples alone. Three settings are defined: **true few-shot learning** chooses the learning algorithm with nothing but a small training set drawn from one distribution; **tuned few-shot learning** instead tunes on a large validation set; **multi-distribution few-shot learning** averages the expected loss over many small train and validation splits from many distributions.

## Method

The candidates are prompts (for LAMA, RTE, CB and WiC) or ADAPET hyperparameters (for SuperGLUE), each scored with leave-one-out cross-validation (CV) or minimum description length (MDL, via online coding), each given just N training examples. Test accuracy of the chosen option is set against the worst option, the mean (a random pick) and the best (chosen on held-out data).

## Results (self-reported)

- Prompt selection on LAMA-UHN, using 9 LMs between 82M and 175B parameters, 5-shot, over 5 runs: on average CV and MDL land 5-7% absolute below the prompt picked using held-out data, closing only 20-40% of the distance from the average prompt to the best one.
- With GPT-3 175B, CV finds the best prompt 21% of the time against 9% by chance. For models from 0.1B to 6.7B, the prompt CV picks beats the average prompt about 56% of the time (MDL about 55%).
- Selection has roughly a 27% chance of costing about 13% accuracy. A more conservative variant does not help: plain CV beats the average prompt 50% of the time, against 51% for alpha=2 (GPT-3 175B).
- Raising N from 5 to 40 gives no consistent improvement (models up to 6.7B), and more compute does not help. Bayesian CV, MDL variants and joint log-probability also land near the random average.
- Hyperparameter selection for ADAPET (32-shot, four training sets, 16 combinations): SuperGLUE average 73.0 with CV and 73.4 with MDL, against a mean of 73.9, a best of 77.2 and iPET at 76.8, so the average falls below PET/iPET. On WiC and MultiRC, CV needs over 2-3k examples before it chooses ADAPET hyperparameters that beat the average.
- The GPT-3 experiments cost $2826.73 through the API.

The authors recommend reporting true few-shot results and say prior few-shot numbers overestimate ability.

## Limits

- The selection criteria tested are not exhaustive; other criteria or heuristics might do better.
- The prompt experiments span LAMA and three classification tasks on GPT-family models up to 175B; N is capped at 40 by the 2048-token context. GPT-3 sizes are assumed, not disclosed.
- Selection with thousands of examples is only preliminary (Appendix C); some Fig 6 task numbers were read from plots.
- 2021-era models; instruction-tuned models were not tested.

## See Also

- [[Few-Shot Prompting]] — prerequisite-for
- [[Prompt Order Sensitivity and Entropy Probing]] — related (order-selection without labels, a different selection route)
- [[LM-BFF and PET Prompt-Based Fine-Tuning]] — related (the extraction lists Gao et al. LM-BFF as comparing with multi-distribution-style hyperparameter choice)
- [[Contextual Calibration]] — related (prompt sensitivity)
- [[LPAQA Prompt Mining and Ensembling]] — related (source of the candidate prompts)
