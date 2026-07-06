# PII Masking Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Productionize S2b PII masking (regex + spaCy NER PER-only) into an importable `PIIRedactor` class and a standalone `scripts/run_pii.py` entry point.

**Architecture:** `PIIRedactor` class in `core/intercom_conv_preprocessing/pii_redaction/` wraps regex pattern application followed by spaCy `da_core_news_lg` NER. Regex patterns live in a separate `patterns.py`. A standalone script `scripts/run_pii.py` reads a CSV, runs `redact_df()`, and writes the output.

**Tech Stack:** Python 3.12, spaCy (`da_core_news_lg`), pandas, pytest

**Spec:** `docs/superpowers/specs/2026-05-19-pii-pipeline-design.md`

---

## File Map

| File                                                         | Action | Responsibility       |
| ------------------------------------------------------------ | ------ | -------------------- |
| `core/intercom_conv_preprocessing/__init__.py`               | Create | Package marker       |
| `core/intercom_conv_preprocessing/pii_redaction/__init__.py` | Create | Expose `PIIRedactor` |
| `core/intercom_conv_preprocessing/pii_redaction/patterns.py` | Create | All regex patterns   |
| `core/intercom_conv_preprocessing/pii_redaction/redact.py`   | Create | `PIIRedactor` class  |
| `scripts/run_pii.py`                                         | Create | CLI entry point      |
| `tests/test_pii_redaction.py`                                | Create | Unit tests           |

---

## Task 1: Regex Patterns

**Files:**

- Create: `core/intercom_conv_preprocessing/__init__.py`
- Create: `core/intercom_conv_preprocessing/pii_redaction/__init__.py`
- Create: `core/intercom_conv_preprocessing/pii_redaction/patterns.py`
- Test: `tests/test_pii_redaction.py`

- [ ] **Step 1: Create package markers**

```bash
touch core/intercom_conv_preprocessing/__init__.py
touch core/intercom_conv_preprocessing/pii_redaction/__init__.py
```

- [ ] **Step 2: Write failing tests for regex patterns**

Create `tests/test_pii_redaction.py`:

```python
from __future__ import annotations

import re
import pytest
from core.intercom_conv_preprocessing.pii_redaction.patterns import PATTERNS


class TestPatterns:
    def test_email(self):
        assert re.search(PATTERNS["EMAIL"], "send to john@example.com ok")

    def test_email_no_false_positive(self):
        assert not re.search(PATTERNS["EMAIL"], "no email here")

    def test_cvr(self):
        # CVR: 8-digit Danish company ID, often written as "CVR 12345678" or "CVR: 12345678"
        assert re.search(PATTERNS["CVR"], "CVR 12345678")
        assert re.search(PATTERNS["CVR"], "cvr: 87654321")

    def test_iban(self):
        assert re.search(PATTERNS["IBAN"], "DK5000400440116243")
        assert re.search(PATTERNS["IBAN"], "DE89370400440532013000")

    def test_swift(self):
        assert re.search(PATTERNS["SWIFT"], "DEUTDEDB")
        assert re.search(PATTERNS["SWIFT"], "NDEADKKK")

    def test_phone_intl(self):
        assert re.search(PATTERNS["PHONE_INTL"], "+45 12 34 56 78")
        assert re.search(PATTERNS["PHONE_INTL"], "+4512345678")

    def test_phone_local(self):
        assert re.search(PATTERNS["PHONE_LOCAL"], "12 34 56 78")

    def test_name_signoff(self):
        assert re.search(PATTERNS["NAME_SIGNOFF"], "Med venlig hilsen\nJens Hansen")
        assert re.search(PATTERNS["NAME_SIGNOFF"], "Mvh\nAnna Larsen")
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_pii_redaction.py::TestPatterns -v
```

