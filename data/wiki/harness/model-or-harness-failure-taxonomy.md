---
title: Model or Harness Failure Taxonomy
tags: [harness, concept]
summary: Label an agent failure by the interaction edge where it starts and the fault side that needs repair (model, harness, environment), taking the earliest unrecovered failure; 41 modes, validated on 40 worked examples with LLM judges.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-raj-2026-model-or-harness.md
---

# Model or Harness Failure Taxonomy

Raj et al. (Scale AI, a July 2026 preprint) propose labelling each agent failure by the interaction edge where it starts (for example TOOL to MODEL) and by a fault side, the component whose repair is needed. The fault sides distinguish three kinds of fix: model post-training, harness engineering, and repair of the environment or grader. The taxonomy organizes 41 failure modes. For cascading errors the rule is to label the first failure after which execution never recovers.

The paper's motivating case: in a long Claude Code session an instruction can vanish because harness compaction removed it, or because the model ignored it while it stayed available. The behaviour looks the same, but one needs a harness fix and the other a model fix. A second example: if a tool wrapper suppresses an error, the failure is TOOL to MODEL with fault on the tool; if the wrapper returns the error and the model ignores it, the fault is on the model. For Context Rationale Erosion, the fault side is the harness if the harness drove the compaction, and the model if the model did.

## Validation

Four frontier models acted as judges (GPT-5.5 with xhigh effort, plus three Claude Opus versions, 4.6, 4.7 and 4.8, using adaptive thinking at max effort), each recovering the human label for 40 worked examples from the definitions in a 3-turn session. One set of results per judge, no repeats (all self-reported):

- Cohen's kappa against the human label on category: 0.76 (GPT-5.5), 0.71 (Opus 4.6 and 4.7), 0.70 (Opus 4.8). Judge-to-judge kappa peaks at 0.84.
- Exact-match category accuracy 0.80 for GPT-5.5 and 0.75 for each Opus; full failure-mode accuracy 0.72, 0.70, 0.62 and 0.68.
- Selective voting: three of four judges agreeing gave a category precision of 0.83 with 0.90 coverage, while requiring unanimity gave 0.96 with 0.68 coverage.
- Of the 41 modes, 36 can be attributed to the model and 5 to other components. The authors say this split is partly produced by their rule of assigning fault to the model whenever a stronger model could have avoided the failure, and is not a share of real failures.

## Limits

- The taxonomy is descriptive. It gives no prevalence, no model-versus-harness score decomposition, no ablations, and never tests whether a fix on the harness or the model actually repairs the labelled failure.
- n=40 examples, one human annotator, no inter-human agreement; agreement on the exact failure mode is lower than on the category; some sources lack the evidence for a root cause.
- The authors built and judged the taxonomy themselves.

## See Also

- [[Harness Subsystem Attribution]] — related (a five-subsystem diagnosis, a different split)
- [[Harness Engineering]] — prerequisite-for
- [[Agent Deployment Anti-Patterns]] — related
