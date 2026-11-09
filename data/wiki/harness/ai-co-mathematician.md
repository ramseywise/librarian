---
title: AI Co-Mathematician
tags: [harness, pattern]
summary: "The AI co-mathematician is a multi-agent research workbench over Gemini 3.1 Pro with no custom training; it reports 23 of 48 (48%) on FrontierMath Tier 4 against 19% for the base model (self-reported), and names false consensus and non-terminating review loops as failure modes."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-zheng-2026-ai-co-mathematician.md
---

# AI Co-Mathematician

A 2026 preprint describes an interactive workbench for open-ended mathematics research. It is a harness around Gemini 3.1 Pro, not a trained model: a project coordinator splits a question into parallel workstreams, each run by sub-agents; review loops check the output and escalate when a workstream stalls; results accumulate in a LaTeX working paper; and failed paths are kept in the record instead of discarded.

## Results (self-reported)

- **FrontierMath Tier 4.** 23 of 48 problems solved (48%), against 19% for the base model. Epoch AI ran the evaluation blind, scoring only the final answer, with up to 48 hours per problem, using the system's own tools and no token cap. Three problems were newly solved by any system and two were missed.
- **Internal benchmark.** On a 100-problem set the authors built, scores of 57%, 70% and 87% are read from a figure image only, so the exact configurations behind each bar are not confirmed from text.
- **Case studies.** The paper describes worked cases, including one on a Kourovka notebook problem (21.10), reported as the authors' own account.

## Limits

- Not compute-matched: the harness uses far more inference than the base model it is compared with, so the 48% against 19% gap mixes architecture and compute.
- The extraction notes no ablation of coordinator, review loops or kept failed paths, and no variance across runs.
- The internal benchmark is private; access to the system is limited.
- Authors report false consensus (reviewers agreeing on a wrong result) and a non-termination "death spiral" in review loops.

## See Also

- [[AI Scientist Automated Research Pipeline]] — related (another autonomous research harness)
- [[Verification Loops]] — related
- [[Multi-Agent Failure Modes at Scale]] — related (false consensus)
- [[Agent Laboratory and mle-solver]] — related
