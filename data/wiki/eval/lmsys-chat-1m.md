---
title: LMSYS-Chat-1M
tags: [eval, benchmark]
summary: "One million real user conversations with 25 LLMs collected from the Vicuna demo and Chatbot Arena in 2023, with four demonstrated uses: a fine-tuned Vicuna-7B moderator matching GPT-4 on a 110-message set, a 50-conversation jailbreak benchmark, instruction tuning, and the Arena-Hard-200 prompt set (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zheng-2023-lmsys-chat-1m.md
---

# LMSYS-Chat-1M

Zheng and colleagues (ICLR 2024) release one million conversations between users and 25 LLMs, gathered between April and August 2023 from two free sites that need no registration, the Vicuna demo and the Chatbot Arena website. Conversations are filtered for personal information on a best-effort basis and tagged with OpenAI moderation output; unsafe content is deliberately kept.

## Contents (self-reported)

- 210,479 users and 154 languages; 69.5 tokens average prompt length, 214.5 tokens average response, 2.0 turns per sample.
- About 5% of conversations (54,427) are flagged by the OpenAI moderation API. By category the counts are 33,968 sexual, 21,167 harassment, 9,499 violence, 3,591 hate and 863 self-harm, and the categories overlap. Most prompts concern coding; the extraction notes the cluster-to-percentage mapping is not recoverable from the text.

## Four use cases (self-reported)

- **Moderation**: a Vicuna-7B tuned on roughly 5K moderation examples together with 3K ShareGPT conversations reached micro-F1 0.65 zero-shot and 0.70 one-shot on 110 hand-labelled toxic messages that an earlier moderation API version missed, against GPT-4 at 0.71 and 0.69. Base Vicuna-7B scored 0.35 and 0.50, GPT-3.5-Turbo 0.45 and 0.64, Claude-2 0.32 and 0.30; Llama-2-7B-chat refused nearly every task (0.00 and 0.01).
- **Safety benchmark**: 50 jailbreak conversations, made of the five best attempts against each of 10 models; an attack succeeded if the response was flagged. Llama-2-13B-chat was broken 16% of the time and Claude-2 18%. For GPT-3.5-Turbo and GPT-4 the rate was 34%, for Vicuna-13B-v1.5 66% and for Alpaca-13B 74%.
- **Instruction tuning** of Llama-2-7B: HighQuality-7B (45K conversations from proprietary models, 33M tokens) reaches 47.7 on MMLU and 6.03 on MT-Bench, not far from Vicuna-7B-v1.5, which reaches 49.8 and 6.17 after 370M tokens. Upvote-7B, trained on 39K conversations with open models picked by user votes, reaches 45.0 and 5.86.
- **Hard prompts**: an LLM scores prompts 0 to 10; GPT-4 wins against GPT-3.5-Turbo on 52% of the 50 highest-scored prompts, but on only 22% of the 50 lowest. Arena-Hard-200 holds the 200 prompts rated 9 or more by three LLM scorers.

## Limits

- Users are mostly LLM hobbyists and researchers; data has repeats and low-quality entries, and Vicuna dominates counts as the default model. No preference annotations are released.
- The moderation API likely misses content, so the 5% flagged share is a lower bound.
- Possible MMLU and MT-Bench contamination in the tuning subsets. No hyperparameters, seeds or variance for the fine-tuned models; the jailbreak set has 50 items and the moderation set 110, chosen against the earlier API.
- The Arena-Hard-200 selection depends on scores assigned by LLMs. Data covers April to August 2023 only.

## See Also
- [[Arena-Hard-Auto and BenchBuilder]] — extends (curates prompts from Chatbot Arena with a quality score)
- [[LLM-as-Judge Evaluation]] — related
- [[XSTest]] — related (over-cautious refusals)
