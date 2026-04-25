# Invoice Fact Object — Implementation Spec

## Problem

`get_invoice_details` stores 7 separate flat fact keys:
`invoice_id`, `status`, `vendor_name`, `amount`, `due_date`, `vat_rate`, `missing_fields`.

This causes three issues:

**Issue 1 — READ always re-fetches.** The prompt's READ step unconditionally calls
`get_invoice_details(invoice_id)` even when the full invoice was already loaded in a
prior turn and all data is in session facts. Every display request costs a tool call.

**Issue 2 — WRITE's "if not already in facts" is ambiguous.** The WRITE step says
`get_invoice_details(invoice_id) if not already in facts`, but "in facts" is vague
across 7 separate keys. The model cannot reliably check whether the specific invoice
it needs is fully loaded.

**Issue 3 — Historical invoice data is unreadable.** The `previous` array in
`_flat_facts` stores raw JSON strings when a fact's value is JSON-encoded. An agent
looking at history sees opaque string blobs like `"{\"status\": \"draft\", ...}"` rather
than structured objects it can reason about. The purpose of storing facts is to let
agents understand what changed across turns — that purpose is defeated when history
entries are unreadable strings.

---

## Solution: single `invoice` fact object

Replace the 7 flat keys with one fact key `invoice` whose value is a JSON-encoded
object stored via `_set_fact`:

```json
{
  "invoice": {
    "status": "draft",
    "value": "{\"id\": \"10\", \"status\": \"draft\", \"vendor_name\": \"Acme\", \"amount\": \"1250.0\", \"due_date\": \"2026-04-01\", \"vat_rate\": null, \"missing_fields\": [\"vat_rate\"]}",
    "previous": []
  }
}
```

The fact display rendered by `_flat_facts` expands JSON values — for both `value` and
every entry in `previous` — so the LLM sees clean nested structures everywhere:

```
[session facts: {
  "invoice": {
    "value": {"id": "10", "status": "approved", "vendor_name": "Acme", "amount": "1250.0", "due_date": "2026-04-01", "vat_rate": "0.25", "missing_fields": []},
    "previous": [
      {"id": "10", "status": "draft", "vendor_name": "Acme", "amount": "1250.0", "due_date": "2026-04-01", "vat_rate": null, "missing_fields": ["vat_rate"]}
    ]
  },
  "_summary": "Current: invoice id=\"10\", status=\"approved\", vendor_name=\"Acme\", amount=\"1250.0\", due_date=\"2026-04-01\", vat_rate=\"0.25\". Prior values — invoice was: status=\"draft\", vat_rate=null."
}]
```

Expanding `previous` entries is the key change for historical readability: an agent
auditing what changed can compare two structured objects field-by-field rather than
trying to parse raw JSON strings.

### READ cache hit

With the invoice as a single object, the READ step can short-circuit:

```
READ request:
  1. Resolve invoice_id (same as today).
  2. Cache check: if facts["invoice"] exists and facts["invoice"]["value"]["id"] == resolved invoice_id
     → skip get_invoice_details; use facts data directly.
     Otherwise: call get_invoice_details(invoice_id).
  3. Respond. STOP.
```

A partial invoice fact (one stored by `note_invoice_id` containing only `{"id": invoice_id}`)
does NOT satisfy the cache check — `missing_fields` and other fields are absent, so the
agent must still call `get_invoice_details`. See Decision 1 below.

### WRITE "already in facts" becomes unambiguous

```
WRITE request:
  2. if facts["invoice"] exists and facts["invoice"]["value"]["id"] == invoice_id
       and facts["invoice"]["value"] contains all required fields (status, vendor_name, amount, due_date)
       → skip get_invoice_details.
     Otherwise: get_invoice_details(invoice_id).
```

---

## Design Constraint Evaluation

### 1. Prefix caching

No impact. Facts are always delivered via `inject_facts_callback` appended to
`contents` after the stable history prefix. The system instruction is static — no
change here.

### 2. LLM calls per turn

| Scenario | Before | After |
|----------|--------|-------|
| READ — same invoice (second+ view) | 2 calls: router + expert with tool call | **1 call**: router + expert reads from facts (no tool call) |
| READ — new invoice | 2 calls (unchanged) | 2 calls (unchanged) |
| WRITE — invoice already loaded | 3 calls: router + get_details + validate + update | **2 calls**: router + validate + update (get_details skipped) |
| VALIDATE | Unchanged | Unchanged |

### 3. Conversation history clarity

Fewer fact keys → shorter `_summary` → cleaner facts block. The LLM reads one
`invoice` object instead of 7 separate string values. Historical entries in `previous`
are expanded objects, not opaque strings — agents can reason about what changed
across turns.

---

## Decisions (open questions resolved)

### Decision 1 — `note_invoice_id` behavior

**Chosen: Option B.** Keep `note_invoice_id`. It stores a partial `invoice` fact
containing only `{"id": invoice_id}`. The READ and WRITE cache checks require the
`invoice` fact to contain a full set of fields (`status`, `vendor_name`, `amount`,
`due_date`). A partial fact (id only) does not satisfy the check, so `get_invoice_details`
is still called. This is safer than Option A (remove the tool) because:

