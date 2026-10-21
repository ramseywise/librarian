---
title: Hydration Gap Silent Input Loss
tags: [patterns, infra, pattern]
summary: Server-rendered markup paints before React attaches listeners, so a tap or keystroke in that window is accepted by the DOM and silently ignored by the app — a product defect, not a flaky test; gate interactivity on mounted state and assert effects, not visibility.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis175-webkit-failures.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis175-webkit-failures.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis175-webkit-failures.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis175-webkit-failures.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis175-webkit-failures.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis175-webkit-failures.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/akira/docs/research/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/playground/docs/research/2026-09-05-dis175-webkit-failures.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis307-save-saved-e2e-deterministic.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis178-hydration-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis178-hydration-sweep.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis178-hydration-sweep.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis178-hydration-sweep.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis178-hydration-sweep.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis178-hydration-sweep.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis178-hydration-sweep.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis178-hydration-sweep.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis178-hydration-sweep.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis178-hydration-sweep.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis178-hydration-sweep.md
---

# Hydration Gap Silent Input Loss

Investigation of two WebKit-only e2e failures on a Next.js product (akira). They were
filed as one issue ("WebKit is flaky"); they had two unrelated root causes, and only one
was WebKit-specific.

## Failure 1 — the hydration gap

The test clicked submit as soon as the button was *visible*, on a fresh full page load.
Static SSR markup paints before React has attached its synthetic event listeners. The
browser accepts the input (the field shows typed text) but no handler runs, so the submit
is lost with no error. WebKit surfaces it because its JS startup is slower, widening the
window; the class generalises to real Safari on slow devices.

Two fixes, both needed:

- **Product:** a mounted/hydrated gate — forms disabled or skeletoned until the component
  has mounted — so a pre-hydration tap cannot be silently dropped.
- **Test:** never assert on visibility as a proxy for interactivity. Assert that an action
  *took effect* (a value changed, a request landed), or wait for an explicit ready signal.

## Failure 2 — a browser-agnostic state race

A save button's handler branched on whether the user's saved-ids list had loaded
(`savedIds !== null`). Before that fetch resolved, an authenticated click silently took the
*anonymous telemetry* path instead of the save path: telemetry was recorded for an action
that never happened, and the save was lost. Nothing about this is WebKit; the browser only
changed the timing. The fix is to await or queue behind the dependency, or disable until it
resolves.

### The race fix that created a regression (plan + review)

The first fix disabled the button with `saveDisabled={savedIds === null}`. One `null` carried
two meanings — *still loading* and *fetch failed* — so a failed fetch disabled save forever.
The repair separated them: a dedicated `savedIdsLoading` flag cleared in `.finally()`, with
the failure state leaving the button usable. Review lessons:

- **The evidencing test was vacuous.** The test written to prove the fix stayed green when the
  fix was deleted. Two tests replaced it: one with the fetch held in flight, one with it
  rejected — each red without the fix (see [[Red-Then-Green Proof for Fix-Stage Tests]]).
- **Two reviewers disagreed because they reconstructed different "pre-fix" baselines.** State
  the baseline explicitly when claiming a test proves a fix.
- **A repeat-count gate before un-skipping.** Removing the WebKit skip required
  `--repeat-each=10` per browser project (40 runs) green, not one lucky pass.
- **Name what was not verified.** No real-device iOS run was done; it went into the risks
  section rather than being implied by the emulated pass.
- **A re-skip needs its own deterministic reason.** One test was re-skipped because of a
  separate, browser-independent bug: a query selected view-model column names, the error was
  swallowed, and the saved list rendered empty for every user. A client-side catch-and-log was
  not added because no client logging seam existed yet; a follow-up was filed instead.

## Lessons

- **Split by root cause, not by symptom.** Two failures in one browser suite are two
  issues when they share no cause, fix, or differentiator.
- **"Silent degrade to the fallback path" is the defect class**, the same one as
  [[Silent Fallthrough in String-Keyed Discovery]]: no error, a plausible result, the wrong
  branch.
- **`NEXT_PUBLIC_*` values are inlined at build time.** Trying to vary them per test run
  via environment is a dead end — the first hour of this investigation.

## The E2E Test That Skipped Its Own Assertion

A save → saved-list E2E test caught a missing or non-200 save POST and then *conditionally
skipped* the saved-page assertion. A broken journey therefore reported green. Once the
earlier id race was fixed, the only remaining nondeterminism was hydration: the save
button is natively disabled until hydration, with no readiness marker to wait on. The fix
has two parts: **fail fast** when the POST is missing or non-200 (never skip), and wait on a
**named readiness marker** set after hydration instead of a timeout or a disabled-state
poll.

## The Sweep: Which Controls Actually Need the Gate

A follow-up rolled the shared `useHydrated()` hook out to every remaining client form. The
triage estimate was ~13 call sites. The real count was 17. Reading each component
rather than trusting the triage list changed the scope in both directions:

- **The defect is not limited to controlled inputs.** Triage excluded the intake form's
  chip and option-card components as "presentational, no local state". But a pure
  `onClick` button with no local state loses a pre-hydration tap the same way: the click
  hits raw DOM, no handler runs, and nothing visible happens. These were the first thing a
  user ever tapped, which made them the highest-traffic case on the list.
- **Uncontrolled inputs are safe and should stay ungated.** Server-action forms with
  plain `<input name>` fields (no `value`/`onChange`) keep a pre-hydration keystroke in the
  DOM, and the server reads FormData. No controlled re-render exists to revert the value.
  Gating them would add a disabled flash with no defect behind it. Only their pure
  `onClick` controls (show-password toggles) and submit buttons were gated.
- **A control reachable only after a successful interaction cannot race.** A confirm
  dialog that opens only after a prior click is proof that hydration already finished.
  The at-risk control is the **trigger row** that opens it, so the fix went into the
  shared row primitive and not into the dialog.
- **Gate every control, not just submit.** Gating only the final submit protects the
  formality and leaves the per-question taps exposed. A sub-second native-disabled window
  does not inflate a tap-count metric either, because a disabled click never fires the
  handler that counts taps.
- **Native `disabled` only.** Overlays, skeletons and opacity or pointer-events tricks
  were rejected, because only native `disabled` gives Playwright's actionability check
  and screen readers the right state for free.

**Static regression guard.** A grep-based test asserts a named, fixed inventory of files
(not a heuristic search) each import the hook and use it in a `disabled=` expression. The
plan's own snippet failed on 3 of its 17 entries when it was first run. Two leaf
components receive `disabled` as a prop and never call the hook. One prop was named
`saveDisabled`, which a case-sensitive `disabled=` regex misses. The fix was two lists:
hook callers, and prop receivers that OR the prop into their disabled state. The guard was
then **shown to be load-bearing**: reverting one file's fix made exactly that file fail
(1/17).

## See Also
- [[Silent Fallthrough in String-Keyed Discovery]] — extends (same defect class in a UI runtime)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a check that passes without exercising the thing)
- [[Re-Scope Over Sequence for Colliding Issues]] — related (splitting an issue along the real seam)
- [[A Fake That Conforms to a Broken Seam]] — extends (an input channel dropped at a port)
- [[Baseline Only a Decided, Deterministic State]] — related (layout, like hydration, is invisible to jsdom)
- [[Server Shell, Client Leaf]] — related (removing mount-time fetches by resolving data server-side)
- [[Fail-Closed E2E Journey Proof]] — extends (the hydration gate exposed as a `data-save-ready` contract the e2e test waits on)
