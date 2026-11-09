---
title: Agent Communication Protocol Taxonomy
tags: [mcp, comparison]
summary: "Sander et al. classify nine open-source agent protocols (MCP, A2A, LAP, agents.json, Agora, ANP, LMOS, ACP, agntcy) on five dimensions and forecast a layered stack; the work is qualitative, hand-classified, and its tables contradict parts of its text."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-sander-2026-technical-taxonomy-llm-agent-communication.md
---

# Agent Communication Protocol Taxonomy

Sander et al. (a June 2026 preprint) built a taxonomy with the Nickerson method over five iterations. The sample was open-source, actively maintained protocols with a running implementation, so Agent Protocol (no commit since June 2024) and AITP (20 GitHub stars) were left out, as of 7 July 2025.

## Dimensions

Counterparty (agent or context), payload, interaction state, discovery mechanism and schema flexibility. Persistent state, initiative flow and simplicity were considered and dropped; persistent state because a protocol does not decide what nodes store.

## Classification (authors' reading of specs; no tests)

- **MCP:** context counterparty, stateless, static discovery (the base address must be known), structured payload, multiple schemas.
- **A2A:** agent counterparty, session state tied to tasks, centralized discovery by a registry option, hybrid payload, multiple schemas; three discovery routes all use a JSON Agent Card, and A2A positions itself as complementary to MCP.
- Across the nine: discovery is 4 centralized (A2A, ANP, ACP, agntcy), 4 static (MCP, LAP, agents.json, Agora) and 1 hybrid (LMOS). All agent-to-agent protocols have session state and hybrid payloads (7 of 9). Schemas: 2 single, 5 multiple, 2 evolving (Agora, ANP).
- Using the communication trilemma of Marro et al. (versatility, efficiency, portability), the paper maps MCP-style rigid protocols to efficiency and portability and evolving-schema protocols to versatility at an overhead cost that is asserted, not measured.
- By the authors' reading none of the nine offers privacy safeguards, compliance checking or enforcement of policy; security was not one of the dimensions.
- **Forecast, not finding:** a layered, federated stack like OSI (identity and transport, discovery, execution, interaction, deliberation), with MCP at execution.

## Limits

- Authors concede there are no dimensions for authentication and security, protocol detail, or policy.
- Nine protocols, a mid-2025 snapshot in a June 2026 paper; one rater, no experiments, no latency, token or accuracy numbers; the paper says Anthropic has not endorsed A2A or agntcy as MCP extensions, a claim that has probably dated.
- Internal inconsistencies noted by the extraction: the text says only LMOS is truly decentralized yet Table 1 marks LMOS hybrid and none decentralized; Table 2 calls Agora decentralized yet lists its discovery as static; the text calls ANP peer-to-peer, but it is classified centralized; the abstract calls decentralized discovery rare whereas the tables contain none; the "7 of 9" with multiple schemas includes the two evolving protocols; and the figure puts MCP alone at the execution layer although the stack is described as not an observed fact.
- Cite it for the taxonomy and table, not the forecast.

## See Also
- [[Agent Interoperability Protocol Stack]] — related
- [[A2A Agent Protocol]] — prerequisite-for
- [[MCP Protocol]] — prerequisite-for
- [[Tool Poisoning and Protocol-Level Attacks on Agents]] — related (security was not a dimension here)
