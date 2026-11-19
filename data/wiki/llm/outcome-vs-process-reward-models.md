---
title: Outcome vs Process Reward Models
tags: [llm, reinforcement-learning, comparison]
summary: "An outcome reward model scores the whole rollout and a process reward model scores each reasoning step. ORM is cheap but cannot tell a lucky guess from sound reasoning. PRM assigns credit better but needs step-level data, and in 2025 practice swung back to ORM with a light PRM used only for verification."
updated: 2026-11-19
sources:
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-22_rl_landscape.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
  - data/raw/papers/2026-11-07-lightman-2023-let-s-verify-step-step.md
  - data/raw/papers/2026-11-07-lambert-2024-tulu-3.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch04-alignment.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch05-inference.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch06-reasoning.md
---

# Outcome vs Process Reward Models

When RL is used to train reasoning, the reward model can score at two levels. Which one
you choose decides how credit flows back through a long chain of thought.

| | **Outcome Reward Model (ORM)** | **Process Reward Model (PRM)** |
|---|---|---|
| Scores | One scalar per *rollout*: was the final answer right? | One scalar per *reasoning step* |
| Training cost | Fast and simple | Slower; needs step-labelled data |
| Credit assignment | Coarse: every step gets the outcome's credit | Fine: catches the step where reasoning went wrong |
| Blind spot | Cannot separate sound reasoning that slipped at the end from bad reasoning with a lucky final answer | Labelling steps is expensive and the labels themselves can be wrong |

## The ORM blind spot

An ORM gives the same reward to a correct derivation and to a wrong derivation that lands
on the right number by accident. Over many updates, the policy is reinforced for whatever
correlates with right answers, including shortcuts. A PRM addresses this by rewarding the
steps directly. This is the same proxy problem as [[Reward Hacking and Overoptimization]],
moved from the response level to the step level.

## Why practice swung back to ORM

The 2025 picture in the source, reported with medium confidence, is that **ORM became
dominant again** for simplicity and scale. Two things made that possible:

- **Verifiable rewards.** For math and code, the outcome can be checked exactly (symbolic
  or numerical checking, running tests). A checked outcome is a much stronger signal than a
  learned outcome score, and it removes most of the reason to pay for step labels. This is
  the setting GRPO and DAPO are built for. See [[Preference Optimization Algorithms]].
- **Multi-trajectory majority voting.** At inference, sample 10–100 rollouts per prompt and
  take the majority final answer. The source reports significant accuracy gains over a
  single pass on competition math. Aggregating many outcomes recovers some of the
  robustness a PRM would provide, without step labels.

The emerging pattern is a **hybrid**. The ORM drives the training loop because it is
simpler, and a light PRM is used after inference for verification or confidence scoring.
The step-level signal moves out of the optimizer and into a checker. That is the same
maker/checker split described in [[Verification Loops]].

## The agent case

For multi-step agents, the same choice appears as **step rewards versus a binary outcome**.
Hand-designed per-step rewards (V-IRL navigation: +1 correct move, −1 wrong move, −1.5
landmark error) give easy credit assignment, but exploration is bounded by the designer's
bias. A binary success reward leaves exploration free at the cost of harder credit
assignment and more samples: SimpleVLA-RL used nothing else, took a robot-manipulation
task from 17.3% (SFT on one demo per task) to 91.7%, and discovered a grasp no human had
demonstrated. The rule of thumb: use process rewards when intermediate correctness is easy
to define, outcome rewards when the optimal path is unknown. An RLVR verifier is a
rule-based ORM; other reward forms for agents are summarized in [[Post-Training for Agents]].
[[RLVP — Verifiable Path Penalties]] sits between ORM and PRM: it keeps an outcome reward
and adds deterministic penalties for path violations, without a learned step scorer.

## Let's Verify Step by Step (PRM800K)

Lightman et al. (2023, preprint) compare process supervision (feedback per reasoning step) with outcome supervision (feedback on the final answer) as ways to train reward models on hard math. One frozen GPT-4 generator writes MATH solutions split into steps, and human labelers rate every step as positive, negative or neutral; the resulting labels are the PRM800K dataset. Both PRMs and ORMs start from GPT-4 plus an extra math pretraining stage, and are judged on best-of-N selection accuracy. For ablations, a small-scale regime has the large PRM stand in as a labelling oracle. Their numbers (self-reported):

- On a 500-problem MATH test subset, selecting from 1860 samples, the large PRM outperforms both the ORM and majority voting and solves 78.2%. The PRM was trained on PRM800K; the ORM on 100 uniformly drawn samples per problem, a different and larger set; neutral steps count as positive and step scores are multiplied. On out-of-distribution STEM tests (AP Calculus, Chemistry, Physics, AMC10/12; 100 samples per problem) the PRM also wins in aggregate.
- Choosing which solutions to label by active learning is about 2.6 times as data-efficient as labelling uniformly, in the small-scale setting at best-of-500.
- At small scale, process supervision outperforms each outcome-supervision variant at every data size (1 to 200 solutions per problem), and outcome supervision via the large PRM beats simply checking the final answer.
- After active learning the labelled data is mostly incorrect solutions (85.1% in phase 1, 13.2% in phase 2). Labelers had to answer 30 quality-control questions and were admitted at 75% agreement with gold labels. A convincing wrong-answer solution is one the current best PRM rates highly that ends in a wrong answer.

