---
title: Sleep Learning
tags: [loop, memory, pattern]
summary: "The offline half of a dual loop: the online loop only appends immutable evidence, and a scheduled consolidation pass (trigger, orient, consolidate, validate, prune and re-index) turns it into long-term knowledge — so one lucky success or injected page can't immediately rewrite behaviour."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop-engineering--notes--08-self-improving-loops.md
---

# Sleep Learning

"Sleep learning" names the offline half of a **dual loop** (term from *AI Agents in Depth*). The
**online loop** finishes tasks and appends immutable evidence; it never rewrites the production
agent. The **offline loop** runs when a threshold is reached — elapsed time, new trajectories,
storage used, or error rate.

## Five steps

1. **Trigger** on the threshold, while no high-priority online work is running.
2. **Orient**: read current knowledge, prompts and Skills, and the boundaries that may not change.
3. **Consolidate**: merge duplicates, mark conflicts, prefer local patches.
4. **Validate** on transfer, retention and safety sets; high-risk writes wait for a human.
5. **Prune and re-index**: expire or archive unused or contradicted capabilities, keeping
   provenance and rollback versions.

Separating collection from consolidation means one lucky success or one injected web page can't
immediately rewrite long-term behaviour, and consolidation can run in larger batches on cheaper
models. The same capture-then-consolidate shape appears in this wiki's own build findings as
[[Single Writer, Offline Consolidation]]. Shipping examples: Claude Code's auto memory (a bounded
`MEMORY.md` index plus on-demand topic files) and Hermes (bounded memory files, FTS session
search over raw messages, background Skill review, a Curator that prunes after a snapshot).

## The maintenance list

- Merge duplicate experience, keeping provenance.
- Move local rules out of the global prompt into Skills.
- Write prompts like an onboarding handbook, not "99 iron rules".
- Re-validate long-unused tools.
- Delete knowledge that new evidence contradicts.
- Retrain LoRAs from the base model rather than stacking them.

## Voyager: the complete loop

Voyager combines an **automatic curriculum** (what to learn next), a **skill library** of
verified, composable code (what was learned), and **iterative prompting with environment
feedback** (how to tell it worked) — 3.3× the unique items and up to 15.3× faster tech-tree
milestones than baselines. Remove any one of the three and the loop stops compounding.

## See Also
- [[Evolve Loop]] — extends
- [[Four Media for Agent Lessons]] — extends
- [[Single Writer, Offline Consolidation]] — alternative-to
- [[Memory Lifecycle]] — extends
- [[Self-Modification as a Release Process]] — extends
