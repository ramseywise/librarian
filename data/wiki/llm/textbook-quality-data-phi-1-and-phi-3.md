---
title: "Textbook-Quality Data: phi-1 and phi-3"
tags: [llm, pretraining-and-data, concept]
summary: "phi-1 reaches 50.6% HumanEval at 1.3B parameters by training on classifier-filtered code plus GPT-3.5 synthetic textbooks, then finetuning on synthetic exercises; phi-3 applies the same data-over-scale bet to a 3.8B model (all figures self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-gunasekar-2023-textbooks-all-you-need.md
  - data/raw/papers/2026-11-07-abdin-2024-phi-3-technical-report.md
---

# Textbook-Quality Data: phi-1 and phi-3

Both reports argue that data quality can beat scale for small models. Gunasekar et al. (2023) hold that training text should read like a good textbook: clear, self-contained, instructive and balanced. The Phi-3 report (Microsoft, 2024) proposes that web data filtered to a suitable "educational level", plus synthetic data, brings a small model nearer to a "data optimal regime": data tuned to the model's scale in place of extra compute or overtraining (the word "optimal" is aspirational).

## phi-1 recipe

- Quality filter: a random forest over CodeGen embeddings, fitted to about 100k GPT-4 annotations of educational value, applied to Stack and StackOverflow code.
- CodeTextbook, the pretraining set, combines about 6B filtered web code tokens with under 1B GPT-3.5 textbook tokens; a 1.3B decoder trains on it for about 8 epochs.
- CodeExercises holds about 180M tokens of GPT-3.5 Python exercises with solutions and is used only for finetuning.
- Results (one generation, 1.3B, about 7B unique tokens): pass@1 of 50.6% on HumanEval and 55.5% on MBPP. Before the exercises, phi-1-base gets 29% on HumanEval; the 350M phi-1-small still gets 45%.
- Table 1 shows WizardCoder-16B ahead on HumanEval (57.3% against 50.6%) and behind on MBPP (51.8% against 55.5%); those rival figures are as reported there.
- Filter ablation (350M, 36k steps): the unfiltered, deduplicated Python Stack plus StackOverflow (about 200B tokens) stalls at 12.19% HumanEval even at 96k steps; the filtered subset reaches 17.68%; adding synthetic textbooks gives 20.12%.
- Cost: under 4 days on 8 A100s plus 7 hours of finetuning. For 1.3B models, Fig 2.1 gives 770 GPU hours for 51B tokens (phi-1 and phi-1-base) against 1090 GPU hours for 76B tokens (The Stack+).
- Checks: a 13-gram search between HumanEval docstrings and CodeExercises found four questions, all false positives. Pruning CodeExercises by AST match drops between 42.5K and 354K of its 879.5K problems as tau moves from 0.95 down to 0.8; retraining phi-1 on data pruned at tau=0.9 gives 45.1% HumanEval, still over StarCoder-Prompted's 41.5%. On 50 unconventional problems graded 0-10 by GPT-4, phi-1 scores 52% and StarCoder 51%.

## phi-3

- Decoder-only transformers go through two sequential training phases on filtered public web data and LLM-generated synthetic data, followed by SFT and DPO. Llama 2's block structure and tokenizer are reused.
- phi-3-mini, with 3.8B parameters and 3.3T training tokens, gets 68.8% on 5-shot MMLU, against 70.5 for Mixtral 8x7b and 71.4 for GPT-3.5 (internal few-shot pipeline, temperature 0), and beats both on 8-shot CoT GSM-8K. Quantised to 4 bits it needs about 1.8GB and exceeds 12 tokens per second on an iPhone 14 (A16 Bionic chip, running natively and offline).
- Two larger models, phi-3-small at 7B and phi-3-medium at 14B, both trained on 4.8T tokens, reach MMLU scores of 75.7 and 78.0. Because the step from small to medium is smaller than from mini to small on some benchmarks, the authors suspect the data mix has not reached the data optimal regime at 14B.
- The phi-3.5 series adds a mini model, an MoE model (phi-3.5-MoE, 42B total, 6.6B active; average 69.2 against 74.9 for GPT-4o-mini on the Table 3 benchmarks) and a 4.2B vision model (phi-3.5-Vision).

## Limits

- phi-1 targets Python only, handles specific APIs and rarer packages poorly, is less robust to prompt style, grammar slips and long prompts, and is poor at counting and spatial reasoning.
- The GPT-3.5 synthetic data contains many errors (the authors suggest GPT-4 would help). Generation details are withheld and the data is unreleased, so the paper cannot be reproduced. No 1.3B ablation separates synthetic textbooks from filtering; there are no seeds, no error bars and no stated decoding settings.
- The authors have no method for measuring data diversity and redundancy. The emergent-capability claims are qualitative examples, and Table 3 shows every model doing worse on non-similar problems, so part of the HumanEval gain is attributed to CodeExercises.
- phi-3 numbers come from an internal pipeline with no prompt optimisation and may differ from published ones. Data, optimiser, learning rate, batch size, hardware and compute figures are neither given nor released.
- phi-3-mini scores low on TriviaQA, which the authors link to limited stored facts (they suggest search augmentation), and it is mostly English. The phi-3.5 models fall sharply on RULER at 128K, attributed to missing long-context mid-training data. Hallucination, bias and safety problems persist, and contamination is not analysed.

## See Also
- [[TinyStories Synthetic Corpus and GPT-Eval]] — prerequisite-for
- [[Phi-4 Training Recipe and Pivotal Token Search]] — extends
- [[Diversity Seeding for Synthetic Data]] — related
- [[HumanEval and pass@k]] — related (the benchmark behind the phi-1 headline)
