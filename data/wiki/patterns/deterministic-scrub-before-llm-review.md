---
title: Deterministic Scrub Before LLM Review
tags: [patterns, eval, pattern]
summary: When real customer tickets become eval fixtures, run a deterministic regex scrub first and let an LLM review only the placeholder-bearing output, using a local or DPA-covered model, then gate the commit on a grep check; the LLM pass exists to catch what the regex structurally misses.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/gdpr-scrub/SKILL.md
  - data/raw/claude-docs/playground/docs/tooling/eval-harness.md
---

# Deterministic Scrub Before LLM Review

From the playground repo's `gdpr-scrub` skill and its VA eval-harness doc. Real
German/Austrian customer-service tickets were turned into eval fixtures for a virtual
assistant. Every personal identifier had to go, and the semantic content the agent is
tested on had to stay.

## The ordering is the pattern

1. **Deterministic pass, no LLM.** An ingest script strips reply chains, signatures and
   ticket boilerplate. It then replaces structural PII with typed placeholders: `[EMAIL]`,
   `[PHONE]`, `[IBAN]`, `[LOCATION]`, `[ADDRESS]`, `[REF]`, `[BIZ-ID]`, and `[NAME]` after
   salutations and honorifics.
2. **LLM review on the post-regex output only.** By this point the text holds
   placeholders, not raw PII. The review is quality assurance. Run it with the assistant
   in session or a local model. An external API batch script (in this case a
   Gemini-backed `gdpr_review.py`) is allowed only once a Data Processing Agreement
   covers EU customer data. Post-regex text can still hold residual PII, which is exactly
   why the review exists, so sending it out without a DPA is still non-compliant.
3. **Pre-commit grep gate.** Fail on any `@`, any `DE\d{20}` IBAN, or any number of 7+
   digits. Strip UUIDs and URLs first so error IDs don't trip the check. The gate must
   pass before `git add`.

Sending raw tickets to an LLM "to find the PII" inverts the order. The review model then
becomes the first recipient of the data it is meant to protect.

## What regex structurally misses

The review pass targets known regex gaps, not open-ended checking:

- **Name-suffix leftovers.** The regex replaces a Slavic or compound name's stem and
  leaves the suffix (`[NAME]ć`).
- **ALL-CAPS hyphenated names**, which slip past a `[A-Z][a-z]+` pattern.
- **Full names mid-sentence** with no salutation or honorific anchor.
- **Personal company names** (`<Surname> GmbH`, `Fa. <Name>`) become `[COMPANY]`. A bare
  `GmbH`/`UG`/`AG` stays.
- **Personal URLs**: someone's own site, personal social pages, screen-recording links
  with session IDs.
- **Short references** such as `RE-1013` invoice numbers and 5–6 digit account IDs with
  no keyword context.

The skill also lists **false positives so the reviewer doesn't churn**. Adjacent `[NAME]
[NAME]` tokens mean first and last name were both scrubbed. Public GitHub URLs and known
SaaS domains are not personal data. UUID error IDs, category labels and role titles
without names also stay.

## How much the second pass catches

The eval-harness doc reports that the LLM review pass found **195 additional findings**
that the regex missed. These were mostly names, company names and unusual address
formats. A regex-only scrub is not enough for free-text tickets. Equally, an LLM-only
scrub breaks the compliance ordering above.

## See Also
- [[Presidio PII Redaction for Langfuse]] — alternative-to (NER plus regex redaction at trace egress, not at fixture ingest)
- [[PII Masking Approaches]] — extends (where this ingest-time variant sits among masking strategies)
- [[VA Eval Harness]] — instance-of (the fixture pipeline this scrub feeds)
- [[Golden Set Mechanics]] — prerequisite-for (scrubbed tickets become golden fixtures)
