---
title: Paper-Replication Completion Gate
tags: [harness, pattern]
summary: A coding-agent skill that makes "done" a state of a persistent workspace, checked by validators outside the agent, instead of the agent's final message; shown on 12 runs over 4 papers with no baseline.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-hans-2026-coding-agents-can-replicate-scientific.md
---

# Paper-Replication Completion Gate

Hans and Bilionis (Purdue, a July 2026 preprint) build a coding-agent skill called Paper-replication. Their argument is that a prompt asking an agent to finish a replication can make it declare completion while the workspace still lacks evidence for each target. The skill has two parts: a persistent workspace and checks that run outside the agent, ending in a completion gate.

## Mechanisms

- **Persistent workspace:** a reproduction matrix, a task ledger, a run recorder and provenance records, so work survives interruptions. Exactly one target is active at a time, and failed or replaced runs stay in the record.
- **Acceptance rule first:** the rule for judging a target is written before the comparison, which stops it being altered once a comparison has failed.
- **Evidence rules:** a produced figure or table is not enough evidence by itself. For numeric targets a validator turns down evidence that is only visual. Hash checks catch paper assets that were copied, and provenance has to link the method back to the equations in the paper, so a substitute that merely looks similar fails.
- **Completion gate:** all checks pass, every target is MATCHED, no target is active and the report PDF exists. Done is a workspace state, not a message.

## Results (self-reported)

Setup for the results below: Codex running GPT-5.4 with extra-high reasoning; 4 papers, each run 3 separate times (12 runs); the authors' code was not allowed; each run had 10 follow-up prompts queued.

- All 12 workspaces passed the gate and all 158 recorded targets reached MATCHED.
- With thresholds fixed from the papers, 37 of 39 scalar anchor-runs landed within them. The other two still got the MATCHED label: one had an L2 error of 4.8e-2 versus a 1% threshold, the other an error of 16.4% versus 10%.
- Elapsed time ranged from 1.2 to 13.0 hours; 25 executions were superseded across runs.
- Across runs the acceptance-rule type agreed for 19 of 20 claims on one paper, yet for only 4 of 8 on another.
- Dollar and token cost are not reported.

## Limits

- No ablation without the skill, which the authors say so; the claims that prompting alone stops too soon or accepts copied figures are asserted and were not measured here.
- Four papers, one agent and model, and only 13 scalar anchors. The authors built the tool.
- "Matched" is decided against acceptance rules that the agent itself writes down, so 158 of 158 is partly self-graded, and targets with out-of-threshold scalars still count as matched. Each distributional target has one comparison per run; independent re-judging is put off.
- A transformed copy would slip past the hash checks; no reuse was seen by the authors, yet a pass is only recorded evidence, not proof that the work is unique.
- Effort differences between papers are not evidence that one paper type is harder.

## See Also

- [[Verification Loops]] — prerequisite-for
- [[Spec, Verifier, Environment Layering]] — related
- [[Three-Layer Termination Check]] — related
- [[Long-Horizon Execution]] — related
