---
title: Tree of Thoughts
tags: [prompting, llm, concept]
summary: Generalizes chain-of-thought into search — a propose prompt generates candidate intermediate steps, a value prompt rates each (sure/maybe/impossible), and a code controller runs BFS/DFS with backtracking; GPT-4 went from 4% (CoT) to 74% on Game of 24.
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/papers/2026-11-07-yao-2023-tree-thoughts.md
---

# Tree of Thoughts

Yao et al. (2023); Long (2023). Where [[Chain of Thought]] commits to one path and
[[Self-Consistency]] samples independent paths, ToT **searches**:

1. **Propose** — a prompt generates several candidate "thoughts" (next intermediate steps).
2. **Value** — a prompt evaluates each candidate (*sure / maybe / impossible* — on Game of
   24: can the remaining numbers still reach 24?).
3. **Search** — BFS or DFS over the tree, backtracking from dead ends.

Result: on Game of 24, GPT-4 solved 4% with CoT and 74% with ToT.

**It is an orchestration pattern more than a prompt.** Both steps are ordinary prompts, but
the controller loop lives in code — the same move as any loop pattern in the harness.

**Cheap single-prompt approximation** (Hulbert, 2023): "Imagine three different experts
are answering this question. All experts write down one step of their thinking, share it
with the group, then go on to the next step. If any expert realises they're wrong, they
leave." Useful for a quick probe; not a real search.

Use it for search problems with dead ends (puzzles, planning). For most tasks a reasoning
model or self-consistency is cheaper ([[Prompting Reasoning Models]]).

## Paper results (self-reported)

Setup for each: GPT-4 chat, single run, unless stated (NeurIPS 2023 paper).

- **Game of 24** (games 901-1,000 from 4nums.com; temperature 0.7; BFS with b=5 over 3 thought steps; each thought valued by sampling the value prompt 3 times): ToT 74%; ToT with b=1 already 45%. Baselines: IO 7.3%, CoT-SC with k=100 9.0%, oracle best of 100 CoT samples 49%, IO plus refine (up to 10 iterations, using ground-truth feedback) 27%. About 60% of CoT samples had already failed after the first step (read approximately).
- **Cost on Game of 24:** $0.74 per case for ToT against $0.47 for best-of-100 CoT and $0.13 for best-of-100 IO; the paper states ToT may need 5 to 100 times the generated tokens of CoT depending on prompts and search. For Creative Writing, ToT costs roughly $0.32 per case and CoT $0.07.
- **Model roles:** GPT-3.5 reaches 19% on Game of 24 (3-shot proposal prompt). Mixing the two models, GPT-4 as generator with GPT-3.5 as evaluator reaches 64%, and the reverse arrangement 31%.
- **Mini Crosswords** (20 test games; DFS capped at 100 steps): 60% word-level success and 4 of 20 games solved, against 14 to 15.6% word success for IO and CoT. Removing pruning gives 41.5% and removing backtracking 20%.
- **Creative Writing** (100 inputs): ToT gets a better coherency score than IO and CoT, but GPT-4 does the scoring and belongs to the same model family as the generator; in a blind comparison by some of the authors, ToT passages were preferred in 41 of 100 pairs, CoT in 21, tie in 38.
- **GSM8K and StrategyQA** (100 questions each, zero-shot ToT): 90 against 86 for CoT, and 83 against 82.

## Limits

- The authors concede that deliberate search may be unneeded for tasks GPT-4 already handles, that only three fairly simple tasks were tried, ToT costs more than sampling, and the state evaluator is imperfect (it pruned valid rare words in crosswords).
- Best-of-k baselines are oracles and the refine baseline uses ground-truth feedback; one run per configuration, with no variance or significance tests.
- The extraction notes that the tasks were built to be hard for GPT-4 as it stood in May 2023, and that reasoning models released since carry out much of this search internally; only BFS and DFS were explored.

## See Also
- [[Chain of Thought]] — extends
- [[Self-Consistency]] — extends
- [[Prompting Technique Selection]] — instance-of
- [[LLM Fundamentals Interview Study Guide]] — prerequisite-for
- [[Self-Ask Prompting]] — alternative-to (another structured reasoning scaffold)
- [[Adaptive Branching MCTS]] — extends (chooses wider or deeper by Thompson sampling)
- [[CoAT Associative-Memory MCTS]] — extends (MCTS with a per-node memory)
- [[MVoT Multimodal Visualization of Thought]] — related
- [[Graph of Thoughts]] — extends (arbitrary graph of thoughts)
- [[ThoughtSculpt]] — extends
- [[RAP Reasoning via Planning]] — alternative-to (MCTS with a world model)
- [[Self-Evaluation Guided Beam Search]] — alternative-to
- [[Discriminator Bottleneck in LLM Planning]] — related
- [[Algorithm of Thoughts Plus (AoT+) State Memoization]] — related (single-pass tree search with memoized states)
- [[Self-Discover]] — related (composes reasoning structure per task)
