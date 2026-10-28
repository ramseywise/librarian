---
title: Hedging Belongs in the Gate, Not the Answer
tags: [patterns, rag, pattern]
summary: Agent-assist suggestions that were technically correct were still ignored because they were three times longer than human replies and hedged; express low confidence by routing to the confidence gate, and keep the generated answer short and direct.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/archived/rag-agent-template-research.md
---

# Hedging Belongs in the Gate, Not the Answer

A finding recorded in the playground repo's RAG-agent template research (2026-04),
taken from a first-generation agent-assist RAG system that drafted reply suggestions
for human support agents.

## What happened

The suggestions were **ignored even when their technical content was correct**. Two
causes:

- **Length.** Suggestions ran about **3× the length** of what agents actually sent.
- **Hedging.** They were full of "this could possibly…" and "please check…" phrasing.

Agents wrote their own direct replies and stopped reading the suggestions. Correctness
didn't save the feature: the output's *register* didn't match the job, so the human in
the loop routed around it.

## The mechanism

Hedging is the model expressing uncertainty **inside the answer**, where it costs the
reader effort and gives the system nothing to act on. A RAG pipeline with a confidence
gate already has a structural place for uncertainty: a low score routes to escalation,
HITL review or a "not sure" response. If the answer text also hedges, uncertainty is
paid for twice, once in the gate and once in every sentence. And the hedge isn't a
signal anything downstream can read.

## The rule for generation prompts

- Enforce **direct, actionable language** in the system prompt.
- **Cap response length** in config, not by hoping the model is brief. Calibrate the cap
  against the length of real human replies.
- **No hedging phrases.** If confidence is low, route to the confidence gate, and don't
  hedge in the answer.

This splits responsibilities: the policy layer decides *whether* to answer, and the
generator, once it is allowed to answer, answers plainly.

## See Also
- [[Confidence That Is Not a Probability]] — related (the gate needs a signal worth routing on)
- [[CRAG Retry Logic]] — related (the score-routed path that should carry the uncertainty)
- [[Copilot Learning Loop]] — extends (ignored suggestions as a feedback signal)
- [[Borderline-Band Sufficiency Probe]] — related (making the gate itself less brittle)
