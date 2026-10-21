---
title: Cost-Leveled Review Ladder
tags: [meta, llm, pattern]
summary: "A cross-repo review entry point with three cost levels (L1 mechanical diff + lint with no agents, L2 adds scanner agents and tests, L3 adds a full contract audit for one repo only), no sub-flags, delegation to each repo's own checks, and headless runs that never ask but write a Needs-input section instead."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-workspace-review-ladder.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-workspace-review-ladder.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-review-sweep.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-review-sweep.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/2026-07-17-review-sweep.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--2026-07-17-review-sweep.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-gh-4-akira-sanyi-research.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-gh-4-akira-sanyi-research.md
---

# Cost-Leveled Review Ladder

The design behind guacamayo's `/review-sweep` skill and the workspace Makefile that
fronts it. One skill reviews many repos at a chosen cost. Each step up the ladder adds
a more expensive kind of judgment.

## The levels

| Level | Adds | Agents | Scope |
|---|---|---|---|
| L0 | `make` targets: lint and test through each repo's own Makefile | none, zero tokens | any group of repos |
| L1 | diff review + mechanical lint + doc-drift flags | none, no tests | sweep |
| L2 (default) | + scanner subagent + test run | yes | sweep |
| L3 | + full contract audit (SANYI) + proposed doc-drift diffs | yes | **single repo only**; refuses a sweep |

**Hard rule: three levels, no sub-flags.** Level creep (levels picking up toggles) was
the named risk. A new need gets a new level or a separate skill, not a flag. The older
binary `fast` token survives only as an alias for L1.

## Delegate, don't duplicate

Each repo owns its mechanical checks in its Makefile and hooks. The sweep **probes**
what a repo has (Makefile targets via `make -n`, a contract file, changed files) and
runs those checks. It does not reimplement lint. That keeps the skill independent of
repo layout, at the cost of weaker guarantees where a repo has no targets.

Edits split by who reads the file. Machine-consumed files (CLAUDE.md, skills,
settings) get proposed diffs. Human-consumed docs (READMEs, wiki) are **flag-only**
(see [[Documentation Boundary — Machine vs Human Docs]]). The sweep never auto-applies a change. It reports.

## Headless means never ask

A scheduled or `make`-launched run cannot stop for a question. The rule: **never
prompt the user**. Every unresolved question goes into a `### Needs input` section of
the report, and the run always ends with the report written. Human-in-the-loop moves
from a blocking prompt to a report section read later.

The first design bridged `make` to `claude -p`, which had a side benefit: agent
definitions register only at session start, so a fresh headless session gets proper
subagent dispatch. In the end the Makefile was made **print-only**. It prints the slash
command to run and never launches Claude itself. That avoided both unattended
permission prompts and silent token spend.

## Admission by eval gate

`/review-sweep` was the first skill sent through the eval gate. Its acceptance criteria
included a **seeded catch**: plant a deliberate bug in a scratch branch and require the
sweep to report it. A review skill that has never been shown to catch a planted defect
is unverified, however clean its reports look.

## What the first sweep found: config rot

The first real sweep on a sibling repo (listen-wiseer) found no code bugs. Every finding
was stale configuration in machine-consumed files:

- a hook matcher still naming a renamed tool, so the hook silently never fired;
- skill text citing command names from before a repath;
- a CLAUDE.md phase table saying IN PROGRESS for a phase whose plan said EXECUTED.

All three were fixed in the same session. The class is written up in
[[Config Reference Rot]].

## Why the scanners stay separate

A later research pass asked whether the defect scanner (akira) and the contract
enforcer (SANYI) should share a scan layer. The answer was **no, do nothing**:

- Defect detection and contract enforcement are different kinds of judgment, so a
  shared scan layer would be an artificial abstraction.
- The only real overlap (hardcoded tunables) was already cross-referenced.
- The shared layer already exists at the right place: `/code-review` maps both tools'
  findings onto one severity scale at report time.
- Two lines of diff-scope logic repeated across skill Markdown are a documentation
  convention, not a function to extract.

The decision recorded its own revisit trigger: reconsider if a new tool joins the
ladder or duplicate findings start appearing.

## See Also
- [[Claude Workflow System]] — extends (where the review skills sit in the workflow)
- [[SANYI Change-Contract System]] — prerequisite-for (the L3 audit)
- [[Size the Gate to the Blast Radius]] — related (cost-sized review in the plan gate)
- [[Parallel Dimension Scanner Architecture]] — related (the multi-scanner fan-out L2 and L3 dispatch)
- [[Config Reference Rot]] — extends (the defect class the first sweep found)
- [[Test-Gated Auto-Fix with Per-Hunk Revert]] — related (the one place the ladder's tools may mutate)
