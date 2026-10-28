---
title: Collapse Site Detection
tags: [llm, infra, pattern]
summary: The fog pass — trace every path where uncertainty enters a system and check whether "I don't know" survives to the output or is silently converted into an answer; the four-row distinction (found nothing / abstain / error / answered from nothing) is the whole mechanism.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/fog/SKILL.md
  - data/raw/claude-docs/galactus/skills/fog/evals/README.md
  - data/raw/claude-docs/galactus/agents/fog-advisor.md
  - data/raw/claude-docs/galactus/skills/fog/evals/fixtures/empty-target-is-error/expected.md
  - data/raw/repos/galactus/.claude--skills--fog--evals--fixtures--empty-target-is-error--expected.md
  - data/raw/claude-docs/galactus/skills/fog/evals/fixtures/finds-planted-defects/expected.md
  - data/raw/repos/galactus/.claude--skills--fog--evals--fixtures--finds-planted-defects--expected.md
  - data/raw/claude-docs/galactus/skills/fog/evals/fixtures/empty-target-is-error/input/SPEC.md
  - data/raw/repos/galactus/.claude--skills--fog--evals--fixtures--empty-target-is-error--input--SPEC.md
  - data/raw/claude-docs/galactus/skills/fog/evals/fixtures/finds-planted-defects/input/SPEC.md
  - data/raw/repos/galactus/.claude--skills--fog--evals--fixtures--finds-planted-defects--input--SPEC.md
---

# Collapse Site Detection

A **collapse site** is the place where a component receives nothing and returns
something that reads as a result. It is the highest-yield defect class in the galactus
prototyping repo's history, and the `/fog` skill (`job: frame`, report-only, never
advances `Status:`) exists to find it on a spec, a plan, or shipped code.

## The four rows

The pass is built on one table. A system that returns the same value for rows two,
three and four cannot be debugged and cannot be trusted.

| Case | Correct behaviour |
|---|---|
| Ran, found nothing, and nothing is the true answer | Report the empty result **as a result** |
| Ran, could not tell | **Abstain** — say so; do not answer |
| Never ran (dispatch failed, input missing, tool errored) | **Error** — never an empty result |
| Ran, answered from nothing | The defect |

The empty-input question to ask of any component is: *"Is 'nothing' distinguishable from
success, by the caller?"* Typical sites: a scanner handed an empty file list; retrieval
returning nothing that feeds generation anyway; a caught exception logged at debug and
treated as a pass; a config default that silently fills an absent value. The skill
inverts on itself — an empty or unreadable `/fog` target is an **error, not a clean pass**,
because producing that failure would be the defect it hunts.

## Grep first, reason second

Candidates are found mechanically, then promoted only when the caller genuinely cannot
tell empty-from-success:

```bash
grep -rn "except.*:\s*pass\|except.*:\s*continue" <target>     # swallow and continue
grep -rn "\.get(.*,\s*\[\]\|\.get(.*,\s*{}\|or \[\]\|or {}" <target>  # defaults hiding absence
grep -rn "return \[\]\|return {}\|return None" <target>          # empty-collection returns
```

Each hit is a candidate, not a finding. Report a promoted site as *what the caller
believes happened* versus *what happened*.

## The surrounding stages

The collapse pass sits inside a six-stage interrogation:

1. **Map the quadrants.** Known-knowns, known-unknowns, unknown-unknowns — and
   **unknown-knowns**, the box everyone skips: information the system holds (a spec, a
   hook, a prior decision) but does not reach. That is a retrieval failure, fixable in a
   way unknown-unknowns are not. Unknown-unknowns are not enumerable; report instead
   whether any **detector** exists (canary, divergence check, human in the loop). Name the
   absence of the detector, not the surprise.
2. **Collapse sites** (above).
3. **Reversibility.** For each decision: reversible yes / no / in principle only, and what
   staging exists (soft-delete before purge, canary before rollout, propose before
   execute, flag before default). *"We could roll it back" is not a rollback* — name the
   branch, flag, retention window or backup. Reversibility is a property of the harness,
   not a promise in a prompt. Irreversible-and-unstaged is `fatal` regardless of
   confidence: confidence does not shrink blast radius.
