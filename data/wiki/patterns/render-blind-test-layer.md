---
title: Render-Blind Test Layer
tags: [patterns, eval, pattern]
summary: "jsdom computes no CSS, so colour contrast and tap-target size cannot fail under vitest-axe (the repo had already disabled the contrast rule for that reason). Guard visual accessibility defects in a real layout engine, with a Playwright boundingBox assertion or a Lighthouse audit, and decline to add a unit-level axe test that cannot go red."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis159-colour-contrast.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis159-colour-contrast.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis159-colour-contrast.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis160-tap-target.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis160-tap-target.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis160-tap-target.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis160-tap-target.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis160-tap-target.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis160-tap-target.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis160-tap-target.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis159-app-a11y-lane.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis159-app-a11y-lane.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis159-app-a11y-lane.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis159-app-a11y-lane.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis159-app-a11y-lane.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis159-app-a11y-lane.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis159-app-a11y-lane.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-10-pr235-catalogue-and-source-rights.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis191-content-sources-tab-slice1.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis191-content-sources-tab-slice1.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-11-d49-interim-stock-photos.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-11-d49-interim-stock-photos.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-11-d49-interim-stock-photos.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-11-d49-interim-stock-photos.md
---

# Render-Blind Test Layer

Two accessibility bugs in akira's frontend came out of the same Lighthouse baseline:
muted grey text below WCAG AA contrast, and a 28×28px show-password toggle against a 44px
minimum. Both plans had to pick a test layer, and they reached the same conclusion.

## The unit layer cannot see it

- **Contrast.** The shared axe config already had `'color-contrast': { enabled: false }`
  with the comment "jsdom does not compute CSS". One render test turned it off again
  locally. Someone had tried the vitest-axe assertion and switched it off before the
  issue was even filed. That is evidence, not a guess.
- **Target size.** The rendered size of a button comes from layout: the icon, the
  padding, and Tailwind classes merged by `twMerge`. jsdom has no layout, so no unit test
  can measure it.

Both plans therefore listed the unit-level axe test under **"explicitly not added"**,
with the reason "a test that cannot fail". Adding one would have made the suite look like
it covered the defect.

## What actually guards it

| Layer | Guard | Catches |
|---|---|---|
| E2E (real browser) | Playwright `toggle.boundingBox()`, asserting width and height ≥ 44 | the regression itself. It must fail on pre-fix `main` (28×28) and pass after |
| Static gate | an extended token lint that bans the failing palette classes outside an allowlist | reintroduction at the source |
| Manual audit | a Lighthouse re-run on the measured routes, comparing audit scores before and after | the score the issue exists to move |

The static gate had its own blind spot. Its regex matched hex literals only, so palette
classes like `text-zinc-500` were invisible to it. The gate was green while the defect
was live ([[Scan-Floor Guard Against Silent No-Op Checks]]).

## Root-cause notes that generalise

- **An override can replace a default that was also wrong.** The toggle passed
  `h-auto w-auto p-1` to a shared `Button` whose default size, `h-12 px-6`, is built for
  a text pill. Deleting the override would have produced a roughly 68×48 button. The fix
  was a new `icon` size variant (`h-11 w-11 p-0`). The explicit `p-0` matters: with
  `h-11 w-11` alone, the default `px-6` would have stayed in force, because nothing else
  displaces it in `twMerge`'s conflict groups.
- **Grow the hit area, not the glyph.** A 44px box at `right-3` would reach 8px into the
  input's 48px text gutter. Moving it to `right-1` makes the box fill the gutter exactly,
  and the icon's centre stays at 26px from the edge (`offset + width/2`), so nothing
  visibly moves. Widening the gutter instead would have shifted the icon by 8px.
- **Fix every instance, or the audit moves to another page.** The broken class string
  appeared at 5 source sites, rendering 8 buttons across 4 routes. Fixing only the login
  form would have left the same audit failing on register, reset-password and
  change-password ([[Audit the Class, Not the Instance]]).
- **Compute whether a second token can exist.** Against the off-white canvas, AA needs
  text luminance ≤ 0.1607. The existing `muted` token sits at 0.147. The lightest
  passing grey is 4 RGB levels lighter, which no reader would notice. So there was no
  room for a visually distinct "lighter muted" token, and all sites collapsed onto
  `muted`, including a disabled control that WCAG exempts. Leaving that one would have
  tripped the new lint for no benefit.
- **Scope the claim to what was measured.** Both plans repeat the same sentence word for
  word, so they cannot drift apart: Accessibility 100 is reachable on the five states the
  baseline measured. That is not a claim about the whole app. Routes never run through
  Lighthouse may still carry violations.

## More render-blind gaps from review (akira, 2026-09-05 to 09-15)

- **A guard in a folder the gate never runs.** An accessibility lane's real-browser check lived
  in `e2e/`, which `make gate` does not run. A guard the gate never runs protects nothing until
  it is wired into CI.
- **A visual mask that paints nothing.** Wrappers with `display: contents` have no box, so
  Playwright's `mask` on them silently masked nothing. It looked like it worked, and it did not.
- **Baselines from the wrong architecture.** Screenshot baselines generated in arm64 Docker
  while CI ran amd64 risked font-rasterization diffs over the threshold on the first CI run.
- **Accessibility tests that grep the source.** Several admin-component a11y suites read the
  component file and pattern-match attributes such as `aria-expanded={editing}`. A broken toggle
  handler leaves that text in place, so the test passes. Reviews accepted it twice as consistent
  with precedent, and deferred the fix to one render harness for the whole admin surface.
- **A fallback branch no fixture reaches.** Cards began rendering `image_url ?? category_image`,
  but every fixture set `image_url`, so the stock fallback, the source-photo-wins precedence and
  an empty-alt rule never ran. The fix was render tests for all three cases. A mutation that
  removed the fallback then turned exactly one test red in each of four files.

## See Also
- [[Eval Falsifiability]] — instance-of (an assertion that cannot fail measures nothing)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (the palette-class blind spot in the token gate)
- [[One-Off Codemod, Permanent Gate]] — related (the contrast fix reused that codemod-plus-gate shape)
- [[Audit the Class, Not the Instance]] — instance-of (five sites, eight renders)