- The MENTION flow continues to work unchanged.
- No risk of a cache false-positive on a partial object.

`note_invoice_id` change: instead of `_set_fact("invoice_id", ...)`, it calls
`_set_fact("invoice", json.dumps({"id": invoice_id}), ...)`.

### Decision 2 — Fact history for `invoice`

Each `previous` entry is a full JSON snapshot of the invoice at that point in time.
This is coarser than per-field history but is more useful for audit: a single history
entry tells you the complete state of the invoice before the change, not just one
field. Acceptable.

### Decision 3 — `validate_invoice` fact

`validation_result` stays as a separate flat key — it is independent from invoice
data. However, `validate_invoice` currently reads `missing_fields` from a flat
`session_facts["missing_fields"]` key that will no longer exist. It must be updated
to read from `session_facts["invoice"]["value"]`. See Change 3.

---

## Changes Required

### 1. `tools/invoice_tools.py` — `get_invoice_details`

Replace 7 `_set_fact()` calls with one. The existing function builds a local dict
(currently named `invoice` in the stub); rename it to `raw` to separate the backend
payload from the fact object, then build `invoice_obj` from it:

```python
import json

raw = {
    "invoice_id":     invoice_id,
    "status":         "draft",
    "vendor_name":    "Acme",
    "amount":         1250.00,
    "due_date":       "2026-04-01",
    "vat_rate":       None,
    "missing_fields": ["vat_rate"],
}
invoice_obj = {
    "id": raw["invoice_id"],
    "status": raw["status"],
    "vendor_name": raw["vendor_name"],
    "amount": str(raw["amount"]),
    "due_date": raw["due_date"],
    "vat_rate": raw["vat_rate"],
    "missing_fields": raw.get("missing_fields", []),
}
_set_fact(
    "invoice",
    json.dumps(invoice_obj),
    f"Full invoice data for invoice #{invoice_id}",
    tool_context,
)
```

The function still returns `raw` (renamed from `invoice`) so callers are unaffected.

### 2. `tools/invoice_tools.py` — `note_invoice_id`

Change from storing a flat `invoice_id` key to storing a partial `invoice` object:

```python
import json

_set_fact(
    "invoice",
    json.dumps({"id": invoice_id}),
    f"Invoice ID stated by user: {invoice_id}",
    tool_context,
)
```

### 3. `tools/invoice_tools.py` — `update_invoice_field`

After a successful field update, refresh the `invoice` fact so it stays consistent.
Read the current invoice object from state, patch the updated field, and re-store:

```python
import json

session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
invoice_entry = session_facts.get("invoice", {})
try:
    invoice_obj = json.loads(invoice_entry.get("value", "{}"))
except (json.JSONDecodeError, TypeError):
    invoice_obj = {}
invoice_obj[field_name] = value
# Clear missing_fields for the updated field if it was listed.
if field_name in invoice_obj.get("missing_fields", []):
    invoice_obj["missing_fields"] = [
        f for f in invoice_obj["missing_fields"] if f != field_name
    ]
_set_fact(
    "invoice",
    json.dumps(invoice_obj),
    f"Full invoice data for invoice #{invoice_id}",
    tool_context,
)
```

### 4. `tools/invoice_tools.py` — `validate_invoice`

The current implementation reads `missing_fields` from `session_facts["missing_fields"]`
which will no longer exist. Update to read from the `invoice` object:

```python
session_facts = tool_context.state.get(PUBLIC_SESSION_FACTS, {})
invoice_entry = session_facts.get("invoice", {})
try:
    import json
    invoice_obj = json.loads(invoice_entry.get("value", "{}"))
    issues = invoice_obj.get("missing_fields", [])
    if not isinstance(issues, list):
        issues = []
except (json.JSONDecodeError, TypeError):
    issues = []
```

Remove the `ast.literal_eval` path — it was only needed because `missing_fields` was
stored as a Python string representation of a list. JSON parsing is unambiguous.

### 5. `tools/context_tools.py` — `_flat_facts` and `_build_summary`

**File note**: the spec previously said `_facts_callbacks.py` — this is wrong. Both
`_flat_facts` and `_build_summary` live in `context_tools.py`.

Add a `_render_value` helper and apply it to both `value` and each entry in `previous`:

```python
def _render_value(raw):
    """Expand a JSON string to a dict for display; return plain strings unchanged."""
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return raw
```

In `_flat_facts`, apply it after building each fact's `value` and `previous` list:

```python
rendered_value = _render_value(current_value)
rendered_previous = [_render_value(p) for p in previous]
result[k] = {"value": rendered_value, "previous": rendered_previous}
```

Update `_build_summary` to handle dict values for the `invoice` key specifically.
When a fact's value is a dict (i.e. the rendered invoice object), the summary entry
should expand the key fields rather than showing `k="<dict>"`:

