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

Live tools return answers that drift, so a stored answer goes stale. The benchmark instead executes a reference agent, following a plan that humans validated, concurrently with the tested agent, and an LLM judge compares the two outputs. The authors contrast this with subjective rubric scoring: the judge checks the agent's output against the reference output. The plans took about 120 expert-hours and every task was checked across a minimum of three runs.

Task success rate (TSR) counts a task as solved when the result gets the top Likert score of 5. The paper also reports an average result score (ARS), an average trajectory score (ATS, the 1-5 trajectory Likert normalised as (score-1)/4), and token cost as output tokens summed over rounds.

## Results (self-reported)

Setup: 18 LLMs (21 table rows counting extended-thinking variants), 101 tasks, ReAct, at most 30 rounds, 15 MCP servers available per task (76 to 125 tools), and GPT-4.1 judging; one run per model in the main table.

- GPT-5 had the highest TSR, 58.42%; o3 was next with 46.53%, then GPT-5-mini with 43.56%.
- GPT-5 scored 86.67% on Easy, 56.67% on Medium and 39.02% on Hard.
- The best open-source model, Qwen3-235B-A22B, got an overall TSR of 22.77% (ARS 42.57%), falling to 4.88% TSR on Hard tasks; Llama-3.1-8B reached 0.99%.
- **Failure mix**, counted over all 101 tasks, one run per model: the biggest category was semantic parameter errors, at 41.6% for GPT-4.1-mini and 16.8% for GPT-5. Syntactic errors hit 48.5% for Llama-3.3-70B and 0.0% for GPT-5. The paper names seven subtypes: output parsing errors, the syntactic and semantic parameter errors, and four behavioural ones (ignoring a requirement, overconfident self-solving, unproductive thinking, choosing the wrong tool).
- **Judge agreement**: blind experts using the same rubric compared with the judge on 30 tasks (10 per tier) and 6 models, and the quadratic-weighted Cohen's kappa exceeded 0.85 for results and 0.78 for trajectories. Replacing the judge with Claude-4-Sonnet or Gemini-2.5-Pro, across all 101 tasks, moved TSR by a standard deviation between 0.57 and 1.14.
- **Stability**: 6 models were run three times each; GPT-5's three TSRs were 58.33, 56.67 and 58.33, with SD 0.96.
- **Round budget**: with 6 models, TSR rose from 15 to about 25 rounds and then flattened (15, 20, 25, 30 and 50 tested). Enlarging the pool of distractor servers from 6 to 15 hurt weaker models, whereas GPT-5 and Claude-4.1-Opus (extended thinking) barely changed.

## Limits

Only 6 models went through the 3-run check, and its percentages (for example 56.67 and 43.33) are all multiples of 1/60, something 101 tasks cannot yield, and GPT-5's run-1 value of 58.33 differs slightly from 58.42 in the main table; the extraction says to treat the SD claim with caution. The reference agent and the judge are both GPT-4.1, and only 6 models were cross-judged. Because the tasks have objectively checkable answers, the paper itself says the judge's job is mostly formatting; how it copes with open-ended output is untested. The plan is a reference, not the only valid path, and trajectory scoring is an LLM Likert score with no step-level match. Tiers come from author consensus. Models are from August 2025, so rankings have aged. There is no dollar-cost or latency claim.

## See Also
- [[MCP Protocol]] — related (the tool protocol the benchmark's agents use)
- [[LLM-as-Judge Evaluation]] — related (a judge validated against humans and other judges)
- [[Trajectory Over Outcome]] — related (scores both result and trajectory)
