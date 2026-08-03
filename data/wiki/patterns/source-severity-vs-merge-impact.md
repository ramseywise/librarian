---
title: Source Severity vs Merge Impact
tags: [llm, pattern]
summary: When a review aggregates findings from external tools, each tool's native severity is preserved unrewritten and a separate merge-impact field answers the different question of whether this particular PR should merge.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/severity-and-decision.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/SKILL.md
  - data/raw/claude-docs/Parallax/agents/parallax.md
---

# Source Severity vs Merge Impact

Parallax keeps two severity-like fields on every finding and forbids collapsing them:
`source_semantics.native_severity` and `review_assessment.merge_impact`. They "answer
different questions — how bad the source system says this is, vs. whether _this specific
PR_ should merge because of it."

## Ownership

**Source severity is owned by the system that produced the finding.** SANYI emits
`blocker | warning | info | notice`; a Parallax-native subagent emits its own internal risk
assessment. The rule is that you "never invent or rewrite a source system's severity" — the
`sanyi-review` subagent must "use SANYI's codes and severities exactly as SANYI's own
taxonomy assigns them."

**Merge impact is owned by Parallax**, assigned by the orchestrator during Stage 7
synthesis, though every subagent proposes an initial value since it has the context to
judge it. Values: `blocker`, `important`, `question`, `suggestion`, `nit`.

## Why not one field

An external analyzer's severity is calibrated to its own universe, without knowledge of the
PR under review. A SANYI `warning` means something definite about a contract violation; it
does not know whether this branch is a spike, whether the affected layer is being deleted
next week, or whether the team has consciously accepted that class of drift. Rewriting the
`warning` down to `nit` destroys the tool's signal for everyone downstream. Treating it as
a hard `blocker` imports another system's calibration as if it were a merge policy.

Two fields let both statements coexist. The published mapping is deliberately
non-injective:

```text
SANYI BY-2 blocker
→ source severity: blocker
→ merge impact: blocker
→ decision influence: request changes

SANYI JY-2 warning
→ source severity: warning
→ merge impact: important or suggestion
→ human decision required
```

One source severity fans out to multiple possible merge impacts. That ambiguity is the
point — it marks exactly where a human judgment call lives, rather than hiding it behind an
automatic conversion.

## Defaults come from code, overrides from judgment

The starting merge impact for a SANYI-sourced finding comes from
`parallax-cli sanyi-default-impact` rather than the model recalling the table — "a starting
suggestion the orchestrator (or a human) may still override, not a rule to skip." The
mapping is deterministic; the deviation from it is not. See
[[Deterministic Review Substrate]].

## Decision outcomes

Merge impacts aggregate into one of four final orchestrator recommendations:

- `approve`
- `comment`
- `request_changes`
- `insufficient_context`

`insufficient_context` is the counterpart to the `question` evidence state in
[[Evidence Classification Model]] — the review is permitted to conclude that it cannot
conclude, instead of defaulting to approval when evidence is thin.

## Contrast with fixed-mapping systems

The guacamayo `/akira` scanners take the opposite approach for contract findings: merge
impact is "fixed by violation code" with an explicit instruction not to deviate
(`BY-*` → blocker, `JY-*` → important). That removes discretion to keep findings comparable
across parallel runs — see [[Parallel Dimension Scanner Architecture]]. Parallax instead
preserves the source severity verbatim and treats impact as a separate synthesis step,
accepting per-review variance in exchange for PR-specific context entering the decision.

## See Also
- [[Evidence Classification Model]] — prerequisite-for
- [[Merge Impact and Evidence State]] — extends
- [[Deterministic Review Substrate]] — extends
- [[SANYI Change-Contract System]] — instance-of
- [[Parallel Dimension Scanner Architecture]] — alternative-to
