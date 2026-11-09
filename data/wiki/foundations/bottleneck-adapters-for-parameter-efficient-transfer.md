---
title: Bottleneck Adapters for Parameter-Efficient Transfer
tags: [foundations, concept]
summary: "Adapters are small trainable modules inserted into a frozen pretrained network: Rebuffi et al. (2017) added residual 1x1-convolution adapters to a ResNet for ten image domains, and Houlsby et al. (2019) added serial bottleneck adapters to BERT, both nearly matching full fine-tuning (all numbers self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-houlsby-2019-parameter-efficient-transfer-learning-nlp.md
  - data/raw/papers/2026-11-07-rebuffi-2017-learning-multiple-visual-domains-residual.md
---

# Bottleneck Adapters for Parameter-Efficient Transfer

An **adapter module** is a small set of new weights added between the layers of a pretrained network. The pretrained weights stay frozen, and only the adapters (plus, in some designs, layer norms and the task head) train per task. Two papers set the pattern, one for vision and one for text.

## Residual adapters for vision (Rebuffi et al., NIPS 2017)

Rebuffi et al. pose the problem of covering ten visually distinct domains with one ResNet, sharing most weights and not forgetting earlier domains. Their hypothesis: small residual 1x1-convolution adapters per domain, plus batch norm, added to a frozen shared ResNet, can equal or exceed per-domain full fine-tuning.

- The residual adapter is g(x; alpha) = x + alpha * x, where alpha is a bank of 1x1 filters, so it reduces to identity at zero coefficients. They are inserted into a ResNet28 pretrained on ImageNet and evaluated on the ten domains of the Visual Decathlon benchmark.
- With per-dataset weight decay, adapters get a higher mean accuracy than full fine-tuning while costing 2x the parameters rather than 10x, about 11% extra per domain (self-reported). One decay value shared across datasets still gives good mean accuracy, but the Decathlon score is low since DTD and Flowers do poorly.
- Tuning just the final two conv layers, at an equal parameter count, is much worse; adapters without the residual connection are worse and converge slower (self-reported).
- In a pairwise setup, with each target task taken in turn, adapters keep ImageNet accuracy exactly while fine-tuning forgets it, with the fine-tuned ImageNet score falling to 0.2 at worst, on Omniglot-like targets (self-reported). Tuning only batch-norm scale and bias, under 0.1% domain-specific parameters, already lifts a frozen extractor on Aircraft (self-reported).

## Bottleneck adapters for text (Houlsby et al., ICML 2019)

Houlsby et al. ask whether a pretrained text Transformer can serve many tasks by training a small number of added parameters for each. They put two serial bottleneck adapters in every layer of a frozen BERT and train them with the layer norms and the classifier. The parameter cost per module is 2md + d + m for width d and bottleneck m.

- With BERT-large, adapters average 80.0 on the GLUE test set against 80.4 for full fine-tuning, training 3.6% of parameters per task. Solving nine GLUE tasks needs 1.3x BERT in total parameters against 9x (self-reported). Fixing size 64 gives 79.6 with 2.1% (self-reported).
- Across 17 additional classification tasks with BERT-base, the adapter average is 73.3 versus 73.7, with 1.14% new parameters per task. Fine-tuning only the top n layers averages 74.0 but trains 52.9% of parameters (self-reported).
- For SQuAD v1.1, adapters of size 64 (2% of parameters) get F1 90.4 against 90.7; size 2 (0.1%) reaches 89.9 (self-reported).
- Removing all adapters drops MNLI to 37%, while removing those in layers 0 to 4 barely changes it. Adapters are robust to initialisation scale below 1e-2 (self-reported).

## Why it matters here

Later vision-language work reuses the idea of training few parameters on a frozen backbone; the LLaMA-Adapter page covers one such use.

## Limits

- Rebuffi (per its extraction): 64 px resolution lowers ImageNet and Flowers accuracy against the state of the art; the test-time domain label is assumed (the domain-prediction variant excepted); no seeds, error bars or significance tests; weight decay was tuned for each dataset against validation data; the Decathlon score is relative to the fine-tuned baseline; CNNs only.
- Houlsby (per its extraction): BERT, classification and SQuAD only, with no generative models; latency and memory at inference were not measured; the GLUE headline chooses the adapter size per task and the best of 5 seeds on validation, and a fixed size of 64 loses 0.4 GLUE points; additional-task epochs were picked by hand from validation curves.
- Neither extraction records an internal inconsistency.

## See Also
- [[LLaMA-Adapter V2 and MultiModal-GPT Parameter-Efficient Visual Tuning]] — extends
- [[Vision-Language Model Architectures]] — related
- [[Vision-Language Model Training Families]] — related
- [[Compacter Adapters]] — extends
