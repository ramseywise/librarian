---
title: "BERT Distillation: DistilBERT and TinyBERT"
tags: [llm, fine-tuning, comparison]
summary: "DistilBERT distils BERT once during pretraining with a triple loss and a student initialised from teacher layers; TinyBERT also matches attention matrices, hidden states and embeddings, in a general stage and a task-specific stage with data augmentation."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-sanh-2019-distilbert-distilled-version-bert.md
  - data/raw/papers/2026-11-08-jiao-2020-tinybert.md
  - data/raw/papers/2026-11-08-qiu-2020-pre-trained-models-natural-language.md
  - data/raw/papers/2026-11-08-zhou-2024-comprehensive-survey-pretrained-foundation-models.md
---

# BERT Distillation: DistilBERT and TinyBERT

Both compress a BERT-base teacher into a smaller Transformer student, building on soft-target distillation ([[Knowledge Distillation with Soft Targets]]). They differ in what the student is asked to match and when.

## DistilBERT

Sanh et al. build a 6-layer student on BERT's architecture, dropping token-type embeddings and the pooler, start it from every second teacher layer, and pretrain it on the BERT corpus with a weighted sum of three losses: soft-target distillation (softmax with temperature T), masked LM, and a cosine embedding loss. The student is then fine-tuned on downstream tasks.

Claims (self-reported):
- GLUE dev (medians of 5 seeds) keeps 97% of BERT-base's score at 40% fewer parameters (66M against 110M), and is 60% faster on CPU at batch size 1 (STS-B dev pass: 410 s against 668 s, Xeon E5-2690 v3). On an iPhone 7 Plus question-answering app it is 71% faster excluding tokenisation, with a 207 MB model.
- Ablations on the GLUE score: masked-LM only (no distillation or cosine loss) costs 2.96 points, starting from random weights rather than teacher layers costs 3.69, and dropping the masked-LM loss costs 0.31.
- Per task, BERT-base against DistilBERT: RTE 69.3 against 59.9, MNLI 86.7 against 82.2. IMDb is 0.6 behind; on SQuAD v1.1 dev it scores 77.7 EM and 85.8 F1, where BERT-base scores 81.2 and 88.5.
- Training used 8 16GB V100 GPUs for about 90 hours, against RoBERTa's one day on 1024 32GB V100s.

## TinyBERT

Jiao et al. train a 4-layer or 6-layer student with four losses: embeddings, per-layer attention matrices (MSE, averaged over heads), hidden states through a learned projection (MSE), and prediction-layer cross-entropy with temperature. It runs in two stages. The first stage, general distillation, uses Wikipedia text with pretrained BERT as teacher and gives the student its starting weights. The second stage, task-specific distillation, uses the fine-tuned BERT as teacher on a task set augmented by word replacement (GloVe is used for the augmentation).

Claims (self-reported, GLUE official test unless noted): TinyBERT4 (14.5M parameters) keeps over 96.8% of BERT-base's accuracy while 7.5x smaller and 9.4x faster (K80 GPU inference), outperforms the 4-layer baselines BERT4-PKD and DistilBERT4 by 4.4% or more, using roughly 28% of their parameters, and reaches the average of the 24-layer MobileBERT-TINY at 38.7% of the FLOPs (the authors flag that comparison as possibly unfair). TinyBERT6 (67M) matches BERT-base on the test average and beats same-architecture baselines by 2.6%. Dev ablations: removing general distillation, task-specific distillation or data augmentation each lowers the average (the last two by similar amounts, more than the first); removing Transformer-layer distillation collapses performance; dropping the attention loss hurts more than dropping the hidden-state loss (72.9 without the latter); uniform layer mapping beats top (70.9) and bottom (71.3) mappings.

## Figures quoted by two surveys

Neither survey ran experiments here; both quote figures from the cited work, so each is second-hand and (self-reported) by the original authors. Qiu et al. list TinyBERT with 4 layers and 14.5M parameters at a 9.4x speed-up against a BERT-base teacher, which matches the TinyBERT figures above. They add that BERT-of-Theseus runs 1.94x faster and keeps over 98% of the source model's performance. Zhou et al. quote DistilBERT as 40% smaller than BERT with 97% of its language comprehension retained, the same headline as above, and Q8BERT as quantising parameters from 32-bit to 8-bit, a fourfold compression with little impact on performance. Q8BERT is a quantisation method, not a distillation one; Zhou et al. group it with the compressed models.

## Limits

- DistilBERT: pretraining hyperparameters (optimiser, learning rate, steps, temperature, loss weights, sequence length) and the fine-tuning setup are not given. Latency comes from a single CPU at batch size 1 plus one phone; only GLUE has seeds. Drops differ widely by task (RTE -9.4, CoLA -5.0) and the headline is an average. Each ablation row is one configuration scored on the GLUE macro-average. The text and Table 2 give different SQuAD numbers for the variant with a second distillation step (79.8/70.4 against 79.1/86.9). Pruning and quantisation are not combined.
- TinyBERT: only a BERT-base teacher was used; wider or deeper teachers, adaptive layer choice per task and a QA-specific TinyBERT are left to future work. Claims about no extra gain from prediction-layer distillation at pretraining rest on unreported preliminary experiments. No seeds, optimiser, warmup, hardware or compute are reported; numbers are single runs. GLUE and SQuAD only, English only.

## See Also
- [[BERT Masked-LM Pretraining and Its Refinements]] — prerequisite-for (the teacher)
- [[Model Compression Landscape]] — related (pruning and quantisation alternatives)
- [[MT-DNN Multi-Task Learning and Ensemble Distillation]] — related (another distillation of BERT-based models, ensemble to single)
- [[Diff Pruning Sparse Task Difference Vectors]] — alternative-to
