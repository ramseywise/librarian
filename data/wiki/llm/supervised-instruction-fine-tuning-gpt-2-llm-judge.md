---
title: "Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge"
tags: [llm, fine-tuning, pattern]
summary: "Raschka's instruction fine-tuning of GPT-2 medium on 1,100 pairs: Alpaca-style prompt formatting, a per-batch padding collate function with -100 target masking, a 2-epoch AdamW run, and a local Llama 3 8B judge scoring 50.32 of 100; with how Huyen and Raieli describe instruction data."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-build-a-large-language-model-from-scratch-ch07-fine-tuning-to-follow-instruction.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch03-exploring-llms-as-powerful-ai-engine.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch02-understanding-foundation-models.md
---

# Supervised Instruction Fine-Tuning of GPT-2 with an LLM Judge

Chapter 7 of Raschka's *Build a Large Language Model (From Scratch)* trains a pretrained model on explicit instruction-response pairs, then scores its answers with another model. The base is GPT-2 medium (355M); Raschka judges the 124M model too small for satisfactory results, with no ablation shown.

## Data and formatting

- The dataset holds 1,100 instruction-response pairs written for the book (a 204 KB JSON file). Sequential slicing, with no shuffle, gives 85% train, 10% test and 5% validation: 935, 55 and 110 examples.
- Entries use the Alpaca prompt style: a fixed preamble sentence saying the text is an instruction describing a task to be completed, then `### Instruction:`, `### Input:` (omitted if empty) and `### Response:`. Phi-3 style is shown as an alternative.

## Collate function and masking

- Each batch is padded to its longest sequence, not the dataset's, and truncated to the model context (`allowed_max_length=1024`).
- Targets are the inputs shifted by one position. Padding targets are set to -100, which PyTorch `cross_entropy` ignores by default, but one end-of-text token is kept so the model learns to stop.
- The chapter does not mask instruction tokens. Researchers are divided; Shi et al. 2024 found that not masking them helps.

## Training run

Setup: GPT-2 medium, 935 training examples, 2 epochs of AdamW with learning rate 0.00005 and weight decay 0.1, batch size 8, about 0.87 minutes on an A100. Loss on 5 batches starts at 3.826 and ends epoch 2 at train 0.300 and validation 0.657 (step 230). Raschka says a third epoch may overfit and does not test it.

## LLM-judged evaluation

A local Llama 3 8B Instruct (Ollama; temperature 0, seed 123, num_ctx 2048) gets the input, the reference output and the model response and scores 0 to 100. On the 110 test examples, in a single run:

| Model | Mean score |
|---|---|
| Fine-tuned GPT-2 medium | 50.32 |
| Llama 3 8B base, no fine-tuning | 58.51 |
| Llama 3 8B instruct (general instruction data) | 82.6 |

Raschka lists three ways to evaluate: MMLU-style benchmarks, human preference voting (the LMSYS arena) and conversational benchmarks scored by an LLM (AlpacaEval), and advises repeating the judge run and averaging because Ollama is non-deterministic. See [[LLM-as-Judge Evaluation]]. Preference fine-tuning is pointed to as an optional later step and not covered; the Alpaca dataset has 52,002 entries.

## How the other books describe instruction data

- Raieli and Iuculano define instruction tuning as further training of a pretrained model on instruction-output pairs, recommend varied tasks, with extra weight on reasoning whose steps appear in the context, and put the usual RLHF supervised set at 10,000 to 100,000 pairs written by people (claim, no model named).
- Huyen calls (prompt, response) examples demonstration data, also called behavior cloning. InstructGPT's 13,000 pairs would cost $130,000 at $10 each, and about 90% of its labelers had a college degree. LAION's 13,500 volunteers produced 10,000 conversations, 161,443 messages in 35 languages and 461,292 quality ratings (reported). See [[RLHF Pipeline]] for the stage that follows.

## Limits

- The judge is a local 8B model rather than GPT-4, Ollama is not fully deterministic, and the run is not repeated and averaged. The 110 test examples come from the book's own set, so the scores cannot be compared with public benchmarks.
- Model size, masking, prompt style and epoch count are not ablated and are left as exercises. The split is sequential and seeds are not varied.
- The Llama 3 8B reference rows differ in kind from the fine-tuned GPT-2 (base, and general instruction data), so they are reference points, not a controlled comparison.
- No RLHF or reward model is covered. Raieli and Iuculano relay other work without experiments, and Huyen's figures are secondhand.

## See Also
- [[Pretraining a Small GPT: Loss, Perplexity and Overfitting]] — prerequisite-for
- [[Classification Fine-Tuning a GPT: Replace the Output Head]] — alternative-to (class labels instead of instructions)
- [[Self-Instruct and Unnatural Instructions]] — related (building instruction data)
- [[LIMA: Small Curated Instruction Data]] — related
- [[Flan-PaLM Instruction Finetuning Scaling]] — related
- [[UltraChat and LaMini Instruction Datasets]] — related
- [[RLHF Pipeline]] — extends (SFT is its first stage)
