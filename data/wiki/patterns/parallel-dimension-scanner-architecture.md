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
  - data/raw/claude-docs/Parallax/agents/parallax.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/SKILL.md
  - data/raw/claude-docs/Parallax/agents/intent-correctness.md
  - data/raw/claude-docs/Parallax/agents/reliability-operations.md
  - data/raw/claude-docs/Parallax/agents/security-privacy-data.md
  - data/raw/claude-docs/Parallax/agents/architecture-docs.md
  - data/raw/claude-docs/Parallax/agents/agent-runtime-tooling.md
  - data/raw/claude-docs/Parallax/agents/accountability-safeguards.md
  - data/raw/claude-docs/Parallax/agents/sanyi-review.md
  - data/raw/claude-docs/Parallax/skills/intent-correctness/SKILL.md
  - data/raw/claude-docs/Parallax/skills/reliability-operations/SKILL.md
  - data/raw/claude-docs/Parallax/skills/security-privacy-data/SKILL.md
  - data/raw/claude-docs/Parallax/skills/architecture-docs/SKILL.md
  - data/raw/claude-docs/Parallax/skills/accountability-safeguards/SKILL.md
  - data/raw/claude-docs/Parallax/skills/agent-runtime-tooling/SKILL.md
  - data/raw/claude-docs/Parallax/docs/documents/Parallax_Subagent_Architecture.md
  - data/raw/claude-docs/Parallax/docs/documents/Evidence_Driven_PR_Review_System_Spec.md
  - data/raw/claude-docs/Parallax/docs/superpowers/plans/2026-07-19-parallax-skills-implementation.md
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

Splitting judgment across agents does not mean splitting context acquisition — Parallax
grounds every dimension from one brief built once by the orchestrator. See
[[Shared Context Brief]].

## Conditional dispatch via signal detection

Two of the six are **gated on repo signals** rather than always dispatched. A
`detect-signals` step runs first and emits booleans:

- `is_agent_code: true` (LLM framework imports or agent path patterns) → dispatch
  `scan-agent-quality`
- `has_sanyi_contracts: true` (`SANYI.md` exists) → dispatch `scan-contracts`

The gated agents are told the gate already passed: *"If you are running, the files have
already been confirmed as agent code."* This keeps the agent from re-litigating its own
activation and wasting turns on a check the dispatcher already made.

A gate that misses is invisible in the output — Parallax adds a recovery path for exactly
this, having its always-dispatched scanners report out-of-dimension signal to re-trigger
the gated ones. See [[Corrective Follow-Up Dispatch]].

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

## A second implementation of the same shape

[[Parallax]] (a separate evidence-driven PR review system) reaches the same
dimension-per-subagent decomposition — four always-dispatched dimensions, two gated on
agent-system signal detection, one gated on `SANYI.md` — but relocates the rules this page
enforces through prompts into an executable CLI, described in
[[Deterministic Review Substrate]]. Two of its constraints have no analogue here:
dispatch must be foreground and single-message because a subagent has no turn for
background completions to land in, and verification is assigned to the producing subagent
rather than the merger ([[Evidence Classification Model]]).

Parallel dispatch also needs a partial-failure path that a sequential reviewer does not. A
subagent whose output fails canonical-schema validation — "errored, hung, or returned
malformed output," which are indistinguishable at that boundary — is retried up to twice,
then dropped, with the review completing on the remaining subagents and the report naming
which one failed rather than silently absorbing the gap. Finding IDs are namespaced per
subagent (`PR-A-001`, `PR-B-001`, …) because seven agents assigning IDs concurrently would
collide on a shared counter before the merge step ever ran. Both are consequences of
choosing a mechanism the runtime actually enforces — see
[[Verified Runtime Capability Constraint]].

The dimension checklists themselves converge too. Parallax's four always-dispatched
skills carry the same generic material as `scan-correctness`/`scan-safety`/`scan-structure`
here, and its two agent-system-gated skills restate
[[Agent Quality Review Checklist]] — split across two subagents rather than one, because
runtime defects and accountability defects are found by reading different things. Both
splits are dispatch-shaped, not taxonomy-shaped: the checklist boundary is drawn where a
separate agent would have to look somewhere else.

## See Also
- [[Merge Impact and Evidence State]] — extends
- [[Wander — Question-Generating Review Agent]] — extends
- [[Agent Quality Review Checklist]] — extends
- [[SANYI Change-Contract System]] — instance-of
- [[Claude Workflow System]] — prerequisite-for
- [[Agentic Workflow Patterns]] — instance-of (parallelization/sectioning)
- [[Deterministic Review Substrate]] — alternative-to
- [[Evidence Classification Model]] — extends
- [[Source Severity vs Merge Impact]] — extends
- [[Corrective Follow-Up Dispatch]] — extends (recovery for missed conditional dispatch)
- [[Shared Context Brief]] — prerequisite-for (one grounding pass for all dimensions)
- [[Skill Preloading via Agent Definition]] — prerequisite-for (how each scanner's checklist reaches it)
- [[Verified Runtime Capability Constraint]] — extends (partial-failure handling and ID namespacing)
- [[Read-Only by Default with Explicit Authorization]] — prerequisite-for (the safe-command scope every scanner runs under)
