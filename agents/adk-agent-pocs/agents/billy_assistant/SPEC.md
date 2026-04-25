# Billy Accounting Assistant — Specification

## Overview

A multi-agent assistant for the Billy accounting system. A root agent routes
user requests to one of six domain expert subagents. Each subagent has a
focused set of tools and a static system instruction that defines its behavior.

The system is implemented in Python using ADK. Subagents live in
`agents/billy_assistant/sub_agents/`. Tools are imported from
`agents/billy_assistant/tools/`.

---

## ADK Instruction Pattern

All agent instructions in this system are fully static. Every agent uses
`static_instruction` for its stable policy content.

```python
Agent(
    model="gemini-3-flash-preview",
    name="...",
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=INSTRUCTION_TEXT)],
    ),
    tools=[...],
)
```

When dynamic per-turn content is needed alongside stable policy, add
`instruction=` in one of two forms:

- **Template string** — placeholders are resolved from `session.state`:
  `instruction="User language: {lang}"`
- **Callable** — receives `ReadonlyContext`, returns a string:
  `instruction=provide_dynamic_instruction`

When both fields are set, ADK sends `static_instruction` as the system
instruction and appends `instruction` as a `user` content turn.

**Why `static_instruction`:**

- Content never changes between turns, so the prefix is cache-stable.
- ADK places `static_instruction` as the system instruction at the start of
  every request, enabling implicit prefix caching by Gemini.
- `static_instruction` alone does not enable explicit caching. To use
  explicit context caching, configure `context_cache_config` at the `App`
  level separately.
- Live API does not support this field — it uses its own cache mechanism.

---

## Root Agent

**Name:** `billy_assistant`
**File:** `agents/billy_assistant/agent.py`

The root agent receives all user messages. It does not call tools directly.
It routes requests to the correct subagent, and handles rejection when no
subagent covers the request or when a subagent returns without resolving it.
The user must always receive a response.

To avoid redundant round-trips, the router uses a dynamic `instruction`
callable alongside `static_instruction`. When a subagent declines, it calls
`report_out_of_domain()`, which appends its name to
`session.state["tried_agents"]` and transfers back in one step. The router's
instruction callable reads this list and injects a "skip these" directive so
the router never re-routes to an agent that already declined.

**static_instruction** — stable domain map (cache-friendly):

> You are a routing assistant for the Billy accounting platform.
>
> **Responsibilities:**
> - Classify the user request into one domain and route to the correct subagent.
> - If the request is ambiguous and you cannot determine the right domain, ask
>   one short clarifying question — nothing else. Never ask more than one question
>   per turn.
> - Never answer domain-specific questions yourself.
> - Always ensure the user receives a response.
>
> **Domains:**
> - **invoice_agent** — invoices (create, view, list, edit, approve, summarize)
> - **customer_agent** — customers and contacts (create, view, list, edit)
> - **product_agent** — products and services (create, view, list, edit prices)
> - **email_agent** — sending an invoice by email
> - **invitation_agent** — inviting a user to the organization
> - **support_agent** — questions about how Billy works
>
> **If the request is outside all domains:** respond directly with a short,
> friendly message explaining what you can help with. Do not route.

**instruction** — dynamic callable, injected each turn:

```python
def provide_router_instruction(ctx: ReadonlyContext) -> str:
    tried = ctx._invocation_context.session.state.get("tried_agents", [])
    if not tried:
        return ""
    agents = ", ".join(tried)
    return (
        f"The following subagents have already indicated they cannot handle "
        f"this request: {agents}. Do not route to them again. "
        f"If no other subagent is relevant, respond kindly and tell the user "
        f"what this assistant can help with."
    )
```

---

## Shared Tool: `report_out_of_domain`

**File:** `agents/billy_assistant/sub_agents/shared_tools.py`

All subagents include this tool. When a subagent determines the request is
outside its domain, it calls `report_out_of_domain()`. The tool does two things
in one call: appends the agent's name to `session.state["tried_agents"]` and
sets `tool_context.actions.transfer_to_agent = "billy_assistant"` to trigger
the handoff. No separate `transfer_to_agent` call is needed.

