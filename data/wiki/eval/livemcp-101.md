---
title: LiveMCP-101
tags: [eval, reference]
summary: "A benchmark of 101 multi-step tasks over live MCP tools (41 servers, 260 tools) that grades an agent against a reference agent run at the same time; GPT-5 had the highest task success rate at 58.42% across 18 LLMs (self-reported), and semantic parameter errors were the largest failure type."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yin-2025-livemcp-101.md
---

# LiveMCP-101

LiveMCP-101 (Yin et al., arXiv 2508.15760) asks how well agents handle real, multi-step queries when the tools are live MCP servers. It has 101 tasks over 41 servers and 260 tools, in three tiers set by author consensus: 30 Easy, 30 Medium, 41 Hard.

## Dynamic ground truth

Live tools return answers that drift, so a stored answer goes stale. The benchmark instead runs a reference agent on a human-validated plan at the same moment as the tested agent, and an LLM judge compares the two outputs. The authors contrast this with subjective rubric scoring: the judge checks the agent's output against the reference output. The plans took about 120 expert-hours and each task was validated over at least 3 runs.

Task success rate (TSR) counts a task as solved when the result gets the top Likert score of 5. The paper also reports an average result score (ARS), an average trajectory score (ATS, the 1-5 trajectory Likert normalised as (score-1)/4), and token cost as output tokens summed over rounds.

## Results (self-reported)

Setup: 18 LLMs (21 table rows counting extended-thinking variants), 101 tasks, ReAct, a 30-round cap, a per-task pool of 15 MCP servers (76-125 tools), GPT-4.1 as judge; one run per model in the main table.

- GPT-5 had the highest TSR, 58.42%; o3 followed at 46.53% and GPT-5-mini at 43.56%.
- GPT-5 scored 86.67% on Easy, 56.67% on Medium and 39.02% on Hard.
- The best open-source model, Qwen3-235B-A22B, scored 22.77% TSR and 42.57% ARS overall and 4.88% on Hard; Llama-3.1-8B scored 0.99%.
- **Failure mix**, as a share of all 101 tasks from one run per model: semantic parameter errors were the largest type (16.8% for GPT-5, 41.6% for GPT-4.1-mini). Syntactic errors were 0.0% for GPT-5 and 48.5% for Llama-3.3-70B. The seven subtypes are ignoring a requirement, overconfident self-solving, unproductive thinking, wrong tool selection, syntactic errors, semantic errors and output parsing errors.
- **Judge agreement**: quadratic-weighted Cohen's kappa between humans and the judge was above 0.85 on results and above 0.78 on trajectories, on 30 tasks (10 per tier) and 6 models with blind experts. Swapping the judge among GPT-4.1, Claude-4-Sonnet and Gemini-2.5-Pro over all 101 tasks gave a TSR standard deviation of 0.57-1.14.
- **Stability**: three runs of 6 models; GPT-5 scored 58.33, 56.67 and 58.33 (SD 0.96).
- **Round budget**: with 6 models, TSR rose from 15 to about 25 rounds and then flattened (15, 20, 25, 30 and 50 tested). Growing the distractor pool from 6 to 15 servers hurt weaker models, while GPT-5 and Claude-4.1-Opus (extended thinking) stayed about flat.

## Limits

The 3-run check covers 6 models only. Its percentages (58.33, 56.67, 43.33, 23.33) are multiples of 1/60, which 101 tasks cannot produce, and GPT-5's run-1 value of 58.33 differs slightly from 58.42 in the main table; the extraction says to treat the SD claim with caution. The reference agent and the judge are both GPT-4.1, and only 6 models were cross-judged. The tasks are objectively checkable, so the paper itself says the judge mainly handles formatting; open-ended output is untested. The plan is a reference, not the only valid path, and trajectory scoring is an LLM Likert score with no step-level match. Tiers come from author consensus. Models are from August 2025, so rankings have aged. There is no dollar-cost or latency claim.

## See Also
- [[MCP Protocol]] — related (the tool protocol the benchmark's agents use)
- [[LLM-as-Judge Evaluation]] — related (a judge validated against humans and other judges)
- [[Trajectory Over Outcome]] — related (scores both result and trajectory)
