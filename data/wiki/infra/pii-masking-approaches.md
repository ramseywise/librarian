---
title: PII Masking Approaches
tags: [infra, eval, concept]
summary: Regex vs LLM-based vs hybrid PII masking for conversation data pipelines — contextual PII is the hard problem; compliance sign-off is a hard gate before data moves.
updated: 2026-10-17
sources:
  - data/raw/meetings/2026-06-25-pii-masking-approval-decision.md
  - data/raw/claude-docs/playground/docs/research/VIR-115-pii-pipeline-design.md
  - data/raw/claude-docs/playground/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/linear/2026-04-24-evaluation-and-improvement.md
  - data/raw/claude-docs/akira/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-06-pii-gdpr-audit.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197a-beta-blockers.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197b-sink-hardening.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197b-sink-hardening.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197b-sink-hardening.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-06-dis197c-retention.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-06-dis197c-retention.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-06-dis197c-retention.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-06-dis197c-retention.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-06-dis197c-retention.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-06-dis197c-retention.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-06-dis197c-retention.md
---

# PII Masking Approaches

## The Problem

Standard PII (email, phone, national ID) is easy — regex handles it reliably. The hard problem is **contextual PII**: company names, account references, and implicit identifiers that only become sensitive in context. Contextual PII is where masking systems fail and where legal and reputational risk is highest.

## Three Approaches

| Approach | Coverage | Cost | Latency | Risk |
|---|---|---|---|---|
| **Regex** | Explicit PII only | Near-zero | < 1ms | Misses contextual PII |
| **LLM-based** | Explicit + contextual | ~$0.01–0.03/conversation | 200–800ms | Over-masking; cost at volume |
| **Hybrid** | Regex for obvious + LLM for contextual | Medium | Medium | Two-step complexity |

**The key insight:** Regex alone will miss contextual PII. LLM-based masking improves coverage but adds cost and latency. The right approach depends on the legal bar set in compliance sign-off and the volume of data being processed.

## Compliance Sequencing

Before any conversation data can be processed, two things must be confirmed in this order:

1. **Storage destination provisioned** — Snowflake or S3 confirmed to meet data residency requirements.
2. **Legal/Ops written sign-off** — Confirmed masking approach and exact pipeline stage where masking is applied.

The masking layer must not be skippable or bypassable. This is a hard gate — the extraction job cannot run until both are done.

## Validation Requirements

Testing must go beyond obvious fields:

- **Explicit PII:** Email, phone, national ID, name fields
- **Contextual PII:** Company names, account references, product references that imply identity
- **Over-masking check:** Legitimate content that looks like PII (product codes, legal citations) — over-masking corrupts the downstream signal

Get Legal/Ops sign-off only after validation results are reviewed.

## Minimising PII in Product Telemetry (not just conversation data)

A GDPR audit of an LLM-ranked consumer product (akira) found the leak was not in prompts
but in what the ranker *logged* about each request. Lessons that transfer:

- **Coarse accuracy is not a coarse stored value.** The intake rounded a user's location to
  a 500 m grid for *display* but logged the raw lat/lng in the result-set row. Minimisation
  is a property of the serialised value, not of what the UI shows.
- **Strip at a single serialisation choke point.** One `redactMomentContext()` applied where
  the log row is built beats per-field care in every caller; a second log path that bypasses
  it is the next leak.
- **Adding a pseudonymous user id before fixing the leak makes it worse** — it turns
  per-request precise locations into a linkable trajectory. Order the work: redact, then
  identify.
- **Build the retention job while the table is small.** A delete-after-N-days sweep over a
  few thousand rows is trivial; the same job over a year of rows is a migration project, and
  "we will add retention later" is the sentence that creates the project.
- **Hot-linked images plus an image optimiser that caches bytes is a reproduction**, with
  rights consequences the hot-link alone did not have (see [[Change the Channel, Not the Count]]).
- Process note from the same audit: "staged but uncommitted does not survive another
  session" — a compliance fix that is not committed has not happened.

### What the fix plans decided (2026-09-06 → 09-20)

- **Drop the field; don't resolve it to something coarser.** The requirement was "never raw
  lat/lng; resolved district plus coarse radius band only". No reverse-geocoder existed, so
  "resolved district" meant either a network call on every near-me request or a new
  hand-maintained lookup table. The team chose to null the field at the one log-row choke
  point. They accepted, and wrote down, that near-me result sets could no longer be
  replayed offline. Ranking still receives the unredacted context: redaction applies to
  what is *written*, not to what is *used*. Dropping also cut the estimate to about an
  hour, against a 6–10 h earlier figure that had quietly priced in district resolution.
  A mandatory regression test asserts that the field never reaches the log row.
- **A logger `redact` config is a guardrail with a depth limit.** pino's `redact` uses
  fast-redact paths. A bare key matches only at the top level, `*` matches exactly one
  segment, and there is no recursive `**`. The config listed sensitive keys at the two
  depths the codebase actually uses (flat, and one level under a named context object).
  It says in a comment that it is best-effort, not a guarantee.
