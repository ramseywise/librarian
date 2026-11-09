---
title: Forgetting Reset for Discovery Teams
tags: [loop, pattern]
summary: "At the end of each round a discovery loop discards every agent session and the whole search history, keeps only the best candidate and its score, and starts fresh agents from it; the paper argues long sessions anchor agents to their own past attempts."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-tan-2026-scaling-discovery-requires-forgetting.md
---

# Forgetting Reset for Discovery Teams

Tan et al. (UC Berkeley and collaborators, October 2026) study autoresearch loops where a verifier scores each candidate. Scaling by one agent, by parallel agents or by a team all stall as session history grows, and the authors' explanation is anchoring: an agent that remembers its failed attempts proposes smaller and smaller edits.

## Mechanism

At each round end, discard all sessions and the entire search state (candidate history, scores, feedback). Keep one candidate and its score. A new agent starts from it with a blank context and the original opening instructions. In the experiments, a team of four agents ran three forgets, so four rounds.

Design details the paper gives: search state (candidates with scores, held as commits in a repository) is kept separate from session state (messages and reasoning). Peers see one another's candidates and scores as files, with no orchestrator and no direct messaging between agents. Each turn ends with the agent's edit; a separate process scores it, so the agent never judges its own change.

## Results (self-reported)

Setup: a Pi agent on DeepSeek V4.1 Flash, $20 to $40 per replicate with equal spend across configurations, and 3 runs on each of 4 tasks (AHC014, a VLIW kernel, Frontier-CS Q171, nanochat-autoresearch).

- A team with forgetting beat four parallel agents by 10% on average and a single agent by 22%. Parallel agents gained nothing on nanochat.
- From one plateaued AHC014 state, continuing gave +1.4% at $24.67 and forgetting gave +9.2% at $15.32 (team of four).
- On AHC014 the gains after forgets 1, 2 and 3 were +11.2%, +4.8% and +1.7%, so most of the value comes from the first reset.
- In a single-agent VLIW run, 532 of 763 turns yielded no candidate yet consumed 66.2% of the budget; the agent often declared a practical limit that a later run beat.
- Edits shrank from roughly 100 lines to a handful as a session grew; after a forget the median edit was 40 lines against 6 under continuation.

The practical reading for a loop designer: the summary note an agent carries forward may be what sustains the anchoring, and a loop that keeps only the best artifact and its score removes that channel. This sits against memory-heavy designs such as [[Rehearse Focused Outcome Memory]] and next to the termination question in [[Loop Termination Design]].

## Limits

- One model, one harness, three runs per task; variance is large (+9.2% with a spread of 6.9%).
- The mechanism (anchoring) is supported by correlational trajectory statistics, not an intervention that isolates it.
- Every task has a numeric scorer and a bounded best value, so discovery with no verifier is untested.
- Only the best candidate is kept; the paper does not test keeping a short summary or notes, and the number and schedule of forgets were fixed.
- The abstract's "up to 15% and 39%" figures are maxima over tasks, not the means above.

## See Also
- [[Loop Termination Design]] — related
- [[Rehearse Focused Outcome Memory]] — alternative-to
- [[Loop State File]] — related
- [[Recursive Self-Improvement]] — prerequisite-for
