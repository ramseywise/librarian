# Escalation Grader — Audit & Extension Record (VIR-259)

Covers: original signal detection audit, Phase 1 implementation decisions,
Phase 2 EDA findings from VIR-256.

---

## Part 1 — Original grader audit

Audit of `escalation.py` as of June 2026, before VIR-259 refactor.

The `EscalationGrader.grade()` method had two responsibilities mixed together:

1. **Signal detection** — infers whether escalation occurred from the agent response
2. **Appropriateness judging** — LLM judge that scores whether escalating was the right call

---

### Signal 1 — Email regex (`_EMAIL_RE`)

```python
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
```

**What it matches:** any email address in the response text.

**Intent:** if the agent included an email address in its response, it's directing
the user to contact someone — treated as a soft escalation signal.

**Potential risks:**

- Matches ANY email — @shine.co, @gmail.com, a user's own email quoted back, example
  emails in KB articles, etc.
- No distinction between a Shine support address, a BD address, a generic support
  address, or an irrelevant email.
- A response saying "your email lrh@aalborgzoo.dk has been updated" would fire this.

---

### Signal 2 — Escalation keywords (`_ESCALATION_KEYWORDS`)

```python
_ESCALATION_KEYWORDS: tuple[str, ...] = (
    # English
    "escalate",
    "escalated",
    "human agent",
    "specialist",
    "manager",
    "support team",
    "contact support",
    "please reach out",
    # Danish
    "kontakt support",
    "kontakt os",
    "skriv til os",
    "ring til",
    "send en email",
    "menneskelig support",
    "menneskelig agent",
    "hjælp fra en person",
    "taler med en",
    "kundeservice",
    "vores support",
    "supportteam",
)
```

**What it matches:** substring match on `response.lower()`.

**Potential risks:**

- Mixes agent-initiated escalation ("please reach out to support team") with
  user-requested human contact ("talk to a human agent").
- No detection of user-side escalation signals in the query (only checks response).
- "specialist" is too broad — "you need a tax specialist" ≠ escalation.
- No Danish equivalent for "explicit human request" — missing coverage.

---

### Signal 3 — `contact_support` structured field

Not a regex — boolean field from `AssistantResponse` schema set by the agent itself
(`src/support_agents/schema.py`). When present, it is the most reliable signal and
takes priority over all heuristic detection.

```python
contact_support: bool = Field(
    default=False,
    description="Set True when agent cannot answer and user should contact support."
)
```

**When it's missing:** older agent outputs or agents that don't consistently populate
this field. In those cases the keyword fallback runs.

---

### Signal 4 — Infrastructure bypass (not a detection signal)

```python
_INFRASTRUCTURE_REASONS = frozenset(["retrieval_backend_error", "unknown"])
```

When `failure_reason` is in this set, the grader short-circuits and returns score=0.5
without running detection or judging. Not a signal — a gate to avoid judging unfair scenarios.

---

### Gaps in original detection

- **OOS intent in query** — whether the user's question is about a topic the HC agent
  fundamentally cannot handle (loans, unauthorized access, refunds). Not detected at all.
- **User-side human request in query** — only scanned the response, not the user's query. -- cause missed false negatives
- **Danish phone numbers** — no detection of phone contact info in response.

---

## Part 2 — Phase 1 implementation decisions (VIR-259)

### `contact_email` — consolidated from 3 flags

Implemented as `contact_email` flag. Three domain/local-part checks
(`@shine.co`, `@ageras.com`, `support@`) are internal to `_check_contact_email()`.

```python
_CONTACT_EMAIL_RE = re.compile(
    r"\b[\w.+-]+@(?:shine\.co|billy\.dk|ageras\.com)\b"
    r"|\b(?:support|help|kontakt)@[\w.-]+\.[a-z]{2,}\b",
    re.IGNORECASE,
)
```

---

### `contact_phone_da` — new flag from VIR-256 EDA

EDA Signal 1 found Danish phone numbers alongside email addresses in admin replies
(2.2% coverage, 232/10,590 conversations). Not in any original flag.

```python
_CONTACT_PHONE_DA_RE = re.compile(
    r"(?:\+45[\s-]?)?\d{2}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}(?!\d)"
)
```

---

### User-side vs agent-side

The original keywords mixed two semantically different events:

- **User-side:** the user said "I want a human" → the user has a need. If the agent
  doesn't escalate in response, that's a miss regardless of query complexity.
