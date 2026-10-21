---
title: Read-Every-Consumer Migration
tags: [infra, pattern]
summary: Splitting one template variable into two is not a rename — when the old value was a multi-segment path, each consumer wanted a different segment, and when the variable is baked into shipped hooks, a wrong substitution ships broken guards downstream; mechanical rewrites then need a render, not a grep, to verify.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-19-two-root-scaffold-decision-tree.md
---

# Read-Every-Consumer Migration

The ai-project-template restructure replaced a single `source_root` (default
`backend/src`) with a universal shell plus two language roots —
`py_project_root` (`backend`) and `ai_source_root`/`ml_source_root` (`src`, `ml`). The
instinct is to treat this as a rename and substitute. The session that did it recorded
why that instinct is wrong, in three findings.

## It is a split, not a rename

The old default was a **two-segment** path. The new model gives each segment its own
variable, so a consumer of `source_root` might have wanted segment one, segment two, or
the join — and only reading the consumer tells you which. 82 references across 25 files
had to be read individually. The migration checklist was the consumer inventory, exactly
as in [[Silent Fallthrough in String-Keyed Discovery]].

Two of the fourteen moved task paths were also **genuine renames** inside the move
(`data/corpus` → `data/raw_corpus`, `ml/` → `{{ ml_source_root }}/`), which a prefix
rewrite would have missed.

## Some consumers ship downstream

The variable was baked into `.claude/hooks/*.sh.jinja`, which render into **generated
repos' hooks**. A wrong migration there does not produce a bad render; it ships broken
guards into every scaffolded project. That raises the stakes of the inventory: readers
inside the template are recoverable, readers that leave the template are not.

## Grep cannot verify a Jinja rewrite

The mechanical pass replaced `~ source_root ~` and left thirteen expressions of the form
`'/_scaffold' ~ py_project_root` — no slash — rendering `_scaffoldbackend/core`. These were
*caught by the render, not by grep*. A further 28 `eval_root` staging references needed
repointing that the original path audit had not counted. The standing fix was a
bidirectional path-audit script that renders and asserts this class directly, rather than
trusting a textual pass.

## The predicted failure mode was wrong — in the safe direction

The research phase predicted that undefined Jinja variables would render as empty strings
and *silently flatten* the Python tree into the shell. At execution the actual behaviour
was a **loud non-zero exit** at the promotion task. The prediction had been labelled
Medium confidence precisely because it was reasoned, not executed; the correction is
recorded so that the next audit of this class does not inherit the wrong model.

## Decisions that kept the migration small

- Root defaults were chosen so that `py_project_root + ai_source_root == backend/src`,
  reproducing the old path exactly. Rendered destinations did not change; only the
  staging layout moved, which made the "update CI's hard-coded paths" step a no-op
  verification.
- Half-finished prior renames surfaced as test failures with misleading messages (an
  empty corpus index raising `executemany requires a non-empty list`), and were fixed at
  source rather than worked around.

## See Also
- [[Silent Fallthrough in String-Keyed Discovery]] — extends (the consumer-inventory discipline, applied to a path variable)
- [[Template Migrations for Structural Moves]] — related (shipping the same structural move to already-rendered repos)
- [[Test Derived Defaults Without Overrides]] — related (the other falsely-green render class from the same session)
- [[Copier Upstream Update Workflow]] — related
- [[AI Project Template Scaffold]] — instance-of
- [[The Untested Copy Wins]] — related (zero-caller functions are found by the same consumer walk)
- [[A Serialized Blob Is a Prompt Contract]] — related (the consumer that never dereferences the field)
- [[Format Contract Lives in the Parser]] — extends (consumer-first markdown-to-JSON migration of model-written logs)
- [[Byte-Diffable Vendor-and-Move Migration]] — extends (moving a subsystem across repos with diff as the proof of no change)
