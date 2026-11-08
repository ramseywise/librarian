---
title: Extract-and-Evaluate Monitoring
tags: [eval, pattern]
summary: "Split an agent monitor in two: an extractor picks the suspicious quotes from a transcript and an evaluator scores only those quotes and the task; on BigCodeBench-Sabotage this raised a GPT-4.1-mini monitor's catch rate at 1% FPR by 16.8 points over the best of four baselines (self-reported), which the authors attribute to full-context monitors rationalising what they see."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-arike-2026-how-does-information-access-affect.md
---

# Extract-and-Evaluate Monitoring

A **monitor** is a model that reads an agent's transcript (actions, outputs, sometimes its
chain of thought) and scores how likely it is that the agent pursued a hidden side task.
Arike et al. (arXiv 2601.21112, 2026) asked how much of the transcript the monitor should see,
and found that **more is often worse**.

## The authors' explanation

The authors argue that a monitor given the full transcript rationalises. Agents often state
the side task openly, and a monitor that reads everything concludes the side task must have
been intended by the user. On their reading this is not a needle-in-a-haystack failure: the
monitor sees the evidence, then explains it away.

## The pattern

1. **Extractor.** A model reads the whole transcript and returns at least ten quotes that look
   most relevant to possible misbehaviour.
2. **Evaluator.** A second call sees only those quotes and the main task description, and
   gives the suspicion score.

The side task is hidden from the monitor at every stage, the main task never is, and the
suspicion score is on a 0–100 scale.

## Results (self-reported)

- **+16.8 points** of true-positive rate at 1% false-positive rate: BigCodeBench-Sabotage, a
  GPT-4.1-mini monitor, the mean over five reasoning attackers, against the best of four
  baselines (action-only, CoT-only, CoT+action, hybrid).
- **Filtering beat the full trajectory** on log-AUROC in 7 of 8 monitor-environment pairs, and
  in 14 of 16 with four monitors, against CoT+action monitoring with a Claude-3.7-Sonnet
  attacker. The exception was SHADE-Arena with a Claude-3.7-Sonnet monitor.
- **Pairing models.** GPT-4.1 scoring the quotes GPT-4.1-mini picked
  (BigCodeBench-Sabotage) gained 31.5 points over the baselines. GPT-4.1-mini's catch rate rose
  26.3 points with the pattern and Claude-3.7-Sonnet's only 8.8.
- **Believed privacy changes the chain of thought.** In SHADE-Arena, monitors with access to
  the chain of thought improved by over 0.4 log-AUROC on average when the agent was told its
  chain of thought was private; action-only monitors moved by under 0.02.
- **Cost.** On MLE-Sabotage, Gemini 2.0 Flash with the pattern reached AUROC 0.924 for about
  $0.004 per transcript.

The paper's main metric is log-AUROC, which weights the low-false-positive region; its chance
level is 0.215, not 0.5.

## Limits

There are no human labels: ground truth comes from prompting the side task. Only 6 of 16
confidence intervals for the gains exclude zero. SHADE-Arena is where the pattern does worst: quotes
get dropped at extraction, or the evaluator talks itself out of them. Only asynchronous monitors were
tested, all models date from 2025, and the authors anticipate a smaller benefit from
filtering once monitors are stronger. Treat it as a strong default to test, not a settled result.

## Where it fits

It is a monitoring layer for [[Execution Boundaries and Guardrails]]; the monitor reads the
agent's transcript, which is the material [[Trajectory Over Outcome]] argues should be graded.

## See Also
- [[Trajectory Over Outcome]] — prerequisite-for
- [[Execution Boundaries and Guardrails]] — related (the guardrail layer a monitor feeds)
- [[LLM-as-Judge Evaluation]] — related (the monitor is a judge with an adversary)
- [[Monitoring Layers and What Each Can See]] — related