4. **Dispatch the advisor** — see [[Rationale-Blind Worst-Case Review]].
5. **Concentrate the complexity.** Assume every model call works; ask whether it needed to
   be a model call. Four chained 95% steps are 81%, and the failure is silent because each
   step emits plausible output. Push toward a narrow probabilistic core with deterministic
   components on both sides, and never let the generative component silently become the
   source of truth.
6. **Merge and rank** by `decision_impact` first, `confidence` second — see
   [[Two-Axis Claim Schema]]. Dedupe by mechanism, not wording; two witnesses to one site
   is corroboration worth recording.

## Evaluating the pass itself

The fog eval scores **precision and recall separately** — a run that finds 4/4 planted
defects and fires on 0/3 negative controls is a *failing* run, not 4/7. The planted
fixture includes controls that word-match defect classes (a typed `Ok | Unavailable`
abstention done right; a unique constraint that looks like a double-send risk) precisely
so over-firing shows in the score. A flaky precision invariant is worse than flaky recall:
it is the noise that makes a reviewer stop reading. See [[Trajectory Over Outcome]] for
the general case of scoring the path rather than the verdict.

### What the two fixtures grade

The **planted-defect fixture** is a competent plan-stage spec for a weekly digest service.
Four defects are planted in it: a per-category `except: continue`, an empty match that skips
the send, a column dropped in the same release as the backfill that reads it, and
liveness-only monitoring with a quality check that runs once before launch. A good run is
graded on judgment, not only on detection:

- **Don't downgrade the irreversible migration because the rehearsal passed.** "Completed in
  40 seconds with no errors" shows the migration *completes*, not that it is *correct*. A
  mis-encoding completes cleanly too. Name the staging: keep the column for a retention
  window, or backfill and verify in one release and drop in the next.
- **Don't accept a rollback that covers a different path.** The spec's feature flag is a
  rollback for sends only.
- **Trace interactions between defects.** Because the other categories still produce sends,
  the zero-send pager can never fire for a down category. And a one-time quality check on
  the last model call leaves the two upstream model calls with no accuracy check at all.
- **Don't brief the advisor with your own findings.** Dispatch it with the spec alone, then
  merge by mechanism. Agreement from an advisor that was handed the conclusions is not
  corroboration.
- **The blind-spots line must be substantive.** On a spec for code that does not exist yet,
  every claim is about described behaviour, not observed behaviour. "None identified" there
  is the failure that line exists to catch.

The **empty-target fixture** is a zero-byte spec. The correct output is an error with no
claims, no verdict and no advisor dispatch. Two failures are graded down here. One is
inventing a plausible spec to interrogate. The other is silently retargeting to the
session's working design or the repo at large, which turns an error into a plausible pass on
a document nobody asked about. The case is kept separate because it is a different judgment
path, not just a different input. It tests whether the skill can tell "ran, found nothing"
from "never ran" about its own input.

## See Also
- [[Rationale-Blind Worst-Case Review]] — extends (stage 4 of the same pass)
- [[Two-Axis Claim Schema]] — prerequisite-for (how findings are ranked)
- [[Silent Failure Catalogue]] — alternative-to (the code-review-time catalogue of the same defect class)
- [[Silent Fallthrough in String-Keyed Discovery]] — instance-of (a collapse site in a config lookup)
- [[An Unrun Scan Is Not a Clean Scan]] — instance-of (the same bug at review altitude)
- [[Data Sufficiency Refusal]] — instance-of (a model metric that collapses to a number with no warning)
- [[Deterministic Review Substrate]] — extends (stage 5's "deterministic beats probabilistic" applied to review)
- [[Silence Reads as Clean]] — extends (the named defect family this pass hunts)
- [[Reversibility Cliff]] — extends (stage 3 located as a policy boundary)
- [[Argued Empty List]] — extends (an empty result counts only with proof the search ran)
- [[A Check That Answers a Proxy Question]] — related (the capability precheck that gates the advisor dispatch)
