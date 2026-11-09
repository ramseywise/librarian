---
title: RAISE Conversational Agent Memory
tags: [memory, concept]
summary: ReAct loop extended with a dialogue-level scratchpad and turn-level retrieved examples, fine-tuned on 848 real-estate scenes; the paper's gain over ReAct plus examples is within noise under GPT-4 prompting (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-liu-2024-llm-conversational-agent.md
---

# RAISE Conversational Agent Memory

RAISE (2024) is a conversational-agent architecture built on a ReAct loop with 12 tools. Its working memory has five parts: the system prompt, the conversation history, the task trajectory, a **scratchpad** and the top-k retrieved **examples**. The scratchpad keeps tool observations and entities as key-value pairs at the level of the dialogue, and is likened to short-term memory. Examples are query-response pairs recalled from an example pool by vector retrieval at turn level, so the retrieval module plays the long-term role. Training data are built from real conversations through selection, scene extraction, chain-of-thought completion by GPT-4 with manual validation, and scene augmentation; Qwen-14B-Chat is then fully fine-tuned. The paper names two failure types its scenes counter: role hallucination (the tuned agent keeps skills like Python coding that conflict with its role) and knowledge hallucination.

## Results (self-reported)

Setup: an in-house real-estate instant-messaging dialogue set, 100 held-out scenes, human-annotated quality scored 0 to 2 on four dimensions and summed to a score out of 8, single run; the fine-tuning set is 948 generated scenes with 100 held out (848 used for training).

- Fine-tuned Qwen-14B-Chat with RAISE has the highest overall quality among the configurations and needs the fewest action and plan steps; per query, fine-tuned RAISE runs faster than fine-tuned ReAct. Fine-tuning lifts it far above prompting the same model, and it matches prompted GPT-4 RAISE.
- Under GPT-4 prompting RAISE scores 7.69, slightly below ReAct plus Examples at 7.72, so the ranking with RAISE first holds only for the fine-tuned model. Fine-tuned ReAct plus Examples scores 7.66.
- Removing the thought step (Act-Only) gives lower fine-tuned quality than ReAct; ReAct plus Scratchpad improves on ReAct, and adding Examples improves further.
- With RAISE, prompted GPT-3.5 scores far below GPT-4 and needs many more action steps.

## Limits

- Evaluation uses one in-house real-estate dataset with 100 held-out scenes, and the dataset, code and weights are not released.
- The annotator count, agreement, blinding and any significance test are not stated, and the quality gaps among frameworks are small (7.5 up to 7.72 with GPT-4 as the backbone); the order may be within noise.
- The fine-tuning data and the GPT-4 prompting baseline both originate from GPT-4, and nothing is said about hardware, optimiser, retrieval k or embedding model.
- Memory components are ablated only as one bundle per framework. Nothing is tested on long conversations, and no other memory designs are compared.
- The authors concede potential hallucination and difficulty with complex logic; speed claims are asserted in prose only.

## See Also
- [[ReAct Pattern]] — prerequisite-for
- [[Scratchpads and Self-Notes]] — prerequisite-for
- [[Agent Memory Types]] — prerequisite-for
- [[Self-Controlled Memory Framework]] — alternative-to
