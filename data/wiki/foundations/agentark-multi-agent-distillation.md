---
title: AgentArk Multi-Agent Distillation
tags: [foundations, pattern]
summary: AgentArk distils five-agent debate trajectories into a single student model by three routes (RSFT, DA, and PAD with a PRM and GRPO); the authors report about 4.8% average gain for a single agent, but most Qwen3-8B gains are under one point (self-reported, single runs).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-luo-2026-agentark.md
---

# AgentArk Multi-Agent Distillation

Luo et al. (CMU and collaborators, arXiv 2602.03955 v3, May 2026 preprint) move the cost of
multi-agent debate to training time. Five debating agents and a summarizer run up to three rounds
on 342k questions (about 2M trajectories); a 72B model filters for correctness and judges diversity.
The paper leaves tool use and memory outside its scope.

## Three methods

- **RSFT** fine-tunes on correct reasoning trajectories from the debate.
- **DA** trains on several diverse correct trajectories per problem and drops
  problems with fewer than two correct agents.
- **PAD** trains a PRM with a contrastive loss and uses
  its step scores as the advantage in GRPO. About 20 hours on 8 H100s, against about 6 and 8 hours on
  one H100 for RSFT and DA.

## Results (self-reported)

Setup: the teacher is Qwen3-32B; the students are three Qwen3 sizes (8B, 1.7B, 0.6B), Gemma-7B and Llama3-8B-Instruct; the data are GSM8K, MATH,
MedMCQA and MetaMathQA; 120 experiments in all, and each cell looks like a single run.

- Headline: single-agent improvement of about 4.8% on average and slightly below the vanilla debate. No table
  gives that average, and the extraction contains no table of the debate baseline numbers.
- In-domain gains were larger than out-of-domain: best cells 30% against 7%, averages 4-6% against 1-3%.
- PAD was the most consistent; RSFT and DA swung widely (DA on Qwen3-0.6B reached 53.37 from 41.93 on
  GSM8K, while RSFT dropped to 21-39 in some cells). PAD gains on Qwen3-8B were often under 1 point
  from a base of 88.17.
- Plain answer-only SFT on GSM8K often hurt (Qwen3-8B 81.35 against 88.17).
- Reasoning judged by an LLM (Qwen3-0.6B student, 100 GSM8K samples): coherence scored 1.88 for the single agent, 2.25 for
  RSFT, 3.07 for DA and 3.96 for PAD. The extraction notes PAD did not top every metric (DA led step
  decomposition and error localisation). RSFT and DA had lower perplexity.
- More than 5 debate agents gave no gain for the 0.6B student; PRM size changed
  GSM8K by 0.07 points for an 8B policy; the authors say reasoning quality, not data volume, limits
  small students.

## Limits

- Authors concede a subset of reasoning benchmarks, one set of pipelines and mostly homogeneous agents.
- The extraction notes no seeds, variances, significance tests, inference-cost table, or matched-data
  comparison with simpler baselines. It also notes that the headline is dominated by weak students and
  MetaMathQA-trained rows, and that process labels derive from debate agreement and answer correctness, which could let the
  PRM entrench majority mistakes. The authors themselves warn students may inherit flawed reasoning.
- Internal inconsistencies noted by the extraction notes: one figure is labelled MedMCQA with a GSM8K axis;
  the self-distillation comparison text ("+0.99% vs +1.62%") is garbled and states no setup; the
  paper claims PAD is best on every metric, which its own table contradicts.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[On-Policy Distillation]] — related (distilling into a student)
- [[Chain-of-Agents AFM Distillation]] — alternative-to (another multi-agent-to-single-model route)
- [[DualDistill Agentic-R1]] — related
- [[Compiling Workflows into Weights]] — related (distilling a workflow into one small model)
