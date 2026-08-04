---
title: Protocol-Driven Multi-Agent Collaboration
tags: [agents, infra, pattern]
summary: "Why multi-agent coordination has to be a protocol rather than a conversation — the nine failure modes conversational handoff produces, the six things a protocol must define, and the three foundations: communication protocol, task graph, and isolation boundary."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--agents-design.md
---

# Protocol-Driven Multi-Agent Collaboration

The governing rule, and the cleanest statement of the multi-agent coordination problem:

> **Use natural language inside a task, but use protocols to coordinate tasks.**

The split is between two uses of language that look identical and behave completely
differently. Inside a task, natural language is the right interface — it is expressive,
tolerant of ambiguity, and what the model is good at. *Between* tasks, those same
properties are defects: coordination needs unambiguous state, and a medium that tolerates
ambiguity will produce it.

## The nine failure modes of conversational coordination

When agents coordinate only through conversational instructions, the source enumerates
what goes wrong:

1. An agent forgets what it committed to do.
2. Two agents believe they own the same task.
3. An agent starts before its dependency is complete.
4. A result is delivered but never acknowledged.
5. A failed task is silently treated as completed.
6. Two workers modify the same files.
7. A retried request is executed twice.
8. The orchestrator cannot determine the current global state.
9. The system cannot recover reliably after a crash.

Read as a list these look like nine separate bugs. They are not — **every one is a
distributed-systems failure with a known name**: lost update, split ownership, missing
happens-before, unacknowledged delivery, silent failure, write conflict, non-idempotent
retry, no global snapshot, no recovery log. Multi-agent systems are distributed systems,
and building one on conversational handoff is building a distributed system with no
protocol, which is why the failures are the classical ones rather than novel LLM ones.

That reframe is the page's main claim, and it has a practical consequence: **the fixes are
also the classical ones.** You do not need agent-specific research to solve #7; you need
idempotency keys.

## The six things a protocol must define

For reliable collaboration, the system must define:

1. **What messages mean** — a shared vocabulary, not free text
2. **Which state transitions are valid** — a task cannot go from `pending` to `done`
3. **Who owns each task** — exactly one owner at a time
4. **Which tasks depend on which others** — declared, not inferred
5. **What files or resources each agent may modify** — a write set per agent
6. **How failures, retries, acknowledgements, and recovery work** — the unhappy paths, specified

Item 6 is the one usually skipped, and skipping it is what produces failure modes 5, 7,
and 9. A protocol that specifies only the happy path is a convention.

## The three foundations

The six requirements collapse into three mechanisms:

| Foundation | Defines | Prevents |
|---|---|---|
| **Communication protocol** | How agents send requests, return results, report failures, and acknowledge state changes | 1, 4, 5, 7 |
| **Task graph** | What work exists, who owns it, and which tasks depend on which | 2, 3, 8 |
| **Isolation boundary** | Which files, branches, tools, and external resources each agent may modify | 6 |

**The communication protocol** is more than a message schema — the requirement that
failures are *reported* and state changes *acknowledged* is what distinguishes it from a
typed function call. An unacknowledged result is indistinguishable from a lost one, and
an unreported failure is indistinguishable from success. Typed I/O between agents is
covered in [[Multi-Agent Orchestration Patterns]]; the protocol layer adds the delivery
semantics on top.

**The task graph** is the piece most often absent, because in a single-agent system the
plan lives in context and that suffices. It stops sufficing the moment two agents need the
same answer to "what is the current state," which context cannot provide — each agent has
a different one. The task graph is the **externalized shared state** that makes global
questions answerable, and it is why orchestrator-holds-plan architectures exist. See
[[Multi-Agent Context]].

**The isolation boundary** is the enforcement half. Declaring which files an agent may
modify (requirement 5) is documentation until something rejects a write outside the set —
the [[Agent Deployment Anti-Patterns]] point about mechanisms versus expectations applied
to concurrency. Worktrees are the usual implementation for code; see
[[Execution Boundaries and Guardrails]].

## Hallucinations amplify under multiple agents

A distinct multi-agent risk, separate from coordination:

> Hallucinations amplify each other under multiple agents.

The mechanism is trust asymmetry. An agent applies more scrutiny to user input than to
another agent's output, so a fabrication that would have been caught at the input boundary
propagates freely once it is inside the system — and each hop makes it look more
established. The stated mitigation is **cross-validation**: have the claim confirmed by an
agent that did not receive it from the originator.

This connects to R5 (cascading hallucination attacks) in the
[[Agent Security Risk Taxonomy]] — the security framing of the same mechanic. It is also
the argument for verifying at handoff boundaries rather than only at the final output,
since a handoff is exactly where the trust asymmetry applies.

## Minimum viable subagent

The closing principle, which is the least-privilege rule stated for three resources at once:

> Give each subagent the minimum context, authority, and execution budget required to
> complete one clearly defined task.

Context, authority, and budget are usually managed separately — context by the assembly
layer, authority by permissions, budget by the loop controller — but they fail together.
An agent with excess context makes decisions outside its task; with excess authority it
acts on them; with excess budget it keeps going. **The three are one constraint viewed
from three angles**, and scoping one while leaving the others open leaves the failure
available.

## See Also
- [[Harness Orchestration]] <!-- auto-linked -->
- [[Agent Interoperability Protocol Stack]] <!-- auto-linked -->
- [[Graph Engineering]] <!-- auto-linked -->
- [[Agentic Engineering and the New SDLC]] <!-- auto-linked -->
- [[Task Decomposition Patterns]] — prerequisite-for (the cut this protocol coordinates)
- [[Multi-Agent Orchestration Patterns]] — complements (topologies and typed I/O contracts)
- [[Multi-Agent Context]] — implements (externalized plan state and isolation)
- [[Agent Security Risk Taxonomy]] — complements (R11–R13, the same boundary from the threat side)
- [[Execution Boundaries and Guardrails]] — implements (the isolation boundary, mechanically)
- [[Production Reliability Primitives]] — extends (durable messaging, idempotency, explicit state in production)
