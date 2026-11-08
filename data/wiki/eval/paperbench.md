---
title: PaperBench
tags: [eval, reference]
summary: "OpenAI's benchmark in which an agent replicates 20 ICML 2024 papers from scratch and is graded by an LLM judge walking a weighted rubric tree of 8,316 binary leaves; o1 with an iterative agent scored 24.4% on all 20 papers, and on a 3-paper subset ML PhDs reached 41.4% against 26.6% for o1 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-starace-2025-paperbench.md
---

# PaperBench

PaperBench (Starace et al., OpenAI, arXiv 2504.01848, 2025) asks an agent to reproduce the results
of a recent paper: write the code, run it and match the reported numbers. It covers 20 ICML 2024
Spotlight and Oral papers. The agent never sees the grading rubric.

## Rubric tree

Each paper has a rubric co-developed with one of its original authors. The rubric is a tree of
requirements with weights that express importance, not difficulty. Only the leaves, 8,316 across the
20 papers, are graded, each pass or fail, and each parent is scored as the weighted mean of its child nodes. Leaves were split until an expert could check one in under 15 minutes. Leaves come in three
types: Code Development, Execution and Result Match. Result Match is checked only against the
output of a fresh re-run of the agent's reproduce script on a clean VM, so results hard-coded
at task time cannot count.

## The judge

An LLM judge (SimpleJudge) grades each leaf independently. It was checked on JudgeEval, leaves from partial replications that the authors graded by hand (self-reported):

- F1 against the hand labels, with cost per paper: o3-mini-high 0.83 ($66), o1 0.84 ($830), GPT-4o 0.73,
  GPT-4o-mini 0.59, and a random judge 0.49.
- o3-mini-high F1 by leaf type: 0.72 for Code Development, 0.82 for Execution, 0.94 for Result Match.
- A coarser rubric inflates the grade: pruning the tree on one submission moved its score from 0.25
  (361 leaves) to 0.93 (a single leaf). Pruning at depth 3 cut grading cost tenfold, and the authors
  report the judge got only slightly worse.

## Results (self-reported)

On all 20 papers, 3 runs each, a 12-hour limit and the o3-mini judge (± is one standard error):

- With a basic agent, Claude 3.5 Sonnet scored 21.0 ± 0.8 and o1 13.2 ± 0.3.
- An iterative agent raised o1 to 24.4 ± 0.7 and lowered Claude to 16.1 ± 0.1; the authors read this
  as sensitivity to prompting. o1 at 36 hours scored 26.0 ± 0.3.
- Score comes mostly from code: Claude's basic-agent run scored 35.4 on Code Development, 1.8 on
  Execution and 0.7 on Result Match.
- Humans: on a 3-paper subset, ML PhDs reached 41.4% after 48 hours (best of three attempts) while o1 reached 26.6%.
- Cost: an o1 12-hour rollout costs about $400 per paper, about $8,000 per 20-paper run.
- 10 of 646 runs were disqualified for using blacklisted resources and scored 0.

## Limits

The set has only 20 papers. The authors say the judge falls short of an expert human and is non-deterministic; it was tested on
human-made submissions, not on real agent output. The authors recommend several seeds because of high
variance (one paper's three runs scored 0.680, 0.542 and 0.144). The human baseline rests on 8 people and 3 papers, takes the best of three attempts, extended selectively, and allowed AI tools, so it is not an average-person figure. There is no inter-rater agreement for the human
labels and no trajectory grading. The models are from early 2025. The source is inconsistent in places: one
table says o1 with the iterative agent used two seeds while another lists three runs, and the human-baseline figure spans four
papers whereas the headline comparison uses three.

## See Also
- [[MLE-bench]] — related (the authors cite it as a benchmark of the same kind)
- [[ScienceAgentBench]] — related
- [[LLM-as-Judge Evaluation]] — related (the judge is validated against human leaf labels)
- [[Trajectory Over Outcome]] — related (artifact grading only)
- [[NatureBench]] — extends (moves from reproducing a paper to matching its published result with the method withheld)
