---
title: Lipton's Notions of Interpretability
tags: [data-science, concept]
summary: "Lipton argues interpretability has no single meaning and splits it into transparency (simulatability, decomposability, algorithmic transparency) and post-hoc explanation (text, visualisation, local explanation, example); on his conceptual argument linear models are not automatically more interpretable than deep nets."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-misfiled-lipton-2016-mythos-of-model-interpretability.md
---

# Lipton's Notions of Interpretability

Lipton (WHI 2016) holds that interpretability is several ideas under one word. The term has no agreed definition but is used as if it were mathematical, which leaves any statement that linear models are readable and deep nets are opaque undefined until one notion is chosen. The paper is a conceptual argument about supervised learning, with no experiments. In his account the call for interpretability appears when predictive accuracy on a test set, the formal objective, fails to match what errors cost in deployment.

## Taxonomy

**Desiderata:** trust, causality, transferability, informativeness, and fair and ethical decision-making.

**Transparency**
- *Simulatability*: one person can hold the whole model in mind and work through its computation for a prediction in reasonable time.
- *Decomposability*: every input, parameter and calculation has an intuitive account.
- *Algorithmic transparency*: the learning algorithm itself is understood, for example the shape of its error surface and whether it converges to a unique solution.

**Post-hoc interpretability** draws information out of a trained model without necessarily revealing how it works. The forms are text explanations, visualisations, local explanations and explanation by example.

## Claims

- Linear models, rule systems and decision trees are not interpretable by nature: with many dimensions, long rule lists or deep trees they can be harder to follow than a small neural network.
- Linear models do best on algorithmic transparency, but many features cost them simulatability and heavy feature engineering costs them decomposability. Their weights can also shift with feature selection: whether age and immunodeficiency indicators are included changes the sign of a flu-vaccination association (an illustration without data).
- Post-hoc explanations can mislead when tuned to satisfy human expectations, which he compares to people justifying hiring or admissions decisions.
- Saliency maps explain one input locally; shifting a single pixel can produce a very different map.
- A pneumonia-risk model gave asthma patients lower risk because they were treated more aggressively, so using it for triage would undermine its own predictions (an example reported from Caruana et al. 2015).
- FICO credit models are logistic regressions chosen for interpretability, yet applicants can game features such as debt ratio and number of accounts, which may destroy their predictive value.

## Guidance (Lipton)

Lipton advises settling on one definition before calling a model interpretable. A post-hoc claim should name its objective and offer evidence that the explanation meets it. He cautions against trading away predictive power for transparency without a reason, and against explanations tuned to sound plausible. Explanations given to people affected by a decision should offer falsifiable reasoning that can be contested.

## Limits

- There is no experiment or dataset; the case rests on examples from the literature.
- Supervised learning only; reinforcement learning is left for later.
- Lipton concedes the line between transparency and post-hoc methods is not sharp, and that what a right to explanation should look like, and how to show an explanation is correct, are still open.
- The paper predates most later post-hoc methods, such as SHAP, and the work on explanation faithfulness.

## See Also
- [[SHAP Attributions and the Limits of Explanations]] — extends
- [[LIME Local Surrogate Explanations and Submodular Pick]] — related
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — related
