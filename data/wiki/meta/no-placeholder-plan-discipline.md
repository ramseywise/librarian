---
title: No-Placeholder Plan Discipline
tags: [llm, pattern]
summary: A plan handed to an implementing agent carries every file's content in full, and a gap is treated as a defect in the plan rather than license for the agent to invent — with verification steps that check structure, not behavior, when the deliverable is markdown.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/docs/superpowers/plans/2026-07-19-parallax-skills-implementation.md
---

# No-Placeholder Plan Discipline

[[Parallax]]'s skills-implementation plan states the rule as a global constraint binding
every task in the document:

> No placeholders anywhere — every file's content is given in full in this plan; if
> something doesn't fit in a step's code block, that's a gap in this plan, not license to
> invent content.

The second clause is what makes it operable. A plan with a `# TODO: fill in the checklist`
does not read as incomplete to the agent executing it — it reads as an instruction to
generate something, and the agent will. Naming the gap as *the plan's* defect in advance
converts an ambiguous prompt into a stop condition, which is the same move
[[Deferred Decision Status]] makes for design decisions that were never resolved.

The constraint has teeth here because the deliverable is content. The plan produces six
dimension skills, a shared skill, a vendored copy, and eight agent definitions — markdown
and YAML, no application code. There is no compiler or test suite to catch an invented
checklist item, so a fabricated bullet would land in a subagent's preloaded context and
silently become part of the review methodology.

## Verbatim as an integrity requirement

Two constraints in the same list forbid paraphrase outright:

- Dimension-skill checklist content "must match `Parallax_Subagent_Architecture.md` Section
  3 **verbatim** — do not paraphrase or drop bullets."
- SANYI's copied files must be "**byte-identical** to the source … except for one added
  provenance comment noting the source commit and copy date — do not edit SANYI's actual
  instructions."

Both are duplication accepted deliberately, on the reasoning that a copy which can be
`diff`ed is safer than a restatement that can quietly diverge — the same tradeoff recorded
in [[Skill Preloading via Agent Definition]], and the reason the vendoring step ends with an
explicit `diff` against the source rather than an eyeball check alone. Rewording a
checklist an LLM will later execute is not a cosmetic edit; it changes the instruction.

## Verification scoped to the artifact type

The plan is explicit that its checks "check structural correctness (valid frontmatter,
required fields, line-count guidance), not program behavior," because there is no program.
Its verification steps are `grep -c "^name: sanyi"`, `ls references/`, `head -20`, and a
`diff` — cheap assertions about file shape.

One constraint exists specifically because a review caught it failing: skill frontmatter
uses `allowed-tools:` while agent frontmatter uses `tools:` and `skills:`, and the plan
notes "this exact mix-up was a review finding on an earlier draft." A wrong-but-plausible
YAML key produces a file that parses, looks right, and grants nothing — the frontmatter
version of the inert-skill failure in [[Skill Preloading via Agent Definition]]. Structural
verification is the only layer that catches it, which is why the checks are keyed to exact
field names rather than to whether the file "looks like a skill."

## See Also
- [[Parallax]] — instance-of
- [[Skill Preloading via Agent Definition]] — extends (what a wrong frontmatter key costs)
- [[Verified Runtime Capability Constraint]] — extends (same discipline, applied to runtime mechanisms)
- [[Deferred Decision Status]] — alternative-to (naming a gap rather than silently filling it)
- [[Claude Workflow System]] — prerequisite-for (the plan-and-execute pipeline this governs)
- [[SANYI Change-Contract System]] — instance-of (the vendored-by-copy source)
