---
title: LLM vs Fine-Tuned Model Practitioner Survey
tags: [llm, fine-tuning, reference]
summary: "Yang et al.'s 2023 practitioner survey on when to use a prompted LLM rather than a fine-tuned smaller model, with remarks by task type and cost, latency and PEFT notes, all quoted from other work (self-reported by the authors, early 2023)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-yang-2023-harnessing-power-llms-practice.md
---

# LLM vs Fine-Tuned Model Practitioner Survey

Yang, Jin, Tang et al. (2023, a survey on ChatGPT and beyond) ask when a practitioner should reach for a prompted LLM instead of a smaller model fine-tuned on task data, given the model, the data and the task. They call a model "fine-tuned" if it is typically under 20B parameters, a working cut-off and not an experiment. A decision flow (Fig 2) spans NLU, generation, knowledge-intensive, scaling and emergent, and real-world tasks.

## Remarks and practices

- Favour LLMs when data is out-of-distribution or annotations are scarce (Remark 1).
- Favour fine-tuned models for conventional NLU with plenty of annotated data and little distribution shift (Remark 2).
- Use LLMs for generation (Remark 3), and test any generated code with care.
- Add retrieval so a closed-book task becomes open-book; small fine-tuned models then do well.
- Where cost or latency matters, consider small fine-tuned models with parameter-efficient tuning (Remark 8).
- Choose a model whose pre-training data resembles the downstream task.

## Evidence the survey quotes from other work

- CivilComments toxicity: under HELM prompting the best LLM only just beats random guessing, whereas popular fine-tuned models do far better. Perspective API, a multilingual BERT-based fine-tuned model, is still among the best detectors (the survey gives no numbers).
- CoNLL03 NER: fine-tuned models score about double the LLMs, according to a cited study.
- GPT-4 is reported at 86.5% on English MMLU and 96.3% on ARC-C.
- LLMs are usually 10 or 100 times larger than fine-tuned models. Estimates from a Lambda Labs blog put one T5 11B training run well above $1.3 million and one GPT-3 175B run at $4.6 million; GPT-3 175B needs ten times the training FLOPs of T5 11B (3.14 x 10^23).
- Pricing on OpenAI's page, accessed 03/02/2023: using a custom fine-tuned model was priced at $0.12 per 1k tokens, plus $0.03 per 1k for training; GPT-3.5-turbo chat was $0.002 per 1k.
- HELM latency: GPT-J 6B goes from 0.077s for 2 output tokens to 0.707s for 32, and InstructGPT davinci v2 needs 1.969s for 32. Scoring one query-passage pair with davinci v2 takes 0.21s, which the survey calls too slow for web search.
- The Alpaca-LoRA repository reports LLaMA-Alpaca tuning in hours on one RTX 4090.
- Cited studies find that fine-tuning on application data may reduce zero-shot robustness and calibration.

## Limits

- The survey runs no experiments; every performance claim comes from other work, frequently through HELM or PaLM. The authors admit nobody has yet compared fine-tuned models and LLMs systematically on real tasks.
- Parameter-efficient tuning gets a single paragraph naming LoRA, prefix tuning, P-tuning and Alpaca-LoRA, with no numbers or hyperparameters; QLoRA, DoRA and adapters are absent.
- Prices, the model landscape and the 20B cut-off all reflect early 2023.

## See Also

- [[HELM Holistic Evaluation]] — related (source of the toxicity and latency findings)
- [[Parameter-Efficient Fine-Tuning Methods]] — related
- [[LoRA Low-Rank Adaptation]] — related
- [[Foundation Models: Homogenization and Emergence]] — related
- [[Few-Shot Prompting]] — related
