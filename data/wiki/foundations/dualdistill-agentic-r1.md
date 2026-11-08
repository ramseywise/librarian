---
title: DualDistill Agentic-R1
tags: [foundations, pattern]
summary: "Distil two teachers, one that reasons in text and one that solves with Python code, into a single student by composing trajectories where one teacher's failure is followed by the other's correction; the 7B student chooses between code and text per problem on math."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-du-2025-agentic-r1.md
---

# DualDistill Agentic-R1

DualDistill (Du et al., CMU, arXiv 2507.05707, preprint) trains one student, Agentic-R1, to pick between text chain-of-thought and Python execution for each math problem. A text teacher and an agentic teacher (OpenHands on Claude-3.5-Sonnet) each attempt a problem. Trajectories are composed by case: if the first teacher fails and the second succeeds, the first attempt, a scripted sentence saying the code looked wrong and text reasoning should be tried instead and the second attempt are joined; if both succeed, a transition frames the second strategy as a check; if only the first succeeds, its trajectory is kept alone. This gave 2,678 composed examples. A second stage, self-distillation, samples K=16 trajectories from the student per problem. At inference the model writes code between tags, generation pauses at the closing code tag, an executor (up to 10 calls, 3 seconds each) runs it, and the output is appended before generation resumes.

## Results (self-reported; 5 seeds at T=0.6, budgets of 4096 and 32768 output tokens)

- At the 32768 budget the self-distilled student scored 65.3 on DeepMath-L (87 problems with answers above 10^5) and 52.0 on Combinatorics300, where the DeepSeek-R1-Distill-7B baseline scored 56.3 and 44.5.
- Benchmark averages: at the 4096 budget 49.3 (Agentic-R1) and 50.9 (self-distilled) against 47.4; at 32768 the baseline's 63.1 compares with 62.8 and 67.4 for the two students. The pre-self-distillation student was therefore slightly below the baseline average at the large budget.
- The only ablation (large budget): composed against single-teacher trajectories, DeepMath-L 59.3 and 40.0, AIME 40.7 and 34.0, AMC 82.2 and 50.8.
- At least one code call occurred in 79.2% of Combinatorics300 problems, but in only 52.0% of AMC ones.
- The agentic teacher scored 48.4% on Combinatorics300 while the student reached 50.9%.
- MATH500 regressed slightly (80.0 against 83.1 at the small budget).
- Fine-tuning took 12.7 hours on 4 A6000 GPUs.

## Limits

- Only output tokens are held equal; tool calls, elapsed time and executor tokens are not, and no other tool-integrated reasoning method is compared.
- The authors admit the scripted transitions may sound unnatural, the model can repeat itself, and about 2.6k examples likely cannot teach a wholly new strategy.
- Math only, one tool (Python); tool-favouring benchmarks were chosen; the extraction notes no variance is reported and test sets are small (AIME 2025 has 30 problems).
- The second teacher is conditionally independent of the first attempt, so the "correction" never sees the failed attempt (as the extraction reads the appendix).
- Internal inconsistency: the prose gives the student's Combinatorics300 score as 50.9 while Table 1 gives 52.0 for the self-distilled model at the large budget; the extraction suggests the prose number is the small-budget column. Table 1 cells are doubled in the extraction and were parsed by hand.
- Fine-tuned tool choice is not a prompt-time method.

## See Also
- [[Post-Training for Agents]] — prerequisite-for
- [[Program-Aided Language Models (PAL)]] — prerequisite-for (code as the reasoning medium)
- [[Chain-of-Agents AFM Distillation]] — related (agent trajectories distilled into one model)
- [[AgentArk Multi-Agent Distillation]] — related
- [[Reinforcement-Learned Teachers]] — related