```python
def report_out_of_domain(tool_context: ToolContext) -> str:
    """Call this when the request is outside your domain. Registers this agent
    as already tried so the router does not route back to it, then transfers
    control to billy_assistant."""
    agent_name = tool_context._invocation_context.agent.name
    tried = tool_context.state.get("tried_agents", [])
    if agent_name not in tried:
        tried = tried + [agent_name]
        tool_context.state["tried_agents"] = tried
    tool_context.actions.transfer_to_agent = "billy_assistant"
    return f"Registered {agent_name} as out-of-domain. Transferring to billy_assistant."
```

### Lifecycle of `tried_agents`

`tried_agents` accumulates across transfers within a single user turn and must
be cleared at the start of each new turn. The root agent uses
`before_agent_callback=clear_tried_agents` for this.

**Why a naïve clear breaks things:**
ADK calls `before_agent_callback` on every `run_async` invocation of the agent
— including when a subagent transfers back mid-turn. A simple
`callback_context.state["tried_agents"] = []` would fire on the transfer,
wiping the list before `provide_router_instruction` can read it, sending the
router into an infinite loop.

**The fix — clear once per ADK invocation using `invocation_id`:**
The Runner assigns a fresh `invocation_id` per user message. All agent hops
within that message share the same id. Storing it lets the callback skip the
clear on re-entry from a transfer:

```python
def clear_tried_agents(callback_context: CallbackContext) -> None:
    invocation_id = callback_context._invocation_context.invocation_id
    if callback_context.state.get("_tried_agents_invocation") != invocation_id:
        callback_context.state["tried_agents"] = []
        callback_context.state["_tried_agents_invocation"] = invocation_id
```

```python
root_agent = Agent(
    ...
    before_agent_callback=clear_tried_agents,
)
```

**Full lifecycle for a single user turn:**

```text
User message arrives
  → Runner creates new invocation (new invocation_id)
  → billy_assistant.run_async()
      → clear_tried_agents fires: new invocation_id → clears tried_agents = []
      → provide_router_instruction: tried_agents is empty → returns ""
      → router routes to support_agent

  support_agent.run_async()
      → support_agent cannot help → calls report_out_of_domain()
          → tried_agents = ["support_agent"]
          → actions.transfer_to_agent = "billy_assistant"

  billy_assistant.run_async()  ← triggered by the transfer
      → clear_tried_agents fires: same invocation_id → skips clear
      → provide_router_instruction: tried_agents = ["support_agent"] → injects skip directive
      → router routes to a different agent
```

---

## Subagents

### 1. `invoice_agent`

**File:** `agents/billy_assistant/sub_agents/invoice_agent.py`
**Tools:** `get_invoice`, `list_invoices`, `get_invoice_summary`, `edit_invoice`, `create_invoice`, `report_out_of_domain`
**Source:** `tools/invoices.py`, `sub_agents/shared_tools.py`

**Instruction (static):**

> You are an invoice expert for the Billy accounting system. You help users
> view, create, and manage invoices.
>
> Rules:
> - Use `list_invoices` to find invoices. Filter by state, date range, or customer when relevant.
> - Use `get_invoice` when the user asks for details about a specific invoice.
> - Use `get_invoice_summary` for overview or dashboard questions (totals, unpaid amounts, overdue counts).
> - Use `create_invoice` when the user wants to issue a new invoice. Always require a customer ID and
>   at least one line item with a product ID, quantity, and unit price.
> - Use `edit_invoice` only for draft invoices. Approved invoices cannot be edited — tell the user.
> - VAT in Denmark is 25 %. Prices are excl. VAT unless the user says otherwise.
> - Default currency is DKK. Default payment terms are net 7 days.
> - Present amounts clearly with currency and VAT status.
> - If the request is not related to invoices and none of your tools can help,
>   call `report_out_of_domain()`.

---

### 2. `customer_agent`

**File:** `agents/billy_assistant/sub_agents/customer_agent.py`
**Tools:** `list_customers`, `edit_customer`, `create_customer`, `report_out_of_domain`
**Source:** `tools/customers.py`, `sub_agents/shared_tools.py`

**Instruction (static):**

