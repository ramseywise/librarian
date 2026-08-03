---
title: Parallel Dimension Scanner Architecture
tags: [llm, pattern]
summary: Code review decomposed into independent single-concern scanner agents dispatched in parallel — each owns one dimension, one ID prefix, and one severity mapping — so review breadth scales by adding agents rather than lengthening one prompt.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/agents/correctness.md
  - data/raw/claude-docs/guacamayo/agents/safety.md
  - data/raw/claude-docs/guacamayo/agents/structure.md
  - data/raw/claude-docs/guacamayo/agents/agent-quality.md
  - data/raw/claude-docs/guacamayo/agents/contracts.md
  - data/raw/claude-docs/guacamayo/agents/wander.md
---

# Parallel Dimension Scanner Architecture

The `/akira` review system (guacamayo) splits code review into **independent dimension
agents dispatched in parallel**, rather than asking one reviewer agent to hold every
concern at once. Each agent is a separate subagent definition with its own system prompt,
scan checklist, and output contract.

## The dimensions

| Agent | Prefix | Owns | Dispatch |
|---|---|---|---|
| `scan-correctness` | `CR-` | Bugs, logic errors, edge cases, data correctness, intent mismatch, cross-usage consistency | always |
| `scan-safety` | `SF-` | Missing safeguards, error/resource handling, secrets/PII, authn/authz, reliability, performance/scale | always |
| `scan-structure` | `ST-` | Naming/layering, complexity/dead code, architecture boundaries, config hygiene, doc accuracy, test shape, operations | always |
| `scan-agent-quality` | `AQ-` | Prompt/LLM smells, tool safety, workflow state, retrieval/context, memory write-back, accountability | conditional |
| `scan-contracts` | `CT-` | SANYI cross-layer violations and contract drift | conditional |
| `wander` | `WD-` | Questions the change raises but doesn't answer | always |

All six run on `haiku` with `tools: Read, Grep, Glob, Bash` and share the
`review-shared` skill. All are **strictly read-only** — the prompt states "never edit,
create, or delete files" as an explicit rule, not an implication.

## Why one agent per dimension

A single reviewer prompt covering all seven concern families competes with itself for
attention: the correctness checklist and the operations checklist crowd each other out,
and the agent silently prioritizes whichever appeared first. Splitting them means each
agent's full context budget goes to one checklist, and the checklists can grow
independently without a rewrite of the others. Adding a dimension is adding a file, not
editing a prompt.

The cost is dispatch overhead and cross-dimension blindness — no single agent sees that a
correctness bug and a structure smell share a root cause. That reconciliation is pushed
to the orchestrator that merges findings.

## Conditional dispatch via signal detection

Two of the six are **gated on repo signals** rather than always dispatched. A
`detect-signals` step runs first and emits booleans:

- `is_agent_code: true` (LLM framework imports or agent path patterns) → dispatch
  `scan-agent-quality`
- `has_sanyi_contracts: true` (`SANYI.md` exists) → dispatch `scan-contracts`

The gated agents are told the gate already passed: *"If you are running, the files have
already been confirmed as agent code."* This keeps the agent from re-litigating its own
activation and wasting turns on a check the dispatcher already made.

## The shared finding contract

Every scanner emits the same canonical line shape, which is what makes parallel output
mergeable:

```
**[merge_impact:evidence_state]** ID file:line — claim
  Evidence: what confirmed it
  Merge impact: blocker
```

Two orthogonal axes travel on every finding — see
[[Merge Impact and Evidence State]]. IDs are dimension-prefixed and **restart numbering
each run**, so `CR-001` is only unique within one review, not across history.

## Findings vs hypotheses vs questions

Each scanner splits its output into a **Findings** section (verified/supported) and a
**Hypotheses** section (unverified, phrased as observations). The rule is explicit:
*"If unsure, classify as `hypothesis` — never bluff `verified`."* Self-verification is
mandated before returning — grep callers before claiming something is unused, trace data
flows to sensitive sinks before claiming a leak.

[[Wander — Question-Generating Review Agent]] is the third output type: not findings at
all, but questions, with `merge_impact: question` and `evidence_state: question` fixed.

## Severity is derived, not chosen

Scanners do not pick severity freely. The mapping is fixed per dimension:

- Generic scanners: `[Blocking]` → blocker, `[Non-blocking]` → important/suggestion,
  `[Nit]` → nit.
- Hard rules override judgment: hardcoded secrets are **always** Blocking (`SF-`);
  safeguard-in-prose-only is often Blocking for production agent code (`AQ-`).
- `scan-contracts` is fully deterministic — merge impact is **fixed by violation code**
  with an explicit "do not deviate": `BY-*` → blocker, `JY-*` → important, `BN-1` →
  suggestion, `MG-1`/`UN-*` → nit. See [[SANYI Change-Contract System]].

Removing severity discretion from the agent is what makes findings comparable across
parallel runs — otherwise each scanner calibrates its own scale.

## The highest-value finding class

`scan-agent-quality` singles out one check as always-flag: **safeguard in prose only** —
a claimed safety behavior (escalation path, validation gate, confidence threshold) that
exists in prompt instructions but has no deterministic code backing. The agent is
instructed to Grep for code backing before accepting a claimed safeguard. This is the
architectural version of [[Silent Fallthrough in String-Keyed Discovery]]: the system appears
to enforce something it merely describes.

## See Also
- [[Merge Impact and Evidence State]] — extends
- [[Wander — Question-Generating Review Agent]] — extends
- [[Agent Quality Review Checklist]] — extends
- [[SANYI Change-Contract System]] — instance-of
- [[Claude Workflow System]] — prerequisite-for
- [[Agentic Workflow Patterns]] — instance-of (parallelization/sectioning)
