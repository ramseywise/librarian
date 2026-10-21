---
title: Hotlink-Not-Copy Image Posture
tags: [infra, decision]
summary: A conservative MVP policy for showing third-party images in a discovery product — the browser loads the image from its original host and nothing is copied, proxied or cached; images come only from first-party sources with stored provenance and attribution, technical blocks are never circumvented, image hosts are vetted as a privacy risk, and a no-deploy kill switch backs a hide-first takedown route.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-10-09-notion-image-hotlinking-policy.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-notion-image-hotlinking-policy.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-notion-image-hotlinking-policy.md
  - data/raw/claude-docs/diskoe/docs/research/2026-10-09-clean-room-repo-plan.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-10-09-clean-room-repo-plan.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-02-dis59-server-error-handling.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis286-image-hotlinking-policy.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-22-dis286-image-provenance-slices-3-6.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-22-dis286-image-provenance-slices-3-6.md
---

# Hotlink-Not-Copy Image Posture

A working product policy (not a legal opinion) from an events-discovery product (repo
akira, mirrored 2026-10-09). It replaced the earlier assumption that the product had to
be image-free. It is the image row of the per-source rights axes in
[[Change the Channel, Not the Count]].

## The premise

Inline-loading an image from its original host can be legally distinct from copying and
hosting it, **provided** the source is publicly accessible, no technical protection is
bypassed, and the operator reacts to concrete signs of missing rights. The product's
role (sending users back to the venue or organizer) is business context, **not a legal
exemption**. Residual risk was accepted for the MVP, with re-review by counsel before
scaling.

## Engineering rules

1. **Never create a copy by default.** No download, re-upload, persistence, caching or
   proxying. **Check the framework's image component**: an image optimiser that caches
   bytes quietly creates exactly the copy the policy forbids.
2. **First-party sources only.** Official venue, organizer or event pages. Never image
   search, Pinterest, blogs, news, aggregators, social reposts, stock or agency sources,
   or (without review) ticketing platforms. An official source is a plausibility signal,
   not proof of ownership.
3. **Store provenance per image.** `image_url`, `source_page_url`, `source_domain`,
   `image_host`, `scraped_at`, `copyright_notice`, `creator_name`, plus rights, framing,
   privacy and review status. The test: can you answer "where did this come from, when,
   and why was it allowed in?"
4. **Automated red flags route to review.** Agency credits (wire services, stock), explicit
   third-party photographer credits, "no hotlinking" language, or a complaint move the
   image out of the display path. States: `ACTIVE / REVIEW / BLOCKED / TAKEDOWN`.
   Ambiguous means block, when the coverage loss is acceptable.
5. **Never circumvent a block.** No server-side fetch because the browser fetch failed,
   and no spoofing or re-hosting. Failure to load shows the fallback visual.
6. **Attribution lives in the data model**, not in hand-written UI copy. Never remove
   watermarks or credits.
7. **No destructive transforms.** Preserve aspect ratio and don't crop out credits.
   Layouts should tolerate variable aspect ratios.
8. **Kill switch without a deploy**, per image, source page, source domain or image
   host. Blocked images fail safe to the no-image fallback everywhere.
9. **Notice and takedown: hide first, review second.** Losing one image for a while
   costs less than keeping a disputed one visible.

## Image hosts are a privacy decision

A hotlinked image exposes the viewer's IP and request metadata to the image host. Host
selection is therefore an allow/block list: official venue CDN → allow; neutral CDN →
review once; tracking or ad host → block; social-platform host → block by default;
unknown → review or fallback.

## Re-review triggers

Revisit the policy if the product starts storing or proxying images, changes the source
classes, receives a rights complaint, or scales materially. In the repo, the
`remotePatterns` config, an `image-hosts` gate and the `image_posture` column were the
enforcement of record. Where they disagreed with the policy text, code won.

## Narrowing the wildcard: census the column the renderer reads

The allowlist began as `hostname: '**'` — every URL in the database a billable
image-optimisation request. Narrowing it (repo akira, 2026-09-03) taught three things:

- **Census the field the image component actually renders** (`events.image_url`), not
  the registry of scraped sites — a venue's image commonly lives on a CDN or asset host
  other than the site it was scraped from. Never infer the list from fixtures.
- **Scope the census to where enforcement applies, not to what is public.** The allowlist
  is enforced globally, and admin review and quality-sampling screens render images for
  *unpublished* rows. A published-only census (8 rows) would have produced a list that
  breaks the first admin page showing a draft; the real census ran over all 486 events:
  281 image URLs, 13 hostnames, plus 28 relative paths (an extraction defect, filed
  separately).
- **The list goes stale whenever a source is added, and an unlisted host fails
  silently**, so the change shipped with `make image-hosts`: it re-runs the census
  against the live catalogue and fails naming the line to add — verified by removing a
  host and watching it go red.

The half had been marked blocked on a credential the agent could not read; the diagnosis
was wrong — the project ref was tracked and a script could load the local env file
itself without anyone handling the secret.

