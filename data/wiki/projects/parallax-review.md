---
title: Parallax
tags: [llm, eval, project]
summary: An evidence-driven PR review system that combines multiple review perspectives into one explainable merge decision — the judging third of the Akira/SANYI/Parallax triad, deliberately optimizing against comment count.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/docs/documents/Parallax_Project_Name.md
  - data/raw/claude-docs/Parallax/agents/parallax.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/SKILL.md
  - data/raw/claude-docs/Parallax/docs/documents/Parallax_Subagent_Architecture.md
---

# Parallax

**Parallax** (repo `parallax-review`) is an evidence-driven PR review system for general
and agentic software changes. It applies a general software-engineering review to every
pull request and *conditionally* adds agent-system review for changes involving LLMs,
agents, tools, workflows, retrieval, memory, evaluation, or human-agent handoffs.

The name is the mechanism. Parallax is the apparent shift in an object's position when
viewed from different points — and "a pull request has the same property. The author,
reviewer, tests, runtime traces, architecture contracts, and domain-specific scanners may
each reveal a different part of the truth. No single perspective is sufficient on its own."
The architecture follows from that premise: dimensions are separate observers, and their
disagreement is signal rather than noise. See
[[Parallel Dimension Scanner Architecture]].

Taglines: *Different perspectives. Better judgment.* / *Evidence before merge.*

## The three-tool division of labor

Parallax is defined against two sibling systems rather than as a standalone reviewer, and
the split is stated as three verbs:

```
Akira observes.
SANYI governs.
Parallax judges the change from multiple perspectives.
```

- **Akira** observes what the agent system has actually become — a standing quality read
  of the repo as it exists.
- **[[SANYI Change-Contract System]]** governs — checks whether a change respects the
  declared architecture change contract.
- **Parallax** judges *this change*, combining perspectives and verifying evidence to
  decide whether it is ready.

The three axes are state, contract, and change. Akira has no particular diff in view;
SANYI has a diff but only asks whether it violates a declaration; Parallax is the only one
of the three that has to produce a merge verdict, which is why evidence discipline
concentrates there ([[Evidence Classification Model]]).

Integration is explicitly non-destructive: Parallax "can integrate findings from Akira and
SANYI without replacing or rewriting their native output schemas." A consumed finding
keeps its origin system's severity, and Parallax records its own merge impact alongside
rather than overwriting — see [[Source Severity vs Merge Impact]].

## Optimizing against comment count

The stated philosophy is a negative objective first: "Parallax should not maximize the
number of review comments." What it should do instead is enumerated as eight obligations —
reconstruct the intent of the change; trace behavior from input to impact; gather evidence
from multiple sources; distinguish verified findings from hypotheses; identify material
risks; reduce duplicate and low-value review noise; support a clear, explainable merge
decision; and preserve human responsibility for approval.

Two of those eight are load-bearing constraints rather than goals. *Reduce duplicate and
low-value noise* is why deduplication is a deterministic CLI step rather than a judgment
call ([[Deterministic Review Substrate]]). *Preserve human responsibility for approval*
is why the system produces a recommendation and never an approval — every terminal action
in the pipeline stops at proposing.

A review system measured by comment volume drifts toward naming things it can name
cheaply; the surface-level review that produces many low-value naming and formatting
comments is named as a documented failure mode, and style is delegated to a linter
outright.

The eighth obligation — preserving human responsibility — is enforced structurally rather
than by instruction: every mutating action sits behind one authorization gate, described in
[[Read-Only by Default with Explicit Authorization]].

## Designed against what the harness verifiably does

The spec's decision log is unusually explicit about mechanisms it specified and then
removed, each on discovering the runtime could not enforce them — a per-subagent timeout
budget, a cost cap, a submodule-vendored skill. See
[[Verified Runtime Capability Constraint]]. Two of its fifteen final design principles
carry the same discipline into the review's own output: *hypotheses are not defects*, and
*automate coverage, not accountability*.

Its one-sentence definition is "an evidence-driven PR review system that combines general
software review, agent-system-specific review dimensions, and architecture change-contract
enforcement to help human reviewers make responsible, explainable merge decisions" — the
verb is *help*, and the decision stays with the reviewer.

## See Also
- [[Parallel Dimension Scanner Architecture]] — instance-of
- [[Deterministic Review Substrate]] — extends
- [[Evidence Classification Model]] — extends
- [[Shared Context Brief]] — extends
- [[Merge Impact and Evidence State]] — extends
- [[Source Severity vs Merge Impact]] — extends
- [[SANYI Change-Contract System]] — alternative-to (governs the contract; Parallax judges the change)
- [[Corrective Follow-Up Dispatch]] — extends
- [[Agent Quality Review Checklist]] — extends (the conditional agent-system layer)
- [[Skill Preloading via Agent Definition]] — extends (the two-file skill/agent structure)
- [[Read-Only by Default with Explicit Authorization]] — extends (the safety boundary)
- [[Verified Runtime Capability Constraint]] — extends (controls dropped as unenforceable)