- **A user-link column is a liability until something reads it.** The spec called for a
  `pseudo_user_id` on telemetry so that one predicate could answer an export or deletion
  request. Leaving it out was what kept erasure clean: deleting the auth user cascades, and
  once coordinates were dropped, the orphaned telemetry rows were anonymous measurements.
  Neither the retention job (time-based) nor the export (doesn't read telemetry) needed
  per-user lookup. So the column waits for a named trigger, such as per-account ranking
  history or an abuse trace. (See [[Study-Scoped Pseudonymous Attribution]] for the
  enrolled-study version.)
- **A data-subject export goes through the admin client with explicit owner filters.** Two
  RLS policies were wrong for this purpose: one had no owner clause on select, and the
  other had no select policy at all. With the session client, the export would leak other
  users' rows or silently miss the user's own. Regression tests assert that every query is
  scoped by its owner column, and that a later "simplify to the session client" fails.
  The export includes only reports the user filed, not reports *about* them, which is a
  product and legal call.
- **Free-text names in a shared artifact get the same retention clock.** A poll voter's
  display name is scrubbed back to the column default after 90 days, whatever the poll's
  status. The tally and the winning option are untouched. A plain filtered admin-client
  update was chosen over new `SECURITY DEFINER` SQL functions: it touches one table with no
  cascade, while the archive-then-delete telemetry job needed an atomic SQL boundary.
- **Re-verify a plan against main before executing it.** The retention plan sat for two
  weeks. In that time an unrelated issue built two of its four phases under a different
  design, and a directory restructure moved every path. The refine pass struck those
  phases and kept them only as a historical record, which cut the estimate from 15–21 h to
  6–8 h.

## When to Revisit the Approach

At high volume (>10K conversations/day), LLM-based masking becomes expensive. Revisit with a purpose-built NER model (spaCy, flair) — cheaper and faster than an LLM call per conversation at scale, with acceptable contextual PII coverage for most use cases.

## Concrete Implementation

For a production hybrid implementation targeting French-language financial support traces, see [[Presidio PII Redaction for Langfuse]] — Presidio orchestration layer with spaCy fr_core_news_lg + CamemBERT NER + custom regex recognizers for 20+ French PII entity types, wired into the Langfuse SDK `mask` hook.

## Regex-then-NER pipeline (playground PII design)

A two-stage masker for conversation logs: regex recognisers run first for structured PII,
then a spaCy NER pass masks **PER only**. Where spans conflict, the regex span wins,
because it is the more precise recogniser. LOC masking was dropped because its miss and
false-hit rates outweighed the benefit. ADDRESS and POSTCODE regexes were deferred because
of their false-positive risk. Masking is batched with `nlp.pipe(batch_size=256)` and spans
are replaced with a `[LABEL]` placeholder, so the redacted text still shows *what kind* of
thing was removed.

## Four-stage masker with a measured residual-risk table (sign-off request)

A later iteration of the same conversation-data masker, submitted for Legal/Ops sign-off,
ran four stages at ingestion so raw PII never reached storage or an LLM:

1. **Regex** — email, company and personal national IDs, IBAN, SWIFT, phone, IP, and
   name sign-offs ("Best regards, X").
2. **NER** — PER entities only, with a **company blocklist** so customer company names are
   not masked as people.
3. **Contact-name lookup** — exact match against the CRM contact list, greedy multi-word
   first, then single-first-name fallback.
4. **Gazetteer address masking** — postcode+city pairs and standalone city names from an
   official postcode dataset, rather than an address regex (the regex was the part
   deferred earlier for false-positive risk).

Measured on 100 **high-risk** rows (not a random sample): 6% of rows had missed PII
(9 spans — almost all isolated first names that neither NER nor the sign-off rule caught,
plus one session token outside scope) and 8% were over-masked (12 spans — city names,
domains, company names and ordinary words tagged as names).

What transfers:

- **Report FN and FP separately, with different compliance weights.** Misses are a privacy
  risk; over-masking costs readability only. One accuracy number hides the asymmetry.
- **The residual false-negative rate is part of what Legal signs.** The request states it
  and asks for explicit acceptance, rather than implying the masker is complete.
- **Isolated first names are the dominant miss class** once regex and NER are in place —
  the case a contact lookup or a sign-off rule only partly covers.
- **Scope the sign-off narrowly** (historical data for an eval set, no live pipeline) so
  the residual risk being accepted is bounded.

## See Also
- [[Presidio PII Redaction for Langfuse]]
- [[HITL Annotation Pipeline]]
- [[RAG Evaluation]]
- [[Bedrock KB vs LangGraph Decision]]
- [[Input Guardrails Pipeline]]
- [[Rate-Limit Keying: Identity Over IP]] — related (identity cookies as a lower-exposure key than IP)
- [[Change the Channel, Not the Count]] — related (rights posture findings from the same compliance audit)
- [[Study-Scoped Pseudonymous Attribution]] — extends (pseudonym is still personal data; erasure must cover linked rows)
- [[Logger Redact Guardrail]] — related (the log-sink layer: a redact list as a guardrail for future call sites)
