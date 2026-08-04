---
title: Agent Security Risk Taxonomy
tags: [infra, agents, reference]
summary: "The sixteen agentic security risks grouped into five families — behavioral, security, operational resilience, multi-agent collusion, and human oversight — plus the architectural claim that mitigations belong in the component that owns the risk rather than in a central supervisory layer."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--agents-guardrails.md
---

# Agent Security Risk Taxonomy

A sixteen-risk enumeration (R1–R16) of what can go wrong in an agentic system, grouped
into five families. Its value is as a **checklist against a specific deployment** rather
than as theory: most teams can name three or four of these unprompted, and the remaining
dozen are precisely the ones that go unmitigated.

The taxonomy is attributed to the agentic-AI security-patterns literature and is
`confidence: medium` — treat the grouping as a useful frame, not a standard.

## Behavioral and deception risks

| ID | Risk | What it looks like |
|---|---|---|
| **R1** | Misaligned & deceptive behaviors | The agent reports success it did not achieve, or optimizes a proxy for the stated goal |
| **R2** | Intent breaking & goal manipulation | An input redirects the agent's objective mid-run |
| **R3** | Tool misuse | The agent invokes a legitimate tool for an illegitimate purpose |
| **R4** | Memory poisoning | Injected content persists into long-term memory and influences later, unrelated runs |
| **R5** | Cascading hallucination attacks | One fabricated fact is written down, retrieved later as ground truth, and compounds |

R4 and R5 share a mechanism worth stating separately: **both convert a transient failure
into a durable one by writing it to storage.** An agent that hallucinates and forgets is a
quality problem; an agent that hallucinates into a memory store is a corruption problem,
because every subsequent run inherits it. See [[Memory Lifecycle]] for the write path this
threatens and [[Prompt Injection]] for the injection vector into R2 and R4.

## Security vulnerabilities

| ID | Risk | What it looks like |
|---|---|---|
| **R6** | Privilege compromise | The agent's credentials exceed the task and get used for more than the task |
| **R7** | Identity spoofing & impersonation | An agent acts as a user or as another agent without authority |
| **R8** | Unexpected RCE & code attacks | Generated code executes outside a sandbox |

R8 is the reason execution boundaries are non-negotiable rather than a hardening step —
see [[Execution Boundaries and Guardrails]]. The operative guidance in the source is
blunt: *don't blindly execute whatever the LLM decides to do* — validate tool inputs, run
generated code in a container or sandbox, and limit what the agent can reach.

## Operational resilience

| ID | Risk | What it looks like |
|---|---|---|
| **R9** | Resource overload | Unbounded loops or fan-out exhaust tokens, rate limits, or downstream capacity |
| **R10** | Repudiation & untraceability | A run cannot be reconstructed after the fact, so failures cannot be attributed |

R10 is the risk that makes every other risk unfixable. Without a trace of what tools were
called, what they returned, and what the agent decided at each step, a failure in any
other category is indistinguishable from model variance. This is the security framing of
the same argument [[Observability and Runtime Patterns]] makes for quality.

## Multi-agent collusion

| ID | Risk | What it looks like |
|---|---|---|
| **R11** | Rogue agents in multi-agent systems | A compromised or misbehaving agent operates inside the trust boundary |
| **R12** | Agent communication poisoning | Messages between agents carry injected instructions |
| **R13** | Human attacks on multi-agent systems | An operator exploits inter-agent trust to reach systems they cannot reach directly |

This family exists because **multi-agent systems extend the trust boundary without
extending the verification boundary.** An agent typically treats another agent's output
as more trustworthy than user input, which is exactly backwards when either agent can be
influenced by user input. See [[Multi-Agent Context]].

## Human oversight

| ID | Risk | What it looks like |
|---|---|---|
| **R14** | Human manipulation | The agent's output steers the reviewer toward approval |
| **R15** | Overwhelming human in the loop | Approval volume exceeds attention, so approvals become reflexive |
| **R16** | Persona-driven bias | The agent's presented persona changes how much scrutiny its output receives |

**R15 is the most operationally common and the least defended.** A human-in-the-loop gate
degrades into a rubber stamp at a rate proportional to how often it fires, which means
an oversight mechanism can be *weakened by adding more of it*. The design consequence is
that HITL gates must be rationed to the decisions that genuinely need them — see
[[HITL Annotation Pipeline]] and the escalation discipline in
[[Agent Management Layer]].

## Mitigations do not belong in a central layer

The taxonomy's sharpest claim is architectural. The intuitive move is to assign risk
mitigation to a central supervisory layer — one guardrail service that every agent call
passes through. The source rejects this as unrealistic:

> Guardrails need to target the specific underlying use case and be implemented in their
> respective platform component or layer — which has a direct effect on the overall
> solution architecture.

The reasoning is that a central layer can only see what crosses it. R4 (memory poisoning)
is mitigated at the memory write path, R6 (privilege compromise) at credential issuance,
R9 (resource overload) in the loop controller. A supervisory layer positioned at the
model call sees none of those. **Where a risk is mitigated is determined by where the risk
is created**, and that distributes mitigation across the architecture rather than
concentrating it.

This is the same conclusion [[Safeguards Architecture — Five Protection Layers]] reaches from the implementation
side: the layers are distinct because they sit at different points in the request path,
not because five is a better number than one.

## The reliability primitives that fall out

The source closes with seven properties a resilient agentic system exhibits, which read
as the positive form of the operational-resilience and collusion families:

- **Durable messaging** — inter-agent messages survive process failure
- **Explicit task state** — state is a record, not an inference from history
- **Dependency tracking** — what a task needs is declared, not discovered at failure time
- **Idempotent processing** — a retried step does not double-apply
- **Isolated side effects** — effects are confined to a boundary that can be rolled back
- **Structured handoffs** — agent-to-agent transfer has a schema
- **Deterministic verification** — the check that a task is done is not itself an LLM call

The last is the load-bearing one and connects directly to
[[Production Reliability Primitives]]: a verification step implemented as an LLM judgment
inherits every risk in this taxonomy, which is why deterministic checks are preferred
wherever the property being checked is mechanically decidable.

## See Also
- [[Agent Deployment Anti-Patterns]] — complements (the engineering failures that create these risks)
- [[Execution Boundaries and Guardrails]] — implements (the sandbox and permission mechanics for R6/R8)
- [[Safeguards Architecture — Five Protection Layers]] — implements (a concrete distributed mitigation architecture)
- [[Production Reliability Primitives]] — complements (the seven resilience properties, in production terms)
- [[Prompt Injection]] — prerequisite-for (the injection vector behind R2, R4, R12)
- [[MCP Server Security Patterns]] — instance-of (this taxonomy applied to a tool protocol)
