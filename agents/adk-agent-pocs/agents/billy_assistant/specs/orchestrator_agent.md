# Billy Orchestrator Agent — Specification

## Purpose

`orchestrator_agent` handles complex, multi-domain requests that require
coordinating two or more existing subagents — for example:

> "Create a customer for Acme ApS, add a Consulting product at 800 DKK/hr,
> create an invoice for 3 hours, and email it to them."

The root `billy_assistant` router routes single-domain requests directly to
the relevant subagent (unchanged). When a request spans multiple domains or
explicitly chains actions, it routes to `orchestrator_agent` instead.

The orchestrator calls each domain expert **as a tool** (`AgentTool`) rather
than transferring control. This allows it to issue multiple calls in a single
model turn, run independent calls in parallel, and synthesize all results into
one coherent reply.

---

## Architecture

```text
billy_assistant (router)
├── invoice_agent          ← single-domain (unchanged)
├── customer_agent         ← single-domain (unchanged)
├── product_agent          ← single-domain (unchanged)
├── email_agent            ← single-domain (unchanged)
├── invitation_agent       ← single-domain (unchanged)
├── support_agent          ← single-domain (unchanged)
└── orchestrator_agent     ← NEW — multi-domain coordinator
    ├── [tool] invoice_agent     (orchestrator variant)
    ├── [tool] customer_agent    (orchestrator variant)
    ├── [tool] product_agent     (orchestrator variant)
    ├── [tool] email_agent       (orchestrator variant)
    ├── [tool] invitation_agent  (orchestrator variant)
    ├── [tool] support_agent     (orchestrator variant)
    └── [tool] report_out_of_domain
```

The existing six subagents are **not modified**. `SubAgentSpec._finalize()`
creates a lightweight **orchestrator variant** of each via `model_copy` that:

- Gets a distinct `_orch` name suffix (e.g. `invoice_agent_orch`) to prevent
  agent tree name collisions with the originals in `root_agent.sub_agents`.
