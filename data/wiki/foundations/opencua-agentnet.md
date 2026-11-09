---
title: OpenCUA and AgentNet
tags: [foundations, pattern]
summary: "OpenCUA is an open recipe for desktop computer-use agents built on AgentNet, a 22,625-task human-annotated trajectory set, with reflective long chain-of-thought synthesized per step; the 72B model reaches 45.0% on OSWorld-Verified at 100 steps (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wang-2025-opencua.md
---

# OpenCUA and AgentNet

OpenCUA (NeurIPS 2025, XLANG Lab and collaborators) is an open framework for training vision-language computer-use agents with supervised fine-tuning only (no reinforcement learning). It has three parts: a capture tool for annotators' own machines, the AgentNet dataset, and trained models.

## AgentNet

22,625 human-annotated tasks across three operating systems (about 12K Windows, 5K macOS, 5K Ubuntu), 140+ applications and 190 websites, averaging 18.6 steps. Tasks need over 15 steps to be accepted. Annotation took 6 months, about USD 20,000 for 634 part-time annotators, plus USD 0.6 per task for chain-of-thought synthesis with a proprietary model; the paper totals about USD 32,000. The action space is a PyAutoGUI subset with coordinates normalised to 0-1. A separate offline benchmark, AgentNetBench, uses 100 held-out Windows and macOS tasks with several valid actions per step.

## Recipe

- Direct fine-tuning on state-action pairs alone gave 4.4% on OSWorld (Qwen-based 27K-trajectory base recipe).
- **Reflective long CoT:** a reflector, generator and summarizer pipeline writes a thought for each step, including error checks. On Qwen2-VL-7B with 17K trajectories, OSWorld at 15 steps went from 11.5 to 15.3 against short CoT.
- Mixed L1/L2/L3 reasoning formats in training beat L2 only (18.5 vs 13.1); at inference L2 (thought plus action) scored 18.5 against 16.9 for L1 and 17.6 for L3, contrary to earlier systems the paper cites.
- Default history is action text plus 3 screenshots; going from 3 to 5 images added about 3K context tokens for little gain.
- Two training stages (250B then 16B tokens for the 72B), with general text data at 35% of the mix giving a small gain.

## Results (self-reported)

OSWorld-Verified, average of 3 runs, 1920x1080, L2 inference, temperature 0: OpenCUA-72B 39.0 / 44.9 / 45.0 at 15 / 50 / 100 steps; OpenCUA-32B 29.7 / 34.1 / 34.8; OpenCUA-7B 24.3 / 28.1 / 26.6. For comparison in the same table, Claude 4 Sonnet 31.2 / 43.9 / 41.5, OpenAI CUA 26.0 / 31.3 / 31.4, and UI-TARS-72B-DPO at 24.0, 25.8 and 27.1; Claude Sonnet 4.5 reaches 61.4 at the 100-step setting. Pass@3 for the 72B is 53.2 (OpenCUA-32B: 34.2 to 45.6). On OpenCUA-Qwen2-7B at temperature 0, Pass@16 was 38.60 against 20.10 for Pass@1 at 50 steps.

Data scaling (Qwen2-VL-7B): combined OSWorld rose from 9.8 to 18.5 when adding Windows and macOS data to Ubuntu data. Grounding: 72B gets 60.8 (ScreenSpot-Pro) and 37.3 (UI-Vision). On AgentNetBench the 32B scores 79.1 against 73.1 for OpenAI CUA.

## Limits

- Scale is bounded by human annotation, and annotators are not experts; consent requirements bring selection bias.
- The reflective CoT depends on a proprietary teacher, and the 72B also used 8k rollouts from other proprietary systems, so the open recipe is not fully open.
- Online variance is high (Pass@1 against Pass@16 differs by over 18 points even at temperature 0); ablations are single runs on 7B models with no confidence intervals.
- Proprietary models still lead (Sonnet 4.5 at 61.4 against 45.0), and its comparison rows come from different sources and step limits.
- Authors list failure modes: missing application knowledge, imprecise grounding, repeated actions, wrong termination, long tasks of 30-50+ gold actions, and weak error recovery.
- Desktop and screenshot only; no latency or safety evaluation.
- Extraction notes mislabelled table references and a comma typo in one number.

## See Also

- [[Computer Use Visual Grounding]] — prerequisite-for
- [[UI-TARS Native GUI Agent]] — alternative-to (native-model training with online reflection and DPO)
- [[Post-Training for Agents]] — prerequisite-for
- [[ComputerRL API-GUI Agent RL]] — related (reinforcement learning on the same benchmark family)
