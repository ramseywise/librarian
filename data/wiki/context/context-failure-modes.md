---
title: Context Failure Modes
tags: [llm, agents, concept]
summary: Five distinct context failures — rot, poisoning, distraction, clash, injection — with separate mechanisms and fixes, routinely misdiagnosed as each other or as "the model isn't smart enough".
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--02-context--notes--07-context-failure-modes.md
---

# Context Failure Modes

The diagnostic note. **When an agent misbehaves, the cause is usually in the window, not
the weights.**

## The Taxonomy

| Failure | Mechanism | Signature |
|---|---|---|
| **Rot** | Occupancy grows; recall degrades | Correct earlier in session, wrong later; facts present but unused |
| **Poisoning** | A false statement enters context and is treated as ground truth | Agent confidently repeats and builds on something wrong |
| **Distraction** | Volume of marginal content crowds out signal | Agent fixates on a tangent; ignores the actual request |
| **Clash** | Two contradictory pieces coexist | Inconsistent answers across turns; arbitrary resolution |
| **Injection** | Adversarial instructions arrive as data | Agent follows instructions the operator never gave |

## Rot

Mechanism in [[Why Context Is Finite]]. Diagnostically:

**Signature.** Quality degrades monotonically with session length. The agent forgets a
constraint it obeyed twenty turns ago. Information verifiably present isn't used.

**Fix.** Compaction at phase boundaries; tool-result clearing; move state to disk. **Not a
bigger window** — that delays onset without preventing it.

**Anti-fix.** Repeating the constraint more forcefully. This adds tokens, which is the cause.

## Poisoning

A hallucination, stale fact, or wrong retrieval enters context and is subsequently treated
as established truth. Everything downstream inherits the error — and the error is now
**self-reinforcing**, because it sits in the window as apparent fact rather than as a claim
under evaluation.

**Memory makes this durable.** A poisoned entry written to long-term memory is re-injected
every future session: a single hallucination becomes a permanent false belief.

**Sources.** Model hallucination captured into notes; outdated documents retrieved without
freshness checks; a tool returning stale data; a summarization step introducing a detail
the source didn't contain.

**Fix.**
- Freshness filters at the retrieval boundary — see [[Context Retrieval Strategies]]
- Citation verification — every claim resolves to a real, retrievable source
- Memory hygiene: deletable, auditable entries — see [[Memory as Context]]
- **Distinguish *observed* from *inferred* when writing notes.** An agent recording
  inference as observation poisons its own future context.

## Distraction

Enough marginally relevant content accumulates that attention drifts to it. Distinct from
rot: the content here is *individually plausible*, not merely voluminous. Retrieving 40
relevant-ish documents when 3 answer the question is distraction.

**Signature.** The agent produces a competent answer to a question *adjacent* to the one
asked, latching onto a detail from a retrieved document and building around it.

**Fix.** Rerank hard and send narrow. Dynamic k scaled to task complexity.
Query-conditional compression.

## Clash

Two pieces of context contradict and both are present. The model resolves arbitrarily and
without flagging — **worse than either input alone, because the output looks confident.**

**Common sources.** Two retrieved docs from different versions. A memory entry
contradicting the current codebase. A system-prompt rule contradicting a project
convention. A user correction mid-session that doesn't invalidate the earlier statement
still sitting in history.

That last one is subtle and common: a user says "actually, use pnpm" at turn 12, but "we
use npm" from turn 3 is still in the window. Both are context; nothing marks one as
superseded.

**Fix.**
- Conflict detection at the validation stage — surface rather than silently inject both
- Explicit precedence: **system > developer > user > retrieved**, and *later* supersedes
  *earlier* within a tier
- **On compaction, resolve rather than carry** — record the *settled* fact, not both sides
- Version-pin retrieved docs so contradictions appear as version differences

## Injection

Structurally different from the others: **an attack, not a degradation.** The root cause is
that context has no type system — instructions and data are the same tokens.

Attack surface grows with every context source: retrieved documents, tool results, web
pages, user uploads, sub-agent summaries, MCP server responses, file contents, error
messages.

**Layered defences — none sufficient alone:**

1. **Structural delimiting** — wrap untrusted content; instruct that content inside is
   data, never instructions
2. **Trust zones** — user input untrusted, retrieved/tool output semi-trusted, agent state
   trusted. **Never promote a zone implicitly.**
3. **Instruction hierarchy** — system prompt outranks retrieved content, unconditionally
4. **Isolation** — process untrusted content in a sub-agent whose window is discarded (see
   [[Multi-Agent Context]]) — but treat its summary as data too
5. **Code-level enforcement** — an injection can talk a model out of a rule; it cannot talk
   a permission hook out of denying a write
6. **Egress control** — injection is mostly harmful when it can *act*: network allowlists,
   confirmation gates on irreversible operations, no credentials in reachable context

**Defence 5 is load-bearing.** Every context-level defence is probabilistic; only
code-level controls are guarantees. Full treatment in [[Prompt Injection]].

## Diagnostic Flow

1. **Print the actual window.** Not what you think you assembled — what was sent. Most
   context bugs are visible immediately and are *assembly* bugs, not model failures.
2. **Check occupancy.** Above ~50%, suspect rot and distraction first.
3. **Search for contradictions.** Grep the window for the claim the agent got wrong; if it
   appears twice with different values, it's clash.
4. **Check provenance.** Trace the wrong fact to its source. No legitimate source →
   poisoning or injection.
5. **Test in isolation.** Same task, minimal context. Works → context problem. Still fails
   → prompt or capability problem.

**Step 5 is the one that gets skipped**, and it's the one that separates a context problem
from a prompt problem.

## See Also
- [[Context Anatomy]] <!-- auto-linked -->
- [[Context Engineering]] — part-of
- [[Why Context Is Finite]] — depends-on
- [[Prompt Injection]] — extends
- [[Context Compaction]] — mitigated-by
