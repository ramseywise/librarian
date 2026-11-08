---
title: Bad Memory File-Based Prompt Injection
tags: [memory, reference]
summary: "A 2026 study plants a malicious rule in a trusted memory file (CLAUDE.md, AGENTS.md, behavior or knowledge files) and measures how often four models act on it and whether it survives later sessions; success and persistence vary widely by model, goal and attack order, and the lowest attack success did not mean the lowest persistence."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-gadgil-2026-bad-memory.md
---

# Bad Memory File-Based Prompt Injection

"Bad Memory" (a 2026 preprint) studies prompt injection that lives in an agent's memory files. The authors liken it to stored versus reflected cross-site scripting: a payload planted once in a trusted file can steer the current session and later ones. They assume the payload is already present; early attempts at getting an agent to copy a payload from untrusted outside content into its memory were unreliable.

## Setup

A synthetic workspace for a fictional user, run on Claude Code with Haiku 4.5 and Opus 4.7 and on Codex with GPT-5.2 and GPT-5.5, 10 trials in each cell. Three payloads, each tied to one file and goal: an SSH-key-reading snippet in the auto-loaded CLAUDE.md or AGENTS.md (credential exfiltration), a pinned package install (pyyaml 5.3.1) in a knowledge file (unauthorized tool use), and an "always recommend one card brand" rule in a behavior file. ASR (the source does not expand it) is the fraction of trials in which the probe carries out the attacker's intended action; persistence counts trials where the payload remains in memory afterwards. By the authors' account, ASR cannot be compared between goals.

## Results (all self-reported by the study's own harness)

- One probe, mean ASR across goals: 63.3% for Haiku 4.5, 30.0% for Opus 4.7, 23.3% for GPT-5.2 and 60.0% for GPT-5.5. For credential exfiltration alone, the rates were 80% (Haiku), 0% (Opus), 30% (GPT-5.2) and 0% (GPT-5.5); for unauthorized tool use they were 100%, 90%, 0% and 80%.
- Repeating one attack: Haiku's credential-exfiltration ASR climbed from 60% to 100% between the two probes. Opus refused both (0% each) but the payload stayed in memory in every sequence. Mean persistence was 96.7% for Opus, 86.7% for Haiku, 73.3% for GPT-5.5 and 50.0% for GPT-5.2.
- Chaining two different attacks (six orderings; persistence requires both payloads to survive): mean ASR was 18.3% for Opus, 22.5% for GPT-5.2, 41.6% for GPT-5.5 and 52.5% for Haiku, with mean persistence of 93.3% (Opus), 81.7% (Haiku), 40.0% (GPT-5.5) and 23.3% (GPT-5.2). Order mattered: after the tool-use attack, Opus's credential attack succeeded 70% of the time, and 0% in the reverse order.
- Qualitatively, Opus flagged the injected instruction as unsafe but left it in place, whereas Haiku and GPT-5.2 removed the brand rule and substituted a policy of their own. The authors note that later sessions may use weaker models.
- Untested defence proposals: treat memory as non-uniformly trusted, require review before files such as CLAUDE.md change, limit who may update memory, validate memory when a session starts, and tier memory so low-trust files cannot override safety rules.

## Limits

- A single synthetic workspace, 10 trials in each cell, no confidence intervals, only three payloads (each confounded with one file and goal), two harnesses, four models, and a longest sequence of probe, stabilization, probe. No defence was evaluated.
- Steering toward a card brand is arguably not malicious. The models' own explanations were produced after the fact and are not evidence of how they reasoned.
- No test put different models on one persistent memory, so the idea of a weaker model reading it later is speculation.

## See Also
- [[Agent Security Risk Taxonomy]] — prerequisite-for
- [[Lethal Triad]] — related
- [[Memory Lifecycle]] — prerequisite-for
- [[Catastrophic Remembering in Context Files]] — related (the same files, studied for growth rather than attack)
