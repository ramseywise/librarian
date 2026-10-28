---
title: Change the Channel, Not the Count
tags: [foundations, pattern]
summary: When a sourcing target is an order of magnitude above per-source yield, adding sources multiplies ops cost without reaching it — mix channels by job (differentiation, volume floor, ephemeral layer), record rights at the source level on three default-deny axes, and use closed incumbents as the measuring instrument, never the inventory.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/akira/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/akira/docs/research/2026-09-09-source-legality-census-and-channels.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-09-source-legality-census-and-channels.md
  - data/raw/claude-docs/akira/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/playground/docs/research/2026-09-09-catalogue-source-scaling-legality.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-09-source-legality-census-and-channels.md
  - data/raw/claude-docs/playground/docs/research/2026-09-09-source-legality-census-and-channels.md
  - data/raw/claude-docs/akira/docs/research/2026-09-24-social-platform-source-legality.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-24-social-platform-source-legality.md
  - data/raw/claude-docs/akira/docs/research/2026-09-25-dis392-s5-open-sources.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-25-dis392-s5-open-sources.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-25-dis392-s5-open-sources.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-24-social-platform-source-legality.md
  - data/raw/claude-docs/akira/docs/research/2026-09-24-curation-source-legality-sweep.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-24-curation-source-legality-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-24-curation-source-legality-sweep.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197d-corpus-legal.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197d-corpus-legal.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197d-corpus-legal.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197d-corpus-legal.md
---

# Change the Channel, Not the Count

A catalogue census for a city events product (akira): target 5,000 events/month; a
*working* venue website yielded ~10–13 events/month; portfolio mean ~2.7. Reaching the
target on that channel meant ~400 working scrapers — 15× the portfolio and 8× past the
threshold where the team's own notes said source discovery should be an agent, not a
human. Each scraper is a recurring extraction-maintenance cost.

## Channels serve jobs, and the mistake is picking one

| Channel | Job | Volume | Rights shape |
|---|---|---|---|
| Individual venue sites | **Differentiation** — the long tail no aggregator lists | low per source | robots mostly clean; terms unreviewed; most will say yes if asked |
| Municipal open-data feed | **Volume floor + reference data** (locations, districts) | high, one integration | open licence; the cleanest available |
| Curated newsletters | **Ephemeral layer** a human already selected | 20–40 per issue | partnership, not crawl |
| Commercial aggregators | not a channel | — | APIs closed; terms forbid crawling |

Measured, not assumed: the open feed carried zero events for 15 of the 16 venues already
scraped, so it does not replace venue scraping — it *adds* a category. Venue scraping stays
as the quality channel whose cost per event is high and whose differentiation is the product
bet. Scale the volume channel; stop expecting volume from the quality channel.

## Rights at the source level, three axes, every default deny

Rights follow from whose terms governed the bytes fetched — that is a *source* (URL under a
ToS), not a venue (an organisation) and not an event (unreviewable at volume; inherits).
Three questions, three columns, because they gate three different surfaces:

| Axis | Question | Gates |
|---|---|---|
| `legal_posture` | may we crawl it? | ingestion |
| `redistribution_posture` | may we sublicense to a partner? | B2B serving |
| `image_posture` | may we show their photograph? | rendering |

Every default is the deny value — a permissive default "silently asserts a legal position
about 92 sources nobody has reviewed". Keep the columns out of any upstream sync payload so
a re-sync cannot clobber a legal record. The blocker is then not schema but admin: one
email per source asking the three questions. Related exposures from the same audits:
hot-linking images is safer than copying, but an image optimiser that caches bytes is a
reproduction and needs a deliberate position; a crawler without a `robots.txt` reader and
with a placeholder contact domain is what turns a polite crawl into an unauthorised one in
a dispute; and buying a scraper does not acquire a licence the seller never held.

## Robots is not the constraint; terms are

A path-matched robots census (each source's actual URL path against its `Disallow` rules,
not just origin) passed 93% of sources. Terms were discoverable from the homepage for only
half. Measure the cheap gate properly, then accept the expensive gate needs a human.

Mechanics from the census worth carrying into any crawler:

- **robots can only ever say no.** An absent or permissive file is the absence of a
  machine-readable refusal, not a grant; the grant lives in the terms.
- **Sources that are safe by accident are not safe.** Five social-profile sources passed
  only because their intake approach happened to be the one value the import gate rejects;
  a single reclassification in the registry would start fetching against an explicit
  blanket `Disallow: /`, and nothing in the fetcher would stop it. The robots check must
  land *before* the bulk re-enable, not after.
- **Read `Crawl-delay`.** One origin declared 60 s; nothing parsed it, and per-source rate
  limits were set by hand.
- **AI-crawler directives are an operator-attitude signal.** Seven origins named AI user
  agents explicitly; they do not bind a conventional event crawler, but they raise the
  priority of asking first over crawling quietly.
- **Dedupe source rows before recording rights.** Six venues had two source rows (an `/en`
  and an `/en/program/` URL); otherwise one legal decision is recorded twice and can drift.

## Incumbents are the instrument, not the inventory

The product's central bet was "≥40% of surfaced results absent from the top-3 incumbent
listings" — unmeasurable without knowing what the incumbents list. Their terms forbid
crawling; a human hand-checking one week of events against their sites is personal,
bounded, non-commercial sampling. **Same data, different act.** Do the desk sample before
investing in any new channel: if the long-tail share is already high, the channel plan is
confirmation; if it is 15%, no volume fixes it.

