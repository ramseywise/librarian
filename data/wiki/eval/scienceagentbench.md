---
title: ScienceAgentBench
tags: [eval, reference]
summary: "A benchmark of 102 data-driven discovery tasks taken from 44 peer-reviewed papers, where an agent must write one self-contained Python program; the best agents solve about a third of tasks best-of-3 and far fewer on average, and in a sample of 50 failures most programs ran but computed the wrong thing (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-chen-2024-scienceagentbench.md
---

# ScienceAgentBench

ScienceAgentBench (Chen et al., arXiv 2410.05080, 2024) asks whether language agents can do
the coding part of data-driven science. Each of its 102 tasks, taken from 44 papers in four
disciplines, gives the agent a dataset and an instruction and expects one runnable program
that produces the paper's output, such as a figure, a table or a trained model.

## Metrics

- **VER**: the program runs without error.
- **SR**: the output passes the task's success criteria. For figures, a GPT-4o judge compares
  the output with the gold figure, averaged over three samples; judge–human agreement is not
  measured here, and the paper relies on prior work for it.
- **CBS**: similarity between the generated and the gold code. It is set to 1 whenever SR is 1.
- **Cost** per task.

## Results (self-reported)

The best non-reasoning setup (Claude 3.5 Sonnet with self-debugging) solved 32.4% best-of-3,
34.3% with expert-provided knowledge; averaged over runs it is 22.9% and 27.8%. o1 reached
42.2% best-of-3. The best-of-3 gap is covered in [[Best-of-k Headline Inflation]].

- **A simple loop beat a full agent framework.** With Claude 3.5 Sonnet and no expert
  knowledge, the self-debug loop solved 32.4% against 21.6% for OpenHands CodeAct, at about
  one-seventeenth the cost ($0.057 vs $0.958 per task).
- **Expert knowledge lowered executability for most agents** while raising success: Claude's
  self-debug VER fell from 92.2 to 86.3. The authors trace this to named tools prompting wrong
  or hallucinated API calls.
- **Failures are semantic.** Of 50 sampled failures per setup, 29 (OpenHands) and 30
  (self-debug) ran but produced wrong results. A runnable program is not evidence of a correct
  one.
- **Where failures sit.** A separate human rubric rating of 102 programs found 25% of failed
  programs scored below 50 on the data-loading stage.

## Contamination defences

The authors drop five test points from each dataset, re-split the datasets for model-building
tasks and replace their test labels with dummy values (e.g. −1), so the agent cannot read the
answers from the files it is given. These are useful patterns ([[Eval Contamination Defenses]]),
though the paper does not measure how much each one helps.

## Limits

Python only, four disciplines, gold programs that run in under ten minutes, and code generation
only: trajectories are read but not scored. The contamination mitigations rest on a single case
study, with no count of what they caught. Rubric scores are not automated and have no
inter-rater agreement, and rubrics follow the gold program, so a valid alternative solution
can score low. The models are from 2024.

## See Also
- [[Best-of-k Headline Inflation]] — related
- [[MLE-bench]] — alternative-to
- [[Eval Contamination Defenses]] — related
- [[Trajectory Over Outcome]] — related (why "it ran" is not "it worked")
