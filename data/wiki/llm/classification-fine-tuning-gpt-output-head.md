---
title: "Classification Fine-Tuning a GPT: Replace the Output Head"
tags: [llm, fine-tuning, pattern]
summary: "Raschka's recipe for turning a pretrained GPT-2 small into a spam classifier: swap the 50,257-way output layer for a 2-way head, train only the head, last block and final LayerNorm on last-token logits with cross-entropy, and why it differs from instruction fine-tuning."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-build-a-large-language-model-from-scratch-ch06-fine-tuning-for-classification.md
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch01-understanding-llms.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch02-transformer-model-behind-modern-ai-revoluti.md
---

# Classification Fine-Tuning a GPT: Replace the Output Head

Chapter 6 of Raschka's from-scratch LLM book. Chapter 1 defines the two fine-tuning kinds: classification fine-tuning uses texts with class labels, instruction fine-tuning uses instruction and answer pairs (see [[Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge]]). Raschka says classification needs less data and compute but is confined to the classes it was trained on.

## The recipe

1. **Data.** The SMS Spam Collection (UCI, 5,572 labelled messages) is balanced by undersampling to 747 spam and 747 not-spam messages, split 70/10/20 into train, validation and test. Messages are padded with token 50256 up to the length of the longest training example, not cut to the shortest.
2. **Model.** Load pretrained GPT-2 small (124M) and replace the 50,257-way `out_head` with `torch.nn.Linear(emb_dim, num_classes)`. Freeze everything except the new head, the last transformer block and the final LayerNorm.
3. **Last token only.** The loss uses `model(input_batch)[:, -1, :]`: under the causal mask the last token has seen all earlier ones.
4. **Loss.** Cross-entropy on those logits, a differentiable stand-in for accuracy, which cannot be differentiated.
5. **Training.** AdamW with learning rate 5e-5, 5 epochs, batch size 8, seed 123, accuracy as the metric. About 5.65 minutes on the author's M3 MacBook Air and under half a minute on a V100 or A100. Raschka calls five epochs a reasonable starting point to adjust by the train/validation loss gap, and suggests raising dropout or weight decay to close a validation/test gap.

Raieli and Iuculano give the same shape of advice for a Hugging Face transformer: keep most layers frozen, train a layer or two added on top, and use a very small learning rate if layers are unfrozen.

## What the extraction does not give

The extraction states the pre-fine-tuning accuracy only as near chance on a random head and omits the loss and the final training, validation and test accuracy values, so none are reported here. A pretrained model without instruction tuning could not follow a spam prompt in section 6.4, shown by one example.

## Limits

- Single run and seed; no variance. Accuracy only, with no precision, recall or F1 even though the data was undersampled.
- The per-epoch accuracies in the log come from just 5 batches (eval_iter=5) and so are noisy.
- Which layers to train is tested in an appendix, not here; exercises 6.1 to 6.3 are left to the reader (longer context, full fine-tune, first token).
- The extraction's results section lacks the accuracy numbers.

## See Also
- [[Pretraining a Small GPT: Loss, Perplexity and Overfitting]] — prerequisite-for
- [[Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge]] — alternative-to (instruction pairs instead of class labels)
- [[Parameter-Efficient Fine-Tuning Methods]] — related (other ways to train a small part of a frozen model)
- [[Transfer and Multi-Task Learning Conditions]] — related
