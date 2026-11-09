---
title: "AutoMem Coordinate-Keyed File Memory"
tags: [memory, pattern]
summary: "AutoMem optimises the scaffold around a file-system memory (coordinate-keyed upsert instead of append, auto-synced state files) and trains a memory specialist; on three BALROG games scaffold optimisation lifted a 32B agent 1.9x to 3.7x (self-reported), but the scaffold was tuned on the evaluation seeds and bundles hand-written game logic."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2026-automem.md
---

# AutoMem Coordinate-Keyed File Memory

AutoMem (a 2026 preprint) treats memory as a trainable skill of a game-playing agent that reads and writes a file system through three actions: append, search and an upsert into a map. A meta model rewrites the scaffold around that memory, and a LoRA memory specialist is then trained on the agent's own traces while the gameplay model stays frozen. The scaffold lesson is that verbatim-append stores bloat and hurt, so entries are keyed by coordinate and overwritten rather than appended, and state files are synced automatically.

## Results

Setup: Qwen2.5-32B-Instruct on BALROG games, 10 seeds (5 episodes for NetHack), mean with standard error; Claude Opus 4.6 as scaffold-writing meta model. All figures are self-reported.

- Scaffold optimisation alone, progression percentages from the first file-memory scaffold: Crafter 25.0 to 47.27, MiniHack 7.5 to 27.5, NetHack 0.42 to 1.57.
- Memory-proficiency training added a smaller amount (51.36, 30.0, 1.85); on MiniHack and NetHack the gains are inside one standard error.
- Coordinate-keyed upsert cut per-step memory growth on NetHack from 138 to 6 characters.
- Training shortened memory writes per search in the logging phase (for example Crafter 0.84 to 0.39).
- Sliding-window baselines scored 19.55, 2.50 and 0.00; frontier-model and 72B numbers are copied from the BALROG leaderboard, not rerun.

## Limits

- The extraction notes the evaluation seeds also decided which scaffold revisions were accepted, so scaffold numbers are optimistic. It includes no no-memory run, full-context run or retrieval baseline, and nothing that separates memory content from scaffold hints; its appendix shows much of the gain is hand-written game logic from the meta model (craft preconditions, directives, preloaded knowledge, action blocking).
- Memory is episodic only, games only, optimised per game; NetHack scores are under 2% on five episodes, and no cost accounting is given for the frontier meta models.

## See Also
- [[Memory Store Operations]] — prerequisite-for
- [[Memory Lifecycle]] — prerequisite-for
- [[MemGPT / Letta Virtual Context Memory]] — related (file-style memory tools for an agent)
