---
title: Component Test in a Shape the App Never Uses
tags: [patterns, eval, pattern]
summary: "A dialog's 'restores focus on close' test stayed green while focus fell to <body> in every real dialog, because the fixture used the uncontrolled Trigger shape, the only shape where the library restores focus itself, and the app only used controlled dialogs. A browser journey test that uses the app's real components catches the mismatch. Its first run also found a locator that matched nothing and a default answer that returned no results."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis301-playwright-accessibility-journey.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis301-playwright-accessibility-journey.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis301-playwright-accessibility-journey.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis301-playwright-accessibility-journey.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis301-playwright-accessibility-journey.md
---

# Component Test in a Shape the App Never Uses

From an akira plan that added a Playwright keyboard and accessibility journey: a
keyboard-only path through intake to a detail page, a dialog focus lifecycle check, axe
WCAG 2.2 A/AA scans of three real pages, and landmark assertions.

## The defect the journey was built to catch, and did

**Focus did not return to the opener when a dialog closed.** In Radix's modal dialog,
`onCloseAutoFocus` calls `preventDefault()` and then focuses `triggerRef.current`. That ref
is filled **only** by `<Dialog.Trigger>`. Every dialog in the app was controlled: an `open`
prop driven by the opening component's state. So `triggerRef` was always `null`. The
library suppressed the natural focus restore and then focused nothing. Focus fell to
`<body>`. A keyboard or screen-reader user who dismissed a destructive confirmation landed
at the top of the document (WCAG 2.4.3).

The component suite already had `restores focus to the trigger on close`, and it was green
the whole time. Its fixture used `<DialogTrigger>`, the one shape in which the library
restores focus by itself, and the one shape the app never used.

**Rule:** a component test proves the contract only for the usage shape in its fixture.
When a library behaves differently by usage mode (controlled vs uncontrolled, with or
without its own trigger), the fixture must use the mode the app actually uses. The fix was
to capture `document.activeElement` on open and restore it on close, composed so that a
caller's own handler still wins. A controlled-dialog test was shown red before the fix and
green after.

## Two defects already in the e2e suite, found on the way

1. **A locator that matched nothing, behind an `if`.** The intake spec selected
   `[data-value]`, an attribute the chip component never rendered, guarded by
   `if (count > 0)`. The test's only intake interaction had been a silent no-op since the
   day it was written.
2. **Defect 1 hid defect 2.** The default intake answer was `when: 'today'`, but the seed
   wrote the event 7 days ahead. The date filter excluded it and the results page showed an
   empty state. A test that changes no answer cannot notice that the defaults return
   nothing. Both specs now choose an explicit date and read the seeded `start_at` back
   instead of recomputing the offset.

Two more harness defects of the same kind:

- The seed's enrichment insert named a column the table had never had. The database
  rejected the whole row, and a warn-and-continue step swallowed the error. Every e2e run
  since then had tested an event with no enrichment.
- A token secret was missing from the local web server's env, so the recommendations API
  returned 503 and no spec could reach results. CI injected the secret as a job secret, so
  CI never saw the problem.

## Assert what the engines actually agree on

Playwright's WebKit inherits Safari's "Tab highlights each item" setting, which is off. Tab
moves focus nowhere, on desktop WebKit and on the iPhone profile alike, and no context
option turns it on. Skipping WebKit entirely was rejected. Tab **order** is asserted on
Chromium. Focus **management** (focus entering the dialog and returning on close) is
asserted on both engines. That is the behaviour the engines might disagree on, and it is
the assertion that caught the defect.

Not done, deliberately: a stale mobile screenshot baseline. Adopting a new baseline is a
design approval, not a test repair.

## See Also
- [[Adoption Ban Needs an Escape Hatch]] — extends (focus restore was the one dialog justification left untested; here it was also broken)
- [[Render-Blind Test Layer]] — related (another accessibility defect class a unit test layer cannot see)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — instance-of (the guarded locator that clicked nothing)
- [[A Fake That Conforms to a Broken Seam]] — related (a double that passes because it matches the wrong shape)
- [[Fail-Closed E2E Journey Proof]] — related (the sibling journey whose conditional skip hid the same seed-date defect)
