---
title: Prototype Hardening Pass
tags: [meta, infra, pattern]
summary: A pre-demo tool (not a pipeline phase) that walks six defect classes distilled from ~1,900 lines of fixes to a prototype whose 300 tests were green — seams, runnable demo, service surface, eval falsifiability, doc parity, recurring patterns — and fixes each gap in-session with a failing test, never committing and never touching Status.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/galactus/skills/proto-harden/SKILL.md
---

# Prototype Hardening Pass

The galactus `/proto-harden` skill is **a tool, not a phase**. It runs after
`/proto-execute` and before `/proto-review`, or on its own against any run that is about
to be demoed or held up as a reference. It never touches the plan doc's `Status:`, so
the state machine does not know it ran. `/proto-review` still produces the verdict
afterwards. Hardening does not replace review.

**Evidence base.** A review of one prototype produced about 1,900 lines of fixes, and that
prototype's 300 tests were all green. Every checklist item is a defect class that fix
diff closed. That gives the skill its premise: **a green suite does not mean demo-ready**,
and the gap has a repeatable shape.

## Ground rules

1. **Fix, don't just list.** Close each gap in-session, with a test that fails without the
   fix. Stop and report only when the fix needs an operator decision (a contract change, a
   dropped guarantee).
2. **Never commit.** Staged changes are the output.
3. **Run the suite before and after.** A hardening pass that breaks tests has made the
   prototype worse.

## The six classes

1. **Seams.** Fakes against the real adapter (see [[A Fake That Conforms to a Broken Seam]]).
2. **Runnable demo.** Start the real process and drive the demo path with real requests.
   A green `TestClient` run proves none of the following:
   - config is readable from env and validated at load (a negative budget must fail
     startup, not silently skip a loop);
   - clients are process-global, not built per request;
   - orphaned `running` jobs from a dead process are failed loudly at boot;
   - concurrent access works (SQLite needs WAL plus a busy timeout once a second client
     exists);
   - the demo transcript in the docs or slides has been re-run, not assumed.
3. **Service surface.** See [[Service Surface Defect Checklist]].
4. **Eval falsifiability.** See [[Eval Falsifiability]].
5. **Doc parity.** Read the design doc against the code, not against memory:
   - every linked path resolves;
   - a reversed decision reverses its rationale too;
   - "cannot fail" states its precondition and backstop;
   - the limitations list is current in both directions;
   - figures match a fresh run.
6. **Recurring patterns.** Cheap greps with high yield:
   - **Re-validate the backstop.** A "cannot fail" fallback's output is still re-checked
     before success is recorded. If it fires, fail loudly rather than ship an invalid
     result labelled degraded.
   - **Load-time over request-time validation.** A designer typo should fail the deploy,
     not the one request that hit the edge.
   - **Coerce at trust boundaries into the recovery path.** Malformed-but-adjacent input
     should reach the existing repair machinery instead of crashing deep in a validator.
   - **Error paths that can themselves fail.** The write that records a failure is
     guarded, and the first state write lives inside the try block.
   - **A single definition for anything compared across modules.** A normaliser duplicated
     on both sides of an equality check is a latent silent mismatch. The same goes for
     constants shared by the app and the eval.
   - **Degradation carries granularity.** Report *which* fields degraded, not a boolean.
   - **Green for the wrong reason.** When adding a check, find the tests that passed only
     because it was missing.

## See Also
- [[Production Hardening Patterns]] — extends (the prototype-scale, evidence-derived subset)
- [[Silent Failure Catalogue]] — extends
- [[Service Surface Defect Checklist]] — extends
- [[Eval Falsifiability]] — extends
- [[A Fake That Conforms to a Broken Seam]] — extends