> You are a customer management expert for the Billy accounting system.
> You help users view, create, and update customer records (contacts).
>
> Rules:
> - Use `list_customers` to search for or list customers.
> - Use `create_customer` when the user wants to add a new customer. A name is required.
>   Default country is DK.
> - Use `edit_customer` to update an existing customer. You need the customer ID.
>   To update the email address, both `contact_person_id` and `email` must be provided.
> - Omitted fields are preserved — only pass fields the user explicitly wants to change.
> - Distinguish between company (`type: company`) and person (`type: person`) contacts.
> - The company registration number field is called CVR in Denmark.
> - If the request is not related to customers and none of your tools can help,
>   call `report_out_of_domain()`.

---

### 3. `product_agent`

**File:** `agents/billy_assistant/sub_agents/product_agent.py`
**Tools:** `list_products`, `edit_product`, `create_product`, `report_out_of_domain`
**Source:** `tools/products.py`, `sub_agents/shared_tools.py`

**Instruction (static):**

> You are a product catalogue expert for the Billy accounting system.
> You help users view, create, and update products and services.
>
> Rules:
> - Use `list_products` to find products. By default only active (non-archived) products are shown.
> - Use `create_product` when the user wants to add a new product. Name and unit price are required.
> - Use `edit_product` to update an existing product. You need the product ID.
>   To update the price, provide both `price_id` (from `list_products`) and `unit_price`.
> - Products are reusable templates for invoice line items.
> - Prices are always excl. VAT.
> - If the request is not related to products and none of your tools can help,
>   call `report_out_of_domain()`.

---

### 4. `email_agent`

**File:** `agents/billy_assistant/sub_agents/email_agent.py`
**Tools:** `send_invoice_by_email`, `report_out_of_domain`
**Source:** `tools/emails.py`, `sub_agents/shared_tools.py`

**Instruction (static):**

> You are responsible for sending invoices by email in the Billy accounting system.
>
> Rules:
> - Use `send_invoice_by_email` to send an approved invoice to a customer.
> - You need: invoice ID, customer/contact ID, email subject, and email body.
> - If the user has not provided a subject or body, draft a short professional one in Danish.
> - Only approved invoices can be sent. If the invoice is a draft, tell the user to approve it first.
> - Confirm the outcome to the user after the tool responds.
> - If the request is not about sending an invoice by email, call
>   `report_out_of_domain()` then transfer back to `billy_assistant`.

---

### 5. `invitation_agent`

**File:** `agents/billy_assistant/sub_agents/invitation_agent.py`
**Tools:** `invite_user`, `report_out_of_domain`
**Source:** `tools/invitations.py`, `sub_agents/shared_tools.py`

**Instruction (static):**

> You handle user invitations for the Billy organization.
>
> Rules:
> - Use `invite_user` to invite a new collaborator by email address.
> - An email address is required. Ask for it if not provided.
> - Invited users receive the role `collaborator`.
> - Confirm the invitation was sent and include the email address in your reply.
> - If the request is not about inviting a user, call `report_out_of_domain()`
>   then transfer back to `billy_assistant`.

---

### 6. `support_agent`

**File:** `agents/billy_assistant/sub_agents/support_agent.py`
**Tools:** `fetch_support_knowledge`, `report_out_of_domain`
**Source:** `tools/support_knowledge.py`, `sub_agents/shared_tools.py`

**Instruction (static):**

> You are a support specialist for the Billy accounting system. You answer
> questions about how Billy works by searching the official help docs.
>
> Rules:
> - Use `fetch_support_knowledge` for every question. Pass 2-3 relevant Danish
>   search terms derived from the user's question.
> - Base your answer on the returned passages. Quote or reference the source URL when helpful.
> - If no relevant documentation is found, say so and suggest the user visit help.billy.dk.
> - Do not invent features or behavior not described in the documentation.
> - If the request is not a question about how Billy works, call
>   `report_out_of_domain()` then transfer back to `billy_assistant`.

---

## App and Context Compaction

**File:** `agents/billy_assistant/app.py`

Billy sessions can grow long. `app.py` wraps `root_agent` in an ADK `App`
configured with `EventsCompactionConfig`. ADK's Runner triggers compaction
automatically each time the session reaches the configured interval.

