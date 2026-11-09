---
title: LLM Action Grounding for Embodied Planning
tags: [prompting, concept]
summary: Two frozen-LLM planners for household tasks, one translating each generated step to the nearest admissible action and one retrieving examples and re-planning on failure; both report executability or low-data gains, with a correctness cost in the first (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-huang-2022-language-models-as-zero-shot.md
  - data/raw/papers/2026-11-08-song-2023-llm-planner.md
---

# LLM Action Grounding for Embodied Planning

Both papers use a frozen LLM to produce plans for an embodied agent and add a layer that ties the free-text output to what the environment can do.

## Zero-shot planners with action translation

Huang et al. (2022) prompt a causal Planning LM with the demonstration most similar to the query (by Sentence-RoBERTa embedding). At each step the LM draws k single-step samples. Each sample is translated to the closest admissible VirtualHome action, scored by cosine similarity plus beta times the mean log-probability, and that admissible action is then appended to the prompt. Evaluation is executability in VirtualHome plus human-judged correctness, on 88 held-out tasks, 7 scenes, one fixed prompt example, averaged over 3 runs with the best hyperparameter run reported (self-reported).

- Executability: Codex 12B goes from 18.07% (vanilla) to 78.57% (translated); GPT-3 175B from 7.79% to 73.05%. A fine-tuned GPT-3 13B baseline reaches 66.07%.
- Correctness (10 annotators): vanilla GPT-3 175B 77.86% against 70.05% for human-written plans; translation lowers it to 66.13% for GPT-3 175B and from 64.87% to 54.88% for Codex 12B. Plans both executable and judged correct by at least 70% of annotators: 35.23% for translated GPT-3 175B, 27.27% for translated Codex 12B and 65.91% for humans.
- Ablations on executability: no action translation 31.49% (Codex 12B), no trajectory correction 40.10% (GPT-3 175B), no dynamic example selection 50.86% (Codex 12B).
- A small model can seem executable just by echoing the prompt's example: vanilla GPT-2 1.5B reaches 39.40% executability but only 7.78% LCS.

## LLM-Planner

Song et al. (2023) have GPT-3 (text-davinci-003) write a high-level plan, a list of (action, object) subgoals, from a prompt holding 9 kNN-retrieved examples, with logit bias restricting the output tokens. If a subgoal fails, or every n steps, the model is prompted again with the completed subgoals and the objects detected so far (grounded re-planning). The planner is attached to the perception and low-level planner of HLSM on ALFRED (self-reported results below).

- With 100 paired examples (under 0.5% of 21,023), the valid-unseen success rate is 15.36 with step-by-step instructions, not far from the 18.28 of HLSM trained on the full data. Retrained on those 100 examples, HLSM completes almost nothing and FILM scores 0.00.
- SayCan with oracle object knowledge scores 9.88; LLM-Planner makes 7 GPT-3 calls per task on average against 22.
- Grounded re-planning adds 1.83 success rate over static planning on test unseen for goal-only instructions (13.41 against 11.58).
- Leave-one-out ablations on the 100 examples: removing the kNN retriever drops high-level plan accuracy from 40.59 to 17.48; removing logit bias gives 38.10, and removing both 13.43.

## Limits

- Huang et al.: correctness falls as executability rises; only mid-level grounding with an assumed low-level controller; no observation or feedback from the environment; one household environment; the LCS metric is a proxy; no significance tests; each method's hyperparameters were grid-searched on the same evaluation tasks.
- Song et al.: success hinges on the low-level planner and detector of HLSM (Heat and Place has 36% plan accuracy but 1.8% success); the SayCan baseline got oracle object knowledge and was not run on test; only text-davinci-003, a single run, no variance; grounding is only an object list and the re-planning interval n is not stated.

## See Also
- [[Task Decomposition Patterns]] — prerequisite-for
- [[Plan-and-Solve Prompting]] — related (in-text planning without environment grounding)
- [[Dynamic Tool Discovery]] — related
