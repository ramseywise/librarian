---
title: Presidio PII Redaction for Langfuse
tags: [infra, pattern]
summary: Presidio orchestration layer with spaCy fr_core_news_lg + CamemBERT NER + custom regex recognizers for French financial PII — wired into Langfuse via the SDK mask hook as a single interception point before traces leave the process.
updated: 2026-07-06
sources:
  - raw/claude-docs/chat-agent/docs/shine_pii_redaction_decision.md
---

# Presidio PII Redaction for Langfuse

A concrete hybrid PII redaction architecture for French-language customer support traces. Extends the general [[PII Masking Approaches]] with a specific implementation decision.

---

## The Stack

```
presidio-analyzer
  ├── NlpEngine: spaCy fr_core_news_lg     ← fast tokenization + basic NER
  ├── Custom Recognizer: CamemBERT NER      ← SOTA French NER (PERSON detection)
  └── PatternRecognizers (regex + checksum):
        IBAN, RIB, CARD (Luhn), NIR (mod-97), SIRET, SIREN, VAT,
        PHONE_FR, EMAIL, IP, DOB, TXREF, BIC, RCS
```

**Why Presidio as orchestration layer:** It composes NER models, regex recognizers, and context-boosting in a single pipeline call. The Langfuse SDK `mask` hook accepts any callable — Presidio slots in directly.

**Why CamemBERT on top of spaCy:** spaCy's CNN-based `fr_core_news_lg` has known false positives on common French words. CamemBERT, fine-tuned on French corpora, significantly outperforms it for person name detection in informal support chat language. Wrapped as a Presidio `EntityRecognizer`.

**Why regex for financial entities:** IBAN, NIR, SIRET, and card numbers are structurally deterministic. A correct regex + checksum is more reliable than any NER model for these — NER adds nothing. Presidio's `PatternRecognizer` supports context words to boost confidence on ambiguous matches.

---

## Entity List and Placeholder Mapping

### Personal Identifiers
| Entity | Placeholder | Method |
|---|---|---|
| Full name | `[NAME]` | NER (PERSON) |
| Date of birth | `[DOB]` | Regex + NER (DATE) |
| Email | `[EMAIL]` | Regex (RFC 5321 subset) |
| Phone (FR) | `[PHONE]` | Regex |
| Postal address | `[ADDRESS]` | NER (LOC) + regex |

### Financial Identifiers
| Entity | Placeholder | Method |
|---|---|---|
| IBAN | `[IBAN]` | Regex + mod-97 checksum |
| BIC/SWIFT | `[BIC]` | Regex |
| Card number (PAN) | `[CARD]` | Regex + Luhn |
| SIRET (14d) | `[SIRET]` | Regex + Luhn-mod97 (check before SIREN) |
| SIREN (9d) | `[SIREN]` | Regex + Luhn (after SIRET to avoid double-redact) |
| TVA intracommunautaire | `[VAT]` | Regex (`FR[A-Z0-9]{2}\d{9}`) |
| NIR (numéro sécu) | `[NIR]` | Regex + mod-97 checksum |

### Government IDs
| Entity | Placeholder | Method |
|---|---|---|
| French national ID (CNI) | `[NATIONAL_ID]` | Regex |
| Passport | `[PASSPORT]` | Regex + context words |
| Driver's license | `[DRIVERS_LICENSE]` | Regex + context words |
| Titre de séjour | `[RESIDENCE_PERMIT]` | NER + context words |

### Digital Identifiers
| Entity | Placeholder | Method |
|---|---|---|
| IPv4/IPv6 | `[IP]` | Regex |
| MAC address | `[MAC]` | Regex |
| Crypto wallet | `[CRYPTO_WALLET]` | Regex (Bitcoin + Ethereum formats) |

**SIREN ordering rule:** Always run SIRET detection first and mask matched spans before the SIREN pass — otherwise the 9-digit SIREN prefix inside a 14-digit SIRET gets double-redacted.

---

## Langfuse Mask Hook (Single Interception Point)

The Langfuse Python SDK accepts a `mask` function at client initialization. It is applied to **all trace data before any network call** — user inputs, model outputs, tool arguments, retrieved chunks, and span metadata.

```python
# redaction/engine.py
from langfuse import Langfuse
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

_analyzer = _build_analyzer()   # built once at module load
_anonymizer = AnonymizerEngine()

def redact_value(value) -> object:
    """Recursively redact strings within any JSON-serializable structure."""
    if isinstance(value, str):
        return redact_text(value)
    elif isinstance(value, dict):
        return {k: redact_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [redact_value(item) for item in value]
    return value

def langfuse_mask(*, data) -> object:
    """Fail-open: on any exception, return original data (never block tracing)."""
    try:
        return redact_value(data)
    except Exception as exc:
        logger.warning("PII redaction failed, publishing unredacted: %s", exc)
        return data

# Wire into Langfuse once at startup
langfuse = Langfuse(mask=langfuse_mask)
```

The mask hook creates a single redaction boundary. Raw PII never leaves the process.

---

## Data Flow

```
User message
  → FastAPI
  → GuardrailsPipeline
  → Engine (tool calls, retrieval, synthesis)
  → Response returned to user

  [async, after response] Langfuse SDK flush:
  → mask(span_data) called in-process
  → Presidio: spaCy NER + CamemBERT + PatternRecognizers
  → Redacted data sent to Langfuse Cloud
```

The Langfuse SDK batches and flushes spans asynchronously — redaction adds latency to the flush, not to the user response path.

---

## Latency Profile

| Component | Latency per call | When |
|---|---|---|
| spaCy fr_core_news_lg | 20–80ms (CPU) | Always (fast first pass) |
| CamemBERT recognizer | 150–300ms (CPU) | For spans > 50 chars |
| Regex PatternRecognizers | < 1ms | Always |

**Mitigation:** Run CamemBERT only when text length > 50 chars and spaCy entity confidence is below a threshold. The async flush path means this latency is invisible to users.

---

## Key Risks

| Risk | Mitigation |
|---|---|
| NIR false positives (any 15-digit mod-97 match) | Context words: `["sécu", "sécurité sociale", "nir"]`; confidence threshold |
| SIREN false positives (any 9-digit match) | Context words + SIRET-first ordering |
| French + English mixed messages | Default `fr` language; fallback to `en` if `langdetect` confidence < 0.8 |
| Model version drift | Pin `fr_core_news_lg` and CamemBERT version in Docker image; treat as code artifacts |
| GDPR right to erasure vs trace immutability | Redact at write time (primary); retroactive batch job via Langfuse API if needed |
| Images in traces | `presidio-image-redactor` (OCR) out of v1 scope — flag to team |

---

## What Is Not Covered (Accepted Risks)

- Images/screenshots embedded in traces — requires OCR (out of v1)
- Langfuse server-side masking for OTel-instrumented spans — client-side mask is the primary control
- Structured data exports (CSV/JSON from Langfuse dashboard) — separate egress control needed
- Coreference across turns (pronoun referencing a redacted name in a prior turn) — accepted limitation

---

## See Also
- [[PII Masking Approaches]]
- [[Langfuse ADK Tracing Patterns]]
- [[Langfuse Platform]]
- [[Input Guardrails Pipeline]]