## Closed platforms: the doors that look open

A follow-up sweep of the big social platforms' published terms and developer docs
(2026-09-24) found every door shut, including the ones that look open:

- **Platform partner status gates event APIs, not the page owner's consent.** Event
  objects on pages were limited to marketing partners, so even a venue that makes you an
  admin of its own page cannot open them. Research-access tiers required an accredited
  academic institution.
- **A `Sitemap` directive grants nothing.** One platform's robots file advertised a public
  future-events sitemap. `Sitemap` is a non-group directive aimed at crawlers that have
  already been granted a path. Fetching it would be the "robots said yes" error, and here
  robots had not even said yes.
- **Serving an app shell instead of `robots.txt` is a refusal.** The other platform
  returned HTTP 200 with about 640KB of web-app HTML for `/robots.txt`. The previously
  measured `Disallow: /` posture stands, now enforced earlier in the request.
- **oEmbed is an embed, not data.** The one open door (tokenless oEmbed since mid-2026)
  returns markup, not fields, so it can never feed enrichment or ranking. It loads
  platform scripts in the visitor's browser, which is consent-gated tracking under German
  telecom-privacy law, so the pattern is click-to-load. It is a licence to embed, never to
  store or cache.
- **Location/selfie density fails three ways.** There is no endpoint (only scraping). It
  profiles identifiable people, a far worse GDPR exposure than a factual listing. And it
  measures photogenic, not fit. The lawful version already existed: **count sources, not
  people** (independent-source corroboration).
- **The partnership unlock is a feed, never an integration.** Platforms hold the
  highest-value long tail, but it arrives only when a venue hands over its listing. When a
  partner says "we post everything there", the answer is a feed, an export or an email.

## Open data: re-measure "unmatched" before buying coverage

A re-measure of names missing from the open-map pool (2026-09-25) found the
name-matcher loss was about 5% (strict). A looser token heuristic was dominated by
false positives on generic words. The bulk of "unmatched" names were genuinely absent
from the pool, so no matcher could fix them. Probing every remaining pool row was cheap
($0.0022/row, about $23 for 10,445 rows), but only 52% of probed rows reached
`evidence_sufficient`, so probing doesn't convert one-for-one into usable rows, and it
can't add names the pool never held. Two more rules came out of it: **a place registry is
not a curation signal** (being listed says the place exists, not that it matters), and a
source not checked against a primary record stays **UNVERIFIED**, not assessed.

## Robots Is One Gate; Terms Are the Other

A legality sweep of curated-guide sources for a "listed by N guides" corroboration signal:

- **Robots.txt alone would have cleared 9 of 10 guides. 5 of those 9 forbid the use in
  their terms.** Permissive robots plus restrictive terms is the dangerous combination,
  because the easy check says yes.
- **Facts aren't protected, but curation is.** Under the EU/German database right
  (§87a–b UrhG), a curated selection is protected even when each fact is not. So the
  risk inverts: factual enrichment (hours, address) is easy and low-value, while the
  valuable "listed by N" signal comes from the protected selection itself.
- **The text-and-data-mining exception (§44b) requires deleting copies once they're no
  longer needed**, so it doesn't cover a persisted ranking boost derived from them.
- Decision: build licensed corroboration first. Small independent operators are partner
  candidates (change the channel) rather than scrape targets.

## Corpus legal posture as engineering inputs (akira, pre-beta plan)

A pre-beta legal plan for an event corpus turned into a list of engineering facts that
counsel needed to see, not legal conclusions:

- **Know which stored field is verbatim source text.** The event description was passed
  through from the source unchanged, behind a 280-character cliff: anything longer was
  dropped to null, never truncated or rewritten. Model-written enrichment prose lived in
  separate tables. "Is this our text or theirs?" therefore has a per-column answer. That is
  what a terms or copyright review actually needs, and the length cap is a reproduction
  limit only if somebody wrote down why it is 280.
- **An undocumented load-bearing number is a defect.** The cliff value had no recorded
  rationale, and a coverage target quoted in the same plan was an aspiration that no test
  checked. Both were filed as defects to fix (rationale recorded, or target tested or
  removed), so that nobody later cites them as considered limits.
- **Size the legal lanes by resource, not by task count.** The plan split the work into
  engineer hours, lawyer hours and desk-research hours. The per-source terms review
  dominated the total, and the engineering changes were small next to it.
- **Robots posture: record and surface it, don't silently skip.** Each source carries its
  robots and terms status, and a crawl blocked by robots is reported as a distinct outcome.
  See [[Polite Crawler Robots Compliance]].

## See Also
- [[Data Engineering Foundations]] — extends (source portfolio and rights as pipeline design inputs)
- [[Cached Derivation Without a Recompute Path]] — related (the stale `enabled` flag found in the same census)
- [[Write-Only Fields and the Reader Map]] — related (vocabulary gap vs corpus gap, from the companion register)
- [[PII Masking Approaches]] — related (the compliance audit that produced the image and crawler findings)
- [[Listing Pages Masquerading as Records]] — related (what the open-data venue lane actually yielded once measured)
- [[Hotlink-Not-Copy Image Posture]] — extends (the `image_posture` axis worked out as a policy)
- [[Relevance Is the Score, Enrichability Is the Gate]] — related (legality-first sourcing of a local-endorsement signal)
- [[Open POI Data Sources]] — extends (measured open POI sources: licence, channel, fill rate, freshness)
- [[Polite Crawler Robots Compliance]] — extends (the crawler-side mechanics of robots compliance)
