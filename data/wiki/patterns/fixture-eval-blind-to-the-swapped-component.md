---
title: Fixture Eval Blind to the Swapped Component
tags: [eval, pattern]
summary: "A fixture eval that feeds stored model outputs through the deterministic post-processing chain never calls the model, so it scores 1.0 for any provider, model or prompt. Using it as the regression gate for a model swap or prompt reorder is a check that cannot fail. Run a live sample through the same deterministic functions, and don't quote a cost delta until the token baseline has been measured."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-b51-cheaper-model-arm.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-b51-cheaper-model-arm.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-b51-cheaper-model-arm.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-b51-cheaper-model-arm.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b51-model-experiment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b51-model-experiment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b51-model-experiment.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b51-model-experiment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b51-model-experiment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b51-model-experiment.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b51-model-experiment.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b49-prompt-cache.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b49-prompt-cache.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b49-prompt-cache.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b49-prompt-cache.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b54-e2e-quality-eval.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b54-e2e-quality-eval.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b54-e2e-quality-eval.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b54-e2e-quality-eval.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b54-e2e-quality-eval.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b54-e2e-quality-eval.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b54-e2e-quality-eval.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis29-deepseek-arm.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis29-deepseek-arm.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-08-04-staff-review-fixes.md
---

# Fixture Eval Blind to the Swapped Component

## The mechanism

An enrichment pipeline (repo akira) had a quality gate, `eval:grade`, that scored a
fixture set at 1.0. The fixtures were **stored model outputs**. The grader passed them
through the deterministic stages (sanitize → validate → review gate → flatten) and never
called `generate()`. That makes it a good regression test *for those functions*, but it
is invariant to everything upstream of them:

- **A model swap** (a cheaper model arm): the fixtures don't change, so the score doesn't.
- **A prompt reorder** (moving dynamic slots to the end of the template for prompt
  caching): an earlier plan named this gate as the primary regression check for the
  reorder. It would have stayed green whatever the reorder did to output quality.

Each plan was written in good faith, and the gate really was green. It just was not
measuring the thing being changed. A retroactive review of the model-experiment plan
caught the problem before any run.

## The fix

- **Ask which component is under change, then confirm the eval executes it.** If the change
  is to the model or the prompt, the eval has to call the model.
- **Use a live sample run piped through the same deterministic functions.** Generate N real
  outputs with each arm and score them with the unchanged sanitize/validate/gate chain. You
  keep the deterministic scoring and add the one thing the fixtures lacked.
- **Watch for confounders in the contract.** Bumping the prompt-version string fails strict
  validation against the old schema version. A live run would report that as a *quality*
  failure of the new arm. Change one variable per arm.
- **Never quote a cost delta without a verified token count.** The plan's cost case rested
  on a baseline of 15,801 tokens per call. A review measured about 3,700, roughly 4× less,
  which shrank the projected saving by the same factor. The plan split into a runnable
  **quality** half and a **cost** half blocked on instrumented token counts.
- **Stage graders don't test the composition.** A separate end-to-end quality plan found
  that each stage's grader scored its own stage in isolation. Nothing scored the composed
  output a user actually sees, so every stage could pass while the whole thing regressed.

## Re-derived plan (2026-09-06)

A re-plan of the same experiment confirmed the earlier findings against the current tree
and added three more:

- **Scoped credentials only help if every entrypoint reads them.** The gateway had an
  enrichment-only key/base-URL/model triple, added for exactly this experiment so the
  judges' shared credential stayed untouched. Two CLI entrypoints still hard-required the
  main provider key before the gateway was ever reached. The workaround was a placeholder
  value; the gateway still prefers the scoped key.
- **A dry run sidesteps the version-string confounder.** Nothing is persisted, so no bumped
  version string ever hits strict validation.
- **Score the live sample with the gates' own logic, by hand.** The plan applied each
  per-call status field (validation, review gate, sanitize) directly, and didn't claim to
  have run the CI gate. How big that sample needs to be is worked out in
  [[Binary Gate Sample Power]].

## Oracle floors gating a pipeline that is not running (librarian staff review, 2026-08)

A review found the retrieval eval graded an oracle-fed path, so its floors passed while
the live search (substring LIKE over an installed-but-unqueried FTS index) was never
exercised. The fix added a `--live` mode that runs the real path, initially report-only,
so the first live numbers become the baseline before they are allowed to gate.

## See Also
- [[Eval Falsifiability]] — instance-of (an eval that cannot fail, here because the changed component is outside its execution path)
- [[Always-Red Check Carries No Signal]] — related (the mirror: an always-green gate is equally unread)
- [[Measurement Fix Mistaken for Model Gain]] — related (the other way a model comparison lies: the scorer, not the model, moves)
- [[Comparable Tables, Not One Source]] — related (a fixture gate at 1.0 that could not fail, from a sibling repo)
- [[Prefix Caching]] — related (the prompt reorder this gate was meant to protect)
- [[Binary Gate Sample Power]] — prerequisite-for (how large the live sample must be, and what it can claim)
- [[Defined but Never Wired]] — related (the unqueried FTS index the oracle eval could not see)
