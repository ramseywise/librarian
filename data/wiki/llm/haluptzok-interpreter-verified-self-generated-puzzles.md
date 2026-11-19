---
title: Interpreter-Verified Self-Generated Programming Puzzles
tags: [llm, pretraining-and-data, pattern]
summary: "A code LM proposes programming puzzles and solutions, a Python interpreter keeps only the verified pairs, and fine-tuning on them improves the LM on held-out puzzles; GPT-Neo-2.7B rose from 7.5% to 20.6% Pass@100 on its own data and 38.2% on Codex's (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-haluptzok-2022-language-models-can-teach-themselves.md
---

# Interpreter-Verified Self-Generated Programming Puzzles

Haluptzok, Bowers and Kalai test whether a code LM can write its own problems and solutions, let a Python interpreter screen them, and then get better on held-out problems by training on what survives. A **programming puzzle** is a checker function f(., x); its solution is a g(x) for which f(g(x), x) is True. **Interpreter distillation** is the authors' name for learning from the interpreter's correctness screen, which they separate from distilling knowledge out of a larger model.

## Procedure

1. Show the LM a few randomly chosen training puzzles, without solutions, and ask for new puzzles. Pre-filtering removes trivial or invalid ones: about half of Codex's output, with under 1% duplicates.
2. The LM tries to solve each puzzle, prompted with the P3 medium few-shot prompt.
3. The interpreter checks every attempt; at most the 8 shortest correct solutions per puzzle are kept.
4. Fine-tune on the verified pairs, then repeat.

The authors built four datasets of 1M pairs each, from Codex and from Neo at 125M, 1.3B and 2.7B, and fine-tuned every Neo size on every dataset for a single epoch.

## Results (self-reported)

Setup: GPT-Neo models, 228 P3 test puzzles, Pass@100, one epoch unless stated; baseline Neo-2.7B is 7.5%.

- Training Neo-2.7B on Verified-Codex gives 38.2%; on its own Verified-2.7B data 20.6%; on Verified-125M data 15.4%, so a small generator already helps a larger model.
- Skipping interpreter filtering costs a lot: Unverified-Codex reaches 21.5% against 38.2%.
- The 635 human-written solutions (74K tokens) lift it only to 10.5%.
- Puzzle diversity (cluster entropy with C=8, on 10,000 puzzles per dataset) grows with generator size, from 2.28 for Neo-125M to 2.69 for Codex, while human P3 puzzles score 2.85.
- A second iteration (1M samples) gained little beyond the first (25K samples), so the pipeline stopped at n=2.
- A temperature sweep in steps of 0.2 found 0.8 best for Pass@100. Even after 11 epochs of fine-tuning, Neo does better with few-shot than zero-shot prompts.

## Limits

- Optimiser, learning rate, batch size, hardware, compute and seeds are unreported, and there are no confidence intervals.
- Only puzzles that a deterministic verifier can check were tested, and the authors observe that most domains lack one.
- Gains level off by the second iteration; the authors suggest reinforcement learning for the generation and filtering steps later.
- Transfer to English-to-code tasks was not tested, and the authors caution about catastrophic forgetting of natural language.
- Because Codex could not be fine-tuned, self-improvement is shown for Neo only; the Codex data is one model's output distilled into another, plus interpreter filtering.
- The synthetic puzzles are shorter and sit nearer the training set than the test set is (distance 0.249 versus 0.302 for Neo-125M).
- Hand inspection found many puzzles uninteresting or flawed, and the judge is not a full sandbox.
- The overall improvement factor of 4.95 comes from a table whose caption names neither model nor dataset.

## See Also
- [[Rejection Sampling Fine-Tuning]] — related
- [[Autodata Agentic Self-Instruct]] — related
- [[Multi-Agent Evolve Self-Play]] — related
- [[AlphaCode Sample, Filter and Cluster]] — related
