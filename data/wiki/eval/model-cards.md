---
title: Model Cards
tags: [eval, safety-and-bias, concept]
summary: "Mitchell et al. (FAT* 2019) propose model cards, short documents released with a model that give intended uses and quantitative results disaggregated by group and condition; Bommasani et al. later recommend labelling adapted derivatives the same way, and the Mitchell paper does not test whether cards change stakeholder behaviour."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-mitchell-2019-model-cards-model-reporting.md
  - data/raw/papers/2026-11-07-bommasani-2021-opportunities-risks-foundation-models.md
---

# Model Cards

Mitchell, Wu, Zaldivar et al. (FAT* 2019) ask how a trained model ought to be documented, so that users can weigh its performance for different groups and conditions and steer clear of uses it does not suit. They propose that brief standard documents, with disaggregated and intersectional evaluation plus statements of intended use, will improve transparency and cut harmful deployment. A **model card** is a short document accompanying a trained model with benchmarked evaluation in a variety of conditions; the proposal covers any trained model, with a focus on human-centred vision and language models. It is presented as a complement to dataset documentation (Datasheets for Datasets).

## What a card holds (the paper's practices)

- A one-to-two-page document released with the model, updated with each new release (the TOXICITY v1 and v5 cards show this).
- What the model is meant for, who it is meant for, and which uses fall outside its scope.
- All confusion-matrix error rates, with a statement of which were prioritised and why. Decision thresholds are stated with the reason for choosing them; digital cards could offer a threshold slider.
- Quantitative results **disaggregated** by chosen factors, for single and **intersectional** groups (two or more characteristics at once, such as gender and age), with confidence intervals where possible and a description of how variability is computed (for example the average of 5 runs or 10-fold cross-validation).
- Public evaluation data spanning both typical and hard cases, with synthetic data considered for uncovered groups.
- Where training data cannot be shared, basic distributions over groups. Group attributes are self-identified or labelled as perceived.

## The two worked cards (self-reported)

- **Smiling classifier** on CelebA: with bootstrapped 95% intervals and a 0.5 threshold, all four error rates fall in the same range overall, but the false discovery rate is far higher for older men than for other groups, and men as a whole show a higher false negative rate.
- **Perspective API TOXICITY** v1 and v5, tested on synthetic Identity Phrase Templates with Pinned AUC (threshold-agnostic separability of toxic from non-toxic comments for each group within a background of other groups): v1 did badly on terms like lesbian, gay and homosexual, while v5 shows more equitable performance after bias mitigation.

## Foundation-model extension

Bommasani et al. (2021) recommend that an adapted derivative carry a label naming the foundation model and data behind it, in a model card or nutrition label, so a harm can be traced back. They add that traceability alone is unlikely to alter the model absent frameworks for assigning responsibility and recourse. See [[Foundation Models: Homogenization and Emergence]].

## Limits

- Whether cards change how stakeholders behave is not tested empirically; interpretation by stakeholders is left to future work.
- The authors call the section list neither complete nor exhaustive, and concede that cards are unlikely to be standardised enough to rule out misleading claims, so they rely on the integrity of whoever writes them.
- Datasets fit for disaggregated evaluation remain scarce. The smiling example has no race or skin-type breakdown and treats gender as binary; the toxicity test set is synthetic, small and not comprehensive.
- Proprietary data may make a training-data section impossible. A card is one transparency tool among several (audits, adversarial testing, user feedback).
- Bommasani et al. state their norms sections are normative and aim mainly to encourage dialogue.

## See Also
- [[BBQ Bias Benchmark]] — related
- [[LLM Bias and Fairness Survey]] — related
- [[LLM Trustworthiness Taxonomy]] — related
- [[HELM Holistic Evaluation]] — related
