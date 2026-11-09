---
title: Tool Poisoning and Protocol-Level Attacks on Agents
tags: [mcp, concept]
summary: "Two 2025 surveys describe attacks that ride the agent-to-tool and agent-to-agent channel: poisoned tool descriptions, tampered tools, retrieved-document injection, chained tool calls and loop exhaustion; one survey shows five single-run demos and Ferrag et al. collect second-hand attack rates."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kong-2025-survey-llm-driven-ai-agent.md
  - data/raw/papers/2026-11-06-ferrag-2025-prompt-injections-protocol-exploits.md
---

# Tool Poisoning and Protocol-Level Attacks on Agents

Both sources are surveys. Their threat model is the communication layer between agent, tool and peer, not sandbox or runtime isolation.

## The agent-communication survey (arXiv June 2025, v4 November 2025)

The survey classifies 19 communication protocols and argues prompt injection is a flaw at the semantic layer where traditional security is blind. Its only empirical content is five single-case demos, four on MCP with Claude as the client (Sonnet 3.7, Sonnet 4.0 and Opus 4) and one on an A2A sample client:

- **Tool poisoning:** an instruction hidden inside the description of an MCP "read file" tool made the agent read the SSH key directory and email the contents to an attacker mailbox.
- **Command injection:** a docstring asked the agent to conceal deletions; it deleted a file and left the others out of its listing. When the concealment instruction was absent, it listed the other files, which would have exposed the attack.
- **Shell persistence:** the filesystem server did not block a request to open an unauthenticated shell on port 4444 and keep it alive through .zshrc.
- **Indirect injection:** a poisoned document in a Chroma vector store led the agent to run `env` and post the output to Slack; the user prompt had said to perform any returned actions.
- **A2A description tampering:** a client with two weather and flight agents, one malicious, was first run on 20 baseline queries without tampering; after the agent description was tampered with, it always selected the malicious agent.

Defences are prospects, untested: sandboxed tools with permission gating and human confirmation, a sandboxed and authenticated controller in client-server networks, draft-only outbound actions with logging and rollback, a coordinator that kills looping tasks after N rounds, token budgets and output truncation, re-validating authorization at every receiving agent, and provenance on cross-agent context.

## Ferrag et al. (arXiv June 2025, v2 December 2025)

A taxonomy survey that ran no experiments. It rates input manipulation and protocol flaws as low-privilege and highly feasible (an author judgement). Its figures are second-hand and the authors say they are not comparable: adaptive attacks bypassed eight prompt-injection defences with above 50% attack success in Zhan et al.; PoisonedRAG 90% with 5 injected texts; DemonAgent near 100% with 0% detection. It covers the GitHub MCP "toxic agent flow" (a malicious public issue leads the agent to leak private repository data in a public pull request, per an Invariant Labs blog), 11 CVEs in agent tooling, MCP vectors (unauthorised calls, infinite tool-call loops, confused-deputy credential theft, SQL injection through arguments), and recursive task spawning modelled as resource exhaustion with a task-tree cap and rate threshold.

## Limits

- The agent-communication survey: no success rates or variance beyond the 20-query baseline, one model family, no defence run against any attack; the authors say agent communication research is nascent. Adoption statistics are third-party and unverified.
- Ferrag: every number is second-hand and mixes models, datasets and targets, including chat and training attacks that are not tool boundaries; the claimed expert review has no detail; sandboxing gets one sentence; the extraction notes that the survey files the Codex CLI sandbox-escape CVE under "Model Compromise", a debatable label, and that MCP is misnamed in places.
- Both are current to mid-2025 specs.

## See Also
- [[MCP Server Security Patterns]] — prerequisite-for
- [[Lethal Triad]] — prerequisite-for
- [[Agent Security Risk Taxonomy]] — prerequisite-for
- [[Execution Boundaries and Guardrails]] — related
- [[Agent Communication Protocol Taxonomy]] — related
