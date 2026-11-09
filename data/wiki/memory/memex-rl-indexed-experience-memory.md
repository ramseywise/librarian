---
title: "Memex(RL) Indexed Experience Memory"
tags: [memory, pattern]
summary: "Memex(RL) lets an agent compress its working context into an indexed summary while archiving the complete text in a separate key-value store outside the context, then dereference an index exactly; RL training on a modified ALFWorld raised success from 24.22% to 85.61% (self-reported) while peak context stayed above its penalty threshold."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wang-2026-memex-rl.md
---

# Memex(RL) Indexed Experience Memory

Memex(RL), a 2026 preprint, makes memory handling part of the agent's own tool set, alongside the environment tools. Two operations matter. CompressExperience swaps the live context for a compact indexed summary (a status plus index-and-description pairs) and files the full text away in a separate key-value store. ReadExperience(index) looks one entry up by its index and restores that text to the context. The system prompt and the task itself stay uncompressed. The authors prefer indexed lookup to similarity search because an index names one specific archived item, which they say makes access auditable and avoids confusion among noisy near-duplicate fragments. Content can be archived two ways: the model writes it, or the model gives start, mid and end text anchors and the system stores the span they identify exactly as it appeared.

## Training

The reward is task success with three subtracted penalties, each scaled to the unit interval: overflowing the context threshold, repeating tool calls, and malformed calls. A status line reporting working and total context against the threshold is appended each step, so compression timing is learned rather than forced. The trajectory is cut at each compression into segments that share the terminal reward, which lets the write policy be credited for effects that appear later (group-relative advantage).

## Results

Setup: Qwen3-30B-A3B-Thinking-2507, a modified ALFWorld in which admissible commands and the initial room description are hidden and summaries are capped at 300 tokens, 3,553 training tasks, 8K penalty threshold. All figures are self-reported.

- Task success rose from 24.22% to 85.61%, and peak working context fell from 16,934 to 9,634 tokens. The comparison is the same agent loop before and after RL, not another memory method.
- During training, CompressExperience calls per episode fell from about 6.5 to 3 and ReadExperience calls rose from about 1 to 6-7.
- Peak context after training still exceeds the 8,000-token threshold, so the budget is approached, not met.
- A theorem says that if the summary is decision-sufficient within a bound, bounded reads match a full-context policy; the authors present it as a regime characterisation, not a learnability guarantee.

## Limits

- Single environment, deliberately modified so the agent must depend on memory. No comparison with other memory methods.
- Training rollout success (over 90%) exceeds the held-out figure; the theory's sufficiency assumption is strong.

## See Also
- [[Memory Lifecycle]] — prerequisite-for
- [[Memory Store Operations]] — prerequisite-for
- [[MemGPT / Letta Virtual Context Memory]] — alternative-to (agent-managed paging of context)
