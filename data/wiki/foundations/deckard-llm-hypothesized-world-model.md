---
title: DECKARD LLM-Hypothesized World Model
tags: [foundations, pattern]
summary: "DECKARD asks a few-shot LLM once for a crafting-recipe dependency graph, then verifies and corrects it through Minecraft experience during RL training, so the LLM guides exploration but not execution; it cut steps to a stone pickaxe from 32M to 2.6M."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-nottingham-2023-do-embodied-agents-dream-pixelated.md
---

# DECKARD LLM-Hypothesized World Model

Nottingham et al. (ICML 2023) study whether a dependency graph guessed by a language model, then tested against what the agent actually experiences, speeds up reinforcement learning on Minecraft crafting despite the model's mistakes. Their argument: if the model only shapes exploration during training and does not plan at run time, the final policies are not capped by how accurate the model was.

## Mechanism

Before training, Codex is asked a single time to output recipes for 391 Minecraft items as a Python dictionary. The result serves as the hypothesised Abstract World Model (AWM), a directed acyclic graph where each node is a subgoal described in text (such as an inventory state) and each edge a dependency. Training then cycles between two phases.

- **Dream phase:** pick a branch of the graph that leads to a node at the edge of what is already verified and lies on the predicted route to the goal.
- **Wake phase:** execute the branch with one policy per subgoal (VPT with adapters, trained by PPO), explore to confirm or fix edges, and learn a fresh subgoal policy for every node that becomes verified.

## Results

Setup unless stated: the MineDojo environment, several random seeds, discrete crafting actions, and a cap of 6M training steps. Every figure is the authors' own (self-reported).

- With LLM guidance the stone pickaxe needs 2.6M steps instead of 32M (Table 2). The extraction gives the reason as DECKARD without an LLM finetuning about fifteen collectable-item policies.
- Codex (code-davinci-002, 2-shot prompt) recipes: exact-match ingredients and quantities 55% over 391 items and 69% over 37 tool items; collectable-versus-craftable label 57% overall and 100% on tools; wrongly inserted dependencies in 42% of items and missing dependencies in 35% (tools: 8% and 26%). The most common error was ingredient quantity.
- Without guidance, the cobblestone step with a wooden pickaxe takes 2x (no LLM) and 3x (VPT) as long as with it. Codex mistakenly marked glass as obtainable without tools, a claim the agent's own experience fixed.
- With artificially inserted or deleted edges in a ground-truth AWM (stone pickaxe, at least 3 seeds), DECKARD with LLM guidance still beat the no-LLM run; this is shown in a figure without numbers in the text.
- Other agents in Table 2 (Align-RUDDER 2M steps, VPT+RL 2.4B, DreamerV3 6M) differ in action space, rewards and shortcuts, so the comparison is loose.

## Limits

- Needs an environment already grounded in language (textual inventory state) and a given state abstraction; discovering one is left open.
- Only deterministic AWM transitions are handled, and the first experienced edge between two nodes is kept.
- The LLM is not queried during training, so it cannot re-plan. Robustness evidence is injected synthetic errors.
- Subgoal training uses a single world seed; the c0 value, compute and wall-clock time are not reported.

## See Also
- [[World Knowledge Model for Agent Planning]] — related
- [[Post-Training for Agents]] — related
