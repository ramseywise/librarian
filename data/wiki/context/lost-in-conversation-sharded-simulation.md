---
title: Lost in Conversation (Sharded Multi-Turn Simulation)
tags: [context, concept]
summary: "A 2025 simulation splits single-turn tasks into one-fact shards revealed turn by turn; across 15 LLMs and six tasks average performance fell 39%, mostly through unreliability rather than lost aptitude, and recap or lower temperature did not close the gap (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-laban-2025-llms-get-lost-multi-turn.md
---

# Lost in Conversation (Sharded Multi-Turn Simulation)

The paper asks how much LLM performance drops when a task's requirements arrive gradually across turns rather than as a single complete instruction. Its method is sharding: a single-turn instruction from a benchmark is split into shards that each carry one fact, with the first stating the high-level intent. A simulated user, itself an LLM (GPT-4o-mini), gives out one shard each turn to the assistant being tested; whenever it attempts an answer, the benchmark's own metric scores it. The same instructions run three ways, FULL (one turn), CONCAT (all shards listed in one turn) and SHARDED, ten times each.

Two metrics split the result. Aptitude (A90) is the 90th percentile score on an instruction, a best-case measure. Unreliability (U90_10) is the difference separating the 90th-percentile score from the 10th.

## Results (self-reported)

Main setup: 600 sharded instructions over six tasks (math, summary, code, database, actions and data-to-text), 15 LLMs, N=10 simulations per model and type, temperature 1.0.

- Every model scored lower on every task going from FULL to SHARDED, 39% lower on average. Average single-turn performance fell to 65% from 90%.
- CONCAT stayed near FULL, so the drop is not from information lost in sharding.
- Aptitude fell about 16% on average, while unreliability more than doubled: for every model, the best and worst of ten multi-turn runs on a single instruction were roughly 50 points apart.
- Reasoning models (o3, DeepSeek-R1) degraded like the others, with longer responses. Smaller models lost more under CONCAT.
- Gradual sharding (GPT-4o and GPT-4o-mini only, 1 to 8 shards, 10 simulations each): the loss was triggered by any conversation containing at least two turns where the task was underspecified; giving everything in one shard was the only effective fix.
- Remedies, tested on GPT-4o and GPT-4o-mini over code, database, math and actions: for GPT-4o, SHARDED scored 59.1, with a final-turn recap (RECAP) 76.6, restating all revealed shards every turn (SNOWBALL) 65.3, and FULL 93.0. Both recovered only part of the loss.
- Temperature 0 (40 instructions, 20 runs per condition) cut single-turn unreliability by 50-80% but barely helped SHARDED; about 30 points of unreliability remained.

## Observed behaviours

These come from log analysis and the authors state the causes as hypotheses.

- Conversations whose first answer attempt came in the last 20% of turns scored double the conversations that answered within the first 20% (code and math, all 15 models; observational binning).
- Final SHARDED answer attempts were 20-300% longer than FULL or CONCAT ones ("answer bloat"); lower scores accompanied longer assistant responses on five of the six tasks.
- In eighth-turn summaries, 20% of citations pointed at turn-8 documents against 8% for turns 2 and 3 (summary task).
- Translation did not degrade when sharded; the authors call it episodic, since each shard adds sentences to translate.
- The authors propose a target of multi-turn unreliability below 15 at temperature 1.0 (a proposal, not a measurement).

## Limits

- The user is fully simulated, and the authors say the conversations do not represent real human-AI exchanges and that the drop probably understates real unreliability. Shards are minimal and arrive singly, which the authors admit may look adversarial.
- Analytical tasks only, English text only. Explanations of the drop are correlational readings of logs.
- Remedies and temperature tests used only GPT-4o and GPT-4o-mini. The work reports no confidence intervals or significance tests, with only N=10 in each cell.
- The closed-API snapshots from 2024-2025 have since been superseded. Internal inconsistencies noted by the extraction: the gradual-sharding sample size is given as 31 instructions in one place and 8, 31 and 248 in another appendix; Table 1 column headers are scrambled, so the Gemini 2.5 Pro cell (97.4 FULL code, 68.1 SHARDED) relies on an inferred column order; and the summary-task analysis says 15 models while two models have no summary scores.

## See Also
- [[Context Failure Modes]] — prerequisite-for (distraction and rot over long sessions)
- [[Simulated User Evaluation]] — related (an LLM plays the user; this paper's shard-revealing user is one such design)
- [[Long-Context Prompting]] — related
- [[Memory-Augmented Conversational RAG]] — related (underspecified multi-turn queries)
- [[Spider Text-to-SQL Benchmark]] — related (source of the database tasks)
