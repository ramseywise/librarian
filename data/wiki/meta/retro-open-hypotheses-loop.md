---
title: Retro Open-Hypotheses Loop
tags: [meta, llm, pattern]
summary: A setup retro becomes a loop only when each applied change records an expected signal and a re-runnable command, and the next retro's first job is to re-run those commands and mark each row verified or failed — with findings ranked by cost × recurrence, a check preferred over a rule, and a control lane to separate real effects from reporting artefacts.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/retro/SKILL.md
  - data/raw/claude-docs/akira/skills/retro/SKILL.md
  - data/raw/claude-docs/diskoe/skills/retro/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/retro/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-17-feedback-loop.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-17-feedback-loop.md
---

# Retro Open-Hypotheses Loop

akira's `/retro` improves the *setup that builds the product* (CLAUDE.md, skills, settings,
refs) rather than the product. It closes one loop: **observe → diagnose → propose → apply →
record**. Steps before apply write nothing; apply touches only what was approved by name;
record writes exactly one file.

## The hypotheses table is the loop

Every applied change gets a row: change, expected signal, how to check next retro. **The
next retro's first job — before reading anything else — is to re-run every command in that
column** and mark each row `verified` or `failed` with output pasted. A row verified from
its own status text is unverified. A failed row is itself a finding: why the fix did not
take is usually more informative than the original friction. Declined proposals are also
recorded, because a declined proposal that recurs is a finding only if it was written down.

## Rules for findings

- **State the window and corpus before measuring**; if transcripts have aged out of
  retention, say so instead of reporting a confident number over missing rows.
- **Every number carries the command that produced it** and the corpus it ran against. A
  number without a re-runnable command is a claim, and claims that reach enforcement become
  hooks built on miscounts.
- **Rank by cost × recurrence**, not by annoyance: a three-second prompt firing forty times
  beats a one-off that cost an hour.
- **Use a control.** When new checklist rows were added to some workflow lanes but not
  others, the untouched lane is the control — a drop in every lane at once is a reporting
  artefact, not the rows working.
- Look for patterns, not incidents.

## Rules for proposals

- Group by write target (CLAUDE.md, a skill, a new skill/agent, a new review dimension,
  settings, cross-repo refs) so each can be approved as a unit.
- Each names the friction, the diff, and **what stops recurring** — if it cannot, it is a
  preference.
- **Prefer a check to a rule.** A CLAUDE.md rule is read by a session that may not be
  looking for it; a gate check fails loudly. Two rounds of "be more careful" did not stop
  migration drift; four layers of mechanical enforcement did. Before proposing a check,
  write the violation two different ways and confirm it catches both.

Mechanical config-health checks run first (dangling refs in CLAUDE.md, settings schema,
skill/agent name alignment, global-vs-repo duplicate skills, always-loaded context budget,
doc-vs-tree build-state drift).

A retro skill ported from a repo with a richer telemetry stack fails at step 0; build it on
what the target repo already produces, and upgrade it when the stack arrives.

## Audit Signals Worth Separating

From the playground copy of the retro skill:
- **"Passed trivially" is a different fact from "passed"**, for example a duplicate check run
  against an empty directory.
- **Never-invoked skills** are either dead weight or an undiscovered capability, and those
  are opposite repairs. The usage counter also misses skills dispatched inside agents, so
  check the stage telemetry before calling one dead.

## Origin: the guacamayo feedback-loop plan

The loop was first built as a global retro skill plus a **tooling ledger**, in that
order, and deliberately together. A retro without a ledger cannot verify anything, and
a ledger without a retro is dead weight. Each ledger row holds date, change, motivating
friction, and status (`hypothesis` / `verified` / `failed`). The retro reads the
unverified rows first. Decisions the plan fixed up front:

- **Proposals are diffs, never auto-applied.** A human reviews and commits, the same
  rule as for code.
- **Write targets by enforcement strength:** hooks > skills > CLAUDE.md and rules >
  MEMORY.md. Choose the strongest target the friction justifies.
- **Process learnings graduate.** Entries in the identity system's growth inbox tagged
  as process learnings are flagged for promotion into a rule or skill, so they don't
  die in the accumulator.
- **A config drift audit comes before anything else,** with a known bug as its test
  case: permission rules naming retired tool names had to be caught. That is the
  [[Config Reference Rot]] class.
- **Skill-changing proposals ship with a before/after eval sketch,** and the ledger row
  links to its result.
- **Keep the ledger to about one screen** by compressing verified rows periodically.

A ledger row can also record a failure honestly. The description rewrite in
[[Pipeline-Absorbed Skills]] graduated as `failed` after 222 sessions with zero
invocations.

## See Also
- [[Workflow Pipeline Telemetry Audit]] — related (the kind of telemetry finding a retro consumes)
- [[Skill Admission Test: Workflow With a Gate]] — related (gate for "new skill" proposals)
- [[Always-Red Check Carries No Signal]] — related (a check must also be read)
- [[Pipeline-Absorbed Skills]] — related (a hypothesis the ledger marked failed, and what the retro did next)
- [[Config Reference Rot]] — related (the drift class the config audit exists to catch)
