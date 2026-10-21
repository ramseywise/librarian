---
title: Adversarial Plan War Game
tags: [llm, pattern]
summary: Attack a plan with 3–5 isolated attackers on diverse angles, require every threat to name who benefits and what they can observe and change (otherwise it is ordinary uncertainty), merge without adding threats, rank impact-first, attach a chosen Prevent/Detect/Recover/Accept to each, and compute the read with "incomplete" first because attacker silence is not a clean bill.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/skills/review-defense/SKILL.md
---

# Adversarial Plan War Game

`review-defense` in galactus war-games a plan before it is built. It only reports. It never
edits the plan or the code, and it never advances `Status:`.

## The admission bound

**Name who benefits, what they can observe, and what they can change.** A threat with none
of the three is not a threat. It is ordinary uncertainty, and it belongs to the
uncertainty-mapping skill (`/fog`). Reporting it as a threat "manufactures fog instead of
locating it." A threat has to be a **mechanism told as a sequence of events**, not a
category.

## Stages

1. **Choose 3–5 diverse angles.** Redundant attackers find the same threat N times, while
   diverse ones find N different threats. The standard angles:
   - **Dependency:** what we don't control.
   - **Scale:** what breaks at 10×.
   - **Adversarial:** hostile or careless users.
   - **Operational:** 3am, who gets paged, can we roll back.
   - **Sequencing:** step 3 done, step 4 can't start.
   - **Human:** the one person who understands this leaves.

   Say which angles were dropped and why. Money, PII or irreversible external effects
   always get a bespoke angle.
2. **Dispatch isolated.** No attacker sees another's output.
3. **Merge without attacking.** An orchestrator that adds its own threats has graded its
   own work. If it spots a gap, it dispatches another attacker.
   - Dedupe by mechanism, not wording. Two angles describing one failure count as
     corroboration and raise confidence.
   - Keep genuine disagreement visible rather than averaging it.
   - Keep an "already mitigated" threat as conditional if the mitigation rests on an
     auditable assumption.
   - Rank by `decision_impact`, then `confidence`, never confidence first. Confidence-first
     ranking buries the speculative-but-fatal cell.
4. **Mitigate each threat** with one of Prevent / Detect (name the signal and who sees it)
   / Recover (name the rollback) / Accept (state the trade). **Accept must be chosen, not
   defaulted into.** Recovery without a named rollback path is not recovery. If no
   mitigation names a rollback, that is itself a finding, because rollback is the most
   commonly missing harness part.
5. **The read is computed, first match wins:**

| Condition | Read |
|---|---|
| Any attacker failed to dispatch or returned unusable output | `incomplete` |
| Any `fatal` threat with no prevent/recover | `redesign` |
| Any `costly` threat unmitigated | `proceed-with-changes` |
| Otherwise | `proceed` |

`incomplete` comes first for the same reason a failed dispatch is rung 1 of the review
verdict ladder: **a war game that could not attack part of the plan has not cleared it.**
The output closes with the single threat to fix first and what the war game could not
evaluate.

## Named failure modes

- **Threat theatre:** long lists of plausible categories with no mechanism.
- **Attacking the strawman:** attacking a simpler plan than the one written.
- **Confidence-first ranking.**
- **Self-attacking:** the orchestrator adding threats during merge.

## See Also
- [[Two-Axis Claim Schema]] — prerequisite-for (the confidence × decision_impact shape each threat uses)
- [[Rationale-Blind Worst-Case Review]] — alternative-to (reading a plan for the worst case without its author's reasoning)
- [[Wander — Question-Generating Review Agent]] — extends (diverse remits instead of N identical scanners)
- [[Silence Reads as Clean]] — instance-of (attacker silence treated as a dispatch result)
