---
title: Codified Context Three-Tier Infrastructure
tags: [harness, pattern]
summary: An experience report proposing an always-loaded constitution, domain-specialist agent specs and an on-demand knowledge base served over MCP, built for a roughly 100,000-line codebase.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-vasilopoulos-2026-codified-context.md
---

# Codified Context Three-Tier Infrastructure

Codified Context (Vasilopoulos, a February 2026 preprint) describes itself as both a systems paper and an experience report, written by one independent author. The argument is that manifests kept in a single file (CLAUDE.md, AGENTS.md) fail to scale to a codebase near 100k lines, and that agent-facing documentation should be handled as infrastructure that bears load, arranged in three tiers:

- **Tier 1, constitution**: about 660 lines and always loaded, holding conventions, build commands and checklists, failure modes already known, and trigger tables that send areas of the code to agents.
- **Tier 2, domain-specialist agents**: 19 specs, more than half of each being project-domain knowledge.
- **Tier 3, cold knowledge base**: 34 subsystem specs served on demand through an MCP server that matches keywords and exposes five search tools. Spec documents carry "known failure modes" tables of symptom, cause and fix.

## Evidence

All numbers are the author's own and describe usage, not correctness. Setup: one developer building one C# multiplayer game of 108,256 lines, across 283 sessions over 70 part-time days, using only Claude Code, and with no baseline.

- The context infrastructure is 54 files and about 26,200 lines, 24.2% of code size (0.6% constitution, 8.6% agents, 15.0% knowledge base). The author says this ratio is particular to the project and is not a target.
- Interaction logs (1,457 files, with some early ones lost; agent-chain data span a window of 31 days): 2,801 human prompts and 1,197 agent invocations, about 6 autonomous turns per prompt; 57% of 757 classifiable invocations were project specialists; 1,478 retrieval calls across 218 sessions.
- Maintenance is self-reported at about 5 minutes per session touching a spec plus a biweekly review of 30 to 45 minutes.
- Four hand-picked case studies, each anecdotal: a save spec used in 74 sessions with no save-related bugs reported, a UI pattern applied correctly on the first attempt, a retrieval query returning nothing that exposed an undocumented subsystem, and a network-protocol agent that found three bugs that earlier attempts missed.
- The paper names specification staleness as the primary failure mode and says agents trust documentation absolutely, so out-of-date specs fail silently.

## Limits

- No baseline, no tier ablation and no controlled benchmark; the paper says no causal claims are made and developer learning cannot be separated out.
- One developer, project and tool; the domain is unusually documentation-heavy.
- Outcome claims are self-reported and the author is the only judge. A context-drift detector is described without results, and the claimed routing redundancy is not measured.
- Retrieval is basic keyword substring matching.
- The extraction notes no model versions are given and an early draft used AI assistance.

## See Also

- [[Harness Anatomy]] — prerequisite-for
- [[Progressive Disclosure and Skill Packs at Library Scale]] — related (on-demand loading of cold knowledge)
- [[AGENTS.md Context File Evaluation]] — related
- [[Harness Handbook Behavior-Organized Map]] — related
