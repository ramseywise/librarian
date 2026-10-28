---
title: Per-Render Image Optimizer Opt-Out
tags: [infra, pattern]
summary: When one image element serves either a third-party URL or a local fallback depending on the data, stop the framework's optimizer from proxying and caching the third-party bytes by passing a per-instance opt-out computed from the resolved src — a global flag is a one-way override that de-optimizes your own assets, and a pass-through loader still fans out a srcSet.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis286-image-hotlinking-policy.md
---

# Per-Render Image Optimizer Opt-Out

From an events-discovery app (repo akira, 2026-09-16 to 09-22) built on Next.js App Router.
The product adopted the [[Hotlink-Not-Copy Image Posture]]: the browser may load a
third-party image from its original host, but the product must never hold a copy, proxy or
cache. Nobody had passed `unoptimized` anywhere in the tree, so `next/image`'s default
optimizer fetched every remote `image_url` server-side and cached it under
`.next/cache/images`: exactly the copy the policy forbids. It was latent only because no
source had yet been cleared to render images.

## Why the opt-out has to be per render

Six of the render sites resolved their source as `image_url ?? category_image`. `image_url`
is a third-party absolute URL. `category_image` is always a local stock photo the product
owns, which should stay on the optimizer. **The same element serves either one, depending
on the data**, so no static switch can be right for both.

| Mechanism | Verdict | Why |
|---|---|---|
| Global `images.unoptimized: true` | Rejected | The framework source ORs the config value over the per-instance prop with no branch back to `false`. It is a one-way override, and it would stop optimizing the local stock photos too |
| Custom pass-through `loader` that returns the URL unchanged | Rejected | `unoptimized` stays false, so the component still builds a multi-width `srcSet` by calling the loader at several widths, and the framework itself warns that a loader ignoring width should use `unoptimized` instead. A loader swaps the optimization *provider*; it is not an opt-out |
| `unoptimized={isThirdPartyImageSrc(src)}` at each call site | Chosen | With `unoptimized`, the component emits the original `src` with no `srcSet` or `sizes`: no proxy URL, no variants. Computing it from the already-resolved `src` optimizes the local fallback and never touches the third-party photo |

**What is lost on the third-party path:** responsive sizing (the `sizes` prop becomes
inert), automatic AVIF/WebP re-encoding and server-side resizing. The browser fetches
exactly the bytes the source serves. That is the policy, not a regression.

The verdicts were checked against the framework's installed docs **and** its
`get-img-props` source, not just the docs. The existing test suite also already asserted the
proxied shape for a *local* asset, which became a free regression guard that the local path
was unaffected.

## Lessons from the build

- **Relocate a shared predicate, don't duplicate it.** The first draft duplicated the URL
  parser because "the app layer cannot import the core layer". That was half the dependency
  rules: both layers may import the shared `lib/` substrate, and the tree already did so. The
  predicate moved to `lib/` and the gate module re-exported it, so all three existing callers
  kept their import paths. The gate module's own docstring already stated the principle (a
  second hand-maintained copy is what let earlier drift slip past).
- **`export { x } from '...'` binds no local name.** The planned one-line re-export made the
  module's own later call to `x` throw `ReferenceError` and fail the type check. A top-level
  `import` plus a same-site `export { x }` does the same job.
- **A decision can be encoded in a gate.** Writing the decision record surfaced a gate that
  failed when a cleared image's host was not the product's own storage domain: the
  superseded copy-to-storage rule, still enforced. It was inert at zero cleared sources and
  would false-fail on the day the first source was cleared. That timing made the code slice
  land before source clearance, not after. When a decision reverses a rule, grep the gates
  for the old rule.
- **Prove the assertion bites.** Stripping the prop from one site turned its new test red
  (the `src` came back as the encoded proxy URL) and restoring it turned it green. One run
  stood as evidence for all six sites, since they share the predicate and test shape. See
  [[Red-Then-Green Proof for Fix-Stage Tests]].
- **Comment-only fixes still go in a new migration.** The column comment describing the old
  rule was corrected by a new migration. Only the non-DDL prose header of the applied
  migration was edited in place.

## See Also
- [[Hotlink-Not-Copy Image Posture]] — instance-of (the engineering enforcement of rule 1, "never create a copy")
- [[Red-Then-Green Proof for Fix-Stage Tests]] — related
- [[Degrade the Render, Surface the Failure]] — related (the earlier narrowing of the image host allowlist)
