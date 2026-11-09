---
title: Prompt-Induced Waste in Coding Agents
tags: [prompting, concept]
summary: "A preregistered coding-agent benchmark reports that wording such as 'consider several approaches' or 'be absolutely certain' multiplies reasoning or verification cost at flat success, that harness choice swings cost more than wording, and that cost per successful task is the metric to watch (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-weinberger-2026-prompt-induced-waste-coding-agents.md
---

# Prompt-Induced Waste in Coding Agents

The paper's thesis is that coding-agent cost comes from the path an agent takes, which prompt wording, inference effort and harness policy shape together, rather than from token price or prompt length; the paper argues for measuring cost per successful task. It is a preregistered benchmark (4,644 core runs, per the extraction) with harness extensions. All numbers below are the paper's own (self-reported); the model and harness names are the versions the paper uses, so treat the figures as tied to them.

## Reasoning waste from wording

Setup: six open-weight models on one small-task harness (PI.DEV), frozen 8-task holdout, 5 repetitions per cell, paired median reasoning-token ratio against the same model and task.

- Asking for several approaches, comparing trade-offs and implementing the best raised reasoning tokens 2.4-7.4x at comparable success. Aggregate success was 96.5% for the baseline and 95.2% with forced branching over 878 branching runs; on easy tasks it fell from 98.8% to 96.4% with about 3x more scope violations.
- A condition-blind LLM judge annotated 2,801 traces: multiple-approach prompts added about 3.5 candidate strategies per run, about 3 of them elaborated then discarded. Deep-thinking prompts gave 2.2x more reasoning text and no median increase in observable functional units.
- Deep-thinking wording raised reasoning 1.6-2.2x and certainty wording 1.3-1.9x.
- Restating the task verbatim cost about 1.0x, so content, not length, drove the effects. All four paraphrases of three wordings raised reasoning on every tested model (12 of 12 cells).
- Misleading hints were the costliest input defect (2.61x reasoning) and was the single semantic marker associated with lower success.
- A "work efficiently, stop when criteria pass" template was neutral on all six models, but in a Sonnet 5 follow-up it produced 3 of 5 hidden-test failures against 0 of 5 at baseline on an ambiguous spec, since the agent skipped the requirements file inside the repo.

## Tool-borne waste

- Certainty wording caused redundant re-verification. Runs at the heaviest redundancy levels (213 runs against 1,585 clean) cost about 18x the clean median with 15 against 6 tool calls and about 3x the wall-clock, at flat success; the extraction notes this is an association, since levels were annotated, not randomised.
- Runs with one unused branch cost roughly 1.9x the clean-run median even though tool calls stayed at 7 to 8.

## Harness and effort

- Matched model, task and prompt: Claude Code against PI.DEV had a cost per success 5-30x higher at similar success rates, with a 12-15x larger fixed prefix and 2-7x more turns. Prompt effects did not transfer between harnesses.
- A DeepSeek Harness extension (Sonnet 5, 5 tasks x 5 arms x 3 repetitions, all cells solved) cut cost 74.7% with effort control alone, against about 19% under Claude Code; the paper says the benefit depends on the harness default.
- On a 25-instance hard slice of SWE-bench Verified run in Claude Code, Opus 5 resolved 17, 18 and 16 instances at low, high and extra-high effort (cost per resolved task $0.75, $1.89, $3.62), and Sonnet 5 resolved 12, 19 and 17. Run-to-run noise was large.
- Caching cut the billed cost by about 61% on open models without changing behaviour.

The authors' advice, their interpretation and untested as its own arm, is to swap demands for certainty for explicit verification and stopping rules, and to require repo inspection when a spec is ambiguous.

## Limits

- Tasks are small (four files or fewer) with high success ceilings; the paper declines to extrapolate to long-horizon production agents.
- Visible reasoning is not complete computation, so trace claims cover observable text only, and Sonnet 5 is excluded from trace-level claims.
- Judge reliability is modest (cross-judge agreement kappa is 0.28 overall and 0.55-0.68 on key fields); the mechanism-level cost associations are correlational.
- The SWE-bench and DeepSeek Harness material is post-registration and separate from the core benchmark; the extension uses one closed model and five ceiling-success fixtures.
- Only the tested wordings are covered, and effect size varies with paraphrase and position.
- The authors are at a cost-optimisation company; the paper is a preprint.

## See Also
- [[Prompting Reasoning Models]] — prerequisite-for
- [[Overthinking and Concise Reasoning]] — related (reasoning-token overhead)
- [[Harness Effect on Token Economics]] — related (harness choice as a cost factor)
- [[Evaluating Prompts]] — prerequisite-for
