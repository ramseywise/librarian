# Orchestration Patterns for VA Agents

**Sources:** langgraph_Yan.pptx, langgraph_extended.pptx, adk-agent-samples-main (wine_expert_multi_agent, billy_assistant), playground VA implementations, librarian wiki (adk-vs-langgraph-comparison.md, multi-agent-orchestration-patterns.md)

---

## Three Multi-Agent Architectures

Not all multi-agent systems use the same routing model. Pick based on your control/latency/cost trade-offs.

### 1. Supervisor (Centralized Routing) — Current VA Architecture

A root agent classifies intent and delegates to a specialist. Only one specialist runs per turn.

```
User → Supervisor → [Invoice Agent | Customer Agent | Report Agent | ...]
                         ↓
                    Specialist executes
                         ↓
                    Response back to user
```

**Pros:** Full control over routing, easy to debug, single point of routing logic  
**Cons:** Supervisor is a bottleneck, complex queries may need multiple hops  
**Best for:** Well-defined domain boundaries, high-stakes actions (billing), when you need routing explainability

```python
# ADK supervisor pattern
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool

invoice_agent = LlmAgent(name="invoice_agent", ...)
customer_agent = LlmAgent(name="customer_agent", ...)
report_agent = LlmAgent(name="report_agent", ...)

root_agent = LlmAgent(
    name="billing_supervisor",
    instruction="""
    You are a billing assistant supervisor. Route requests to the right specialist:
    - Invoice questions → invoice_agent
    - Customer management → customer_agent  
    - Reports and analytics → report_agent
    
    Previously tried agents this turn: {tried_agents}
    User preferences: {user_prefs}
    """,
    tools=[
        agent_tool.AgentTool(agent=invoice_agent),
        agent_tool.AgentTool(agent=customer_agent),
        agent_tool.AgentTool(agent=report_agent),
    ]
)
```

### 2. Handoff (Agent-to-Agent Routing) — Flexible, Decentralized

Each agent decides when to hand off to another agent. No central supervisor.

```
User → Agent A → (decides to hand off) → Agent B → Response
```

**Pros:** More flexible, agents can chain naturally, no routing bottleneck  
**Cons:** Harder to debug (routing logic is distributed), risk of infinite handoff loops  
**Best for:** Open-ended workflows where routing is hard to predetermine

```python
# LangGraph handoff via Command
from langgraph.types import Command

def invoice_agent_node(state: AgentState) -> Command:
    if needs_customer_info(state):
        return Command(
            goto="customer_agent",
            update={"handoff_reason": "need customer details before creating invoice"}
        )
    # ... handle invoice task
    return Command(goto="__end__", update={"response": result})
```

### 3. Parallel Swarm (All Agents Run, Best Wins)

All domain agents run simultaneously. Results are aggregated or best answer selected.

```
User → [Invoice Agent]  ─┐
       [Customer Agent] ─┤→ Aggregator → Response
       [Report Agent]   ─┘
```

**Pros:** Lowest latency for the winning path, no routing error possible  
**Cons:** High token cost (all agents run regardless), complex result aggregation  
**Best for:** When routing accuracy is very low and cost/latency is acceptable

```python
# LangGraph Send API for parallel execution
from langgraph.types import Send

def fan_out_node(state: AgentState) -> list[Send]:
    return [
        Send("invoice_agent", state),
        Send("customer_agent", state),
        Send("report_agent", state),
    ]

def aggregate_node(state: AgentState) -> dict:
    results = state["agent_results"]
    # Pick the result with highest confidence
    best = max(results, key=lambda r: r["confidence"])
    return {"response": best["response"]}
```

---

## Try-Agent History Pattern

Prevents re-routing to a failed agent within the same conversation turn.

```python
async def supervisor_node(state: AgentState, llm) -> dict:
    tried = state.get("tried_agents", [])
    prefs = state.get("user_prefs", {})
    
    routing_prompt = f"""
    Route to the best agent. Do NOT route to: {tried}
    User language preference: {prefs.get('language', 'en')}
    
    Available agents: invoice_agent, customer_agent, report_agent, support_agent
    """
    
    decision = await llm.ainvoke(routing_prompt + "\n" + state["messages"][-1].content)
    chosen = parse_agent_decision(decision)
    
    return {
        "next_agent": chosen,
        "tried_agents": tried + [chosen],
    }
```

---

## LangGraph Domain Subgraph Pattern

For large VA systems (11+ domains), each domain is a self-contained subgraph compiled separately and wired into the parent graph. Keeps complexity manageable.

