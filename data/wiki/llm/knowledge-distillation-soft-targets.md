---
title: Knowledge Distillation with Soft Targets
tags: [llm, fine-tuning, concept]
summary: "Hinton et al. (2015) train a small model on a large model's temperature-softened class probabilities mixed with the hard labels, transferring most of an ensemble's gain; the soft targets also act as a regulariser."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-hinton-2015-distilling-knowledge-neural-network.md
  - data/raw/papers/2026-11-06-tie-2025-survey-post-training-large-language.md
---

# Knowledge Distillation with Soft Targets

Hinton, Vinyals and Dean (arXiv 1503.02531, preprint) ask whether the knowledge in a cumbersome model or ensemble can move into one small model that is cheap to deploy. Their hypothesis: a small network fitted to the teacher's softened class probabilities generalises far better than an identical network fitted to hard labels only.

## Mechanism

- The teacher's softmax is computed with a temperature T, giving q_i = exp(z_i/T) divided by the sum over j of exp(z_j/T). T is raised until the targets are suitably soft, and the student is trained at the same T.
- The loss combines two terms with weights: cross-entropy against the soft targets (multiplied by T^2) and cross-entropy against the hard labels. At test time the student uses T=1.
- The gradient with respect to a logit is (1/T)(q_i - p_i). For large T the paper approximates the gradient as proportional to z_i - v_i, the difference of teacher and student logits, which shows logit matching is a special case of distillation (matching logits is the earlier model-compression approach of Bucilua et al.).
- The transfer set can be unlabelled data or the original training set.

## Reported results (self-reported)

- Speech acoustic model (85M-parameter DNN, 8 layers of 2560 ReLU units, 14,000 HMM-state softmax, about 2000 hours of English speech, 700M frames; a 10-model ensemble distilled, T chosen from 1, 2, 5, 10, hard-label weight 0.5): frame accuracy 58.9% baseline, 61.1% ensemble, 60.8% distilled, so more than 80% of the ensemble's gain transfers. Word error rate was 10.9% baseline and 10.7% for both ensemble and distilled model; the authors attribute the small WER gain to objective mismatch.
- Regularisation: trained on 3% of the speech data, hard labels overfit to 44.5% test frame accuracy with early stopping, while soft targets from the full-data model gave 57.0% without early stopping; the full-data baseline is 63.4% on train.
- MNIST (60,000 training images; the teacher has two 1200-unit ReLU layers and uses dropout, the student two 800-unit ReLU layers with no other regularisation): 74 test errors at T=20 against 146 without soft targets and 67 for the teacher. With no 3s in the transfer set the student made 206 errors, 109 after raising the bias for class 3 by 3.5, and got 98.6% of test 3s right.
- Specialist ensemble on JFT (100M images, 15,000 classes, one generalist plus 61 specialists of 300 classes each, using a dustbin class for the rest): top-1 accuracy rose from 25.0% to 26.1%, a 4.4% relative gain, and gains grew with the number of specialists covering a class (+3.4% with one, +16.6% with nine). Specialists trained in days from the generalist against about six months for the baseline.

## Distillation in LLM post-training

A 2025 post-training survey (Tie et al.) describes the DeepSeek-R1 distillation as plain SFT, with no RL on the students, of smaller Qwen and LLaMA models on about 800K teacher samples: 200K non-reasoning instances from DeepSeek-V3 and 600K reasoning instances from the DeepSeek-R1-Stage1 checkpoint. This is sequence-level imitation, not the soft-target matching above.

## Limits

- The authors did not demonstrate distilling specialist knowledge back into a single net; their suggestion of specialists with a full softmax, trained on soft targets to curb overfitting, is only a proposal.
- No seeds, variance or significance tests; learning rate, batch size and steps are not given; the JFT and speech data are internal.
- The MNIST bias correction was tuned on the test set.

## See Also
- [[Sequence-Level Knowledge Distillation]] — extends (soft targets moved from word level to whole sequences)
- [[On-Policy Distillation]] — extends (per-token teacher signal on the student's own samples)
- [[Distilling Step-by-Step]] — extends (a task-distillation baseline it builds on)
- [[Model Compression with MUNGE Mimic Nets]] — related (earlier ensemble compression)
- [[Model Compression Landscape]] — related
