---
title: Transactional Email Sender Setup
tags: [infra, pattern]
summary: Setting up auth-flow email (provider choice, sending subdomain, SPF/DKIM/DMARC, templates, rate limits) — most failure modes are silent spam-folder routing, so verify on a real delivered message's Authentication-Results header.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis148-sending-domain.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis148-sending-domain.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis148-sending-domain.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis148-sending-domain.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis148-sending-domain.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis148-sending-domain.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis148-sending-domain.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis39-auth-smtp-templates.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis39-auth-smtp-templates.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis39-auth-smtp-templates.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis39-auth-smtp-templates.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis39-auth-smtp-templates.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis39-auth-smtp-templates.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis39-auth-smtp-templates.md
---

# Transactional Email Sender Setup

From the akira sending-domain and auth-SMTP plans: wiring an auth provider's confirmation and
magic-link mail through a dedicated email provider. Almost every misconfiguration here fails
*silently* — mail is accepted, then lands in spam or is throttled — so the plan is built around
explicit verification. The sequencing argument (domain → DNS → warm-up as the long pole) is in
[[The Free Decision Is the Long-Lead Item]].

## Provider choice: what you can actually reach

When every message is sent by the auth provider, the email provider is used only as an SMTP
relay. Its API, SDK, and template-tooling differentiators are unreachable from that path, so
they should not drive the choice; data residency and deliverability did (an EU-hosted provider
was picked). Reversibility is asymmetric: switching providers later is cheap, but *starting*
late is expensive, because sender reputation is measured from the first send.

## DNS

- **Use a sending subdomain.** The apex already carried an SPF record for other mail, and a
  name can hold only one SPF record; a subdomain keeps the transactional sender's SPF, DKIM, and
  reputation separate.
- **DMARC starts at `p=none`** (monitor only), and add an apex DMARC record as well.
- **DKIM keys break silently when line-wrapped** on paste into the DNS UI.
- **The From address must sit on the verified subdomain.** A sender off that domain fails DKIM
  alignment and goes to spam with no error anywhere.

## Verification

Done means: a real message sent *through the auth flow* (not a provider test send) arrives with
an `Authentication-Results` header showing `spf=pass`, `dkim=pass`, `dmarc=pass`.

## Templates and auth settings

- Keep the confirmation-URL template token intact when restyling templates.
- Check the auth provider's site-URL setting is not still `localhost` — links will render and
  point nowhere.
- Include a plain-text part.
- Don't forget the less-visited templates (email-change confirmation).
- The auth provider's default email rate limit (a couple per hour on the built-in sender)
  throttles without surfacing an error — raise it once custom SMTP is in place.

## Order of switches

Toggle magic-link sign-in last, after delivery is verified. Do not route production mail
through the new sender before warm-up has begun. (Warm-up length estimates in the sources range
from hours to ~3 weeks without a cited basis — treat it as unknown and start early.)

## See Also
- [[The Free Decision Is the Long-Lead Item]] — extends (the operational checklist behind the chain)
- [[Silent Failure Catalogue]] — instance-of (spam-folder routing and silent throttling)
