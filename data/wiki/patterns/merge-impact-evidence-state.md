---
title: Merge Impact and Evidence State
tags: [llm, pattern]
summary: A two-axis finding schema that separates how much a problem matters (merge_impact) from how sure the reviewer is (evidence_state) — so an uncertain critical finding and a certain trivial one stay distinguishable.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/agents/correctness.md
  - data/raw/claude-docs/guacamayo/agents/safety.md
  - data/raw/claude-docs/guacamayo/agents/structure.md
  - data/raw/claude-docs/guacamayo/agents/agent-quality.md
  - data/raw/claude-docs/guacamayo/agents/contracts.md
  - data/raw/claude-docs/guacamayo/agents/wander.md
---

# Merge Impact and Evidence State

Every finding emitted by a guacamayo dimension scanner carries **two independent
labels**, not one severity:

```
**[merge_impact:evidence_state]** ID file:line — claim
```

e.g. `**[blocker:verified]**`, `**[important:supported]**`,
`**[suggestion:hypothesis]**`.

## The two axes

**`merge_impact`** — how much this matters for the merge decision:

| Value | Meaning |
|---|---|
| `blocker` | Must fix before merge |
| `important` | Should fix; doesn't block |
| `suggestion` | Worth considering |
| `nit` | Style/preference beyond lint |
| `question` | Not a defect — reserved for `WD-` wander output |

**`evidence_state`** — how sure the reviewer is:

| Value | Meaning |
|---|---|
| `verified` | Inspected code/callers/tests and confirmed |
| `supported` | Strong evidence, one assumption remains |
| `hypothesis` | Unverified — must be phrased as an observation |
| `question` | Fixed value for wander output |

## Why they must be separate

Collapsing confidence into severity is the failure this schema prevents. On a single
scale, a reviewer who is 60% sure of a data-loss bug has no honest label: calling it
"blocking" overstates certainty, calling it "non-blocking" understates consequence. Both
distortions are costly — the first trains the reader to discount blockers, the second
buries real risk.

With two axes, `[blocker:hypothesis]` says exactly the true thing: *if this is real it
stops the merge, and I have not confirmed it's real.* The reader knows to go verify
rather than to either panic or ignore.

## The anti-bluffing rule

Every scanner prompt carries the same instruction: *"Self-verify before returning:
inspect code, callers, tests. If unsure, classify as `hypothesis` — **never bluff
`verified`**."*

The axis is enforced structurally — each scanner's output template has a separate
**Hypotheses** section, and the section header itself requires the finding be "phrased as
observations" (`this appears to…`) rather than assertions. Verification is dimension-
specific: grep callers before claiming unused (`ST-`, `CR-`), trace data flow to sinks
before claiming a leak (`SF-`), grep for deterministic backing before accepting a
prose-only safeguard (`AQ-`), read `SANYI.md` and cite the entry before claiming a
violation (`CT-`).

One dimension makes uncertainty the *default*: performance/scale findings in `SF-` are
`hypothesis` unless backed by production data (query plans, load numbers), because
algorithmic complexity claims without measurement are speculation.

## Interaction with fixed severity

`evidence_state` is always the agent's judgment. `merge_impact` sometimes is not — for
`CT-` contract findings it is fully determined by the violation code, and for certain
checks it is pinned by rule (hardcoded secrets always `blocker`). See
[[Parallel Dimension Scanner Architecture]] for the per-dimension mapping.

## See Also
- [[Parallel Dimension Scanner Architecture]] — prerequisite-for
- [[Wander — Question-Generating Review Agent]] — extends
- [[SANYI Change-Contract System]] — instance-of
