---
title: Proposer-Reviewer and Sidecar Gating
tags: [llm, agents, infra, comparison]
summary: "Two shapes for putting a second model in front of risky tool calls when no human can be in the loop — a serial proposer–reviewer that sees intent, and a parallel sidecar that sees only structured call fields — plus the design rules both need."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--04-execution-boundaries.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--notes--03-tool-design.md
---

# Proposer-Reviewer and Sidecar Gating

When a human cannot be in every loop, put a **second model in front of risky calls**. Two
shapes (from Li, *AI Agents in Depth*, ch. 4–5):

| | **Proposer–Reviewer** | **Sidecar** |
|---|---|---|
| **Sees** | The proposed action plus enough context to judge intent | Only the structured tool-call fields (name, arguments) |
| **Runs** | In series — the proposer waits for the verdict | In parallel with streaming; gates only the call itself |
| **Best for** | High-stakes, low-frequency actions | Every call to a risky tool class, at low latency |
| **Injection exposure** | Higher — it reads the conversation | Lower — untrusted text never reaches it |

The trade is the classic one: **more context buys better judgment of intent and costs
injection exposure.** A sidecar that reads only `{tool, args}` cannot be talked into
anything by a poisoned document, because the document never reaches it.

## Design Rules

- **Reviewer from a different model family, at similar capability.** A same-family reviewer
  shares the proposer's blind spots. (This is a different axis from the *asymmetric QA* rule
  in [[Verification Loops]], which is about capability at an output-quality gate; here the
  point is decorrelated errors at an action gate.)
- **Return a rejection as a tool result, with the reason**, so the proposer revises rather
  than retrying blindly.
- **Circuit breaker:** after N consecutive rejections, escalate to a human instead of looping.
- **Pre-approve or post-validate.** Review *before* execution for irreversible actions; for
  reversible ones let it run and validate the result — possibly in another modality, such
  as checking a screenshot after a UI action.

## Make the Check Invisible

Show a side-effect-free progress hint ("Reading `src/main.py`…") while the sidecar check
runs. Most checks finish before the user notices; a failed check just turns the hint into
"waiting for confirmation". **Nothing has to be rolled back**, because nothing ran.

## Where It Sits

The gate is one leg of the structural defence against the [[Lethal Triad]], alongside
egress control. It complements, not replaces, deterministic hooks: hooks hold the rules you
can write down; a reviewer covers the judgement calls you cannot.

## See Also
- [[Execution Boundaries and Guardrails]] — extends (model-based gating when HITL is not available)
- [[Lethal Triad]] — related
- [[Verification Loops]] — alternative-to (output review vs action review)
- [[Canary Testing for Permission Boundaries]] — related (test that the gate fires)
