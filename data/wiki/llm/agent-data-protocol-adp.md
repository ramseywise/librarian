---
title: Agent Data Protocol (ADP)
tags: [llm, agent-training, pattern]
summary: "A Pydantic schema that sits between raw agent-trajectory datasets and agent-specific SFT formats, turning dataset-times-harness conversion work into dataset-plus-harness; SFT on the mixed ADP data reports gains on coding, web and OS benchmarks (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-06-song-2025-agent-data-protocol.md
---

# Agent Data Protocol (ADP)

Agent Data Protocol (Song et al., ICLR 2026) starts from the claim that the problem is a lack of standardisation, not a lack of agent datasets. It defines one schema as an interlingua: each source dataset gets a converter into ADP, and each target agent harness gets one converter from ADP to its SFT format.

## The schema

A trajectory is an alternating list of actions and observations.

- Actions are API calls, code actions (with `language`, `content` and a `description` that holds the thought) or messages.
- Observations are text or web observations (`content`, `name`, and a `source` of user or environment).
- Every entry has an `id`, a `content` list and `details`.

## What was built

13 existing datasets were converted, 1.3M trajectories in all (ADP Dataset V1), with converters to three harnesses: OpenHands, SWE-Agent and AgentLab. Across datasets the average trajectory has 10.1 rounds (1.0 for Synatra to 26.8 for SWE-smith); the action mix is 53% API, 24% code and 23% message; the share of actions paired with a thought is 83.8% overall (0.0% for Mind2Web, 42.0% for SWE-Gym).

Mixing is by hand-set per-dataset multipliers (for example 0.001 for Orca AgentInstruct, 0.01 for Synatra, 3 for SWE-Gym, 2 for the AgentTuning subsets, 1 for the rest). The two coding harnesses (OpenHands, SWE-Agent) are trained on the non-web data, about 30K samples, and AgentLab on the web data, about 20K. SFT uses LLaMA-Factory.

## Engineering cost

Counting lines of code as the effort proxy, converting the 13 datasets took 4,892 lines and each ADP-to-SFT converter about 77 on average; by harness that is roughly 150 (OpenHands), 50 (SWE-Agent) and 30 (AgentLab). Extrapolated to 100 harnesses the paper gives 12,592 lines with ADP against 489,200 without (an extrapolation, not a measurement).

## Reported results (self-reported)

Setup: Qwen2.5-Coder-Instruct (7B, 14B, 32B) for coding, single runs, no seeds.

| SWE-Bench Verified | 7B | 14B | 32B |
|---|---|---|---|
| SWE-Agent, base to ADP | 0.4 to 20.2 | 2.0 to 34.4 | 2.2 to 40.3 |
| OpenHands, base to ADP | 2.8 to 20.4 | 5.8 to 30.6 | 10.6 to 36.8 |

- Other 7B gains: WebArena 4.5 to 21.0, GAIA 7.3 to 9.1, and AgentBench OS from 3.5 up to 27.1. The abstract's "about 20% average gain" is not computed in the body.
- Against single-dataset baselines (numbers copied from earlier papers, not retrained): 32B SWE-Agent 40.3 vs 40.2 for SWE-smith; 32B OpenHands 36.8 vs 20.6 for SWE-Gym.
- Cross-task: with 7-8B models, single-dataset training can leave a target near zero while ADP lifts it (GAIA 0.6 with AgentInstruct only vs 9.1 with ADP; SWE-Bench on Qwen2.5-7B-Instruct 1.0 with SWE-smith only vs 10.4). The authors say ADP avoids the negative transfer of single-domain tuning.
- Volume control: Qwen3-8B on OpenHands with about 30K samples per side gives 11.0 for up-sampled SWE-smith and 16.6 for ADP.

## Limits

- No ablation of the mixing weights or of any single dataset; the multipliers were set by hand with no search.
- Any one harness trains on a small slice (about 30K or about 20K trajectories), so the 1.3M total is not a training-set size.
- The matched-size control covers SWE-Bench only, against an up-sampled baseline.
- Baselines in the main tables come from other papers, so harnesses, prompts and bases may differ; some use other base models.
- No seeds or confidence intervals. GAIA gain at 7B is small (+1.8 points), with nothing reported at 14B or 32B.
- Text only. Quality assurance is automated format checks (for example an 80% threshold on tool calls paired with a thought); no filtering or deduplication study.
- SFT only, no RL.

## See Also
- [[AgentTuning and AgentInstruct]] — prerequisite-for
- [[Agent-FLAN Agent Tuning Data Design]] — related (task- or agent-specific unification of agent data)
- [[Post-Training for Agents]] — prerequisite-for
- [[AgentBench]] — related
- [[GAIA General-Assistant Benchmark]] — related
