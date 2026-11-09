---
title: Adversarial Examples (Intriguing Properties of Neural Networks)
tags: [foundations, concept]
summary: Szegedy et al. (2013) found that small, minimum-norm input perturbations found with L-BFGS flip a trained network's prediction, that the perturbed inputs transfer across models and training sets, and that training on them lowered test error in a preliminary run.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-szegedy-2013-intriguing-properties-neural-networks.md
---

# Adversarial Examples (Intriguing Properties of Neural Networks)

The paper's best-known finding is that a perturbation chosen to minimise its L2 norm while changing the predicted class can be very small. The perturbations were found with L-BFGS on MNIST, AlexNet and QuocNet.

## Reported results

All figures are (self-reported), from the paper's own models.

- **Transfer between models.** An error rate of 87.1% was reported when adversarial examples built for one fully connected network were fed to another. Across different training sets, transfer was 5.9% without amplification and 43% when the perturbation was amplified.
- **Adversarial training.** Mixing adversarial examples into training gave test error below 1.2% on MNIST, against 1.6% when only weight decay was used and roughly 1.3% for dropout. The authors call this preliminary.
- **Stability bounds.** Spectral-norm bounds on layer Lipschitz constants were 10 for the second convolutional layer and 11 for the fifth.

## Limits

- Small 2013-era networks and image tasks; the adversarial-training result is a single preliminary comparison.
- The perturbations require access to the model being attacked, and the transfer rates depend on amplification.
- Nothing here concerns language models; the link to text attacks is by analogy.

## See Also
- [[GCG Adversarial Suffix Attack]] — extends (a gradient-based attack on language models)
- [[Prompt Injection]] — related
