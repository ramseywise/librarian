---
title: AutoGym Blueprint-First Verifiable Gyms
tags: [foundations, llm, pattern]
summary: "AutoGym generates agent training environments from a blueprint that fixes the solution, requirements and verification before any environment exists, with ground truth computed by execution; moving only difficulty parameters raised a hard-task share from 10% to 39% (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-noronha-2026-autogym.md
  - data/raw/papers/2026-11-06-chen-2026-trainee-trainer.md
---

# AutoGym Blueprint-First Verifiable Gyms

AutoGym (Amazon AGI authors, a September 2026 preprint) generates tool-using environments with built-in difficulty control and verifiers. The aim is a gym that gives a learning signal: not uniformly easy, not uniformly hard.

## Pipeline

1. Seed with tools and a corpus; 2. initialise a blueprint (scenario, persona, parameters); 3. construct the blueprint; 4. materialise the environment; 5. assemble ground truth and a verifier; 6. evaluate and analyse failures.

- The blueprint pins down what counts as a solution and how to verify it before anything else; a follow-up check confirms that anything omitted from the prompt remains discoverable and that the available tools make a solution reachable.
- **Answerability invariant.** Ground truth is computed by running the blueprint's derivation against the built environment, not by trusting values the generator proposed; a separate pass checks for authoritative sources, distractor immunity and no equally defensible alternative.
- **Verifier.** Four signals (outcome, process, distractor resilience, personalisation); programmatic rules cover the deterministic parts, and a three-stage judge ends in a meta-judge that returns a reward plus a root-cause label (pass, environment failure, ambiguous, or agent error).
- **Difficulty parameters.** Topology tiers, seven capability axes, an obfuscation gradient and a distractor budget. Repair runs for at most three iterations, and only a defect in the environment or verifier starts it; a failing agent never does.
- **Curriculum.** Sampling weights shift when a capability's success falls below 0.30 or exceeds 0.80.

## Results (self-reported)

Setup: productivity gym with 7 tools, Sonnet-class generator, 8 rollouts per task, hard means verifier score below 0.30.

- Two configurations differing only in topology weights, obfuscation and distractors: hard share for an Opus-class model 10.0% against 39.0%; for gpt-oss-120b the second configuration made 70% of tasks hard.
- Against an expert-authored set (21.5% hard) and an automated-world-model baseline (4.0% hard).
- Failure-driven temporal gym: 92 tasks from 100; no task was harder for the stronger model than the weaker.
- Cost per task $2 to $5 at mid-tier prices against an estimated $500 to $1000 for expert authoring.
- A 500-step GRPO run on a 600-task gym with one 8B model showed rising reward, without numbers or held-out evaluation.

## Related approach (Trainee-to-Trainer)

A June 2026 preprint has a 4B policy act as its own environment engineer: after each GRPO round it reads failure evidence and revises the data, hole and wait ratios per map size of a fixed MAPF-FrozenLake generator, for three rounds on 2-agent instances. Setup: Qwen3-4B, evaluated on 3, 4 and 5 agents, 50 samples per map size, single runs. Valid/optimal rates (self-reported): 51.67/31.67 on 3 agents against 46.17/29.25 for the best frontier solver and 40.42/26.08 for GRPO on a random fixed configuration. The current checkpoint also beat the untrained base model as engineer (51.67 against 45.21 valid, 3 agents). Giving the engineer raw failure facts worked better than self-written summaries. The frontier models were compared only as solvers, never as engineers.

## Limits

- Trainee-to-Trainer covers a single task family and the extraction notes it says two epochs per round in the text but three in the appendix; no seeds, and gaps of a few points on 50 samples may be noise.
- The extraction notes that the prose gives 89.1% for the easy tier where Table 4 gives 89.2%. Two evaluated settings, two models, no seeds or intervals, eight rollouts.
- The generator and the frontier reference come from one family; no ablation against single-pass generation; the curriculum loop is demonstrated for a single round; the LLM certification audit has no human comparison; nothing shows that training on these gyms improves skills on held-out tasks.

## See Also

- [[Post-Training for Agents]] — prerequisite-for
- [[Parameterised Benchmark Instances]] — related
- [[DreamGym Synthetic Experience RL]] — alternative-to
- [[AgentScaler Environment Scaling]] — alternative-to
- [[FrogNano Online Task Synthesis]] — alternative-to
