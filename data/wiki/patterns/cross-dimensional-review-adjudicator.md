---
title: Cross-Dimensional Review Adjudicator
tags: [llm, pattern]
summary: After parallel per-dimension review reporters return, one adjudicator agent merges, deduplicates, and re-ranks their findings into a proposal — every kept, dropped, or re-severitied finding carries a one-line reason, and the output is a proposal the orchestrator applies, never a direct edit of the ledger.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/agents/review-adjudicator.md
  - data/raw/claude-docs/diskoe/agents/review-adjudicator.md
  - data/raw/claude-docs/kiez-archive/agents/review-adjudicator.md
  - data/raw/claude-docs/akira/skills/workflow-review/SKILL.md
  - data/raw/claude-docs/diskoe/skills/workflow-review/SKILL.md
  - data/raw/claude-docs/kiez-archive/skills/workflow-review/SKILL.md
  - data/raw/claude-docs/akira/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/playground/docs/reviews/2026-08-27-b41-operator-identity.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-08-27-b41-operator-identity.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-08-27-b41-operator-identity.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-08-27-b41-operator-identity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-19-dis329-retire-enrichment-callback.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-19-pr333-consolidated-branch.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-19-pr333-consolidated-branch.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-19-pr333-consolidated-branch.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-19-pr333-consolidated-branch.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-19-pr333-consolidated-branch.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-21-pr356-dis353-feed-review-followup.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-20-dis343-venue-open-facts.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-20-dis343-venue-open-facts.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-20-dis343-venue-open-facts.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-23-dis372-dis374-evidence-stage-data-platform.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-16-dis276-pipeline-health-check.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
---

# Cross-Dimensional Review Adjudicator

[[Parallel Dimension Scanner Architecture]] gives review breadth by dispatching one
reporter per dimension (correctness, security, architecture, performance, …). The cost
is that the reporters cannot see each other: the same root cause surfaces as three
findings with three IDs and three severities, and one reporter's blocker is another's
"intended". The akira pipeline adds a single **adjudicator** agent that runs after all
reporters return.

## What it does

1. **Merge** — collapses findings that cite the same lines or the same root cause into
   one, keeping the strongest evidence and listing the absorbed IDs.
2. **Resolve disagreements** — when dimensions conflict on severity or on whether
   something is a defect at all, it picks one and states why in one line, citing the
   repo rule or file that settles it.
3. **Re-rank** — orders the merged list by merge impact, not by the order reporters
   returned.
4. **Flag the unobserved** — any finding that asserts a runtime fact no reporter
   observed (a build result, a Lighthouse score) is marked as such rather than carried
   at its claimed severity.

## What it must not do

- It does **not** write to the findings ledger or the plan. Its output is a proposal;
  the orchestrator applies it. This keeps one writer per artifact and makes the
  adjudication itself reviewable.
- It does **not** re-run reporters, gates, or tests, and it does not read the diff to
  find new findings. It works only on what the reporters returned — otherwise it becomes
  an (N+1)th reporter with no dimension.
- Every drop and every downgrade carries a reason. A silent drop is indistinguishable
  from a miss.

## Why a proposal, not a verdict

The adjudicator is the single point where all dimensions meet, so it is also the single
point where a bad merge loses a real finding. Making its output a proposal with stated
reasons means the orchestrator (or a human) can disagree with one line without
re-running the whole review.

## Worked example: a small seam review (akira, 2026-08)

A review of a two-file operator-resolver change dispatched seven dimensions and showed
two adjudicator moves:

