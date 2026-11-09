---
title: ScienceWorld Benchmark
tags: [eval, agents, benchmark]
summary: "ScienceWorld is an interactive text environment of 30 elementary-science tasks over a simulator with thermodynamics, circuits, chemistry and biology; five trained agents averaged between 0.05 and 0.17 on unseen variations, and a 1.5M-parameter interactive agent beat 11B models trained on static data (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-wang-2022-scienceworld.md
---

# ScienceWorld Benchmark

A text environment built to ask whether agents can carry out elementary-science experiments or only retrieve answers seen in static training. The simulator (Scala and Python) has ten locations, as many as 200 object types and 25 actions, driven by engines for heat, electric circuits, chemical reactions and living things. There are 30 task types over 10 topics from the elementary curriculum, with 7,200 parametric variations split 50, 25 and 25 percent into train, development and test. Scores are normalised to 0 to 1. Some tasks are forced choice: the agent answers by placing an object in an answer box.

## Reported results

Setup for all rows: 30 subtasks, unseen test variations, zero-shot, scores averaged over tasks, 5 seeds except where noted. All numbers are self-reported.

| Agent | Average score |
|---|---|
| DRRN (1.5M parameters, interactive training) | 0.17 |
| KG-A2C | 0.11 |
| Behaviour-cloned 11B T5 | 0.08 |
| Text Decision Transformer 11B | 0.08 |
| CALM (GPT-2, 3 seeds) | 0.05 |
| Random valid action | 0.03 |

- The small agent trained interactively for 100k steps beat the 11B models trained statically on science QA and expert demonstrations. The two 11B models used 211,092 and 224,902 training examples. The comparison had the interactive agent use the simulator's valid-action list, with the T5 outputs filtered against the same list.
- Science-QA pretraining (Macaw-Large) beat general T5-Large, and 770M models beat 11B models by roughly a factor of two: 0.17 against 0.08 for behaviour cloning and 0.15 against 0.08 for the decision transformer.
- The easiest task (find a non-living thing) was solved best by the random-valid baseline at 0.63, above DRRN at 0.56. Every agent scored near zero on the open-ended task of causing any change of state (DRRN 0.03). On the paired conductivity tasks DRRN scored 0.20 on the unnamed substance and 0.07 on the named one, which the authors use to contrast experimenting with retrieving.
- The authors compare the top agents to performance with its reading of mid-difficulty interactive fiction such as Zork.

## Limits

- Apart from two agents, all depend on the simulator's check for valid actions at test time, which makes action search easier.
- Descriptions are kept short for sequence-length reasons and fidelity is elementary level (series circuits only, staged biology). Oracle trajectories cover canonical solutions only.
- The model-size comparison is only suggestive, since hyperparameter differences are not ruled out. CALM ran with three seeds, and a minor prompt mistake was left uncorrected (a pilot suggested an effect of about 0.01 either way). Agents trained on a single subtask per run; no significance tests.
- Agents are 2022-era RL and fine-tuned transformer agents, not prompted large language models.

## See Also
- [[Text-Game Agent Environments (Jericho, ALFWorld, CALM)]] — related (closest environments)
- [[World Knowledge Model for Agent Planning]] — related (reports ScienceWorld results)
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[AgentBench]] — related
