---
title: FACTS Leaderboard
tags: [eval, reference]
summary: "Google's four-part factuality suite (grounding to a document, closed-book parametric recall, search use, image-grounded answers) averaged into one FACTS Score; Gemini 3 Pro led at 68.8 over 15 proprietary models (self-reported), with the authors' judges mostly Google models."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-cheng-2025-facts-leaderboard.md
---

# FACTS Leaderboard

Cheng, Jacovi, Globerson and about 60 co-authors at Google (arXiv 2512.10791, preprint) treat factuality as several skills rather than one: grounding to a given document, recalling facts from model parameters, using search, and answering about images. The four sub-benchmarks are combined into a single **FACTS Score**, an average of their accuracies; each sub-score is itself averaged over a public and a private set. The leaderboard is run by Kaggle.

## Results (self-reported)

- **Overall.** 15 proprietary API models, public and private sets, accuracy with 95% intervals: Gemini 3 Pro 68.8, Gemini 2.5 Pro 62.1, GPT 5 61.8 and Claude 4.5 Opus 51.3.
- **Grounding v2.** Gemini 2.5 Pro scored 74.2 with a ±2.0 interval, then GPT 5 at 69.6 and Gemini 3 Pro at 69.0, Claude 4.5 Opus at 62.1 (±3.3), and lower for o3 at 36.2 (±2.2) and o4 mini at 29.3. The prompts match v1 and the judges are new: Gemini 2.5 Flash and GPT-5, and each model's score averages the two judges' accuracy percentages. A response is accurate only if every information-bearing claim is grounded in the prompt, and only if it is judged eligible; the authors add that filter because context-grounding metrics can be gamed by ignoring what the user asked. The paper gives no n for Grounding and documents up to 32k tokens.
- **Judge validation.** Against human ratings on N=320 held-out private items (class ratio 79:19), Gemini 2.5 Flash with prompt v2 scored Macro-F1 65.33, GPT-5 with v2 65.18 and Gemini 2.5 Pro with v1 64.87. The older v1 judges scored lower: Gemini 1.5 Pro 55.65 or 56.89 depending on the prompt, GPT-4o 59.73 and Claude 3.5 Sonnet 53.15. The extraction notes these are low values in absolute terms and the margins are small.
- **Parametric.** 2,104 closed-book questions (1,052 public, 1,052 private), graded by Gemini 2.5 Pro alone, averaging three sampled grades. GPT-o3 had higher accuracy than GPT-5 (57.0 against 55.7), but GPT-5 hedged 13.3% of the time against 1.9% and so led on attempted accuracy (64.3 against 58.2) and F1 (59.7 against 57.6). GPT-5 mini hedged 67.6%.
- **Search.** 1,884 questions (890 public, 994 private) answered through the Brave Search API and graded by an auto-rater built on Gemini 2.0 Flash. Gemini 3 Pro reached 83.8 accuracy with 3.39 searches on average, and GPT-5 77.7 with 4.28.
- **Multimodal.** Roughly 1,500 questions (711 public, 811 private), where Gemini 2.5 Pro reached 46.9 accuracy. Its rubric autorater has Macro-F1 of 72.3 on Coverage and 78.2 on No-Contradiction.

## Limits

Beyond Table 1 the paper gives no per-model Grounding results and no Grounding n; one run per model is implied, with no repeats beyond the three judge samples in Parametric. The judges are mostly Google models, and the authors concede self-preference bias in judges; the Grounding judges were validated weakly (Macro-F1 about 65, N=320, skewed classes). The Parametric questions were filtered adversarially using five open models, and their silver labels were produced by Gemini 2.5 Pro, and Search relies on a single engine. The suite leaves out video, fast-changing information and knowledge-base tool calls, and the authors did not analyse question hardness such as tail entities. The extraction adds that private-set results cannot be reproduced independently, and that the authors are at Google while Gemini models top the table.

## See Also
- [[Grounding Claim Methodology]] — related (its Grounding sub-benchmark also counts a response as accurate only when every claim is grounded)
- [[SAFE Long-Form Factuality Scoring]] — related (an earlier search-based factuality grader)
- [[FreshQA]] — alternative-to (another factuality benchmark; tests currency, with search)
- [[LLM Judge Biases]] — related (the paper concedes judge self-preference)
- [[FActScore]] — alternative-to (scores long-form factual precision against Wikipedia rather than a multi-part suite)
