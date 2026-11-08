---
title: GAIA General-Assistant Benchmark
tags: [eval, reference]
summary: "GAIA is a 2023 set of 466 human-written questions with unique short answers that are conceptually simple for people but need multi-step tool use; humans scored 92% against 15% for GPT-4 with plugins (self-reported), and every system scored 0 on Level 3."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-mialon-2023-gaia.md
---

# GAIA General-Assistant Benchmark

GAIA (Mialon et al., arXiv 2311.12983, 2023) rests on the authors' premise that questions people find conceptually easy but that demand reliable multi-step tool use make a better measure of general assistants than tasks that keep getting harder for people, and that such questions can be graded automatically against a single factual answer.

## Construction

Compensated annotators wrote 466 questions from author-made seeds. Each was answered by its writer and independently by two new annotators, and kept only if the answers agreed. Of 623 new questions, 68% were valid as written (75% at Level 1, 68% at Level 2, 47% at Level 3); the two validation rounds plus repairs came to roughly two annotator-hours per question. There are 146 Level 1, 245 Level 2 and 75 Level 3 questions. 166 annotated dev questions are public, and the other 300 have held-out answers behind a leaderboard. Systems get a zero-shot prompt with a system message that fixes the answer format, and the final answer is scored by quasi exact match.

## Results (self-reported)

Setup: all 466 questions, zero-shot, quasi exact match.

- Humans scored 92% overall against 15% for GPT-4 with plugins (the abstract's figure). By level, human annotators scored 93.9, 91.8 and 87.3, taking 6.8, 10.5 and 17.7 minutes.
- GPT-4 without tools scored 9.1 on Level 1 and 2.6 on Level 2; GPT-4 Turbo 13.0 and 5.5 (means of 3 runs each).
- AutoGPT with a GPT-4 backend scored 14.4 and 0.4, taking 7.6 and 11.7 minutes, against 0.65 minutes for GPT-4 with plugins on Level 1.
- With questions typed into a search engine and the answer required to be deducible from the first results page, it solved 7.4% of Level 1 and none of Level 2.
- Every system scored 0 on Level 3.

## Limits

Only the final answer is scored, not the trace or plan. The GPT-4 plugin score is an oracle: plugins were picked by hand per question and queried manually in ChatGPT, so it cannot be reproduced, and plugins change. The 15% figure appears only in the abstract and cannot be derived from the table without weighting. AutoGPT's showing may come from its use of the GPT-4 API and needs re-evaluation. The API gives no tool-call logs, so only the strongest tool-capable models were run and failure analysis is coarse. The questions are English only, from US-based annotators, and some are unnaturally detailed. With 466 questions the set is small and will decay as contamination or web changes arrive. Levels are loose proxies built from annotators' step and tool counts, and no decoding parameters are reported. The models are from 2023, and later systems score higher (not shown in this source).

## See Also
- [[Gaia2]] — related (a different benchmark with a similar name)
- [[MedBrowseComp]] — related (browsing-based factual questions)
- [[Eval Contamination Defenses]] — related (held-out answers behind a leaderboard)
- [[AgentBench]] — alternative-to (closed-environment agent evaluation)
- [[Alita]] — related (a generalist agent reporting GAIA validation results)
- [[Deep Research Agent Systems]] — related (search agents that report GAIA scores)
- [[WebThinker Deep Research Agent]] — related (reports GAIA results)
