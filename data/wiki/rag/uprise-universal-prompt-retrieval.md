---
title: UPRISE Universal Prompt Retrieval
tags: [rag, pattern]
summary: Train a small retriever, labelled by a frozen LLM's task scores, that picks demonstrations from a pool of other tasks and prepends them to a zero-shot input; gains transfer to larger models but are uneven across task types.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-cheng-2023-uprise.md
---

# UPRISE Universal Prompt Retrieval

UPRISE does not rewrite a prompt. It retrieves prompt text from a pool of demonstrations drawn from other tasks. A frozen GPT-Neo-2.7B labels candidate demonstrations (50 sampled per example) as positive or negative by the task score they yield, and a BERT-base bi-encoder pair is trained contrastively on those labels (20 negatives, 3 retrieved at inference, 3 epochs, 36 hours on 8 V100 GPUs). "Zero-shot" here means no demonstrations from the test task; three demonstrations from other tasks are still prepended. Numbers are the paper's (self-reported), single runs, held-out task clusters.

## Reported results

- **On the tuning model (GPT-Neo-2.7B):** Reading Comprehension average 31.6 to 40.1; Paraphrase 47.0 to 61.6.
- **Transfer without retuning:** Paraphrase 51.2 to 62.3 on BLOOM-7.1B and 47.3 to 59.0 on text-davinci-001; Reading Comprehension on text-davinci-001 45.9 to 53.6.
- **Not universal:** Coreference drops (GPT-Neo from 64.0 to 62.1, OPT-66B from 73.1 to 68.0) and Commonsense is flat or lower. The authors attribute this to tasks formulated as language modelling. NLI on text-davinci-001 slips from 50.2 to 46.9. Against three random few-shot demonstrations from the target task, UPRISE is ahead on Reading Comprehension (40.1 against 37.4) and clearly behind on Sentiment (61.8 against 72.7).
- **The retriever must be learned:** random selection, BM25 and SBERT all did worse (values shown only in a figure). A pool of other tasks' demonstrations beat a pool of raw text on every cluster (Paraphrase 61.6 against 44.7).
- **ChatGPT (gpt-3.5-turbo-0301), human-judged, 66 to 100 samples:** FEVER2.0 rose from 51.0 to 56.0 and Covid-19 from 47.0 to 83.0 (partly a scoring rule for ambiguous answers); TruthfulQA unchanged at 86.3.

## Limits

- Language tasks only; no chain-of-thought demonstrations, hand-written prompts or instruction-search baselines; no per-query cost; no seeds or intervals.
- Models date from 2020 to 2022 with one chat model; ChatGPT samples are small.
- It selects among existing text and cannot generate new instructions.

## See Also
- [[Dynamic Tool Discovery]] — related
- [[RAG Reranking]] — related
- [[Tuning an Embedding Model from Match Labels]] — related
