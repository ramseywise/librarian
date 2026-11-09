---
title: Analogical Prompting
tags: [prompting, pattern]
summary: One prompt asks the model to recall relevant example problems (optionally with a tutorial) and then solve the target problem, replacing hand-labelled few-shot exemplars; helps larger models, hurts small ones.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yasunaga-2023-large-language-models-as-analogical.md
---

# Analogical Prompting

Analogical prompting asks the model, inside a single prompt, to recall several distinct relevant problems, describe and solve each, and then solve the original. For code tasks the prompt can first request a tutorial on the core algorithms. It uses no labelled exemplars and no retrieval, so it needs no exemplar set. The prompt asks for diverse problems and about three to five of them.

## Reported results (self-reported)

- The paper states an average accuracy gain of +4% over zero-shot and few-shot CoT across GSM8K, MATH, Codeforces and five BIG-Bench tasks, with GPT-3.5-turbo, GPT-4 and PaLM2.
- GSM8K, self-generated exemplars against 5-shot CoT against zero-shot CoT, temperature 0. In that order, GPT-3.5-turbo scores 77.8, 76.7 and 75.8; PaLM2 81.7, 80.7 and 78.2; text-davinci-003 61.0, 54.0 and 50.3 (its prompts included a demonstration of how to generate exemplars). On MATH, GPT-3.5-turbo scores 37.3, 34.9 and 33.9.
- Scale: on GSM8K, text-curie-001 and davinci-001 favour labelled few-shot CoT; from davinci-002 up, self-generation wins (48 against 47 for retrieved CoT at davinci-002).
- Retrieved exemplars (Sentence-BERT top five) are the steadier choice and suit small models; self-generation suits larger ones.
- Codeforces (50 level-A problems), GPT-3.5-turbo-16k Acc@1: 15 with tutorial plus exemplars, against 13 with exemplars only and 9 for zero-shot CoT; GPT-4 reaches 19.
- Number of exemplars: one was worse; three to five were about equal. Asking for diverse exemplars lifted GSM8K from 75.9 to 77.8. Adding self-consistency gave 85.3 on GSM8K and 46.0 on MATH.
- Error analysis of 50 correct and 50 incorrect GSM8K and MATH answers: 9 of the correct answers rested on exemplars whose own solutions were wrong.

## Limits

- More output tokens and compute than zero-shot CoT; the authors say it suits stronger models and is prompt-sensitive.
- GSM8K gains on chat models are about 1 point; no variance, seeds or tests; Codeforces differences of 1 to 2 points are small (50 problems, two runs); the self-consistency sample count is not given.
- Exemplar correctness is not verified. Only 2023 models; BIG-Bench only on GPT-3.5-turbo; no comparison with other dynamic selection beyond one retrieval baseline.

## See Also

- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[Few-Shot Prompting]] — prerequisite-for
- [[Zero-Shot Chain-of-Thought]] — alternative-to
- [[Self-Consistency]] — related
- [[Prompt Optimization]] — related
