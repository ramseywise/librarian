---
name: gdpr-scrub
description: GDPR/PII compliance process for ingesting real customer service tickets into eval fixtures. Covers German/Austrian-language Clara tickets: regex pre-pass, post-scrub quality review, placeholder convention, and commit checklist. Invoke AFTER the ingest script has run — never on raw ticket data.
---

# GDPR Scrub: Eval Data Ingestion

Use when ingesting real customer conversation data into the eval fixture pipeline. The goal is to remove all personal identifiers while preserving the semantic content needed to test the agent.

> **GDPR compliance gate:** This skill operates on *post-regex* output only. Never invoke it on raw or unprocessed ticket data. Sending real PII to any external LLM API (including this one) before deterministic scrubbing is a GDPR violation — there is no legal basis for doing so without a signed Data Processing Agreement and a documented legitimate interest assessment.

---

## Scope

Currently applies to:
- `help-support-rag-agent/data/single_engagement_tickets.csv` → VA eval fixtures at `va-langgraph/tests/evalsuite/fixtures/clara_tickets.json`
- Any future import of real CS ticket data

---

## Step 1: Run the Ingestion Script (deterministic regex pass — no LLM)

Run this first, before any LLM is involved.

```bash
make va-eval-ingest
# or directly:
cd va-langgraph && uv run python eval/ingest/clara_ingest.py
```

The script automatically handles:
- Email reply chain stripping (German: `Am ... schrieb`, `schrieb am`, `Von:`, `-----` separators)
- Angle-bracket URLs from email clients (`<https://...>`)
- Agent signature blocks (`Viele Grüße`, `Mit freundlichen Grüßen`, `Dein [Name]`)
- Sevdesk ticket boilerplate footer (`Deine Ticketnummer:`)
- TICAT classification notes leaked into CONTENT field
- Email addresses → `[EMAIL]`
- German/Austrian phone numbers (`+49`, `+43`, `T +43`, `0` prefix) → `[PHONE]`
- IBANs (DE + 20 digits) → `[IBAN]`
- German/Austrian postal code + city (5-digit DE, 4-digit AT) → `[LOCATION]`
- Salutation names (`Hallo Nicole,` → `Hallo [NAME],`)
- `Herr/Frau + Name` in body text → `Herr/Frau [NAME]`
- Street addresses (Musterstraße 12, Hauptstr. 5a, Am Nelkenberg 13) → `[ADDRESS]`
- Ticket/account refs (7+ digit IDs, `Kundennummer \d{6,}`, `Rechnung Nr. XXXXX`) → `[REF]`
- Business registration IDs (UID, ATU, USt-IdNr, FN, HRA, HRB) → `[BIZ-ID]`
- Skips subscription-cancellation tickets (CRM-meta, not relevant)

---

## Step 2: Post-Scrub Quality Review (Claude review of already-scrubbed output)

**Only run this after Step 1 is complete.** At this point the data contains placeholders, not real PII. The goal here is quality assurance — verify placeholders are correct, check for structural gaps the regex is known to miss, and confirm no obvious identifiers slipped through.

Read the post-regex fixtures and check for the following known regex gaps:

**Names not following Herr/Frau or a salutation**
- Full names mid-sentence: "Klaus Meier hat angerufen" → `[NAME]`
- Slavic/compound names where regex replaces the stem but leaves a suffix: `[NAME]ć` → `[NAME]`
- ALL-CAPS hyphenated names: `MARKUS-STRENZL` (not matched by `[A-ZÄÖÜ][a-z...]+` pattern)

**Personal company names**
- `Müller GmbH`, `Becker & Partner Steuerberatung`, `Fa. Erich Wutzig` → `[COMPANY]`
- Generic legal forms alone (`GmbH`, `UG`, `AG`) are fine — leave them

**Personal URLs**
- Individual's own website: `www.erikbender.de` → `[URL]`
- Personal social media pages: `www.facebook.com/engelhardt.atelier` → `[URL]`
- Screen recording links with session IDs: `https://demodesk.com/recordings/abc123` → `[URL]`

**Short account/invoice refs**
- RE-prefix invoice numbers: `RE-1013` → `RE-[REF]`
- 5-6 digit IDs without keyword context but clearly an account number

**Known false positives — do NOT flag**
- `Hallo [NAME] [NAME],` — first + last name both correctly replaced by regex
- `liebe [NAME]\n[NAME]` — salutation + closing signature, both already replaced
- Two adjacent `[NAME]` tokens anywhere — means both are scrubbed
- Public GitHub repository URLs — shared technical references, not personal PII
- Known SaaS domains: sevdesk.de, stripe.com, help.sevdesk.de, etc.

Apply fixes directly to `va-langgraph/tests/evalsuite/fixtures/clara_tickets.json`.

> **Note on `gdpr_review.py`:** The repo contains `eval/ingest/gdpr_review.py`, which batches fixtures through Gemini 2.5 Flash. Do not use this script unless a DPA covering EU customer data is in place with Google. Even post-regex output may contain residual PII that regex missed — that is the whole point of the review pass, and sending it externally without a DPA is non-compliant. Prefer this Claude-based review (Step 2 above) or a local model (Ollama) as the default path.

---

## Step 3: Pre-Commit PII Check

```bash
make va-eval-pii-check
# or:
cd va-langgraph && uv run python eval/ingest/pii_check.py
```

Checks every fixture for: `@` characters, `DE\d{20}` IBANs, and 7+ digit numbers (with UUID
and URL stripping to avoid false positives from error IDs). Must pass before `git add`.

---

## Placeholder Convention

| PII Type | Placeholder |
|---|---|
| Email address | `[EMAIL]` |
| Phone number | `[PHONE]` |
| Personal name | `[NAME]` |
| Personal company name | `[COMPANY]` |
| Street address | `[ADDRESS]` |
| Postal area | `[LOCATION]` |
| IBAN | `[IBAN]` |
| Ticket / account / invoice reference | `[REF]` |
| Business registration ID | `[BIZ-ID]` |
| Personal URL / recording link | `[URL]` |

---

## Full Pipeline

```bash
# Step 1 — deterministic, no LLM
make va-eval-ingest

# Step 2 — invoke this skill (Claude reviews post-regex output)
# Run /gdpr-scrub after ingest completes

# Step 3 — automated grep check
make va-eval-pii-check
```

---

## What NOT to scrub

- Generic business terms: `GmbH`, `UG`, `AG` used alone
- Category and intent labels
- Generic greetings: `Hallo`, `Sehr geehrte Damen und Herren`
- CES ratings, timestamps, category strings
- Agent role titles without names: `Customer Success Manager`, `Support Team`, `Ihr Team`
- UUID error IDs: `Fehler-ID: a1c16c1e-92e9-43f0-...`
- Public GitHub URLs shared by support agents
