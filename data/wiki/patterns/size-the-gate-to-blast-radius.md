---
title: Size the Gate to the Blast Radius
tags: [meta, pattern]
summary: A readiness gate's cost should scale with what the plan can break, not how much it types — a Light path for small, effect-free plans that still runs every cheap blocking check, with two mandatory escapes back to Full (any check fails; the plan writes a hook, gate, shared skill or anything every session loads).
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/proto-refine/SKILL.md
---

# Size the Gate to the Blast Radius

Stage 0 of the galactus `/proto-refine` readiness gate picks a path before anything else
runs, and says which path it took and why in one line.

| Path | When | What changes |
|---|---|---|
| **Light** | ≤2 files written, AND no persistent-state or external effect, AND no shared config other sessions load | Trio lenses compressed to one ≤3-sentence card. **All seven Definition-of-Ready checks still run.** Adversarial pass skipped by default |
| **Full** | anything else | Everything |

Light still returns a real verdict, and it records the skip (`Epistemic: UNTESTED`, with
`skipped — light path, <reason>`). What it drops is the *adversarial* apparatus, the
expensive half, which only pays for itself when something irreversible is at stake. The
cheap checks are the gate, so they never drop.

## Two mandatory escapes back to Full

Light is a starting position, not a commitment.

1. **Any DoR check fails.** A failing check is evidence the plan is not as small as it
   looked.
2. **The plan writes a hook, a gate, a shared skill, or anything every future session
   loads.** Go Full regardless of file count.

> Blast radius is not measured in files.

**Founding case.** A ~150-line bash hook plus its test file counted as Light by file count.
It was run Full anyway, and the failure pass found a defect that would have blocked every
settled plan doc in the repo on the first write after the hook was registered. "Size the
gate to what the plan can break, not to how much it types."

## Narrow dispatch conditions

On the Full path, the adversarial advisor is dispatched if *any* of several conditions
hold. Because the conditions are OR'd, each one has to be narrow. "EM's lens flagged blast
radius" only counts if it **named what would be damaged**. "A gate that dispatches an
advisor on every trivial plan trains people to ignore the advisor." The three trio lenses
(PM / Designer / EM) run inline rather than as agents, because they grade different axes
and their agreement was never evidence. **When they disagree, the disagreement is the
finding.**

## See Also
- [[Verification Thins Where Blast Radius Widens]] — extends (the eval-layer counterpart: widest-reach changes had the thinnest automated check)
- [[Plan Epistemic State Axis]] — extends (what the gate records whichever path ran)
- [[When a Lens Earns Agenthood]] — prerequisite-for (why the trio stays inline)
- [[Rationale-Blind Worst-Case Review]] — extends (the advisor the Full path dispatches)
- [[Plan-Doc Status Enum]] — extends (the READY transition this gate guards)
- [[Test-Gated Auto-Fix with Per-Hunk Revert]] — related (blast-radius tiers deciding auto-apply versus surface-only)
