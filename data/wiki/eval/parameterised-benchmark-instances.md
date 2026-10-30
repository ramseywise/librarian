---
title: Parameterised Benchmark Instances
tags: [eval, concept]
summary: The answer to benchmark leakage for agent evals — publish the instance generator, keep instances private and freshly drawn per run, grade on final environment state, and when training on a benchmark reuse its environments but hold out whole templates or domains, because parameterisation stops answer memorisation but not template overfitting.
updated: 2026-10-30
sources:
  - data/raw/repos/sisyphus/interviewing--guides--6-evals-observability--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--2-llm-fundamentals--interview-guide.md
---

# Parameterised Benchmark Instances

Provisional (low confidence): synthesised from reference answers in *AI Agents in Depth*
(Li), which the book flags as AI-drafted with light human review.

## The problem

A static question bank has no endgame against leakage: once the questions are public they
end up in training data, and the score measures recall of the bank instead of capability.
Hiding the bank does not scale either — the benchmark then cannot be reproduced.

## The mechanism

Split what is published from what is scored:

1. **Publish the generator, not the instances.** Each task is a template with parameters
   (entities, values, environment seed). Fresh instances are drawn every run.
2. **Grade on final environment state**, not on a matched answer string. A parameterised task
   has no fixed answer to memorise, and a state check (was the booking made, is the record
   correct) survives rewording. (State checks cover the outcome only; the path still needs
   its own grading — [[Trajectory Over Outcome]].)

## Training on a benchmark without fooling yourself

If a benchmark's environments are useful as training ground (agent-RL benchmarks with
simulated users and tools are the usual case), **reuse environments, not questions**.
Parameterisation prevents memorising answers but not overfitting to the *template* — the
model learns the shape of each task family. So hold out whole templates or whole domains and
treat the out-of-distribution score on those as the real metric. This is the eval-side twin
of keeping a held-out domain before deployment in fine-tuning.

## Relation to other contamination controls

This prevents leakage *by construction* at evaluation time. Its complement is detecting
contamination after the fact — proving a corpus or repo does not contain excluded material,
as in [[Hashed Fingerprint Contamination Gate]] — and keeping a suite measuring as it
saturates ([[Eval Suite Maintenance]]).

## See Also
- [[Evals and Observability Interview Study Guide]] — instance-of (asked as "is there an endgame to benchmark leakage?")
- [[Eval Suite Maintenance]] — extends (saturation and staleness, the other way a suite stops measuring)
- [[Hashed Fingerprint Contamination Gate]] — alternative-to (detect contamination instead of preventing it)
- [[Golden Set Mechanics]] — extends (fixed golden cases vs generated instances)
