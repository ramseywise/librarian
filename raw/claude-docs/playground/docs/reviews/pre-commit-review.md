# Pre-Commit Code Review

Date: 2026-04-27

---

## Summary

The changeset is in good shape overall. The cleanup fixes (model factory, datetime, regex
ordering) are correct; the hc-rag-agent is a well-structured LangGraph service with proper
pyproject.toml, a working Dockerfile, and solid guardrails code. There are **no
showstopper bugs** that would break production, but there are three issues that should be
fixed before the commit: a missing blank line that will trip ruff in vendor-a_ingest.py, a
typing import out of PEP-8 order in support_agent.py, and pervasive stdlib `logging`
usage throughout hc-rag-agent's runtime/orchestration layer (the project convention is
`structlog`). The eval pipeline changes (models.py, friction_grader.py, regression.py) are
correct and safe.

---

## Critical Issues (must fix before commit)

### 1. `vendor-a_ingest.py` — missing blank line between `_sub_doc_ref` and `_BIZ_ID_RE`

**File:** `va-langgraph/eval/ingest/vendor-a_ingest.py`, lines 164–166

```python
    return "([REF])"
# Business registration / tax IDs ...    ← no blank line after function body
_BIZ_ID_RE = re.compile(...)
```

The `_sub_doc_ref` function closes with no blank line before the next module-level
statement. ruff E302 requires two blank lines between a function and the next top-level
definition. The project's post-write hook runs ruff check and will flag this on commit.

**Fix:** add a blank line (two blank lines before `_BIZ_ID_RE`).

---

### 2. `va-google-adk/sub_agents/support_agent.py` — `typing` import after third-party block

**File:** line 12

```python
import httpx
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.genai import types
from typing import Any          # ← should be in stdlib block above httpx
```

`from typing import Any` is a stdlib import but sits inside the third-party import
block. ruff I001 (isort) will fail on this. Move it above the blank line that separates
stdlib from third-party imports.

**Fix:**
```python
from __future__ import annotations

import os
from pathlib import Path
from typing import Any          # ← here

import httpx
from google.adk.agents import Agent
...
```

---

### 3. `hc-rag-agent` — stdlib `logging` used throughout runtime/orchestration layer

**Convention:** project style is `structlog` not stdlib `logging` in src code.

The hc-rag-agent uses stdlib `logging` in 76 places across its runtime/orchestration
layer while `structlog` is used correctly in `clients/llm.py`, `evals/`, `ingest/`, and
`rag/datastore/factory.py`. The split is inconsistent.

**Affected files (non-exhaustive):**
- `main.py`
- `orchestrator/langgraph/runtime.py`
- `orchestrator/langgraph/nodes/answer.py`
- `orchestrator/langgraph/nodes/escalation.py`
- All other nodes under `orchestrator/langgraph/nodes/`

The hook (`no stdlib logging`) will fire on any of these if they go through a Write/Edit
pass. They do not currently block commit (the hook fires on write, not on commit), but
this is a style violation that will require a follow-up sweep.

**Recommended fix:** convert `import logging; log = logging.getLogger(__name__)` to
`import structlog; log = structlog.get_logger(__name__)` in all orchestration modules.
This is a mechanical change across ~15 files.

---

## Should Fix (recommended, not blocking)

### 4. `vendor-a_ingest.py` — `_sub_doc_ref` missing blank line at end of function

Related to issue #1 above. While ruff will catch the E302 at the top, there is also no
blank line between the function close and the comment on line 165. A single blank line
would make the code readable even before ruff runs.

---

### 5. `hc-rag-agent/orchestrator/langgraph/runner.py` — `print()` in src

**File:** `orchestrator/langgraph/runner.py`, lines 23–98

The CLI runner uses `print()` for all its output. This is a CLI entrypoint (not a
library), so it is reasonable, but the project hook blocks `print()` in src. Add
`# noqa: T201` comments to the CLI print calls (as is already done correctly in
`evals/runner.py` and `rag/ingestion/corpus_v2.py`) or switch to `sys.stdout.write`.

---

### 6. `hc-rag-agent/guardrails/pii_redaction.py` — uses old-style `List` / `Tuple` annotations

**File:** lines 12–14, 98–101

```python
from typing import List, Tuple
_RAW_PATTERNS: List[Tuple[str, str]] = [...]
PII_RE: List[Tuple[re.Pattern, str]] = [...]
```

The project targets Python 3.12 and has `from __future__ import annotations` available.
Use lowercase built-in generics: `list[tuple[str, str]]`. Not a runtime bug, but
inconsistent with the rest of the codebase.

---

### 7. `eval/models.py` — hardcoded `"gemini-2.5-flash"` default in `EvalRunConfig`

**File:** `va-langgraph/eval/models.py`, line 61

```python
model_id: str = "gemini-2.5-flash"
```

The CLAUDE.md style rule says no hardcoded model strings. This is an eval config model
(records which model ran the eval), so it arguably needs a concrete default, but it
should at minimum read from an env var or `model_factory` to be consistent. Similarly,
`gdpr_review.py` line 198 has `default="gemini-2.5-flash"` as an argparse default.

