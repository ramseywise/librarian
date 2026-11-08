---
title: InterCode
tags: [eval, reference]
summary: "A 2023 gym-style framework that wraps Bash, SQL and Python execution so an LLM can retry with execution feedback; on Spider SQL, GPT-4 rose from 9.1% single-turn to 73.7% with Try Again (self-reported), though the retry loop sees the reward computed against the gold answer."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-yang-2023-intercode.md
---

# InterCode

InterCode (Yang et al., NeurIPS 2023 Datasets and Benchmarks, arXiv 2306.14898) asks whether giving a coding LLM execution feedback over several turns beats one-shot generation, and provides a standard way to test it. It runs code in Docker as a gym-style POMDP: the code is the action, the execution output is the observation, and the reward lies in [0,1]. It builds Bash (NL2Bash), SQL (Spider) and Python (MBPP) environments; seven LLMs were prompted with no training. The strategies are Single Turn, Try Again (retry with the execution output and reward until the reward is 1 or n turns pass), ReAct, and Plan & Solve.

## Results (self-reported)

Setup: InterCode-SQL is Spider 1.0 dev, 1,034 tasks, MySQL, zero-shot, temperature 0, observations capped at 1,000 tokens. InterCode-Bash is 200 NL2Bash-derived tasks over four file systems. Try Again uses n=10 with the reward shown in each observation. One run per configuration.

- GPT-4 SQL success went from 9.1% single turn to 73.7% with Try Again; gpt-3.5-turbo went from 10.5% to 47.3%.
- On Bash the gain was smaller: GPT-4 34.0% to 48.5%, gpt-3.5-turbo 34.5% to 46.5%.
- Weaker models gained little (chat-bison-001 Bash 17.7 to 19.2; StarChat-16B SQL 8.9 to 9.7).
- With gpt-3.5-turbo, ReAct beat Try Again on SQL (58.7% against 47.3%, in 5.30 turns against 7.25) but did far worse on Bash (20.5% against 46.5%). Plan & Solve scored 49.1% on SQL and 28.0% on Bash.
- Giving gpt-3.5-turbo the relevant schema in the prompt lifted single-turn SQL from 10.5% to 67.9%; Try Again still beat it, 72.8 to 67.9.
- On the first turn, 90.2% of gpt-3.5 SQL actions were not admissible (hallucinated tables or columns), falling to 46.4% on turn 2, where 60.3% of actions were SHOW TABLES or DESC.
- Success plateaus as turns grow; the authors observe that models repeat earlier actions and do not use recent observations.
- The authors themselves solved 13 of 15 random SQL tasks.
- ReAct and Plan & Solve solve overlapping but different tasks: of the tasks either solved, both solved 57% (407 of 708) on SQL and 27.6% (21 of 76) on Bash.

## Limits

Try Again feeds back a reward computed against the gold output and stops automatically at reward 1, while ReAct and Plan & Solve stop on the agent's own judgment. The extraction therefore reads the headline gains as retry against an oracle, not self-verification. The SQL single-turn baseline has no schema, and the schema ablation shows much of the SQL gain is information gathering. Only Bash and SQL were evaluated; the Python environment is built but not benchmarked. The paper states 100 CTF objectives in one section and just four task instances in its limitations. The Plan & Solve plus refine test used 44 tasks and the human baseline 15, both small. There is a single run per configuration at temperature 0, with standard errors only for Bash file systems 2-4. Models are 2023 versions.

## See Also
- [[AgentBench]] — related (concurrent interactive Bash and SQL evaluation)
- [[Verification Loops]] — related (feedback from execution)
- [[Repository-Level Coding Benchmarks]] — related