**Requires ADK Python v1.16.0 or later.**

```python
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.apps.llm_event_summarizer import LlmEventSummarizer
from google.adk.models import Gemini

_summarizer = LlmEventSummarizer(llm=Gemini(model="gemini-2.5-flash"))

app = App(
    name="billy_assistant",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=10,
        overlap_size=2,
        summarizer=_summarizer,
    ),
)
```

| Parameter | Value | Reason |
| --- | --- | --- |
| `compaction_interval` | `10` | Covers ~2 full exchanges before first compaction. |
| `overlap_size` | `2` | Carries the last 2 events into the next compaction window. |
| `summarizer` | `gemini-2.5-flash` | Faster and cheaper than the main model for summarization. |

`root_agent` remains the primary ADK entry point. `app` is exported from
`__init__.py` for runners and tests that need the full App configuration.

---

## Implementation Notes

**Entry point:** `agent.py` must expose a module-level variable named
`root_agent` — this is required by ADK.

**Prompts:** All instruction strings live in `prompts/` as plain `.txt` files.
Agent files load them at module level via a relative path:

```text
agent.py
app.py                        ← wraps root_agent with context compaction (App)
prompts/
  billy_assistant.txt
  invoice_agent.txt
  customer_agent.txt
  product_agent.txt
  email_agent.txt
  invitation_agent.txt
  support_agent.txt
  router_tried_agents.txt   ← dynamic directive injected by provide_router_instruction
specs/
  context_compaction.md     ← detailed spec for the App and compaction config
```

Subagent files (in `sub_agents/`) load their prompt one level up:

```python
from pathlib import Path
_INSTRUCTION = (Path(__file__).parent.parent / "prompts" / "invoice_agent.txt").read_text()
```

`agent.py` loads both the static prompt and the dynamic directive template:

```python
_PROMPTS = Path(__file__).parent / "prompts"
_INSTRUCTION = (_PROMPTS / "billy_assistant.txt").read_text()
_TRIED_AGENTS_TEMPLATE = (_PROMPTS / "router_tried_agents.txt").read_text()
```

`router_tried_agents.txt` contains a single `{agents}` placeholder:

```text
The following subagents have already indicated they cannot handle this request: {agents}.
Do not route to them again. If no other subagent is relevant, respond kindly and tell
the user what this assistant can help with.
```

**Relative imports — required:** All imports in `agent.py` and `sub_agents/` must use
relative imports (`.` / `..`), not absolute `agents.billy_assistant.*` paths.

ADK's web server loads the package under its short name (`billy_assistant`), while
tests may import it under the full name (`agents.billy_assistant`). With absolute
imports these are two separate entries in `sys.modules`, so the same subagent instance
gets `parent_agent` assigned twice and Pydantic raises a validation error. Relative
imports bind to whichever module namespace is active, keeping instances unique.

```python
# agent.py — correct
from .sub_agents.invoice_agent import invoice_agent

# sub_agents/invoice_agent.py — correct
from .shared_tools import report_out_of_domain
from ..tools.invoices import get_invoice, list_invoices, ...
```

**Package files:** `sub_agents/__init__.py` must exist (can be empty) so
subagent modules are importable.

---

## Data Model Summary

| Entity | ID format | Key fields |
|---|---|---|
| Customer | `cus_XXX` | name, type (company/person), country, email, registrationNo (CVR) |
| Contact person | `cp_XXX` | email, isPrimary — linked 1:1 to a customer |
| Invoice | `inv_XXX` | contactId, state (draft/approved), lines, grossAmount, dueDate |
| Invoice line | `line_XXX` | productId, description, quantity, unitPrice, amount, tax |
| Product | `prod_XXX` | name, unit, prices (list with price_id and unitPrice) |

States:
- Invoice state: `draft` → `approved`. Only draft invoices can be edited.
- Invoice sent state: `unsent` → `sent` (set by `send_invoice_by_email`).

---

## Out of Scope

- Authentication and multi-tenancy
- Real API calls (all tools use in-memory mock data)
- Payment registration
- Bank reconciliation
- Annual reports or VAT reports