```python
# invoice_subgraph.py
invoice_builder = StateGraph(InvoiceState)
invoice_builder.add_node("fetch", fetch_invoice_node)
invoice_builder.add_node("create", create_invoice_node)
invoice_builder.add_node("confirm", confirm_invoice_node)
invoice_builder.add_conditional_edges("fetch", route_invoice_action)
invoice_graph = invoice_builder.compile()

# parent graph wires subgraphs as nodes
parent_builder = StateGraph(AgentState)
parent_builder.add_node("invoice", invoice_graph)   # subgraph as node
parent_builder.add_node("customer", customer_graph)
parent_builder.add_node("router", supervisor_node)
parent_builder.add_conditional_edges("router", route_to_domain)
```

**Subgraph state isolation:** each subgraph gets its own `StateGraph` with its own state schema. Parent state is passed in; subgraph manages its own intermediate state internally.

---

## Lazy Tool/Skill Loading

For agents with 50+ tools, loading all at startup bloats the context and slows LLM decisions. Load only the relevant skill set per intent.

```python
# skills registry — lightweight descriptors
SKILLS = {
    "invoicing": ["get_invoice", "list_invoices", "create_invoice", "edit_invoice"],
    "customers": ["list_customers", "create_customer", "edit_customer"],
    "reports": ["get_profit_and_loss", "get_balance", "get_aged_debtors"],
    "email": ["send_invoice_by_email", "send_quote_by_email"],
}

def load_skill(intent: str) -> list[Tool]:
    skill_names = SKILLS.get(intent, SKILLS["invoicing"])  # default to invoicing
    return [TOOL_REGISTRY[name] for name in skill_names]

def router_node(state: AgentState) -> dict:
    intent = classify_intent(state["messages"])
    tools = load_skill(intent)
    return {"active_tools": tools, "detected_intent": intent}
```

---

## ADK vs LangGraph Decision Matrix

| Dimension | Google ADK | LangGraph |
|-----------|-----------|-----------|
| **Time to working prototype** | Hours (opinionated defaults) | Days (more setup) |
| **Cloud integration** | Native (Vertex, Agent Engine, GCS) | Bring your own |
| **Memory** | Built-in session service + memory service | Manual — Store, checkpointer |
| **Multi-agent** | `AgentTool` + `SequentialAgent` + `ParallelAgent` | Full graph control |
| **HITL** | Limited (no built-in interrupt) | Native `interrupt()` + `Command(resume=...)` |
| **Observability** | Cloud Trace + BigQuery Agent Analytics | LangSmith or Langfuse |
| **Eval** | `adk eval` built-in | Roll your own pytest harness |
| **Custom backends** | Hard (ADK APIs are opinionated) | Easy (any checkpointer, any store) |
| **Multi-cloud / on-prem** | Google-locked | Fully portable |
| **Data sovereignty** | Google Cloud only | Anywhere |

**Rule of thumb:**
- **ADK** → prototyping quickly on Google Cloud, team is already GCP-native, want managed eval + observability out of the box
- **LangGraph** → need fine-grained HITL control, multi-cloud/on-prem, custom memory backends, or the full power of time travel + fork debugging

**Current architecture:** playground VA agents use both. ADK for the agent layer (tool definition, instruction, session). LangGraph for complex orchestration flows with HITL (copilot action subgraphs).

---

## Typed I/O Contracts Between Agents

When agents call other agents (via `AgentTool` or `Send`), use Pydantic schemas for both input and output to catch integration bugs at test time.

```python
from pydantic import BaseModel

class InvoiceRequest(BaseModel):
    customer_name: str
    amount: float
    currency: str = "EUR"
    line_items: list[dict] = []

class InvoiceResponse(BaseModel):
    invoice_id: str
    status: str
    pdf_url: str | None = None
    error: str | None = None

# Supervisor validates before delegating
def supervisor_node(state: AgentState) -> dict:
    request = InvoiceRequest.model_validate(state["extracted_params"])
    # type error here → caught at test time, not prod
```

---

## See Also
- [hitl-and-interrupts.md](hitl-and-interrupts.md) — HITL patterns within the supervisor graph
- [memory-architecture.md](memory-architecture.md) — how user prefs are loaded before routing
- [observability-and-runtime.md](observability-and-runtime.md) — tracing across agent hops
- librarian wiki: `ADK vs LangGraph Comparison`, `Multi-Agent Orchestration Patterns`
