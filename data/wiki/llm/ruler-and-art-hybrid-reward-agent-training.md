---
title: RULER and ART Hybrid Reward Agent Training
tags: [llm, agent-training, pattern]
summary: "RULER uses an LLM judge to rank an agent's trajectories relative to one another, and ART trains on those scores with GRPO-style group-normalised rewards; for verifiable tasks the chapter gates a RULER quality term behind a binary correctness check."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-ai-agents-definitive-guide-ch03-advanced-planning-reasoning-scalable-execution-a.md
---

# RULER and ART Hybrid Reward Agent Training

This is the book-chapter treatment of how an LLM agent can be trained when a reward cannot be hand-coded, from Koenigstein's *AI Agents: The Definitive Guide* (O'Reilly Early Release, chapter 3). Everything below comes from that one chapter, which gives worked examples and no controlled results.

## The pieces

- **Trajectory and rollout.** The chapter calls a trajectory the step-by-step record of an agent's path to its answer, and a rollout one full run of a task that yields one or more trajectories.
- **RULER.** A general-purpose reward function: an LLM-as-judge ranks several trajectories for the same task from 0 to 1 on goal completion and efficiency. The chapter advises it when rewards cannot be hand-coded, and it advises comparing several rollouts per task with group-normalised rewards instead of absolute scores.
- **ART.** An open-source framework that trains agentic LLMs from structured rollouts and is built on GRPO. GRPO compares several responses to one query, ranks them and learns from the relative ranking with token-level ratios and no critic; see [[Preference Optimization Algorithms]]. The chapter separately defines GSPO as a GRPO variant with a sequence-level, length-normalised importance ratio and clipping.
- **KL penalty.** The chapter advises adding one so the updated policy stays near the reference.

## The hybrid reward

For a verifiable task (the worked example is a Countdown arithmetic game), a deterministic reward checks correctness and RULER scores reasoning quality. The two are combined as a gated reward, `final_reward = gate * (alpha + beta * ruler_norm)`, where the gate is a binary correctness check. The chapter's weights are 0.7 on correctness and 0.3 on the RULER quality term. A different RULER example scores three mocked cat-poem trajectories with an o3 judge: good 0.9, mediocre 0.6, off-topic poem 0.05.

## The worked run (not an experiment)

Setup: Qwen/Qwen2.5-7B-Instruct on Countdown with ART's local backend; learning rate 1e-5, 64 scenarios, and per step 4 groups of 2 rollouts, for at most 3 steps. The chapter advises keeping ART training small while debugging. On the first 10 held-out scenarios, scored by the same hard judge, 8 are correct (two failures returned empty expressions). There is no pre-training baseline, so the number shows the pipeline running, not a gain.

## Related chapter material

- The chapter asserts, citing Zheng et al. 2025 and giving no data, that GSPO is markedly more stable than GRPO and requires no additional stabilisation for mixture-of-experts models.
- It points to rLLM, an open-source framework for training entire workflows such as solver-judge or planner-executor: the user subclasses Workflow, implements run() and returns an Episode.
- It frames test-time search, MCTS and AB-MCTS, as an alternative to scaling model size; see [[Adaptive Branching MCTS]]. Its AB-MCTS demonstration uses gpt-4o at temperature 0.7 as both generator and judge for 5 steps, so it shows mechanics and not gain.

## Limits

- This is Early Release text, described as raw and unedited; complete code lives in the book's notebooks and is not printed in the chapter.
- The Countdown run works as a smoke test only: few scenarios and steps, ten test items, and neither a baseline nor seeds.
- The GRPO versus GSPO comparison is asserted with no numbers.
- Table 3-5 gives GRPO a need for value-model surrogates in mixture-of-experts stability, although GRPO has no value model.
- One section heading says absolute scoring is easier, but the text under it argues that comparing trajectories relatively is easier.
- In the AB-MCTS demonstration the judge and the answer writer are the same model.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Preference Optimization Algorithms]] — prerequisite-for (GRPO)
- [[RL Training Frameworks for LLMs]] — related (other RL training backbones)
- [[Adaptive Branching MCTS]] — related (the test-time search half of the chapter)