- **Agent-side:** the agent said "please contact support" → the agent made a routing
  decision. The grader then judges whether that decision was appropriate.

Knowing which side fired lets future prompt logic reason differently:

> "User asked for human → escalation almost always warranted."
> "Agent escalated on its own → was the query actually complex enough?"

| Flag                        | Side  | Language |
| --------------------------- | ----- | -------- |
| `explicit_human_request_en` | user  | EN       |
| `explicit_human_request_da` | user  | DA       |
| `escalation_keyword_en`     | agent | EN       |
| `escalation_keyword_da`     | agent | DA       |

EN/DA split is a language implementation detail, not a semantic distinction.
"specialist" and "manager" deliberately dropped — too noisy (false positives on
"tax specialist", "Manager settings" in UI).

`EscalationFlags` exposes two composite properties reflecting this distinction:

- `agent_escalated` — only agent-side signals (`any_contact_signal`, `escalation_keyword_en/da`). Used by `escalation.py` to set `escalated=True/False` when `contact_support` is absent. User-side signals do NOT affect this — a user asking for a human while the agent answered normally is correctly marked as `escalated=False`.
- `escalated` — any signal, user or agent side. Not used for executed/warranted determination.

`explicit_human_request_*` are injected separately as `human_request_note` in the LLM prompt, informing the judge that escalation was _warranted_, without claiming it was _executed_.

---

### Original → implemented mapping

| Original signal                    | Problem                     | Implemented flag(s)                                 |
| ---------------------------------- | --------------------------- | --------------------------------------------------- |
| `_EMAIL_RE`                        | Matches any email           | `contact_email` (domain/local-part filtered)        |
| _(missing)_                        | —                           | `contact_phone_da` (new, from EDA)                  |
| `_ESCALATION_KEYWORDS` (EN, agent) | Single bool, no attribution | `escalation_keyword_en`                             |
| `_ESCALATION_KEYWORDS` (EN, user)  | Only scanned response       | `explicit_human_request_en` (query + response)      |
| `_ESCALATION_KEYWORDS` (DA, agent) | Single bool, no attribution | `escalation_keyword_da`                             |
| `_ESCALATION_KEYWORDS` (DA, user)  | Missing entirely            | `explicit_human_request_da` (new, query + response) |
| `contact_support` field            | —                           | Preserved as highest-priority override              |
| _(missing)_                        | —                           | `oos_intent` (implemented Phase 2)                  |

---

## Part 3 — Phase 2 EDA findings & pattern extensions (VIR-256)

Source: `nbks/intercom/04_eda_oos_escalation.ipynb` + `nbks/intercom/intent_taxonomy_review.csv`

EDA analysed 10,590 Intercom conversations (user ↔ human support).

---

### Flag extensions applied

#### `explicit_human_request_da` — significant expansion

EDA `da_talk_to` + `da_person` patterns found verbatim user messages not covered:

| Added pattern                 | Verbatim example from EDA           |
| ----------------------------- | ----------------------------------- |
| `tal(?:er?)?  med`            | "Kan jeg tale med en person"        |
| `vil gerne tale med`          | "vil gerne tale med en person"      |
| `ønsker at tale med`          | "ønsker at tale med en medarbejder" |
| `overføre (mig) til ... team` | "overføre til en medarbejder"       |
| `viderestil*` / `videresend`  | "viderestille til support"          |
| `connecte? til`               | "connecte til jeres team"           |
| `transferere (mig) til`       | "transferere mig til support"       |
| `rigtig person`               | —                                   |
| `jeres (medarbejder\|team)`   | —                                   |

**Known false positive risk:** `\btal(?:er?)?\s+med\b` can match "tal med" as "number with" in accounting queries (e.g. "hvad er det tal med moms?"). A negative lookahead would reduce this, but in practice accounting queries use `beløb`/`sum` rather than `tal` for amounts — risk accepted as low.

#### `explicit_human_request_en` — minor expansion

Added: `live agent`, `put me through`, `transfer me to` (from EDA verbatim examples).

#### `escalation_keyword_en` — noun form added

Added `escalation` (noun) alongside existing `escalate[sd]?` (verb forms).
`manager` and `supervisor` deliberately excluded — low precision.

#### `escalation_keyword_da` — transfer/forward terms added