Low risk since these are eval/ingest tooling, but worth tracking.

---

### 8. `hc-rag-agent/core/observability.py` — configures stdlib logging root logger

**File:** lines 25–41

`configure_runtime()` sets up the stdlib root logger. Because the hc-rag-agent also
imports `structlog`, calls to `structlog.get_logger()` will output via structlog's
pipeline while calls to `logging.getLogger()` will go through the stdlib handler. Both
work, but the output format will be inconsistent under production load. Consider routing
structlog output through the stdlib handler (the standard pattern:
`structlog.configure(wrapper_class=..., processors=[..., structlog.stdlib.ProcessorFormatter.wrap_for_formatter(...)]`)
or switching everything to structlog.

---

### 9. `docker-compose.va.yml` — `va-gateway-adk` missing `postgres` dependency

`va-gateway-lg` correctly depends on `postgres`, but `va-gateway-adk` only depends on
`product-a-mcp` and `hc-rag-agent`. If the ADK gateway ever needs postgres (e.g. if it gains
its own checkpointer), this will silently race. Not a current bug but worth noting.

---

## Notes / Observations

### Correctness

- **`regression.py` thresholds removal** — correct. The `thresholds` param was dead
  weight; callers compute floors from the returned report. No existing callers passed
  the argument (confirmed by grep).

- **`eval/models.py` datetime fix** — correct. Replacing `datetime.utcnow()` (deprecated
  in 3.12, removed in future) with `datetime.now(timezone.utc)` is the right fix.

- **`domains.py` support_subgraph refactor** — the CRAG loop removal is intentional and
  correct; the new HTTP call to hc-rag-agent is the correct architectural move. Error
  handling delegates to `r.raise_for_status()` which will bubble as an httpx exception —
  acceptable, the caller wraps in try/except at the graph level.

- **`support_agent.py` thread_id fix** — using `tool_context.state.get("session_id")`
  with a safe fallback is correct. The bare `except Exception: pass` (line 28) is
  intentional — tool_context is an ADK internal; any AttributeError or missing key
  should silently fall back to the default thread_id.

- **`vendor-a_ingest.py` regex ordering** — moving `_ANGLE_URL_RE` and its application
  to the top of `_scrub()` is correct; stripping angle-bracket URLs before email/phone
  patterns prevents false matches on URLs containing email-like substrings.

- **`vendor-a_ingest.py` `_CHAIN_RE` broadening** — removing the `Original` suffix from
  `-----+` is a reasonable improvement for non-English CRM exports. Low risk.

- **`pii_check.py`** — the URL/UUID strip before digit check prevents false positives on
  fixture IDs. Logic is sound. `_REPO_ROOT` path computation (`parents[3]`) assumes
  the file lives at `va-langgraph/eval/ingest/pii_check.py` — confirmed correct.

- **`friction_grader.py`** — well-implemented. The `escalation_signal is not None` guard
  is correct; the field defaults to `False` (not `None`) in `EvalTask`, so this guard
  always fires. That means `ground_truth_signal` and `ground_truth_match` will always be
  populated in dimensions — fine, but consider whether you want to gate it on
  `task.escalation_signal` only being meaningful for certain test_types.

### Security

- No hardcoded secrets found in any reviewed file.
- `pii_redaction.py` patterns are thorough. One known over-redaction: the 16-digit card
  pattern will fire on invoice numbers of that length. Acceptable for a guardrail.
- `prompt_injection.py` pattern #6 (`api_key`, `secret`, `password` in any key=value)
  is aggressive — a user asking "how do I set my API key in vendor-a?" will trigger it.
  This is intentionally conservative, but worth monitoring false-positive rate.

### hc-rag-agent — general assessment

Architecture is consistent with va-langgraph: pydantic v2 models at API boundaries,
`from __future__ import annotations` throughout, f-strings, `httpx` (not `requests`),
`async`-first I/O, no magic numbers. The main divergence is the stdlib/structlog logging
split (issue #3) and the old-style typing generics (issue #6). The pyproject.toml is
well-structured with proper optional extras for cross-encoder, postgres, and alternate
providers. The Dockerfile correctly copies only the src tree (not `.venv/`); the
`.venv/` is confirmed gitignored by the root `.gitignore`.

### Postgres init SQL

`infrastructure/containers/postgres-init/init.sql` — the `SELECT ... WHERE NOT
EXISTS ... \gexec` idiom is correct for idempotent database creation in Postgres without
needing `CREATE DATABASE IF NOT EXISTS` (which Postgres does not support natively).

### `.gitignore` additions

All additions are correct:
- `hc-rag-agent/.venv/` is covered by the existing `.venv/` rule.
- `va-langgraph/eval/ingest/gdpr_findings*.json` is the right exclusion for PII review
  working files.
- `.claude/docs/plans/` exclusion aligns with stated workflow.
