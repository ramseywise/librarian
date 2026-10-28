---
title: "Orchestrator Verifies, Never Relays"
tags: [patterns, eval, pattern]
summary: "In a multi-agent review or build loop, the orchestrator checks agents' claims against the repository (the git index, the merge-base, the base branch, a mutation of the fix) before acting on them. Agents' reports describe intent, and in one repo's review series they were confidently wrong often enough to make verification a standing rule."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis156-candidate-pool.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis156-candidate-pool.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis156-candidate-pool.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis156-candidate-pool.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis156-candidate-pool.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis156-candidate-pool.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis156-candidate-pool.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis178-hydration-sweep.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis178-hydration-sweep.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis167-admin-contrast.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis167-admin-contrast.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis167-admin-contrast.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis167-admin-contrast.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis167-admin-contrast.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis167-admin-contrast.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis167-admin-contrast.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis56-server-client-boundary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis151-waslosheute-fit-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis151-waslosheute-fit-vocabulary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis151-waslosheute-fit-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis54-share-metadata.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis54-share-metadata.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis195-prompt-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis185-saved-read-path.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis185-saved-read-path.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis185-saved-read-path.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis185-saved-read-path.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-10-dis222-b93-kulturdaten-backfill.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-14-dis73-occurrence-read-path-pr1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis73-occurrence-remaining-step12.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-11-d49-interim-stock-photos.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-11-d49-interim-stock-photos.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-env-guard-a2.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis272-prompt-identity-phase1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis272-prompt-identity-phase1.md
---

# Orchestrator Verifies, Never Relays

These lessons come from a series of akira code reviews (2026-09). In each one, an
orchestrator dispatched review reporters and fix or build agents, then decided what to
act on. The same failure kept recurring: an agent's confident claim did not match the
repository. The orchestrator's job is to check claims before acting on them, not to pass
them along. Each rule below is a cheap check that turned a wrong report into a caught one.

## Check the repository, not the report

- **Verify the index, not the report.** A fix stage reported everything "staged
  explicitly". In fact six files had the working tree ahead of the index, and a new test
  was untracked. Committing would have shipped the stale code while the report said it was
  fixed. `git show :<path>` shows what would actually be committed. It was the second
  staging claim in one session that did not match the index.
- **Diff against the merge-base during parallel waves.** A review diff taken with
  `git diff origin/main` after main advanced mid-build showed every commit main had gained
  as a *reversal*. One reporter returned a blocker claiming that a CI fix had been
  reverted, and the claim was fictional. Use `git merge-base origin/main HEAD`. The two are
  the same only while main stands still.
- **Confirm an execute agent has exited before reviewing its tree.** In one loop, the
  orchestrator edited files while the agent was still writing, and an unrelated audit doc
  was swept into the commit.

## Test causation claims

- **"True before, false after."** Three times in one session, an agent's confident
  "checked, not caused by us" claim was wrong: a stale spec line, an allowlist comment, and
  two docs. The test is whether the claim was true on the base and false after the change.
  If so, the change caused it, and fixing it is in scope.
- **Check a premise against the base, in both directions.** The orchestrator told a
  reporter there was no index on a table, because its grep missed a multi-line form. The
  reporter checked and correctly rejected the premise. In another case, a reporter inferred
  that the change had deleted a guard. `git show <base>:<file> | grep -c` showed the guard
  had never existed. A plan once classed a polling flag as read-only, and it was not.

## Verify fixes yourself

- **Mutation-test the fix.** Invert the guard the fix added and watch its test go red, then
  restore the file to byte-identical. Reviewers did this for a dry-run guard, for a
  render check, and for lint rules (see
  [[Green Lint Proves Absence, Not That the Rule Fires]]).
- **Escalate decision findings; do not dispatch them.** When a finding is a choice (scope,
  product behaviour, an explicit human instruction), a fixer agent can only invent an
  answer or do nothing. Route it to a human.
- **Record fixes that land after the loop as unreviewed.** In one review, three fixes were
  closed after the review loop had ended. The review states "no reviewer has seen these
  fixes" and lists the probes and tests that stand in for review.

## Hold agents to their scope

- **Take unreported out-of-scope edits out of the PR.** Build agents made edits nobody
  asked for: dependency security pins in two PRs, and notebook-doc edits that pointed at a
  folder that does not exist. These were moved to their own change. Mixing gate-sensitive
  changes into an unrelated PR makes a failing gate ambiguous.
- **Read the diff yourself.** In several reviews, the orchestrator's own reading found
  findings that no reporter raised, including a read path that exposed expired events and
  a misleading date-range comment.
- **Hold reporters to the right bar.** A safety reporter described a real disclosure
  mechanism and then dismissed it, because the leaked string was not rendered. The
  dispatcher raised it. See [[Review Reporter Ground Rules]].

## See Also
- [[Review Reporter Ground Rules]] — extends (the reporter side of the same discipline)
- [[Cross-Dimensional Review Adjudicator]] — extends
- [[Verify Merge State by Content, Not Label]] — related (another case of checking content rather than a label)
- [[Worktree Agent Dispatch Contract]] — related (scoping what dispatched agents may touch)
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related (mutation-testing a fix)
- [[Sanitize Never Fails, Validate Never Mutates]] — related
