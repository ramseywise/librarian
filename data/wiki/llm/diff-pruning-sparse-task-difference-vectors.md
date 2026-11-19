---
title: Diff Pruning Sparse Task Difference Vectors
tags: [llm, fine-tuning, concept]
summary: "Diff pruning stores, per task, a sparse difference vector added to frozen pretrained weights, trained with a relaxed L0 penalty; structured diff pruning matched fine-tuned BERT-large on GLUE with 0.5% new parameters per task (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-guo-2021-parameter-efficient-transfer-learning-diff.md
---

# Diff Pruning Sparse Task Difference Vectors

Guo, Rush and Kim (ACL-IJCNLP 2021) study diff pruning, in which each task stores only a sparse difference vector layered over unchanged pretrained weights, and test whether this equals full fine-tuning with much less storage per task.

## Mechanism

- Task parameters are theta_task = theta_pretrained + delta_task, with theta frozen.
- The difference is delta = z * w. The mask z is a relaxed binary mask (stretched Hard-Concrete) under an expected-L0 penalty.
- After training, delta is magnitude-pruned to a target sparsity and fine-tuned again with the mask fixed. Without that fixed-mask stage GLUE performance fell from 84.9 to 81.4 (structured, BERT-large).
- The structured variant multiplies a per-group scalar mask (393 groups, one per matrix or bias vector).
- Non-adaptive diff pruning, which fine-tunes normally, takes the difference and magnitude-prunes it, was much worse, so the learned mask matters.

## Reported results (self-reported)

- Structured diff pruning matched fine-tuned BERT-large on the GLUE test server with 0.5% new parameters per task (single hyperparameter-searched run per task). Unstructured was slightly worse.
- Validation GLUE average by target sparsity (structured): 82.5 at 0.10%, 84.5 at 0.25%, 84.8 at 0.50%, 85.1 at 1.00%, and 85.0 for the unpruned diff.
- Adapters scored 80.4 on average with 3.6% new parameters per task and 79.8 at 2.1%; these figures were taken from Houlsby et al., and the average omits QNLI since that test set was changed.
- On SQuAD v1.1 (validation) structured diff pruning at 1.0% beat full fine-tuning F1, and was still above it at 0.5%. The authors read this as a regularisation effect, which they did not test.
- Storage per task: 13.6 MB for diff pruning, 51.7 MB for adapters and 1297.0 MB for full fine-tuning (BERT-large, simple Python implementation storing weights as float32 and positions as int32).
- On BERT-base (109M), structured diff pruning at 0.5% matched full fine-tuning and beat DistilBERT, TinyBERT and MobileBERT on the test average; the compression numbers come from Jiao et al.
- Restricting the diff to the fully connected layers after self-attention (adapter-like placement) was much worse, which the authors take to mean that adapters' restricted read and write points limit their efficiency.
- Training is 1.5 to 2 times slower per minibatch than regular fine-tuning and extra memory goes to alpha and w.

## Limits

- Training is slower and uses more memory, which the authors call a concern for larger models.
- The stored diff must keep the positions of nonzero entries along with their values.
- Inference is not sped up, whereas compression methods do speed it up (TinyBERT4 runs 9.4 times faster).
- The main experiments cover BERT-large and BERT-base on GLUE and SQuAD alone; RoBERTa and XLNet appear only in preliminary runs that are not reported. No generative LLM was tried, and the storage figure comes from a simple implementation.
- The adapter rows were not rerun by the authors, and the average without QNLI cannot be compared directly.
- Seed variance is not reported for the main results; the figure for which layers are modified shows nontrivial variation.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for
- [[AdapterDrop Efficient Adapters]] — alternative-to (the adapter line of PEFT)
- [[BitFit Bias-Term Fine-Tuning]] — alternative-to (sparse update of existing weights)
- [[BERT Distillation: DistilBERT and TinyBERT]] — alternative-to (compression baselines it is compared with)
