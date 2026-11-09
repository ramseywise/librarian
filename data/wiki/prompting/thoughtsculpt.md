---
title: ThoughtSculpt
tags: [prompting, concept]
summary: Inference-time Monte Carlo Tree Search over LLM thought nodes whose action space includes revising earlier output; the paper reports gains over Tree of Thoughts and Self-Refine on story outlines, crosswords and constrained generation (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-chi-2024-thoughtsculpt.md
---

# ThoughtSculpt

ThoughtSculpt (preprint) argues that tree search limited to candidates generated at earlier steps, as in [[Tree of Thoughts]], and linear self-refinement, as in [[Self-Refine]], are both weaker than a search that can go back and revise an intermediate node. Each node holds a full or partial output. Three LLM-driven parts work on it:

- A **thought evaluator** returns a numeric score, used as the search heuristic, and natural-language feedback, either holistic or itemised per sub-unit.
- A **thought generator** proposes k child nodes from the task, the parent node and that feedback.
- A **decision simulator** performs MCTS rollouts and returns the node with the highest average reward. Each rollout uses UCB1 selection, expansion, a single-child simulation down to a fixed depth, and back-propagation.

It needs no training or external feedback and runs purely at inference, using GPT-3.5 and GPT-4. It also works with depth-first search in place of MCTS.

## Results (self-reported)

- Story outline improvement, GPT-4, scored by a fine-tuned Flan-T5 evaluator: MCTS 65.0, ToT 49.9, CoT 28.8 and Self-Refine 27.9. The paper notes that on this task the GPT-4 baselines can score lower than GPT-3.5 ones.
- Mini-crossword, GPT-4, 100 search steps: 66.0 word, 83.0 letter and 35.0 game success, against 60, 78 and 20 reported for ToT; with only 20 steps it already matches ToT's 100-step result.
- CommonGen-Hard (20 to 30 concepts), run on GPT-3.5 with a depth of 3 and 3 candidates: both ThoughtSculpt variants far exceed ToT coverage, with the DFS variant a little ahead of MCTS on that measure. Where MCTS comes out ahead, this rests on a GPT-4 preference judgement.
- Game of 24 on the test set of the original ToT paper: 79 for ThoughtSculpt (MCTS, b=5) against 74 for ToT, where the ToT figure is copied from that paper, so the base model and prompts are not the same.
- Cost with GPT-4: roughly 2.2 times the ToT cost per case on story outlines, and 1.6 times on crosswords.
- Replacing GPT-4 with Llama3.1-8B-Instruct in both evaluator and generator drops CommonGen-Hard coverage to 90.7 from 99.0; weakening just the evaluator costs more (96.3) than weakening just the generator (98.5).

## Limits

- Because of the many LLM calls it costs more than most sampling methods, and the authors concede it is not advisable when the base model already does well enough.
- The Flan-T5 evaluator learned from GPT-3.5 outlines, so it may prefer GPT-3.5 output; the authors give this as the reason GPT-4 scores come out lower.
- The test sets are small (50 outlines, 20 crossword puzzles). Seeds, variance and significance tests are absent.
- The text claims 1.2x ToT cost, lower than the token tables suggest (the extraction notes this).
- Game of 24 baselines are copied rather than rerun; the exploration constant and rollout count are not stated; closed API models make exact reproduction drift-prone.

## See Also
- [[Tree of Thoughts]] — prerequisite-for
- [[Self-Refine]] — prerequisite-for
- [[RAP Reasoning via Planning]] — alternative-to (MCTS with a world-model state predictor)
- [[Graph of Thoughts]] — alternative-to
