---
title: Evidence Classification Model
tags: [llm, pattern]
summary: A four-state classification (verified / supported / hypothesis / question) every review finding must carry before it is returned, with self-verification assigned to the producing subagent rather than the orchestrator.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/evidence-model.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/SKILL.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/communication-and-handoff.md
---

# Evidence Classification Model

Every candidate finding in Parallax must be classified into **exactly one** of four states
before a subagent returns it, carried in the canonical schema's `status.evidence_state`
field.

| State | Definition | Phrasing constraint |
|---|---|---|
| `verified` | Directly confirmed by code, test, reproduction, explicit contract, trace, or other deterministic evidence | May be asserted |
| `supported` | Strong evidence exists, but one external assumption remains | May be asserted with the assumption named |
| `hypothesis` | Plausible risk without enough evidence | Must **not** be phrased as a confirmed defect |
| `question` | Missing context prevents judgment | Must be phrased as a clarification request, not a finding |

The bottom two rows carry phrasing rules, not just labels. A hypothesis written as though
it were verified is a violation of the model even when the underlying claim turns out to
be true.

## Communication is part of correctness

The rule is stated explicitly: "a correct finding that's phrased as a certainty when it's
only a hypothesis is itself a defect in the review." Accuracy of the claim and accuracy of
the confidence signal are treated as the same obligation.

This is why `question` exists as a first-class state rather than being folded into
`hypothesis`. A question is not a weak finding — it is the absence of enough context to
have a finding at all, and collapsing it into a low-confidence defect claim would
manufacture a problem out of missing information. The orchestrator applies the same
principle upstream at Stage 0: "Missing context is not a code defect — record it as
'unknown,' don't guess."

## Self-verification is the producer's job

Stage 6 puts verification on the subagent that produced the finding, before it returns:

- inspect code, contracts, callers, tests
- run safe checks (`Bash`, scoped to a safe-commands allowlist — never edit, commit, push)
- create a minimal reproduction when appropriate
- inspect traces
- run repeated scenarios for nondeterministic behavior
- **downgrade** unsupported claims to `hypothesis` or `question` rather than asserting them
- validate the finding's JSON against the schema via `parallax-cli validate-finding`

The division of labor is stated outright: "The orchestrator does not re-verify your
findings from scratch — it only reconciles cases where two subagents' findings conflict, or
where verification requires combining two subagents' outputs. Assigning the correct
`evidence_state` is your responsibility, not the orchestrator's."

This matters architecturally. In a fan-out review, the orchestrator is the scarcest
context — it holds every dimension's output at once. Making it the verifier would force it
to re-derive evidence it never gathered. Pushing verification to the edge keeps the
orchestrator's job to reconciliation and merge synthesis, which is the work that genuinely
requires seeing all dimensions together. See [[Parallel Dimension Scanner Architecture]].

## Per-finding communication shape

The classification is not just an internal label — it determines how the finding is
written up. Every returned finding must be usable as a standalone PR comment, carrying a
`comment_type` (`request_change | question | suggestion | nit`) and a `proposed_comment`
that "states the claim, references the evidence location, and (if actionable) a
recommendation with trade-offs — not just 'this looks wrong.'"

The governing principle is stated as a prohibition: "Do not optimize for the largest
number of comments. A surface-level review that produces many low-value comments about
naming or formatting is a documented failure mode, not a feature." The intended work is to
"reconstruct intent, trace behavioral change, identify material risks, verify claims with
evidence, and support an explainable merge decision" — which is why style and formatting
are deliberately delegated to a linter instead ([[Deterministic Review Substrate]]).

## The safe-command boundary

Self-verification is allowed to execute things, which requires a boundary on what
executing means. Safe without authorization: reading files, grep/search, `git diff`,
`git status`, test discovery, and known project checks such as running the existing test
suite. Everything mutating is denied by default — edit, patch, `--fix`, commit, push, post
GitHub comments, approve, request changes, delete, modify configuration.

One rule generalizes past the list: "Unknown scripts must be inspected before execution."
A verification step may not itself become an unreviewed side effect.

## Malformed vs weakly evidenced

The model draws a line between two failure modes that look similar from outside. A finding
whose JSON doesn't validate "is malformed, not just weakly evidenced — fix the JSON (e.g. a
`review_finding_id` not namespaced as `PR-<your letter>-NNN`) before returning it, the same
way you'd fix an unsupported claim rather than return it as-is."

Schema conformance is checked by [[Deterministic Review Substrate]]; evidence state is the
model's own judgment. Both must pass, and neither substitutes for the other.

## Relation to the two-axis schema

`evidence_state` is one of the two orthogonal axes in
[[Merge Impact and Evidence State]] — the other being how much the finding matters for the
merge decision. Parallax keeps a further separation on that second axis between the source
system's severity and Parallax's own merge impact; see
[[Source Severity vs Merge Impact]].

## See Also
- [[Merge Impact and Evidence State]] — extends
- [[Source Severity vs Merge Impact]] — extends
- [[Deterministic Review Substrate]] — extends
- [[Parallel Dimension Scanner Architecture]] — instance-of