The DeepSeekMath paper's curves also favour process over outcome supervision for GRPO ([[GRPO Group Relative Policy Optimization]]), and a pass@k study questions what RLVR adds beyond the base model ([[RLVR Pass@k Reasoning Boundary]]). The problems come from the [[MATH Dataset]].

## Tulu 3's verifiable reward (Lambert et al.)

Tulu 3 (Lambert et al., 2024) runs PPO with a binary verifiable reward after preference tuning (RLVR): the verifier returns alpha for a verifiably correct answer and 0 otherwise, with alpha set to 10 from pilot experiments and not tuned (self-reported, all RLVR runs). In a GSM8K RLVR sweep of the KL coefficient beta from 0.1 down to 0.001, a variant that also added reward-model scores to the verifiable reward scored below the verifiable reward alone (self-reported; Figure 22).

## Xiao and Zhu's textbook treatment

Xiao and Zhu define an outcome model as scoring only the final answer and a process model as scoring each step given the input and earlier steps. Their example of the outcome failure is a solution to 2x+4=10 with wrong logic but the correct answer 3, which an outcome model would score high (a worked example, no model run).

- **Aggregation and labels.** They aggregate step scores with the minimum or the mean. They build process labels by human annotation or by rollouts sampled from each step and checked against a known final answer, and advise annotating steps where the model is confident yet mistaken. In chapter 4 the process reward is the sum over steps of `log Pr(correct | x, y<=k)`.
- **Generative verifiers.** A generative verifier prompts an LLM to critique the steps in words, and its score is the probability that the first token is "Correct".
- **Choosing a verifier.** They advise choosing by availability: tools or tests, a trained reward model, an LLM judge, or majority vote, and using formal systems (code execution, equivalence checkers) where the task allows, feeding error messages back to the model.
- **Credit assignment.** With outcome-only feedback the model must guess which step caused a failure. Shaping the reward as step differences `r_t = v_t - v_{t-1}` makes the sum of rewards telescope to the final step score minus the starting score. Their illustration has a process-model confidence rising from 0.4 to 0.9 (reward +0.5) and then falling to 0.1 (reward -0.8), with a starting score of 0; it is not an experiment. They link this to the advantage through potential-based shaping, an argument they do not measure.

## Limits

- Lightman et al.: the large-scale ORM and PRM training sets cannot be compared directly, since the PRM set is biased by active learning and an order of magnitude smaller. No RL is applied to the generator; only the reward models are evaluated, via best-of-N. Whether this carries beyond math is unknown. Retraining the selector iteratively was unstable and brought no gain. MATH test contamination is possible, though the authors expect relative comparisons to hold. The optimizer, learning rate, batch size and hardware go unreported.
- Lambert et al.: the RLVR stage handles just math and checkable instruction following, and its targets overlap with evaluation benchmarks; alpha was not tuned; the reward-model comparison is a GSM8K-only sweep, one run per configuration.
- Xiao and Zhu's chapters 4 to 6 give almost no empirical numbers: the shaping and false-positive cases are worked examples, and the claim that search gains plateau is asserted from cited work without data. The chapter 6 PDF is truncated in its summary section and has no reference list.


## See Also
- [[Preference Optimization Algorithms]] — prerequisite-for (GRPO and DAPO, the reasoning methods that consume these rewards)
- [[Reward Hacking and Overoptimization]] — extends (the proxy problem, at step level rather than response level)
- [[RLHF Pipeline]] — extends (Stage 2's reward model, specialised for reasoning)
- [[Verification Loops]] — alternative-to (step checking moved to inference time instead of training)
- [[RL Training Frameworks for LLMs]] — related (where these reward models are wired into training)
- [[RLVP — Verifiable Path Penalties]] — alternative-to (outcome reward plus deterministic path penalties)
- [[Post-Training for Agents]] — extends (reward forms for agent RL)
- [[FrogNano Online Task Synthesis]] — related
- [[Role Anchor and Role Drift]] — related (module drift under final-answer rewards)
- [[Post-Training Reasoning Data Primer]] — related
- [[SelfCheck Step Verification]] — alternative-to (prompted step checks with no trained scorer)
- [[Olympiad Proof Agents and Verifier Loops]] — related
- [[Phi-4 Training Recipe and Pivotal Token Search]] — instance-of (token-level process supervision for DPO pairs)
- [[PAPO Process Rewards for Diffusion LLMs]] — related (step reward from a one-step denoised completion)
- [[DeepSearch MCTS in RLVR Training]] — related
- [[SDPO Self-Distillation Policy Optimization]] — related
- [[GRPO Group Relative Policy Optimization]] — related
- [[Tulu 3 Post-Training Recipe and RLVR]] — related (verifiable outcome reward with PPO)
- [[Verifier Reranking for Math Word Problems]] — instance-of
