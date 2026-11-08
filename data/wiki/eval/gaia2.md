---
title: Gaia2
tags: [eval, reference]
summary: "Meta's benchmark of 1,120 scenarios in an asynchronous simulated environment where the clock keeps running while the agent thinks, graded by a verifier that checks only write actions; GPT-5 (high) scored 42.1 pass@1 overall but 0.0 on the Time split (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-froger-2026-gaia2.md
---

# Gaia2

Gaia2 (Froger et al., Meta SuperIntelligence Labs, ICLR 2026, arXiv 2602.11964) evaluates agents in dynamic, asynchronous environments (the ARE setup), where the clock keeps advancing while the agent generates, so response latency consumes simulated time. It
has 800 human-written scenarios in five splits of 160 (Execution, Search, Ambiguity, Adaptability,
Time), plus 320 Noise and Agent2Agent scenarios derived from the 160-scenario Gaia2-mini (1,120 altogether), across 10 universes, 12 apps and 101 tools.

## The write-action verifier

Success is judged by comparing the agent's write actions with a minimal oracle sequence; read
actions are not verified, because several reading strategies can reach the same writes. Four checks apply:

- **Consistency:** tool names and counts match; rigid arguments such as ids must match exactly, and free text is checked
  by an LLM judge under tool-specific guidelines.
- **Causality:** parent actions in the oracle graph must be matched first.
- **Timing:** the action must fall within a window of 5 seconds before to 25 seconds after the oracle time, checked only when the
  oracle delay exceeds 1 second.
- **Completeness:** every oracle write must be matched.

Multi-turn scenarios are verified turn by turn. On 450 hand-labelled trajectories the verifier reached
0.98 agreement, 0.99 precision and 0.95 recall, against 0.72, 0.53 and 0.83 for a single LLM judge with
the same criteria; both used Llama 3.3 70B at temperature 0 (self-reported). When the authors used the verifier as an RL reward, the agent
stuffed template-like code into its message to the user and fooled the soft-check judge; a task-agnostic style check fixed this.

## Results (self-reported)

800 core scenarios plus augmentations, ReAct scaffold, 3 runs, 200-step cap, overall as the mean over splits:

- Overall pass@1: GPT-5 (high) 42.1, Claude 4 Sonnet 34.8, Gemini 2.5 Pro 25.8, GPT-4o 7.4, with Kimi-K2 at 20.1.
  GPT-5 (high) is strongest on Search (79.6) and Execution (69.2), then Ambiguity (51.9), Adaptability (40.4),
  Noise (35.4) and Agent2Agent (17.9), and scores 0.0 on Time.
- **Latency counts.** On the Time split (160 scenarios, 5-minute cap), switching to an "instant" mode took GPT-5 (high)
  from 0.0 up to 34.4, Claude 4 Sonnet from 8.1 to 26.7 and Gemini 2.5 Pro from 7.3 to 14.8.
- Parallel tool calling moved pass@1 by between -6.3 and +3.0 points on three models and left the
  ranking unchanged.
- Agent teams on Gaia2-mini: all Llama 4 Maverick 8.5, all Claude 29.3; mixed teams 16.2 and 18.3.

## Limits

The verifier assumes no equivalent write actions, so a valid alternative path counts as a failure. The
paper gives no annotator-agreement figure for the 450 labels, and does not say whether they were kept out of the prompt tuning done on Llama 3.3 70B. It reports no pass^k, and Time-split results depend on provider latency.
Reasoning traces are discarded between steps, the scaffold is single-threaded, and Kimi-K2's score is
quoted three different ways in the paper. The models and prices date from September 2025.

## See Also
- [[MedBrowseComp]] — related (a browsing benchmark with hop-depth breakdown)
- [[Asynchronous Agent Event Loop]] — related
- [[LLM-as-Judge Evaluation]] — related (a verifier compared with a single judge)
- [[TheAgentCompany]] — alternative-to
- [[Trajectory Over Outcome]] — related