```python
def _build_summary(facts: dict) -> str:
    current_parts = []
    for k, v in facts.items():
        val = v["value"]
        if isinstance(val, dict) and k == "invoice":
            # Expand the invoice object into a readable summary fragment.
            id_ = val.get("id", "?")
            status = val.get("status", "?")
            vendor = val.get("vendor_name", "?")
            amount = val.get("amount", "?")
            due = val.get("due_date", "?")
            vat = val.get("vat_rate", "null")
            current_parts.append(
                f'invoice id="{id_}", status="{status}", vendor_name="{vendor}", '
                f'amount="{amount}", due_date="{due}", vat_rate="{vat}"'
            )
        else:
            current_parts.append(f'{k}="{val}"')

    history_parts = []
    for k, v in facts.items():
        if not v["previous"]:
            continue
        prev_items = []
        for p in v["previous"]:
            if isinstance(p, dict) and k == "invoice":
                s = p.get("status", "?")
                vat = p.get("vat_rate", "null")
                prev_items.append(f'status="{s}", vat_rate="{vat}"')
            else:
                prev_items.append(f'"{p}"')
        history_parts.append(f"{k} was: " + ", ".join(prev_items))

    summary = ("Current: " + ", ".join(current_parts)) if current_parts else "No facts loaded yet."
    if history_parts:
        summary += ". Prior values — " + "; ".join(history_parts) + "."
    return summary
```

### 6. `prompts/invoice_agent.txt` — READ, WRITE, and HISTORY steps

**HISTORY** — update fact reference:

```
  - If "invoice" appears in the summary: answer exactly "You previously viewed invoice #<id from summary>." STOP.
  - If "invoice" is absent from the summary: answer exactly "No invoice has been loaded yet." STOP.
```

**READ** — add cache check before `get_invoice_details`:

```
READ request (show, display, inspect, what is) — NOT for history questions:
  1. Resolve invoice_id (same rules as today).
  2. Cache check: if facts["invoice"] exists and facts["invoice"]["value"]["id"] equals
     the resolved invoice_id AND facts["invoice"]["value"] contains "status"
     → skip get_invoice_details; use facts data directly.
     Otherwise: call get_invoice_details(invoice_id).
  3. Respond. STOP.
```

**WRITE** — tighten the already-in-facts check:

```
  2. if facts["invoice"] exists and facts["invoice"]["value"]["id"] == invoice_id
       and facts["invoice"]["value"] contains "status"
       → skip get_invoice_details.
     Otherwise: get_invoice_details(invoice_id).
```

Replace all prompt references:

| Old reference | New reference |
| ------------- | ------------- |
| `facts["invoice_id"]["value"]` | `facts["invoice"]["value"]["id"]` |
| `facts["status"]["value"]` | `facts["invoice"]["value"]["status"]` |
| `facts["vendor_name"]["value"]` | `facts["invoice"]["value"]["vendor_name"]` |
| `facts["amount"]["value"]` | `facts["invoice"]["value"]["amount"]` |
| `facts["due_date"]["value"]` | `facts["invoice"]["value"]["due_date"]` |
| `facts["vat_rate"]["value"]` | `facts["invoice"]["value"]["vat_rate"]` |
| `facts["missing_fields"]["value"]` | `facts["invoice"]["value"]["missing_fields"]` |

### 7. `eval_apps/invoice_agent/evalset.json` — new and updated cases

**State format note**: eval `session_input.state` must use the real state key
`public:session_facts` (not `public:facts`) and the full fact schema
`{"value": "...", "status": "persisted", "description": "..."}`.
The existing `show_invoice_with_prestated_id` case uses the wrong key and a bare
string value — this must be fixed in the same PR.

| Case | Change |
|------|--------|
| `show_invoice` | Unchanged — first load, tool call expected |
| `show_invoice_cache_hit` | **New**: pre-seed full `invoice` object in `session_input.state`; assert `get_invoice_details` is NOT in tool trajectory |
| `write_already_loaded` | **New**: pre-seed full `invoice` in state; assert `get_invoice_details` is NOT called; assert `validate_invoice` is called |
| `show_invoice_with_prestated_id` | **Fix + update**: correct state key to `public:session_facts`; use full fact schema; pre-seed as `invoice` object (not flat `invoice_id`) |

Pre-seeded state shape for the new cases:

```json
"state": {
  "public:session_facts": {
    "invoice": {
      "status": "persisted",
      "description": "Full invoice data for invoice #10",
      "value": "{\"id\": \"10\", \"status\": \"draft\", \"vendor_name\": \"Acme\", \"amount\": \"1250.0\", \"due_date\": \"2026-04-01\", \"vat_rate\": null, \"missing_fields\": [\"vat_rate\"]}",
      "fact_id": "test-fact-id-001"
    }
  }
}
```

---

## What Is NOT In Scope

- Changing how support_agent or orchestrator_agent interact with invoice facts
- Changing the `PUBLIC_SESSION_FACTS` schema or `_set_fact` API
- Generalizing `_render_value` / JSON expansion to non-invoice fact keys (future work)
- Any router or routing eval changes

---

## Evalset Review

| Eval | Impact |
|------|--------|
| `eval-routing` | None — router does not inspect invoice fact structure |
| `eval-response` | None — response format unchanged |
| `eval-invoice-agent` | Must add `show_invoice_cache_hit` and `write_already_loaded`; fix + update `show_invoice_with_prestated_id` |
