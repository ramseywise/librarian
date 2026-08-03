---
title: Skill Preloading via Agent Definition
tags: [llm, context-management, pattern]
summary: A skill file is inert until an agent definition names it in a `skills:` field — the two-file split (`.claude/skills/<name>/SKILL.md` plus `.claude/agents/<name>.md`) is what turns checklist content into context actually loaded at subagent startup.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/Parallax/docs/documents/Parallax_Subagent_Architecture.md
  - data/raw/claude-docs/Parallax/docs/documents/Evidence_Driven_PR_Review_System_Spec.md
  - data/raw/claude-docs/Parallax/docs/superpowers/plans/2026-07-19-parallax-skills-implementation.md
---

# Skill Preloading via Agent Definition

Each Parallax subagent is backed by **two separate files, not one**, both under
`.claude/` — "the only location Claude Code actually discovers skills and agents from":

| File | Carries | Role |
|---|---|---|
| `.claude/skills/<name>/SKILL.md` | the dimension checklist and instructions, with `allowed-tools` frontmatter | knowledge/content — "could in principle be invoked by anything" |
| `.claude/agents/<name>.md` | `tools` (its own tool access) plus `skills: [<name>]` | the subagent that actually runs |

The `skills:` field is the load-bearing one. It "preloads the skill's full content into
this subagent's context at startup" — and the doc states the consequence plainly: this "is
the file that makes preloading actually happen — without it, the skill is just a file
nobody preloads."

## The failure mode this was written against

The document records its own prior defect as the motivation. An earlier version showed only
one YAML block per subagent and "never actually demonstrat[ed] the `skills:` field for A–F
(only G had it)." The assessment: "That was a real gap: the one mechanism the whole design
is built around was undemonstrated for six of the seven subagents."

The same mistake appears a second time in the same doc, at a different layer. The
cross-cutting `parallax-shared` content originally "left this content in an unpackaged
`shared/` folder with no preload mechanism, relying on each subagent's own prose to
remember to go read it." That is named as "exactly the unreliable 'soft suggestion' pattern"
the design had already rejected once — and the fix was to give it "the same `skills:`
treatment as everything else," so all seven subagents plus the orchestrator preload it
alongside their own dimension skill.

A third instance is structural rather than a missing field. Every repo-structure tree in
both documents originally placed `skills/` and `agents/` at the repo root — "one level too
shallow to actually be found," since Claude Code discovers them only under `.claude/` and
"there is no setting to add custom search paths." The same discovery killed a plan to
vendor SANYI as a git submodule at `vendor/sanyi`: an arbitrary path "isn't scanned
regardless of what `skills:` references it," so the skill was copied into
`.claude/skills/sanyi/` instead, recording the source commit as a paper trail. See
[[Verified Runtime Capability Constraint]].

Both bugs share a shape worth generalizing: content existed, was correct, and was
discoverable *in principle* — but nothing loaded it. Documentation that describes where a
file lives is not a loading mechanism, and an instruction telling an agent to go read
something is a request, not a guarantee. This is the context-assembly instance of the
prose-only-safeguard defect in [[Agent Quality Review Checklist]]: a capability asserted in
prose with no deterministic path making it real.

## Progressive disclosure decides the split

Which content goes in `SKILL.md` versus a `references/` subfolder follows Claude Code's
skill-authoring guidance — keep `SKILL.md` concise (well under the ~500-line guideline),
with detailed reference material split into `references/` and data files into what the open
standard calls `assets/`. Parallax's two skill types sit at opposite ends:

- **Dimension skills** are one checklist each — "short enough that no internal
  `references/` split is needed." Their `SKILL.md` body is the checklist, nothing else.
- **`parallax-shared`** bundles five reference topics plus report templates, so it gets its
  own `references/` and `templates/` subfolders. `templates/` is Parallax's more specific
  name for what the standard calls `assets/` — "data files, not necessarily images."

The structure is explicitly copied from [[SANYI Change-Contract System]], which uses the
same `SKILL.md` + `references/*.md` load-on-demand discipline. The subagent-architecture
document itself is an application of the same idea one level up: it is kept separate from
the parent spec so "an implementation session working on one subagent's skill only needs
this document plus that subagent's own section — not the entire parent spec (problem
statement, schema design, testing strategy, evaluation metrics, etc.) that has nothing to
do with that task."

## Two sources of truth, deliberately split

Where the companion document and the parent spec overlap, authority is divided by *kind* of
claim rather than by document precedence: the parent spec "is the source of truth for
dimension *content*; this document is the source of truth for dimension *assignment*
(which subagent owns which dimension)." Every dimension bullet is reproduced verbatim
rather than paraphrased, so the duplication is a copy that can be diffed rather than a
restatement that can quietly diverge.

That is the same tradeoff the vendored SANYI copy takes — see
[[SANYI Change-Contract System]] on vendoring — and it has the same weakness: nothing
detects the drift automatically.

The implementation plan turns both into hard constraints on the agent building the files:
checklist bullets copied *verbatim*, SANYI's files *byte-identical* but for a provenance
comment, and no placeholder anywhere. See [[No-Placeholder Plan Discipline]], which also
records the `allowed-tools:`/`tools:` frontmatter mix-up this design is vulnerable to.

## See Also
- [[Skill-Knowledge Information Flow]] <!-- auto-linked -->
- [[Multi-Repo Claude Organization]] <!-- auto-linked -->
- [[Claude Workflow System]] <!-- auto-linked -->
- [[SKILL.md Pattern]] — extends (the skill file; this page is the agent-side preload)
- [[Parallax]] — instance-of
- [[Parallel Dimension Scanner Architecture]] — prerequisite-for (how each scanner gets its checklist)
- [[Shared Context Brief]] — alternative-to (per-run context vs. startup-preloaded context)
- [[SANYI Change-Contract System]] — instance-of (the structure Parallax copied)
- [[Agent Quality Review Checklist]] — extends (prose-only mechanism, at the context layer)
- [[Verified Runtime Capability Constraint]] — instance-of (the verified mechanism this design selected)
- [[No-Placeholder Plan Discipline]] — extends (how these files were required to be built)