## Enforcing the posture before anyone has reviewed a source

The rights plan (akira, 2026-09-10) split the work into two independent tracks that
could run in parallel. The human track was reading each source's terms, emailing the
92 sources, and hand-sampling a competitor's long tail. Its tooling (a CSV export and a
table editor) already existed. The engineering track was correct **using only the
default-deny `review_needed` value**, so it did not wait for the review:

- **A render gate, default-deny.** No image renders unless its source is `licensed`.
  With 0 of 92 licensed, every image disappeared from the consumer surface the moment it
  shipped (281 hotlinked images fell back to the typographic card). That was the intended
  effect, and it was called out before merge as a visible product change so it would not
  read as a regression.
- **The gate has N read points, not one.** It had to sit at 6 independent image reads,
  and one of them (a poll summary page) was missed by the first grep. The plan's rule was
  to re-grep every `image_url` read across the app before calling the step done, since
  the same miss had already happened once. See
  [[Audit the Class, Not the Instance]].
- **The CI check runs in observe mode** with a countable flip condition. See
  [[Observe-Mode Gate With a Named Enforce Trigger]].
- **Text follows the same rule.** Raw source prose stopped rendering. The model-rewritten
  description is shown instead, and nothing is shown where it doesn't exist yet. See
  [[Write-Only Fields and the Reader Map]] for why the rewritten field was missing.

## Where hotlinking stops working: derivatives

A later plan (diskoe, 2026-10-09) to generate 3D or video from venue images found the
edge of this posture. Hotlinking avoids making a copy. A derivative requires downloading
and transforming the image, which is an adaptation and needs the rights holder's
consent; non-commercial use is no exemption, and a text-and-data-mining exception covers
analysis, not publishing a new work. The usable sources for derivatives:

- **Wikimedia Commons**, which hosts only free or public-domain files: CC0 and public
  domain need nothing; CC BY needs credit, a licence link and a note of changes; CC BY-SA
  also makes the derived 3D or video CC BY-SA, so keep those in a separate asset store
  with the licence attached. Store per-file licence and author from the Commons API
  metadata and render the credit wherever the image or a derivative appears. A Wikidata
  image property often links a venue straight to a Commons file.
- **Your own street photos of exteriors** where freedom of panorama applies (exteriors
  from public ground only, not interiors).
- **Openly licensed street imagery** on the same share-alike terms, after checking them.
- **Venue permission in writing**, covering display and derivatives.

Prefer exteriors and empty interiors: identifiable people carry their own rights.

## Per-image state is an exception, not a second gate (akira, 2026-09-22)

The provenance slices added per-image columns (source page URL, scraped-at, copyright
notice, creator) directly on the events row, because image to event was already 1:1, so
a join table was unjustified. Each column named its reader up front: the admin
compliance tab, and an attribution resolver that prefers the per-image notice over the
source-level credit.

The per-image `ACTIVE/REVIEW/BLOCKED/TAKEDOWN` vocabulary collided with the source-level
`image_posture` gate. It was kept as a separate column with AND composition:
`renders ⇔ source posture = licensed AND image_state = ACTIVE`. `ACTIVE` is the identity
value and the default. The other states are exceptions an operator sets on one image,
for example one photographer objecting at an otherwise-licensed venue, without flipping
the whole source back to review. Defaulting to `REVIEW` was rejected, because it would
make the column a second review queue duplicating the source-level review.

Two more decisions from the same plan:

- **Public "report an image" route without a rate limiter.** No rate-limit seam existed.
  The mitigations: submissions must name an existing catalogue item (not a free URL),
  land in a review-only queue that never auto-hides, and pass a CSS-hidden honeypot field.
  A real limiter is an operator follow-up.
- **The gate's renderability function gained a required parameter.** A missed call site
  then fails compilation, a stronger guarantee than a runtime test for the N-read-points
  problem above.

The same slices found a host-drift check that the hotlink decision had silently inverted.
See [[Vacuous Check Turns Backwards on Policy Change]].

## See Also
- [[Change the Channel, Not the Count]] — extends (`image_posture` as one of three default-deny rights axes)
- [[PII Masking Approaches]] — related (image hosts as a request-metadata privacy leak)
- [[Hide-Unknown Display Contract]] — complements (a missing or blocked image never blocks publishing)
- [[Kiez Project]] — instance-of
- [[A Sourcing Gap Is Not an Effect Problem]] — related (what the licence rules left available, measured)
- [[Degrade the Render, Surface the Failure]] — related (the issue that narrowed `remotePatterns` from a wildcard)
- [[Observe-Mode Gate With a Named Enforce Trigger]] — related (the image-hosts check ran observing until every source had a posture)
- [[Per-Render Image Optimizer Opt-Out]] — extends (how rule 1 was enforced against the framework image optimizer)
- [[Review Stamp Moves Only When the Verdict Does]] — related (the admin UI that records per-axis posture verdicts and evidence)
- [[Vacuous Check Turns Backwards on Policy Change]] — related (the drift check this policy inverted)