Added: `vores team`, `viderestil*`, `sender (dig) videre`.

#### `escalation_keyword_en/da` — ambiguous phrases duplicated from `explicit_human_request_*`

Phrases like `human agent`, `live agent`, `menneskelig agent/support`, `hjælp fra en person`
appear in both user queries and agent responses. They were originally only in
`explicit_human_request_*` (scanning both query + response), which meant agent-said
instances did not set `agent_escalated=True`.

Fix: duplicated into `escalation_keyword_en/da` (response-only). They remain in
`explicit_human_request_*` as well — no semantic conflict, each flag has independent
responsibility.

---

### OOS intent patterns (for `oos_intent` flag — Phase 2)

EDA distinguishes two OOS types:

**Type A — Structural OOS** (conversation_type label, not detectable by query regex):

| Type                | Coverage      | Escalation labels               |
| ------------------- | ------------- | ------------------------------- |
| OPS ACTION REQUIRED | 13.2% (1,399) | 1,375 / 1,797 — dominant signal |
| FEATURE REQUEST     | 0.9% (99)     | 97 / 1,797                      |

**Type B — Intent-based OOS** (regex-detectable from query, implemented in `_OOS_INTENT_RE`):

| OOS category                   | Keywords                                                | EDA source        |
| ------------------------------ | ------------------------------------------------------- | ----------------- |
| Loans / financing              | `lån`, `froda`, `finansiering`, `erhvervslån`           | hc=0%             |
| Refunds                        | `refundering`, `tilbagebetaling`, `refund`              | esc=25%           |
| Account closure                | `lukke.*konto`, `slette.*konto`, `afslutte.*abonnement` | OPS type dominant |
| Insurance                      | `forsikring`, `sundhedsforsikring`                      | hc=0%             |
| SWIFT / IBAN payments          | `SWIFT`, `IBAN`, `SEPA`                                 | hc=0%             |
| Unauthorized access / phishing | `phishing`, `uautoriseret`, `officiel mail`             | esc=50%           |

Note: `opsige` (cancel) appears in both OOS (account cancellation) and in-scope
(cancelling an invoice line) — avoid as standalone OOS signal.

**Coverage gap:** 8,118 of 10,590 conversations lack taxonomy annotation.
Patterns above cover the annotated subset only.

---

### Current pipeline scope — BKH only

The current `EscalationGrader` is designed for BKH (single-turn HC agent Q&A):

|                   | BKH (current)                | Intercom golden set (future)          |
| ----------------- | ---------------------------- | ------------------------------------- |
| Data structure    | Single-turn Q&A              | Multi-turn conversation               |
| `query`           | One user message             | First / representative user message   |
| `response`        | One HC agent response        | Full conversation text (user + admin) |
| `contact_support` | Agent's own structured field | GT label                              |
| `failure_reason`  | Agent retrieval metadata     | Does not exist                        |

For Intercom golden set, `response` would need to be the full conversation text.
See VIR-265 for dataset design.

---

### `contact_support` dual use — BKH vs Intercom golden dataset

`contact_support` is the override mechanism in `EscalationGrader.grade()`. The caller
decides what to pass — no code change needed to support both use cases:

| Data                | `contact_support` value | `executed` meaning         | `alignment` meaning           |
| ------------------- | ----------------------- | -------------------------- | ----------------------------- |
| BKH                 | Agent's own field       | Did agent escalate?        | Was agent decision correct?   |
| Intercom golden set | GT label                | Should this escalate? (GT) | Does LLM judge agree with GT? |

For Intercom golden dataset, `alignment` measures grader calibration (does the LLM judge
predict correctly against GT?), not agent quality. No code change required — the evaluation
purpose is different, the machinery is the same.

---

### Signal strength from EDA

| Signal                               | Coverage | n     | Notes                                |
| ------------------------------------ | -------- | ----- | ------------------------------------ |
| OPS ACTION REQUIRED type             | 13.2%    | 1,399 | Structural OOS                       |
| FEATURE REQUEST type                 | 0.9%     | 99    | Structural OOS                       |
| HC URL citation (in-scope indicator) | 6.4%     | 675   | Inverse signal — hc_can_handle       |
| Contact email/phone in admin reply   | 2.2%     | 232   | `contact_email` + `contact_phone_da` |
| Explicit human request KW (user msg) | 2.1%     | 222   | `explicit_human_request_*`           |
