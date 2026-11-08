---
title: Branch-Solve-Merge
tags: [prompting, pattern]
summary: "A three-prompt program: the model plans parallel sub-tasks, solves each independently, then merges; on MT-Bench writing pairs with LLaMA-2-70B-chat it lifted judge-human agreement from 0.43 to 0.55 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-saha-2023-branch-solve-merge-improves-large.md
---

# Branch-Solve-Merge

Branch-Solve-Merge (BSM; Saha et al., 2023) is a zero-shot program of three prompts to the same base model. Branch: the model decides the sub-tasks and how many there are. Solve: each sub-task is handled in isolation. Merge: the results are fused. For judging, the branches are evaluation criteria, each solved as a 1-5 score per response, and merge is a plain sum of scores (no extra model call). For generation, branch splits a set of concepts into two groups, solve writes a story per group, and merge fuses the stories.

For position bias, the full program runs twice with the two answers in swapped order; a verdict counts only if both runs agree, otherwise it is a tie. Baselines got the same treatment.

## Reported results (LLaMA-2-70B-chat, greedy decoding, MT-Bench)

- Writing, 300 response pairs: agreement with humans was 0.55 (BSM), 0.52 (self-consistency) and 0.43 (both Plan&Solve and zero-shot); position bias 17.33 against 35.66 for self-consistency (all self-reported). Self-consistency drew as many samples as BSM has branches.
- Up to 26 points absolute gain over zero-shot on some domains; STEM 0.46 to 0.72, equal to GPT-4 at 0.72 (self-reported). Extraction stayed well below GPT-4 (0.55 vs 0.71).
- Branching factor: agreement peaked at 4 branches (0.53) in a 100-sample test (self-reported).
- Constrained story generation, 100 samples: all ten concepts present in 28.0% of stories against 22.0% zero-shot (self-reported); GPT-4 preferred BSM stories 93% of the time. Even so 72% of stories missed a concept, mostly lost in the solve step.
- Adding self-consistency inside each branch left agreement unchanged at 0.55.

## Limits

- The main table is one category (writing); samples are small and no seeds or intervals are reported.
- Compute is matched to self-consistency only by generation count; tokens and cost are not reported, and the swapped-order run doubles calls.
- Gain on GPT-4 was 3 points and its bias did not improve (Table 3 caption).
- Reference-based categories depend on GPT-4-written reference answers; 2023-era models.

## See Also
- [[Self-Consistency]] — prerequisite-for (a special case: the same problem sampled k times)
- [[Skeleton-of-Thought]] — related (parallel fan-out for speed)
- [[LLM Judge Biases]] — related (position bias is the measured failure)
- [[Prompt Chaining]] — related
- [[LLM-as-Judge Evaluation]] — related
