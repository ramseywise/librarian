---
title: ToxiGen
tags: [eval, safety-and-bias, reference]
summary: "ToxiGen is 274,186 GPT-3-generated toxic and benign statements about 13 minority groups, built with demonstration prompts and an adversarial classifier-in-the-loop decoder called ALICE, to train better implicit-hate detectors (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-hartvigsen-2022-toxigen.md
---

# ToxiGen

Hartvigsen, Gabriel, Palangi et al. (ACL 2022) ask whether a large LM, given demonstrations in its prompt and guided by a classifier at decode time, can produce a large and balanced set of implicit toxic and benign statements about minority groups that improves toxicity detectors. They hypothesise that balanced machine-generated text reduces spurious identity-toxicity correlations and helps on human-written implicit hate data.

## Construction

GPT-3 receives a prompt of 5 demonstrations sampled at random from 20 to 50 curated statements per group (26 prompt sets), with the group-specific prompt label serving as a proxy label. Two decoders are used.

1. **Top-k decoding** from GPT-3 as usual.
2. **ALICE** (Adversarial Language Imitation with Constrained Exemplars): a constrained beam search where each step mixes the LM log-probability and the log-probability that a classifier (HateBERT) assigns, the score for the next word w is lambda_L times the LM's log-probability of w given the prefix, plus lambda_C times the classifier's log-probability for the text extended with w. The classifier acts as an adversary, so the generator is pushed towards statements the detector gets wrong.

The result is 274,186 statements about 13 groups, of which only 14,174 come from ALICE. A subset of 792 statements (TOXIGEN-HUMANVAL) was labelled by three MTurk annotators each.

## Results (self-reported)

- On average 90.5% of the machine-generated examples were judged human-written by a majority of annotators (TOXIGEN-HUMANVAL).
- 98.2% of statements are implicit by a profanity-word-list match; 94.56% of the toxic examples are hate speech per annotators (the abstract says 94.5%).
- Statements from ALICE get past HateBERT more often than top-k ones do (125 prompts, 62 toxic and 63 non-toxic, one generated statement per prompt). For toxic prompts it lowers the human-rated toxicity of the output (p<0.001). The extraction gives no rates.
- Fine-tuning HateBERT on ALICE plus top-k data raises AUC on DynaHate from 0.47 (zero-shot) to 0.66, and on the TOXIGEN validation split from 0.57 to 0.96.
- Inter-annotator agreement on toxicity ratings is moderate.

## Limits

- Fine-tuning hyperparameters (learning rate, epochs, batch size, seeds) are not stated.
- Prompt labels stand in for ground truth and are noisy; annotator subjectivity and demographics skew, and only 51 of 156 workers annotated.
- Only minority groups from a US perspective, and GPT-3 sometimes conflates groups.
- The authors flag misuse: the methods can make an LLM produce more toxic text.

## See Also
- [[RealToxicityPrompts]] — related (a prompt benchmark for toxic continuation, in contrast to a detector-training dataset)
- [[Detoxification Trade-offs]] — related (classifier bias against identity terms is the failure ToxiGen's balanced data targets)
- [[LM Red Teaming]] — related (another LM-generated adversarial test set)
