---
title: AgentBench
tags: [eval, reference]
summary: "A 2023 benchmark of eight interactive environments for LLMs as agents, scoring 29 models at temperature 0; gpt-4 had the top overall score and Task Limit Exceeded was the most common failure cause (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-liu-2023-agentbench.md
---

# AgentBench

AgentBench (Liu et al., ICLR 2024, arXiv 2308.03688) evaluates LLMs acting in eight interactive environments in three grounding types (OS, Database, KG, Digital Card Game, Lateral Thinking Puzzles, House Holding, Web Shopping, Web Browsing), wrapped in a server-client toolkit. It has 269 dev and 1,014 test items. Its Web Shopping environment uses [[Web Agent Benchmarks (WebShop and Mind2Web)]] data, and its House Holding environment uses ALFWorld.

## Results (self-reported)

Setup: the Test split; 29 LLMs across 8 environments; chain-of-thought prompting in a Thought+Action format with one example; temperature 0; one run per model; every open-source model is 70B or smaller.

- API-based models average far above open-source models on the overall score. The best open-source model, codellama-34b, is still below gpt-3.5-turbo.
- gpt-4 (0613) has the top overall score and reaches 78% on House Holding. It is best on 6 of 8 datasets; claude-3 is best on Database (51.7) and gpt-3.5-turbo on Web Shopping (64.1).
- Code tuning looked helpful on Web Shopping, where codellama-34b scored far above llama-2-70b, and harmful on Digital Card Game, where it scored below it. The vicuna-13b model, aligned on ShareGPT, beat llama-2-13b from the same base; llama-2-13b and llama-2-70b scored about the same, and a re-run left that unchanged.

## Why runs fail

The paper sorts non-completions into four outcomes: Context Limit Exceeded (the history outgrows the context), Invalid Format (the agent ignores the format instruction), Invalid Action (the format is right but the chosen action is not valid) and Task Limit Exceeded (TLE: no solution by the round cap, or repeated generations).

- TLE is the predominant cause, shares averaged over models per environment; it is highest in Lateral Thinking Puzzles, while Invalid Format dominates in Database.
- Pooled by model type across environments, open-source models complete fewer tasks and have more Invalid Format and Invalid Action outcomes; TLE is 36.9% for open-source and 24.9% for API models.
- Most TLE trajectories contain repeated responses (two of the last 10 responses with Rouge-L at least 0.8, on trajectories cut to 3,500 tokens) and are much longer than completed ones. Completed trajectories are short: a median of 6 rounds and about 1,850 tokens.
- A small batch re-annotated with Claude-2 gave gpt-4 and gpt-3.5-turbo a comparable pattern on Database.

## Limits

One run per model at temperature 0, with no variance reported. Only simple chain-of-thought prompting was tried (no ensembles, reflection or search). Open-source models stop at 70B for compute reasons. The Lateral Thinking Puzzles judge is more lenient than humans. Datasets are small (20 test items for Digital Card Game, 50 for Lateral Thinking Puzzles), and the test sizes in Table 2 disagree with the appendix counts: KG is 500 against 150, Web Shopping 500 against 200, Web Browsing 912 against 100 and House Holding 134 against 50. claude-3 and glm-4 were scored after the task weights were fixed. Models are mid-2023 versions.

## See Also
- [[Web Agent Benchmarks (WebShop and Mind2Web)]] — related (two of its environments' sources)
- [[InterCode]] — related (concurrent interactive Bash and SQL evaluation)
- [[Eval Failure Taxonomy]] — related
- [[Holistic Agent Leaderboard (HAL)]] — related (agent evaluation across many benchmarks)
- [[Text-Game Agent Environments (Jericho, ALFWorld, CALM)]] — related (the ALFWorld environment behind House Holding)
