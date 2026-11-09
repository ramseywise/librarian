---
title: Confucius Code Agent
tags: [harness, pattern]
summary: A coding-agent scaffold combining file-based working memory, threshold-triggered structured summarisation, a cross-session note-taking agent and a meta-agent that tunes tool prompts.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wong-2025-confucius-code-agent.md
---

# Confucius Code Agent

Confucius Code Agent (CCA, Wong et al., Meta and Harvard, a preprint with a February 2026 version) argues that scaffolding matters as much as the model for long software-engineering tasks. The authors built the system.

## Mechanisms

- **Compression:** once context approaches thresholds that can be configured, a separate Architect call swaps the older turns for a structured summary (goals, decisions, errors and open TODOs) while recent raw messages stay in a rolling window.
- **Externalised state:** a per-instance memory tree with analysis, implementation-summary and todo files.
- **Cross-session notes:** an asynchronous note-taking agent reads trajectories and writes Markdown notes, with front matter, an index, and project and shared folders. Failed attempts are recorded in the notes alongside successes.
- **Meta-agent:** tunes tool-use prompts.
- **Context separation:** the agent receives compressed results while humans can read full traces.

## Results

Self-reported by the authors.

- SWE-Bench-Pro, public split of 731 tasks, scored as mean Pass@1 across 3 seeds: with Claude 4.5 Sonnet CCA reaches 52.7 against 45.8 for Live-SWE-Agent and 43.6 for SWE-Agent; with Claude 4.5 Opus 54.3 against 52.0 for Anthropic's scaffold (a reported figure, not a rerun); with GPT-5.2 59.0 against 56.0 (also reported).
- SWE-Bench-Verified has 500 tasks; with Claude 4 Sonnet, CCA reaches 74.6, OpenHands 72.8 and SWE-Agent 66.6.
- Ablation on a 100-example Pro subset, restricted to the tasks that both variants finished: Claude 4.5 Sonnet 44.0 without context management and simple tools, 51.0 with advanced tools, 51.6 with context management added (+0.6). On Claude 4 Sonnet context management gave 42.0 to 48.6.
- Summariser quality on 50 long instances where summarisation fired: Haiku 3.5 resolved 22 and Sonnet 4 resolved 26.
- Notes carried across sessions (151 instances, same tasks rerun): turns fall from 64 to 61, tokens from 104k to 93k, and the resolve rate rises from 53.0 to 54.4.

## Limits

- Compression is ablated only inside the full system on a small subset, without variance, and the subset has survivor bias.
- The note result reruns the same preselected tasks, so it shows reuse on the same task rather than transfer.
- No comparison of compaction against context reset, and no study of note staleness or conflicts.
- Competitor numbers for the Anthropic and OpenAI scaffolds are reported, not reproduced.
- The extraction notes the largest measured gain came from tool-use refinement, not context management.

## See Also

- [[Context Compaction]] — prerequisite-for
- [[Harness Anatomy]] — prerequisite-for
- [[SWE-agent Agent-Computer Interface]] — related (a baseline)
- [[OpenHands Generalist Agent Platform]] — related (a baseline)
