# PII Masking Pipeline Design

**Date:** 2026-05-19  
**Strategy:** S2b — Regex + spaCy NER (PER only, no LOC)

---

## Goal

Productionize PII masking logic from `nbks/intercom/02_pii_redaction.ipynb` into a reusable Python module with a standalone runnable script. Designed to be composable with a future cleaning pipeline.

---

## Architecture

```
core/intercom_conv_preprocessing/
├── pii_redaction/
│   ├── __init__.py       # exposes PIIRedactor
│   ├── patterns.py       # all regex patterns
│   └── redact.py         # PIIRedactor class
└── cleaning/             # future

scripts/
└── run_pii.py            # entry point: CSV in → masked CSV out
```

---

## Components

### `patterns.py`

Defines a `PATTERNS` dict mapping label → compiled regex for each PII type extracted from the notebook:

- `EMAIL`
- `CVR` (Danish company ID)
- `IBAN`
- `SWIFT`
- `PHONE_INTL`
- `PHONE_LOCAL`
- `NAME_SIGNOFF`

Placeholder format: `[LABEL]` (e.g. `[EMAIL]`, `[CVR]`).

---

### `redact.py` — `PIIRedactor`

```python
class PIIRedactor:
    def __init__(self, spacy_model: str = "da_core_news_lg"):
        self.nlp = spacy.load(spacy_model)

    def redact_text(self, text: str) -> str:
        """Single string → redacted string. Applies regex then spaCy NER (PER)."""

    def redact_df(
        self,
        df: pd.DataFrame,
        col: str = "body_clean",
        out_col: str = "body_redacted",
    ) -> pd.DataFrame:
        """Batch-processes a DataFrame column using nlp.pipe(batch_size=256).
        Returns df with new out_col added."""
```

**Redaction order inside `redact_text`:**

1. Apply all regex patterns sequentially (replaces matches with `[LABEL]`)
2. Run spaCy NER (configured model) on the result, mask `PER` entities with `[PER]`
3. Span conflicts resolved by regex taking priority (regex runs first, spaCy skips already-masked spans)

**spaCy model:** Accepts any model name at init — supports future multi-language use (e.g. `en_core_web_lg` for English rows).

**Null handling:** `redact_text` returns the input unchanged for `None` / empty string. `redact_df` skips null rows.

---

### `__init__.py`

```python
from .redact import PIIRedactor
__all__ = ["PIIRedactor"]
```

---

### `scripts/run_pii.py`

Standalone script — reads input CSV, applies `PIIRedactor`, writes output CSV. Input/output paths read from env vars or hardcoded defaults pointing to `data/`.

```python
from core.intercom_conv_preprocessing.pii_redaction import PIIRedactor

redactor = PIIRedactor()
df = pd.read_csv(INPUT_PATH)
df_out = redactor.redact_df(df)
df_out.to_csv(OUTPUT_PATH, index=False)
```

---

## Future: Cleaning Pipeline

When `cleaning/` is built, a combined pipeline script can chain steps:

```python
from core.intercom_conv_preprocessing.cleaning import Cleaner
from core.intercom_conv_preprocessing.pii_redaction import PIIRedactor

df = Cleaner().clean_df(df)
df = PIIRedactor().redact_df(df)
```

---

## Out of Scope

- Language detection / per-row model routing (future work)
- LOC entity masking (S2a — dropped due to higher miss rate)
- ADDRESS / POSTCODE regex (high false-positive risk, deferred in original notebook)
- S1 (regex-only) and S3 (Presidio) strategies
