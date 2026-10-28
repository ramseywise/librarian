---
title: Capability Token in a Serialized Row
tags: [infra, pattern]
summary: When a bearer token doubles as a row field (an anonymous participant id that both keys the vote row and authorises editing it), passing whole rows to a client component serialises every participant's credential into the page payload; aggregate server-side so the client gets counts, sign the token so it cannot be fabricated, and reject a bad token instead of minting a fresh identity.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b42-poll-surfaces.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b42-poll-surfaces.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b42-poll-surfaces.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b42-poll-surfaces.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b60-b61-poll-integrity.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b60-b61-poll-integrity.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b60-b61-poll-integrity.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b60-b61-poll-integrity.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b60-b61-poll-integrity.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b60-b61-poll-integrity.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b60-b61-poll-integrity.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-fp16-poll-list.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-fp16-poll-list.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-fp16-poll-list.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-fp16-poll-list.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-fp16-poll-list.md
---

# Capability Token in a Serialized Row

## Finding

An account-free group poll (repo akira) identified each voter by a random UUID kept in a
cookie scoped to the poll. The same UUID was stored verbatim as `participant_id` on every
vote row, and the vote route treated "request carries this UUID" as "request may overwrite
this participant's votes". The design was sound for one browser.

The summary page then fetched the vote rows on the server and passed them, whole, as a prop
to a client component that needed only per-option counts. In a React Server Components
app, a prop handed to a client component is serialised into the page payload. **Every
participant's token was readable by anyone who opened the summary**, and replaying one
through the vote endpoint overwrote that person's vote. It was found by a retroactive
review of the poll work and filed as a blocker.

The mechanism generalises: once a credential is also a data column, every "just pass the
rows" shortcut becomes a credential disclosure. Nobody decided to expose the token. A
type that carried it flowed across the server-to-client boundary.

## Fix (two halves, both required)

1. **Strip it from the payload.** Aggregate on the server into the shape the view needs
   (`{yes, maybe, no}` per option plus a distinct-voter count) and pass that. The client
   component no longer imports the row type at all, so the field cannot come back by
   accident. This closes the **leak**.
2. **Sign the token.** The cookie becomes `<uuid>.<HMAC(uuid, secret)>`. The database
   keeps the raw UUID as the token's subject, so no migration is needed. The route verifies
   the signature before using the subject. This closes **forgery**: a guessed or harvested
   bare UUID is useless without the secret.

Two details carry most of the value:

- **A bad token is rejected (401), never re-minted.** The tempting fallback, "invalid
  cookie, so treat them as a new participant", silently lets a tampered request vote as a
  fresh identity. Minting happens only when there is *no* cookie.
- **A missing secret fails closed.** If the signing secret is unset, the route returns 500
  and logs on the server. It never degrades to unsigned tokens. Existing unsigned cookies
  are invalidated on deploy. For a demo that cost was accepted openly, and a legacy
  fallback mode was explicitly *not* built unless someone asked for it.

## Why the host token did not need the same fix

The host's token was compared on the server against a stored value and never reached a
client prop, so signing it was out of scope. The test is not "is this a token" but **"can
this value reach a serialised payload"**. A display name in the same payload was also left
alone, because it is not a security boundary.

## Companion defect from the same review

The poll's `winning_option_id` had no foreign key. The store checked membership, but the
database did not, so any write that bypassed the store could set an arbitrary id. The fix
was an additive FK with `ON DELETE SET NULL`: the poll's history stands even if the
option goes. This is the same "invariant enforced only by the writer you remember"
failure that [[Migration Done Means Pushed and Probed]] warns about.

## Checks

- Grep every client-component prop type for fields that are also credentials or
  capability keys (`*_token`, `participant_id`, `host_*`, signed-URL parts).
- Inspect the actual page payload (network tab) during review, not just the types.
- For every token check, ask what happens on an *invalid* value. It should be rejected,
  not treated as absent.

## Listing from the cookie jar (FP-16)

A later slice built "My polls / Participating" lists with no accounts. It enumerated the
existing per-poll cookies (`poll_host_<id>`, `poll_participant_<id>`) server-side, with no
schema change and no new identity concept. Its refine pass found four more rules:

- **A cookie's name is not a credential.** Poll ids are the share link, so anyone who has
  seen a link can set a cookie *named* for that poll. Listing on name presence would have
  shown strangers' polls under "My polls". Every host value is checked against the stored
  host token before a poll is listed.
- **A signature must bind the resource, not just the subject.** The participant HMAC
  signed only the participant UUID. A genuine token from poll A, copied into a cookie
  named for poll B, verified fine. The fix lists a participant ref only if its verified
  subject actually appears in that poll's votes. The general rule: sign `(resource,
  subject)`, or check membership.
- **Split credential lifetime from visibility lifetime.** One 180-day `maxAge` was first
  proposed for both roles. But the poll page is public by link, so viewing a closed poll
  never needed the cookie. Only *acting as host* did, and the host token had no
  server-side expiry or revocation, so the cookie `maxAge` was the **only** bound on write
  authority. The outcome: host 30 days, participant 180 days (low stakes, since it can
  only resubmit its own ballot).
- **A read-side cap doesn't prevent header overflow.** Around 100 poll cookies would
  exceed the server's 16 KiB request-header limit and return `431` on *every* request,
  before any application code runs. Capping how many cookies the page enumerates bounds
  only fan-out cost. The plan accepted the risk explicitly, with a sizing (5–10× above
  expected use), and added a `logger.warn` threshold so the stated migration trigger
  ("users accumulating dozens of polls") is actually observable.

## See Also
- [[Written-but-Inert RLS Policies]] — related (the other half of the same app's authorisation model: which client a file imports)
- [[Rate-Limit Keying: Identity Over IP]] — prerequisite-for (the signed participant cookie later became the per-person rate-limit key)
- [[Service Surface Defect Checklist]] — extends (one more defect class for the list: credentials leaking through serialised props)
- [[Principal Write-Surface Matrix]] — related (an anonymous participant's write surface silently included everyone else's votes)
- [[Indistinguishable Rejection on Best-Effort Sinks]] — related (the generic signer later extracted from this one, applied to telemetry ids)
