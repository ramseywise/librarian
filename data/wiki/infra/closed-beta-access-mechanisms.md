---
title: Closed-Beta Access Mechanisms
tags: [infra, reference]
summary: "\"Closed beta\" names no mechanism until one is picked. For a founders-only alpha, host-level deployment protection (no app code) or a separate beta credential pair that can never unlock admin is enough. For an external cohort, choose between a shared password (revoking it breaks everyone), an unguessable link (no revoke, needs noindex) and an invite code (selective revoke, most build). robots.txt is advisory, so noindex is the real control. The legal-pages gate is non-waivable once anyone beyond the founders gets in."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-dis324-beta-access-control.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-dis324-beta-access-control.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-dis324-beta-access-control.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-dis324-beta-access-control.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-dis324-beta-access-control.md
---

# Closed-Beta Access Mechanisms

From an access-control plan for a consumer app whose sessions are anonymous by product
decision (repo akira, 2026-09-29). At that point "closed beta" named no mechanism at all.
There was no invite list. The only gate was Basic auth on `/admin`, and `robots` allowed
indexing of everything public. A beta gate is a **temporary layer on top of** the
anonymous-viewing decision, not a reversal of it.

## Split by audience, because the blockers differ

The single ticket mixed two asks with different blockers, so the plan recommended
splitting it:

- **(a) Internal alpha, founders only.** The bar is "a stray link doesn't leak and nothing
  gets indexed", not "build an invite system". It is unblocked once the host exists.
- **(b) External beta.** This needs a mechanism, a cohort-ramp schedule, and the legal
  pages. It is blocked on a product decision and, non-waivably, on legal.

## (a) Founders-only alpha

| Option | Code | Notes |
|---|---|---|
| **Host deployment protection** (account-gated) | none, a dashboard setting | Preferred. Zero app-code risk in the highest-exposure, lowest-tester-count phase. Plan inclusion was marked unverified at the time |
| **Host shared-password protection** | none | Middle option when a founder must get in without a host-account login (e.g. from a phone) |
| **App-level Basic auth** on all routes | a matcher change, a second check, two env vars | Fallback only. Use a **separate `BETA_USER`/`BETA_PASSWORD` pair**, never the admin pair, so a beta credential can never unlock `/admin` |

The existing admin check was already generic (it read a user/password from env), which
made reusing its credentials the tempting shortcut. Separate credentials keep the trust
boundaries separate.

## (b) External cohort

| Mechanism | Gate | Indexing | Ramp / revoke | Build cost |
|---|---|---|---|---|
| **Shared password** (host-level) | one password for the cohort | protected | ramp = who you tell; revoking means changing the password, which **breaks everyone** | none |
| **Unguessable link, no gate** | anyone with the URL | still needs `noindex`; **a leaked link is permanently exposed** | no selective ramp or revoke | small |
| **Invite code at the door** | per-tester codes before the session starts | pairs with `noindex` | **selective per-code revoke, real cohort ramp** | largest: code store, gate screen, revoke path |

The plan picked none of these. It was a joint product and engineering call tied to the
ramp schedule, and the plan laid out the trade-offs without making it.

## robots.txt is advisory, noindex is the control

A `robots.txt` disallow only asks well-behaved crawlers to stay out. It does not stop a
shared link from being indexed. The per-page control is `noindex`, set as a
`<meta name="robots">` tag or an `X-Robots-Tag` header. The two should change together.
With host protection in front of every route, the alpha needs no robots change. The
`noindex` decision still has to be made once, for the URL that will later carry the
external beta.

## The legal gate is non-waivable

Once the cohort includes **anyone beyond the founders**, the privacy notice and imprint
must carry real legal facts. That gate is a hard exposure gate, not a checklist item a
date can override. A founders-only alpha was judged to add no legal-page requirement, and
that judgment was marked "operator-verify, not a legal opinion".

## See Also
- [[Rate-Limit Keying: Identity Over IP]] — related (host deployment protection makes per-route limits moot for a 2-person alpha)
- [[Production Hardening Patterns]] — extends
- [[Paid Tiers Start at the Beta, Not the Alpha]] — related (the paid host plan carries the deployment-protection feature)
- [[Uptime Probe Asserts the Journey]] — related (the same alpha/beta split)