- **Downgrade, then re-home.** A silent-failure finding ("null conflates unknown with
  lookup failure") came in as `important`. It was downgraded to `suggestion` because the
  failure needs I/O this diff does not contain. Building the error channel now would add
  an unused path against the plan's out-of-scope list. The finding was not dropped. It
  was recorded against the later item that swaps in the database.
- **Round 2 re-dispatches only the dimensions that found something.** After the fix stage,
  testing and architecture were re-run on the fixed tree. Every round-1 finding was
  closed, and **two new findings were introduced by the fix stage itself**. A new public
  interface method had no test proving it returned a copy. A roadmap row was marked done
  in place, copying a neighbouring section's format instead of moving the row to the
  file's dedicated Done table. A third finding ("test-driven interface bloat") was kept
  as a recorded trade, not reverted.
- **Pre-existing gate failures are verified independently.** Lint errors outside the
  changed files were confirmed by the orchestrator, not taken from the executor's
  report, and logged as "not this change". Skipped dimensions are listed with reasons
  (no contract file, no ML code, wrong profile).

## Worked example: retiring a dead route (akira, 2026-09)

The change retired an enrichment callback route. It had zero callers, and its shared secret
had no configured store, so any external caller was already broken. Retiring it could only
make nothing worse. Historical and dated docs that mentioned the route were left unedited.

- **The adjudicator refuted a causal coverage claim.** A reporter flagged that deleting the
  route's test reduced coverage of the pipeline runner. The adjudicator checked and found the
  deleted test mirrored the runner's logic in its own copy and never exercised the runner, so
  no coverage was lost.
- **Many empty reporters on a high-risk diff is not the same as clean.** Eight of ten
  reporters returned nothing on a diff that deleted an auth-bearing route. Rather than
  accepting silence, the adjudicator confirmed the diff was inert on four named grounds:
  dependency closure (nothing imports the deleted files), safeguard parity (no check was
  removed without its target), environment sealing (no env var is still read), and spec
  coherence (specs no longer describe the route).

## Lessons from a month of akira reviews (2026-09)

- **The most serious findings often come from the cross-dimensional pass.** In one review nine
  of eleven small-model reporters returned empty and the blocker came from the adjudicator; in
  another, the adjudicator combined three candidates no single reporter had connected (a wrong
  migration comment, a grep-only test and a probe that read grants, not rules) into one finding
  ([[Do-Instead-Nothing Rule Silences a Loud Denial]]).
- **A downgrade needs a reason the scenario cannot occur.** Adjudicator downgrades were rejected
  when the orchestrator could not state why the reporter's failure scenario was impossible.
- **Reporters sometimes answer a different question** (one judged exit codes unambiguous after
  reading only the alarm branch); the orchestrator then verifies directly against the code.
- **Steer reporters away from known items.** Telling reporters not to re-report findings already
  tracked makes an empty result meaningful rather than ambiguous.
- **Fall back to direct review on reporter stalls.** When small-model reporters hit the watchdog
  timeout the orchestrator reviewed the diff itself; on one high-risk branch the reporter model
  was upgraded deliberately.
- **Count tests against the true baseline**, not a plan's stale numbers; trusting the plan's
  count would have deleted five tests during a file split.
- **A specific reproduction claim is the most expensive kind of review error**, because nobody
  re-checks it. Mark each finding's evidence as verified or inferred.
- **Branches that are too large get only sampled review.** A 167-file branch could not be
  reviewed exhaustively; say so in the verdict rather than imply full coverage.

## See Also
- [[Parallel Dimension Scanner Architecture]] — extends (the merge step that architecture lacks)
- [[Source Severity vs Merge Impact]] — extends (re-ranking by merge impact is the adjudicator's ordering rule)
- [[Review Reporter Ground Rules]] — prerequisite-for (the adjudicator trusts reporters only because of those rules)
- [[Corrective Follow-Up Dispatch]] — related (what happens when the adjudicator finds a dimension missing)
- [[Deterministic Review Substrate]] — related (adjudication over LLM findings sits on top of the deterministic layer)
- [[An Unrun Scan Is Not a Clean Scan]] — extends
- [[Shared Context Brief]] — extends
- [[Async Seam Before the Table]] — instance-of (the reviewed change)
- [[Do-Instead-Nothing Rule Silences a Loud Denial]] — related (a finding only the adjudicator could assemble)
- [[Orchestrator Verifies, Never Relays]] — extends (what the adjudicator checks itself before dispatching)
