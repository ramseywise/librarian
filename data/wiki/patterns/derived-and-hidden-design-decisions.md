---
title: Derived-and-Hidden Design Decisions
tags: [llm, decision]
summary: "A scaffold variable marked `when: false` ships the code correctly and prevents the design conversation entirely — the failure mode where observability and guardrails exist as files nobody chose, distinguished from legitimate derivation by whether a silent default has an irreversible failure mode."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-30-system-design-rigor-gap.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold-decision-tree.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--friction-log.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--render-review.md

---

# Derived-and-Hidden Design Decisions

A scaffold reduces interview burden by deriving variables instead of asking them —
`observability_provider`, `include_security_guards`, and the metric toggles are all
`when: false`, computed from whether the project is agent-shaped. The generated project
gets `observability/tracing.py` and `security/guards.py` without anyone being asked.

The finding: this is correct as *scaffolding* and wrong as *design*.

> *"That is a defensible scaffolding decision: the code ships correctly without an
> interrogation. But it means the user is never asked what to trace, what a guardrail
> should block, or what a leak would cost."*

The diagnosis is sharper than "a missing feature":

> *"The gap is not 'the template lacks these capabilities'; it's that the design
> conversation never forces the decisions those capabilities exist to serve."*

A tracing module nobody scoped traces the defaults. A guardrail nobody scoped blocks the
defaults. Both pass every check that asks whether the file exists.

---

## The distinguishing test: irreversible silent failure

The same scaffold contains the counter-example, and it carries its own justification.
`human_approval` is *also* a governance posture, and it is *"always asked out loud"* —
because *"a silent default has an irreversible failure mode."*

That phrase is the test. Derivation is legitimate when a wrong default is discovered and
corrected cheaply; it is illegitimate when the wrong default causes damage before anyone
notices. Under `data_sensitivity=restricted`, unplanned trace redaction leaks restricted
data into an observability backend — silent, and not undone by later configuration. By that
test, trace redaction belongs with `human_approval`, not with the derived toggles.

The distinction is *not* "important vs. unimportant." Plenty of important variables are
correctly derived — see [[Asked vs Derived Scaffold Variables]], where the split is set by
blast radius of a wrong guess rather than by significance.

## Config-shaped vs. decision-shaped

The deeper claim is that these variables were misclassified in kind:

> *"You need traces — not just logs… you should be able to replay any request end-to-end"*
> is *"a design decision with a schema attached, not a dependency toggle."*

A dependency toggle answers *do we install this*. A design decision answers *what does it
do here*. Collapsing the second into the first is what produces a repo where observability
exists and no observability plan does. The structural cause is a
[[Block Attribute Inversion]] finding: cross-cutting concerns were classified as config
while topology-shaping choices were classified as design, and the cross-cutting set is
exactly where these gaps landed.

## The gate encodes the same gap

Hidden decisions do not fail at the gate, because the gate checks process rather than
content. Of the five discovery-exit criteria, four are process checks and one is a content
check:

> *"A DESIGN.md with an empty `Scale:` line, no latency target, no cost ceiling, no named
> failure mode, and every trade-off rationale reading 'Set at scaffold time' passes G1
> today."*

The delivery-exit gate downstream has four content checks including documented monitoring —
so the rigor exists in the pipeline, just later:

> *"The rigor exists in the pipeline; it's gated at delivery-exit rather than
> discovery-exit."*

This reframes the whole finding as **phase misplacement rather than absence** — with the
caveat that makes it still matter: *"a decision made at G2 is a decision the architecture
may already have foreclosed."* See [[Deferred Decision Status]] for the artifact-level
version of the same problem, and [[Design-Before-Infrastructure Sequencing]] for the phase
boundary being violated.

## Dead flags: the opposite failure (two-root scaffold research)

The two-root scaffold audit found the inverse of a hidden decision — a flag that *looks*
like a decision but controls nothing structural. `include_frontend` and `include_ts_rag`
were asked in the interview, yet only toggled lines in generated docs; no directory or
dependency changed with them. Of the template's variables, roughly 79% were derived
(`when: false`), so at prompt time the user could not see the tree that their few answers
would produce. Both are the same defect: the interview does not correspond to the shape of
the output. The remedy is to delete dead flags, surface the derived tree in the
post-generation message, and test derived values with no overrides — see
[[Test Derived Defaults Without Overrides]].

## The honest counter-argument

The research explicitly hunted for evidence that the omissions were deliberate and found
real support — the scaffold's own comments warn against over-scaffolding "just in case,"
and the discovery skill demands plain language for first-time volunteers. The conclusion
does not dismiss it; it partitions:

> *"Several gaps may be correctly omitted for the weekend-sprint tier and only warranted at
> the semester tier. It does not rescue [trade-off rationale] or [observability], which cost
> nothing to ask and are already half-built."*

The surviving test is cost-to-ask against half-built-already. A question that is expensive
for the user and speculative for the project stays derived; a question that is cheap and
whose implementation already ships should have been asked. Tier-conditioning the rest is
consistent with [[Complexity Floor]].

## Shipped unconditionally on a rationale that was switched off (genesis dry-run)

A template dry-run found the reverse of a dead flag: a capability with **no** flag. An
example RAG agent rendered into every project. The rationale in its README tied it to a
retrieval toggle, and that toggle was *off* in the render under review. Nobody consented to
the component, and the stated reason for it did not apply. The fix gates it behind its own
toggle with an explicit question. The test: every shipped component should either answer
to a toggle or be justified by something true in *this* render.

## See Also
- [[Verified Runtime Capability Constraint]] <!-- auto-linked -->
- [[Asked vs Derived Scaffold Variables]] — extends (when derivation is legitimate)
- [[Block Attribute Inversion]] — complements (the topology/config split that produced the hidden set)
- [[Scope-POC Design Interview]] — extends (the conversation that should have forced the decision)
- [[Design-Before-Infrastructure Sequencing]] — related (the phase boundary a G2-gated decision crosses)
- [[Deferred Decision Status]] — related (a decision recorded as deferred vs. never surfaced at all)
- [[Complexity Floor]] — constrains (tier-conditioning which questions are warranted)
- [[DESIGN.md Artifact]] — instance-of (the artifact that passes its gate while empty)
- [[Test Derived Defaults Without Overrides]] — extends (how to keep a 79%-derived variable set honest)
