---
title: UI-TARS Native GUI Agent
tags: [foundations, pattern]
summary: "UI-TARS trains one vision-language model on screenshots to emit thoughts and keyboard-mouse actions, replacing prompted agent frameworks; the 72B DPO model reports 24.6 on OSWorld at 50 steps against 22.0 for Claude Computer Use (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-qin-2025-ui-tars.md
---

# UI-TARS Native GUI Agent

UI-TARS (preprint) is a "native agent model": workflow knowledge sits in one end-to-end model that perceives screenshots, reasons and acts, instead of a framework of prompted modules around a commercial model.

## Training

Qwen-2-VL at 2B, 7B and 72B is trained on about 50B tokens in three phases: continual pre-training on perception, grounding, action traces and reasoning data for GUIs; annealing, giving UI-TARS-SFT; and DPO on reflective pairs from online bootstrapping across many virtual machines, giving UI-TARS-DPO. Reasoning data covers about 6M GUI tutorials with thought augmentation. At each step the model sees the last N=5 observations plus its full thought and action history, then writes a thought and an action from a unified cross-platform action space. Reflection tuning trains on errors the model made online, with annotators supplying corrections, using only the corrected steps. The paper contrasts "system-2" reasoning (explicit intermediate thoughts) with direct "system-1" action output.

## Results (self-reported)

- OSWorld, screenshot only: 72B-DPO scores 24.6 at 50 steps against 22.0 for Claude Computer Use, and 22.7 at 15 steps against 14.9. At 15 steps: 7B-DPO 18.7; 7B-SFT 17.7; 72B-SFT 18.8.
- AndroidWorld (live emulator): 72B-SFT 46.6 against 44.8 for GPT-4o with Aria-UI.
- Grounding: ScreenSpot-Pro average 38.1 for 72B (UGround-V1-7B 31.1, OS-Atlas-7B 18.9, GPT-4o 0.8); ScreenSpot 89.5 for 7B and 88.4 for 72B; ScreenSpot-V2 91.6 for 7B and 90.3 for 72B.
- VisualWebBench 82.8 for 72B (GPT-4o 78.5, Claude-3.5-Sonnet 78.2).
- Multimodal Mind2Web cross-task step success 68.6 for 72B (Aguvis-72B 64.0); AndroidControl-High success 74.7; GUI Odyssey success 88.6.
- On 7B with best-of-N sampling, explicit reasoning trails direct action at N=1 on in-domain benchmarks and leads at N=16 and 64; on AndroidWorld, outside the training mix, it leads already at N=1 (values only in a figure).

## Limits

- No hyperparameters, compute, annotated-trace counts or bootstrap rounds are given, so the training cannot be reproduced from the paper.
- Only OSWorld uses the DPO model; other benchmarks use the SFT model. DPO gains are from OSWorld only (7B from 17.7 to 18.7; 72B from 18.8 to 22.7, at 15 steps).
- AndroidControl, Mind2Web and GUI Odyssey sit inside the training mix, so they count as in-domain; baseline figures appear copied from other papers with no discussion of protocol parity.
- The ScreenSpot results do not separate 7B from 72B, which the authors suggest means those benchmarks lose resolution at scale.
- OSWorld numbers date from January 2025 and later releases supersede them.

## See Also

- [[Computer Use Visual Grounding]] — prerequisite-for
- [[OpenCUA and AgentNet]] — alternative-to (open data recipe, supervised only)
- [[Post-Training for Agents]] — prerequisite-for
- [[GUI Agent RL with GUI-R1 and ARPO]] — extends (ARPO starts from a UI-TARS model)
- [[ReAct Pattern]] — prerequisite-for
