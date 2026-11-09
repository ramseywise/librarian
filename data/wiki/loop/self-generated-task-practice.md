---
title: Self-Generated Task Practice
tags: [loop, concept]
summary: "Two agent-training recipes have the model invent its own practice tasks and train on the outcomes: PAE scores them with a VLM judge, and Self-Challenging agents write a code-defined verifier for each task; both report gains and both depend on how good the task checker is."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-zhou-2024-proposer-agent-evaluator-pae.md
  - data/raw/papers/2026-11-06-zhou-2025-self-challenging-language-model-agents.md
---

# Self-Generated Task Practice

When no labelled tasks exist, an agent can propose tasks, attempt them and learn from the results. The open question is who says whether an attempt succeeded.

## PAE (Proposer-Agent-Evaluator)

A frozen VLM proposes web tasks from a website's name or from user demonstrations, a LLaVa-1.6 agent attempts them in a browser, a frozen VLM judges the last three screenshots plus the answer as 0 or 1, and Filtered BC (imitating the thoughts and actions of successful trajectories) updates the policy each iteration. Reported (self-reported, WebVoyager across 13 websites, Claude 3 Sonnet as proposer and evaluator): LLaVa-34B reached 33.0% against 22.6% for the previous open-source best, Qwen2VL-72B, and a 7B model matched a 34B model that had only supervised fine-tuning. On 85 unseen websites the 34B model scored 21.4% against 16.1% for SFT. Outcome-based evaluation beat step-based evaluation in an ablation. The autonomous evaluator disagreed with human labels at 8.6% of instances.

## Self-Challenging agents (CaT)

The same model acts as challenger and executor. The challenger writes a task as Code-as-Task: an instruction, a verification function, a reference solution and failing cases, and a task is kept only if the verifier accepts the solution and rejects the failures. The executor trains on its own successful rollouts by rejection fine-tuning. Reported (Llama-3.1-8B, 800 synthetic tasks and 12k rollouts per environment, evaluated on M3ToolEval and Tau-Bench): average Pass@1 rose from 12.0 to 23.5 against 12.9 for a PAE baseline in that paper (self-reported). Share of generated tasks that survived each filter was 47.7% with verification only, 9.5% adding the solution check and 5.2% for the full recipe, so the checks that remove false positives also discard most tasks. Solution-only checks made verifiers lenient.

The shared lesson is that the quality of the practice signal sets the ceiling.

## Limits

- PAE: open-source VLMs hallucinate too much to judge, so the headline relies on Claude 3 Sonnet; gains are measured over an SFT warm start that itself uses Claude trajectories; no seeds, variance or significance tests; websites change over time; web navigation only; Claude 3.5 Sonnet still scores 50.5% on WebVoyager.
- CaT: one pass of the loop, no variance reported, a 4-task evaluation, and the full-recipe pass rate is given as 5.2% in one figure and 5.3% in another. The extraction also notes the text's "two-fold" claim against a 95.8% figure.
- The two papers' numbers use different base models and benchmarks and are not comparable.

## See Also
- [[Oracle-Gap Recovery by Selection]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
- [[Evaluator Exploits in Discovery Loops]] — related
- [[Learned Skill and Action Libraries]] — alternative-to (stores artifacts instead of training weights)