Expected: `ERROR` or `ModuleNotFoundError` (patterns.py doesn't exist yet)

- [ ] **Step 4: Create `patterns.py`**

Create `core/intercom_conv_preprocessing/pii_redaction/patterns.py`:

```python
import re

PATTERNS: dict[str, re.Pattern] = {
    "EMAIL": re.compile(
        r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
        re.IGNORECASE,
    ),
    "CVR": re.compile(
        r"\bcvr[:\s.#]*\d{8}\b",
        re.IGNORECASE,
    ),
    "IBAN": re.compile(
        r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b",
    ),
    "SWIFT": re.compile(
        r"\b[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?\b",
    ),
    "PHONE_INTL": re.compile(
        r"\+\d{1,3}[\s\-]?\d[\d\s\-]{6,14}\d",
    ),
    "PHONE_LOCAL": re.compile(
        r"\b\d{2}[\s\-]\d{2}[\s\-]\d{2}[\s\-]\d{2}\b",
    ),
    "NAME_SIGNOFF": re.compile(
        r"(?:med\s+venlig\s+hilsen|mvh|venlig\s+hilsen|regards|best\s+regards)[,\s\n]+([A-ZÆØÅ][a-zæøå]+(?:\s+[A-ZÆØÅ][a-zæøå]+)+)",
        re.IGNORECASE,
    ),
}
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_pii_redaction.py::TestPatterns -v
```

Expected: all 8 tests PASS

- [ ] **Step 6: Commit**

```bash
git add core/intercom_conv_preprocessing/__init__.py \
        core/intercom_conv_preprocessing/pii_redaction/__init__.py \
        core/intercom_conv_preprocessing/pii_redaction/patterns.py \
        tests/test_pii_redaction.py
git commit -m "feat: add PII regex patterns with tests"
```

---

## Task 2: `PIIRedactor` class — `redact_text`

**Files:**

- Create: `core/intercom_conv_preprocessing/pii_redaction/redact.py`
- Modify: `core/intercom_conv_preprocessing/pii_redaction/__init__.py`
- Test: `tests/test_pii_redaction.py` (add class)

- [ ] **Step 1: Write failing tests for `redact_text`**

Append to `tests/test_pii_redaction.py`:

```python
from core.intercom_conv_preprocessing.pii_redaction import PIIRedactor


@pytest.fixture(scope="module")
def redactor():
    return PIIRedactor()  # loads da_core_news_lg once for this test module


class TestRedactText:
    def test_masks_email(self, redactor):
        result = redactor.redact_text("Kontakt os på support@firma.dk tak")
        assert "[EMAIL]" in result
        assert "support@firma.dk" not in result

    def test_masks_cvr(self, redactor):
        result = redactor.redact_text("Vores CVR 12345678 er registreret")
        assert "[CVR]" in result
        assert "12345678" not in result

    def test_masks_phone_intl(self, redactor):
        result = redactor.redact_text("Ring til +45 12 34 56 78")
        assert "[PHONE_INTL]" in result

    def test_masks_per_entity(self, redactor):
        # spaCy da_core_news_lg should detect Danish person name
        result = redactor.redact_text("Hej jeg hedder Anders Jensen")
        assert "[PER]" in result

    def test_empty_string_returns_empty(self, redactor):
        assert redactor.redact_text("") == ""

    def test_none_returns_none(self, redactor):
        assert redactor.redact_text(None) is None

    def test_no_pii_unchanged(self, redactor):
        text = "Hej, kan du hjælpe mig med min ordre?"
        result = redactor.redact_text(text)
        # No PII — text may differ slightly but no mask tokens for PII types
        assert "[EMAIL]" not in result
        assert "[CVR]" not in result
        assert "[PHONE_INTL]" not in result
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_pii_redaction.py::TestRedactText -v
```

Expected: `ImportError` (PIIRedactor not defined yet)

- [ ] **Step 3: Create `redact.py`**

Create `core/intercom_conv_preprocessing/pii_redaction/redact.py`:

```python
from __future__ import annotations

import pandas as pd
import spacy

from .patterns import PATTERNS


class PIIRedactor:
    def __init__(self, spacy_model: str = "da_core_news_lg") -> None:
        self.nlp = spacy.load(spacy_model, disable=["morphologizer", "parser", "senter"])

    def redact_text(self, text: str | None) -> str | None:
        if not text:
            return text
        # Step 1: regex pass
        for label, pattern in PATTERNS.items():
            text = pattern.sub(f"[{label}]", text)
        # Step 2: spaCy NER — mask PER entities only
        doc = self.nlp(text)
        spans = [(ent.start_char, ent.end_char) for ent in doc.ents if ent.label_ == "PER"]
        # Replace spans in reverse order to preserve character offsets
        for start, end in sorted(spans, reverse=True):
            text = text[:start] + "[PER]" + text[end:]
        return text

    def redact_df(
        self,
        df: pd.DataFrame,
        col: str = "body_clean",
        out_col: str = "body_redacted",
    ) -> pd.DataFrame:
        df = df.copy()
        texts = df[col].tolist()
        valid_mask = [isinstance(t, str) and bool(t) for t in texts]
        valid_idx = [i for i, v in enumerate(valid_mask) if v]
        # Step 1: regex pass on all valid texts
        regex_masked = []
        for t in [t for t, v in zip(texts, valid_mask) if v]:
            for label, pattern in PATTERNS.items():
                t = pattern.sub(f"[{label}]", t)
            regex_masked.append(t)
        # Step 2: batch NER on regex-masked texts
        results: list[str | None] = list(texts)
        for i, text, doc in zip(valid_idx, regex_masked, self.nlp.pipe(regex_masked, batch_size=256)):
            spans = [(e.start_char, e.end_char) for e in doc.ents if e.label_ == "PER"]
            for start, end in sorted(spans, reverse=True):
                text = text[:start] + "[PER]" + text[end:]
            results[i] = text
        df[out_col] = results
        return df
```

- [ ] **Step 4: Update `__init__.py`**

Edit `core/intercom_conv_preprocessing/pii_redaction/__init__.py`:

```python
from .redact import PIIRedactor

__all__ = ["PIIRedactor"]
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_pii_redaction.py::TestRedactText -v
```

Expected: all 7 tests PASS (note: `test_masks_per_entity` depends on spaCy model quality — if it fails, check that `da_core_news_lg` is installed: `python -m spacy download da_core_news_lg`)

- [ ] **Step 6: Run all PII tests**

```bash
pytest tests/test_pii_redaction.py -v
```

Expected: all 15 tests PASS

- [ ] **Step 7: Commit**

```bash
git add core/intercom_conv_preprocessing/pii_redaction/redact.py \
        core/intercom_conv_preprocessing/pii_redaction/__init__.py \
        tests/test_pii_redaction.py
git commit -m "feat: add PIIRedactor class with redact_text"
```

---

## Task 3: `redact_df` tests + `scripts/run_pii.py`

**Files:**

- Test: `tests/test_pii_redaction.py` (add DataFrame tests)
- Create: `scripts/run_pii.py`

- [ ] **Step 1: Write failing tests for `redact_df`**

Append to `tests/test_pii_redaction.py`:

```python
class TestRedactDf:
    def test_adds_output_column(self, redactor):
        df = pd.DataFrame({"body_clean": ["email: test@x.com", "ingen pii her"]})
        result = redactor.redact_df(df)
        assert "body_redacted" in result.columns
        assert result.shape[0] == 2

    def test_email_masked_in_df(self, redactor):
        df = pd.DataFrame({"body_clean": ["skriv til ceo@firma.dk"]})
        result = redactor.redact_df(df)
        assert "[EMAIL]" in result["body_redacted"].iloc[0]
        assert "ceo@firma.dk" not in result["body_redacted"].iloc[0]

    def test_null_rows_preserved(self, redactor):
        df = pd.DataFrame({"body_clean": ["test@x.com", None, ""]})
        result = redactor.redact_df(df)
        assert result["body_redacted"].iloc[1] is None
        assert result["body_redacted"].iloc[2] == ""

    def test_original_df_not_mutated(self, redactor):
        df = pd.DataFrame({"body_clean": ["test@x.com"]})
        original_cols = list(df.columns)
        redactor.redact_df(df)
        assert list(df.columns) == original_cols

    def test_custom_col_names(self, redactor):
        df = pd.DataFrame({"msg": ["ring +45 12 34 56 78"]})
        result = redactor.redact_df(df, col="msg", out_col="msg_clean")
        assert "msg_clean" in result.columns
        assert "[PHONE_INTL]" in result["msg_clean"].iloc[0]
```

- [ ] **Step 2: Run tests to verify they pass (redact_df already implemented)**

```bash
pytest tests/test_pii_redaction.py::TestRedactDf -v
```

Expected: all 5 tests PASS

- [ ] **Step 3: Create `scripts/` directory and `run_pii.py`**

```bash
mkdir -p scripts
```

Create `scripts/run_pii.py`:

```python
"""Standalone script: apply PII masking to a cleaned conversation CSV.

Usage:
    python scripts/run_pii.py

Reads from INPUT_PATH, writes to OUTPUT_PATH (set via env vars or defaults below).
"""

from __future__ import annotations

import os

import pandas as pd

from core.intercom_conv_preprocessing.pii_redaction import PIIRedactor

INPUT_PATH = os.getenv("PII_INPUT_PATH", "data/conv_parts_cleaned.csv")
OUTPUT_PATH = os.getenv("PII_OUTPUT_PATH", "data/conv_parts_redacted.csv")
SPACY_MODEL = os.getenv("PII_SPACY_MODEL", "da_core_news_lg")


def main() -> None:
    print(f"Loading data from {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df):,} rows. Running PII masking...")

    redactor = PIIRedactor(spacy_model=SPACY_MODEL)
    df_out = redactor.redact_df(df)

    df_out.to_csv(OUTPUT_PATH, index=False)
    print(f"Done. Saved {len(df_out):,} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run full test suite**

```bash
pytest tests/test_pii_redaction.py -v
```

Expected: all 20 tests PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_pii_redaction.py scripts/run_pii.py
git commit -m "feat: add redact_df tests and run_pii.py entry point"
```

---

## Task 4: Smoke-test `run_pii.py` with small data

- [ ] **Step 1: Create a tiny test CSV (5 rows) and run the script**

```bash
python - <<'EOF'
import pandas as pd
df = pd.DataFrame({"body_clean": [
    "Hej, min email er anders@test.dk",
    "Ring til +45 12 34 56 78",
    "CVR 12345678",
    None,
    "Ingen PII her overhovedet",
]})
df.to_csv("/tmp/pii_smoke_input.csv", index=False)
EOF

PII_INPUT_PATH=/tmp/pii_smoke_input.csv PII_OUTPUT_PATH=/tmp/pii_smoke_output.csv python scripts/run_pii.py
```

- [ ] **Step 2: Inspect output**

```bash
python - <<'EOF'
import pandas as pd
df = pd.read_csv("/tmp/pii_smoke_output.csv")
print(df[["body_clean", "body_redacted"]].to_string())
EOF
```

Expected output (approximately):

```
                       body_clean                    body_redacted
0  Hej, min email er anders@test.dk  Hej, min email er [EMAIL]
1      Ring til +45 12 34 56 78       Ring til [PHONE_INTL]
2                   CVR 12345678                  [CVR]
3                           None                       None
4      Ingen PII her overhovedet      Ingen PII her overhovedet
```

- [ ] **Step 3: Commit if smoke test passes**

```bash
git add .
git commit -m "feat: PII masking pipeline complete"
```
