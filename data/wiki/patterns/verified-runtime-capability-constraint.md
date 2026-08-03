---
title: Verified Runtime Capability Constraint
tags: [llm, pattern]
summary: A design rule that a control may only be specified if the runtime demonstrably enforces it — three separate Parallax mechanisms (a timeout budget, a cost cap, a submodule-vendored skill) were dropped on discovering the harness had no way to make them real.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/docs/documents/Evidence_Driven_PR_Review_System_Spec.md
---

# Verified Runtime Capability Constraint

[[Parallax]]'s design-decisions log records the same correction four times, against four
unrelated mechanisms. In each case a plausible control had been specified, and it was
removed on discovering that the runtime provides no way to actually enforce it. The
resulting rule is narrow and checkable: **a spec may only require a control the harness
demonstrably enforces**; anything else is either reframed onto a property that *can* be
checked, or named as an accepted tradeoff.

## The four corrections

| Proposed control | Why it was unenforceable | What replaced it |
|---|---|---|
| Per-subagent **timeout budget** for a hung agent | "There is no documented per-agent wall-clock kill-switch" | Retry-on-invalid-output: check whether the return validates against the canonical schema at all |
| A **cost/concurrency cap** across seven parallel subagents | No hook into the operator's API budget — nothing the spec could enforce | Named as a tradeoff and a non-goal; capping delegated to the operator's own `config.py` |
| **`vendor/sanyi` as a git submodule** | Claude Code discovers skills only under `.claude/` — "an arbitrary path outside `.claude/` isn't scanned regardless of what `skills:` references it" | Vendored by direct copy into `.claude/skills/sanyi/`, recording the source commit |
| **Prose telling one skill to invoke another** | Compliance is a runtime model choice, not a guarantee | The `skills:` preload field, "verified against current Claude Code documentation" ([[Skill Preloading via Agent Definition]]) |

The submodule case is the sharpest, because the unenforceable path had *already been
written into every tree in the spec*. Repo-structure diagrams placed `skills/` and
`agents/` at the repo root — "one level too shallow to actually be found; this affected all
seven subagents, not just SANYI." A structure can be internally consistent, reviewed, and
reproduced across two documents while being inert.

## Reframing onto a checkable property

The timeout case shows the constructive half of the rule. The concern was real — a
subagent can hang or error, and the review must still finish. What was unavailable was the
specific mechanism. The fix was not to abandon the concern but to move it onto something
the orchestrator can actually observe: *did this subagent return output that validates
against the canonical schema?* A subagent that "errored, hung, or returned malformed
output" is indistinguishable at that boundary, and all three get the same treatment —
retry up to twice, then proceed without it and state the gap in the report's Subagent
Dispatch section "rather than silently absorbed."

This trades precision for enforceability. A wall-clock budget would distinguish slow from
broken; schema validation cannot. But the coarser check runs, and the finer one was
fiction.

## Naming a tradeoff instead of inventing a control

The cost decision refuses the reframe and takes the third option. Parallel dispatch across
seven subagents "costs more than one sequential pass, and nothing in the spec acknowledged
this." Rather than inventing "an enforceable cost or concurrency limit this spec has no way
to actually control," the cost is stated plainly and paired with the mitigations that exist
by construction — conditional dispatch means most PRs skip three of seven subagents
entirely, the context brief is built once rather than per-subagent
([[Shared Context Brief]]), and lighter-weight single-subagent invocation modes exist.

An unenforceable limit written into a spec is worse than a stated tradeoff, because it
reads as a guarantee to everyone downstream while enforcing nothing. This is the
specification-layer form of the prose-only-safeguard defect in
[[Agent Quality Review Checklist]] — a control that exists only as description.

## Verification as a design step

What makes the rule operable is that capability claims are checked against documentation at
design time, not assumed. The `skills:` field is adopted specifically because it was
"verified against current Claude Code documentation" as "distinct from the generic `tools:`
allowlist." The timeout is rejected because it "doesn't correspond to anything Claude Code
actually lets this spec configure." The same sentence structure appears in the
concurrency correction: preloaded skill content "is not executed in parallel — it is
concatenated into one shared context and worked through by a single sequential LLM pass,"
which killed an intermediate design that had bundled every dimension into one preloading
agent expecting a speed benefit that the mechanism does not provide.

That last one is the cheapest failure to make and the hardest to notice: the mechanism
existed, was correctly used, and simply did not do the thing the design was counting on it
for.

The same discipline carries into the implementation plan, where an unverified assumption
would be an invented file rather than an unenforceable control — hence its rule that a gap
is a defect in the plan, not license to fill it in. See
[[No-Placeholder Plan Discipline]].

## See Also
- [[Parallax]] — instance-of
- [[Skill Preloading via Agent Definition]] — extends (the verified mechanism this rule selected)
- [[Agent Quality Review Checklist]] — extends (prose-only safeguard, at the spec layer)
- [[Deterministic Review Substrate]] — alternative-to (move it into code vs. drop it entirely)
- [[Parallel Dimension Scanner Architecture]] — prerequisite-for (the parallelism this constrained)
- [[Read-Only by Default with Explicit Authorization]] — extends (a control that *is* enforceable)
- [[No-Placeholder Plan Discipline]] — extends (the same rule at the plan layer)