- Has `report_out_of_domain` **removed** from its tools (agent transfers
  don't work inside an `AgentTool` call) and replaced by `request_clarification`.
- Gets an instruction addendum (via `instruction=`) for tool-call mode behavior.

Only these variants are wrapped as `AgentTool` and given to the orchestrator.
The originals in `root_agent.sub_agents` are untouched.

---

## Clarification Flow

When a subagent is called as an `AgentTool` by the orchestrator it cannot
interact with the user directly — its output is a tool result, not a user
message. If the subagent is missing required information it must signal this
back to the orchestrator, which then surfaces the question to the user and
resumes the workflow once the user replies.

### Why not `signal_follow_up` from fast_multi_agent_system?

`signal_follow_up` writes to `public:follow_up_agent` in session state,
which the router reads on the *next turn* to direct the user's reply back to
the same agent. This works when the agent responds directly to the user.
Inside an `AgentTool`, the agent's output is a tool result consumed by the
orchestrator — the router never sees the follow-up signal.

### Solution: `request_clarification` tool + orchestrator mediation

```text
User  →  orchestrator
           ├── customer_agent_tool  → cus_001  ✓
           ├── product_agent_tool   → prod_001 ✓
           └── invoice_agent_tool   → "CLARIFICATION_NEEDED: What due date?"

         Orchestrator detects CLARIFICATION_NEEDED
         Orchestrator → User: "One detail needed: What due date? (default: net 7 days)"

User  →  orchestrator  ("30 days")
           └── invoice_agent_tool   → inv_001 ✓  (customer + product steps skipped)
           └── email_agent_tool     → sent    ✓
         Orchestrator → User: "All done — invoice inv_001 sent to Acme ApS."
```

**Key properties:**

- The orchestrator retains full workflow state via conversation history across
  turns; completed steps are not repeated.
- Only one clarification per turn is surfaced to the user (the first
  `CLARIFICATION_NEEDED` found halts the turn).
- Subagent confirmation prompts (e.g. `create_invoice`, `send_invoice_by_email`)
  are still enforced by the individual subagents via their inner conversation —
  the orchestrator surfaces these as clarifications too.

---

## `request_clarification` Tool

**File:** `sub_agents/shared_tools.py` (append to existing file)

```python
def request_clarification(question: str, tool_context: ToolContext) -> str:
    """Call when you are missing required information to fulfil the request.

    Use this ONLY when invoked as a tool by the orchestrator (i.e. you received
    a structured `request` argument rather than a live user message). Do NOT
    use this in direct routing mode — ask the user in your text reply instead.

    Writes the question to session state so the orchestrator can surface it,
    then returns a tagged string you MUST include verbatim as your entire
    response — nothing else.

    Args:
        question: The specific question to ask the user, with enough context
                  for the user to answer without re-reading the full request.

    Returns:
        Tagged string to output as your entire response.
    """
    agent_name = tool_context._invocation_context.agent.name
    tool_context.state["public:clarification_needed"] = {
        "agent": agent_name,
        "question": question,
    }
    return f"CLARIFICATION_NEEDED: {question}"
```

**Session state key:** `public:clarification_needed`

- Set by the subagent calling `request_clarification`.
- Read by the orchestrator after each tool call.
- Cleared by the orchestrator at the start of each new user turn via a
  `before_agent_callback` (same pattern as `clear_tried_agents` on the router).

---

## SubAgentSpec Registry Pattern

Inspired by `fast_multi_agent_system/expert_registry.py`, a `SubAgentSpec`
dataclass is the single source of truth for each subagent's identity inside
the orchestrator. Specs are defined inline in `orchestrator_agent.py` —
no changes to existing subagent files are required.

### `SubAgentSpec` dataclass

```python
# sub_agents/orchestrator_agent.py

from __future__ import annotations
from dataclasses import dataclass, field
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


@dataclass
class SubAgentSpec:
    """Describes one subagent available to the orchestrator.

    Required args:
        agent:   The existing Agent instance (imported from sub_agents/).
        domains: Short list of domain keywords used in the orchestrator
                 prompt description block (auto-generated).

    Set by _finalize() — do NOT pass manually:
        orchestrator_variant: Agent clone with request_clarification injected.
        tool:                 AgentTool wrapping the orchestrator_variant.
        prompt_line:          One rendered line for the orchestrator's agent catalogue.
    """
    agent: Agent
    domains: list[str]
    # Set by _finalize()
    orchestrator_variant: Agent = field(init=False)
    tool: AgentTool             = field(init=False)
    prompt_line: str            = field(init=False)

    @property
    def name(self) -> str:
        return self.agent.name

    @property
    def description(self) -> str:
        return self.agent.description or ""

    def _finalize(self) -> None:
        """Phase 2: build orchestrator variant, AgentTool, and prompt line.

        orchestrator_variant — a model_copy of the original that:
          - Gets a distinct name suffix (_orch) so it does not collide with
            the original sub_agent of the same base name in root_agent's tree.
          - Strips report_out_of_domain (agent transfers don't work inside an
            AgentTool — the tool just returns a string result).
          - Does NOT include signal_follow_up. That tool is part of
            fast_multi_agent_system's routing; it has no role here and must
            not be injected into billy_assistant variants.
          - Adds request_clarification so the subagent can signal missing info
            back to the orchestrator.
          - Adds an instruction addendum (dynamic instruction= field) that
            tells the subagent how to behave when invoked as an AgentTool.

        The original agent's static_instruction and all other fields are
        preserved unchanged. model_copy produces a new Python object — the
        original instance in root_agent.sub_agents is not mutated.
        """
        _ORCHESTRATOR_ADDENDUM = (
            "You are being called as a tool by the orchestrator, not directly by a user.\n"
            "Rules for this mode:\n"
            "- If you are missing required information that the user did not provide "
            "in the request, call request_clarification(question=\"...\") immediately.\n"
            "- After calling request_clarification, output ONLY the returned string — "
            "nothing else. Do not attempt to guess or invent missing values.\n"
            "- If you have all required information, proceed normally and return your "
            "result as a concise summary (not a conversational response).\n"
            "- Confirmation prompts (e.g. for create/edit operations) still apply: "
            "include the confirmation question inside your result summary so the "
            "orchestrator can surface it to the user."
        )

        # Keep all domain tools; strip report_out_of_domain (routing tool,
        # not meaningful inside an AgentTool call).
        _domain_tools = [
            t for t in self.agent.tools
            if getattr(t, "__name__", None) != "report_out_of_domain"
            and getattr(t, "name", None) != "report_out_of_domain"
        ]

        self.orchestrator_variant = self.agent.model_copy(update={
            "name": f"{self.name}_orch",
            "instruction": _ORCHESTRATOR_ADDENDUM,
            "tools": [*_domain_tools, request_clarification],
        })
        self.tool = AgentTool(agent=self.orchestrator_variant)

        domains_str = ", ".join(self.domains)
        self.prompt_line = (
            f"- **{self.name}_orch** — {self.description} (domains: {domains_str})"
        )
```

### Registry and finalization

```python
_SPECS: list[SubAgentSpec] = [
    SubAgentSpec(agent=invoice_agent,    domains=["invoices"]),
    SubAgentSpec(agent=customer_agent,   domains=["customers", "contacts"]),
    SubAgentSpec(agent=product_agent,    domains=["products", "services"]),
    SubAgentSpec(agent=email_agent,      domains=["email"]),
    SubAgentSpec(agent=invitation_agent, domains=["invitations"]),
    SubAgentSpec(agent=support_agent,    domains=["support", "documentation"]),
]

# Phase 2: build orchestrator variants, tools, and prompt lines
for _spec in _SPECS:
    _spec._finalize()

_AGENT_CATALOGUE = "\n".join(s.prompt_line for s in _SPECS)
_TOOLS           = [s.tool for s in _SPECS] + [report_out_of_domain]
```

---

## Files to Create or Modify

### Modified file: `sub_agents/shared_tools.py`

Append `request_clarification` (full implementation above). No changes to
existing `report_out_of_domain`.

### New file: `sub_agents/orchestrator_agent.py`

Full module. Contains `SubAgentSpec`, the `_SPECS` registry, finalization
loop, prompt loading, `clear_clarification` callback, and `orchestrator_agent`
Agent definition.

```python
from pathlib import Path

from google.genai import types
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from .shared_tools import report_out_of_domain, request_clarification
from .invoice_agent import invoice_agent
from .customer_agent import customer_agent
from .product_agent import product_agent
from .email_agent import email_agent
from .invitation_agent import invitation_agent
from .support_agent import support_agent

# ... SubAgentSpec dataclass and _SPECS registry as above ...

_INSTRUCTION_TEMPLATE = (
    Path(__file__).parent.parent / "prompts" / "orchestrator_agent.txt"
).read_text()

_INSTRUCTION = _INSTRUCTION_TEMPLATE.format(agent_catalogue=_AGENT_CATALOGUE)


def clear_clarification(callback_context: CallbackContext) -> None:
    """Clear any pending clarification state at the start of each user turn."""
    callback_context.state["public:clarification_needed"] = None


orchestrator_agent = Agent(
    model="gemini-3-flash-preview",
    name="orchestrator_agent",
    description=(
        "Coordinates multi-domain requests that require more than one subagent. "
        "Calls subagents as parallel tools when order does not matter, sequentially "
        "when one result is needed as input for the next. Synthesizes all results "
        "into a single coherent reply."
    ),
    static_instruction=types.Content(
        role="user",
        parts=[types.Part(text=_INSTRUCTION)],
    ),
    tools=_TOOLS,
    before_agent_callback=clear_clarification,
)
```

### New file: `prompts/orchestrator_agent.txt`

```text
You are the orchestrator for the Billy accounting system. You handle complex
requests that span multiple domains by calling the right domain experts as tools.

Available agents:
{agent_catalogue}

Rules:
- Decide whether to call agents in parallel or sequentially based on the request.
  Call in parallel when inputs are independent. Call sequentially when one result
  is needed as input for the next step.
- Before issuing tool calls for a sequence of more than two steps, state the plan
  briefly to the user.
- Each agent tool accepts a single request string in natural language. Write it as
  if you were a user addressing that agent directly. Include all IDs, amounts, and
  details the agent will need — do not assume it has context from prior tool calls.
- If any agent result starts with "CLARIFICATION_NEEDED:", stop issuing further
  tool calls, extract the question, and ask the user that question — nothing else.
  On the user's next reply, re-call only the agent that requested clarification,
  enriched with the user's answer. Do not repeat steps that already succeeded.
  Then continue with the remaining steps in the original plan.
  If multiple agents return CLARIFICATION_NEEDED in the same turn, surface only
  the first and resolve the rest in subsequent turns.
- Confirmation requests from agents (e.g. "Please confirm you want to create this
  invoice...") follow the same pattern: surface the question to the user, wait for
  their reply, then re-call the agent with the confirmed answer.
- After all agent calls complete, combine the results into one clear reply. Do not
  repeat raw tool output verbatim. If a step failed, say so and tell the user what
  action is needed to recover.
- If the request is not multi-domain and is better served by a single subagent,
  call report_out_of_domain() then transfer back to billy_assistant.
```

### Modified file: `agent.py`

Add `orchestrator_agent` to the import list and to `sub_agents=[...]`:

```python
from .sub_agents.orchestrator_agent import orchestrator_agent   # NEW

root_agent = Agent(
    ...
    sub_agents=[
        invoice_agent,
        customer_agent,
        product_agent,
        email_agent,
        invitation_agent,
        support_agent,
        orchestrator_agent,   # NEW — append last
    ],
    ...
)
```

### Modified file: `prompts/billy_assistant.txt`

Add one entry to the domain list:

```text
- orchestrator_agent — multi-step or cross-domain requests (e.g. create a
  customer then an invoice; list customers and their invoice totals; send
  multiple invoices at once)
```

**Router guidance:** Route to `orchestrator_agent` when the user's request
explicitly contains two or more actions across different domains, or when
fulfilling the request requires output from one domain as input to another.
Route to individual subagents for any single-domain request.

---

## Execution Examples

| Request | Expected orchestrator decision |
| --- | --- |
| "List all customers and all products" | Parallel: customer + product (independent reads) |
| "Create customer, then create invoice for them" | Sequential: customer → invoice (ID dependency) |
| "Invite Alice and create a product called Support" | Parallel: invitation + product (independent) |
| "Create invoice and email it" | Sequential: invoice → email (invoice ID + approval needed first) |
| "Show invoice summary and support docs on VAT" | Parallel: invoice + support (independent reads) |

---

## Clarification Examples

| Scenario | Subagent signals | Orchestrator does |
| --- | --- | --- |
| Invoice missing due date | `CLARIFICATION_NEEDED: What due date?` | Asks user, then re-calls invoice_agent with due date included |
| Email missing subject | `CLARIFICATION_NEEDED: What subject?` | Asks user, then re-calls email_agent; customer + product steps not repeated |
| Create invoice confirmation | Returns confirmation text ending in "?" | Surfaces question; re-calls with "confirmed" on next turn |

---

## Implementation Notes

**`AgentTool` import path:**

```python
from google.adk.tools.agent_tool import AgentTool
```

**Tool naming:** ADK derives the tool function name from `agent.name`. The
`orchestrator_variant` of `invoice_agent` has `name="invoice_agent_orch"`,
so the orchestrator model calls it as `invoice_agent_orch`. The `_orch` suffix
also prevents any name collision with the original `invoice_agent` sub_agent
in the root agent tree.

**`report_out_of_domain` shared tool:** The orchestrator includes
`report_out_of_domain` from `sub_agents/shared_tools.py` exactly like other
subagents, so the router's tried-agent tracking still works.

**No changes to existing subagent files:** All six existing subagents remain
unchanged. `SubAgentSpec._finalize()` uses `model_copy` to create a new
agent instance; the originals are untouched.

**`static_instruction` with `{agent_catalogue}` placeholder:** The template
is formatted once at module load (before the Agent is constructed), so
`static_instruction` still holds a fully static string at runtime, preserving
prefix-cache stability.

**Instruction addendum delivery:** The `orchestrator_variant` adds
`instruction=_ORCHESTRATOR_ADDENDUM` alongside the existing
`static_instruction`. ADK sends `static_instruction` as the system prompt and
appends `instruction` as a `user` content turn — the subagent sees both. The
addendum only activates tool-call-mode rules and does not affect the
subagent's domain knowledge.

**`clear_clarification` callback:** Clears `public:clarification_needed` at
the start of each orchestrator invocation so stale clarification state from a
prior turn does not interfere with a new request.

**Multi-turn workflow resumption:** The orchestrator retains conversation
history (`include_contents` default). On the turn after a clarification,
the history shows which steps completed and which had `CLARIFICATION_NEEDED`.
The prompt instructs the orchestrator to re-call only the blocked agent and
continue — not restart the full workflow.

**Model:** `gemini-3-flash-preview` — consistent with the other subagents.

---

## Out of Scope

- Retry logic on partial subagent failures (respond with partial results and
  tell the user what failed)
- State persistence across multi-turn orchestration workflows beyond
  conversation history
- Approval / human-in-the-loop checkpoints at the orchestrator level beyond
  what individual subagents already enforce
