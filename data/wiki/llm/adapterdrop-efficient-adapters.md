---
title: AdapterDrop Efficient Adapters
tags: [llm, fine-tuning, concept]
summary: "Rucklé et al. time adapters against full fine-tuning (training up to 60% faster, inference 4-6% slower) and drop adapters from lower layers: five dropped layers kept 97.1% of GLUE performance with a specialised model (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-ruckle-2021-adapterdrop.md
---

# AdapterDrop Efficient Adapters

Rücklé, Geigle, Glockner et al. (EMNLP 2021) measure the training-time and inference-time cost of efficient adapters (Houlsby, Pfeiffer) and AdapterFusion against full fine-tuning, and test whether dropping adapters makes them faster. They hypothesise that the lower transformer layers' adapters contribute little, so dropping them and pruning seldom-used AdapterFusion adapters saves compute at small cost.

## Timing results (self-reported)

Measured on a BERT-base configuration, V100 and Titan X GPUs, using AdapterHub.

- Against full fine-tuning, a training step with adapters is up to 60% quicker (Pfeiffer adapter, sequence length 128, batch size 32, relative speed 1.60).
- Adapter inference runs at 94-96% of the speed of a fully fine-tuned model, which is 4-6% slower.
- Convergence takes no extra steps for adapters, and pre-training them with masked language modelling did not speed convergence (RoBERTa-base, 8 GLUE tasks).
- Compared with full fine-tuning, AdapterFusion over eight adapters costs roughly 47% slower in training and 62% slower at inference. Over 16 adapters its relative speed is 0.33 when training and 0.24 when running inference.

## AdapterDrop

Adapters are removed from the first n layers.

- **Specialized AdapterDrop:** n is fixed during training, giving one model per n.
- **Robust AdapterDrop:** n is drawn randomly from 0 to 11 on every training batch, so a single model is usable when the count of dropped layers varies.
- Setup: RoBERTa-base, 8 GLUE tasks, dev sets, mean of three runs. Dropping five layers, the specialised variant retains 97.1% of a standard adapter's mean GLUE score and the robust variant 95.4%. A standard adapter, with layers dropped only at test time, fell to 89.0%, so training for dropping is what makes it safe.
- Robust training speeds up training steps by 26% (4.7% per dropped adapter, 5.5 dropped on average).
- Multi-task inference: dropping the first five layers makes inference on eight simultaneous tasks 39% faster (21-42% depending on the task count); each shared layer speeds up 16-task inference by up to 8.4%.

## AdapterFusion pruning and sharing

- Removing least-activated adapters per layer after fusion training: two remaining adapters of eight matched the full AdapterFusion models on RTE and CoLA while speeding inference by 68%.
- Dropping AdapterFusion layers: on RTE, removing the first five layers still beat the single-task adapter and improved inference efficiency by 26%; on CoLA, removing even the first layer fell below the single-task adapter.
- Applying fusion dropout at 75% (six of eight adapters) sped each training step by 74% on average, while RTE went from 85.4 to 80.9 and CoLA from 63.9 to 60.4.
- Sharing adapter weights across layers at compression rate 16 uses 74k parameters and lowers mean GLUE by 2.35% (85.35 to 83.0). Rate 4 uses 295k, which is 66% below the 884k of the standard Pfeiffer architecture.

## Limits

- Speed was measured only on a BERT-base configuration on V100 and Titan X GPUs with PyTorch 1.5.1; no decoder-only or billion-parameter models were timed.
- Accuracy was assessed only with RoBERTa-base, on GLUE dev sets.
- The authors caution that AdapterDrop may not fit every task; CoLA degrades sharply, and in the multi-task setting both RTE and CoLA decline steeply.
- The multi-task speedups require several independent predictions to be run on one shared input.
- A parallel AdapterFusion implementation gave no gain, and training speedups depend on input size.
- Appendix B-E results are described by the authors as preliminary. Nothing is printed about the optimizer, the learning rate or the adapter settings, and no code link appears in the text.

## See Also
- [[Parameter-Efficient Fine-Tuning Methods]] — prerequisite-for
- [[LoRA Low-Rank Adaptation]] — alternative-to (merges into the weights instead of adding adapter layers)
- [[Diff Pruning Sparse Task Difference Vectors]] — alternative-to
- [[LLaMA-Adapter Zero-Initialized Attention]] — related (another adapter variant)
