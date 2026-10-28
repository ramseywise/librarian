---
title: Printed URL Is a Public Contract
tags: [infra, pattern]
summary: "Once a URL is printed on a QR card it cannot be recalled, so the decisions that shape it are contract decisions: keep the locale out of the path (cookie, then Accept-Language, then default) rather than invalidate printed codes; build the absolute origin from the request (forwarded headers first) instead of an env var that serves another purpose; and when the URL would be unreachable (localhost), show a visible dev-only warning, because an unscannable QR looks perfect and fails without a sound."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b30-i18n.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b30-i18n.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b30-i18n.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b30-i18n.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b30-i18n.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b30-i18n.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b30-i18n.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b39-operator-board.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b39-operator-board.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b40-operator-tonight.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b40-operator-tonight.md
---

# Printed URL Is a Public Contract

An events app (repo akira) had a business-to-business surface. Venues print a QR code on
a table card or lobby screen, and the code opens `/c/[code]`. Three otherwise unrelated
plans (i18n, the QR board, a desk-side list) each hit the same constraint: **a URL that
has been printed is a public API with no versioning and no recall.**

## Locale out of the path

Adding German and English had two App Router options. One was path segments (`/de/...`,
`/en/...`): canonical and SEO-friendly, but the whole route tree moves. The other was a
cookie or header locale with unchanged URLs. The plan chose the second. Path segments
would make every QR locale-specific and **invalidate every QR already printed**, on top
of the restructuring cost. Detection order: explicit cookie, then `Accept-Language`, then
a default matching the city's primary language. The cost was accepted and recorded: a
single URL can't carry hreflang, so B2C SEO would mean a separate migration later.

Other decisions from the same plan:

- Translate UI chrome only. Scraped titles and descriptions stay in their source
  language. For stored tag values, only the humanised display string is translated,
  never the value used as a key.
- Ship machine-first German marked `draft` until a native speaker reviews it, because
  German speakers are the primary audience.
- A label field left on the question type after extraction can drift from the message
  file while type checks still pass. Remove the field once nothing outside the form
  reads it.
- Combining locale detection and basic-auth in one middleware risks the auth check
  skipping locale redirects. Test admin routes under both locales and both auth states.

## Origin from the request, not an env var

The QR encodes an absolute URL, so the server needs its own public origin. The options:

- **Build-time env var only.** Rejected. The LAN IP used for phone testing changes with
  DHCP, so every session would mean hand-editing `.env.local`. Forget to revert it and
  production prints a LAN IP.
- **Overload the existing base-URL variable.** Rejected. That variable was used only for
  server-side self-fetch. Reusing it for a printed URL would let a later change to
  self-fetch silently retarget every QR, and the reverse.
- **Request headers (chosen).** Read `x-forwarded-proto` and `x-forwarded-host` first
  (proxy-aware), then `host`, then infer the scheme from the environment. This resolves
  to the LAN IP in dev and the canonical domain in prod, with no configuration.

## The guard is code, not a docs note

The plan first treated "opened via `localhost`, so the QR encodes `localhost`" as a
docs/UX note. A dispatcher overrode it: a board whose only job is to be scanned, rendering
a code that does nothing when scanned, fails *invisibly*. The QR looks perfect, which is
the worst failure for a demo in front of a prospective customer. The fix is a one-line
condition. When not in production and the resolved host is `localhost` or `127.0.0.1`,
render a visible warning above the QR with the LAN-address alternative. It stays dev-only
so it can never reach a lobby screen. Acceptance: the warning shows on localhost and not
on the LAN IP.

## Share the destination, not the console

The desk-side list's "send to guest" action shares the public event URL, not the
operator's own page, so guests land on content rather than on staff tooling. Fetching the
list server-side meant the request-derived origin also gave every card an absolute
share URL without touching `window.location`.

## See Also
- [[Async Seam Before the Table]] — related (resolves the code in the printed URL)
- [[Silent Failure Catalogue]] — instance-of (an output that looks correct and does nothing)
- [[Silence Reads as Clean]] — related
- [[URL-Carried Rationale Is Forged Provenance]] — related (a query parameter rendered as the product's own voice)
