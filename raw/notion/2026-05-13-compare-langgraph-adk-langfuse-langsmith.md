# Compare: LangGraph vs ADK — Python vs TypeScript — Langfuse vs LangSmith

**Source:** Notion — Virtual Assistant Team Documents Database
**URL:** https://app.notion.com/p/350f148b3ab7804db9f0dcc290c32c4b
**Status:** Draft
**Type:** Decision
**Teams:** Virtual Assistant
**Last updated:** 2026-05-13

---

## LangGraph vs Google ADK

### Google ADK

**Description:** Software-defined framework that prioritizes structured, hierarchical agent teams. Event-driven state machine with opinionated "Agent Tree" model — parent coordinator manages specialized sub-agents.

**Pros:**
- Fast initial build speeds due to high-level workflow primitives (Sequential, Parallel, Loop agents)
- Strong support for enterprise governance, evaluation, native protocols (A2A and MCP)
- Excellent context isolation and token efficiency via sub-agent delegation pattern

**Cons:**
- Heavily biased toward Google Cloud and Vertex AI; AWS deployment requires extra setup and forfeits managed governance features
- Base 1.x lacks arbitrary conditional branching; 2.0 graph-workflow release still in beta
- RAG is not native — must be integrated via external tools

### LangGraph

**Description:** Low-level orchestration framework from LangChain ecosystem modeling agentic workflows as explicit stateful graphs. Every step is a node, transitions defined by standard or conditional edges. Engineered for total transparency and granular control over decision-making paths.

**Pros:**
- Cloud-agnostic; highly compatible with AWS-first architecture (ECS, Lambda, DynamoDB) without vendor lock-in
- Durable execution via checkpointer architecture — state persistence, HITL interrupts, "Time Travel" debugging
- Unmatched workflow-level traceability and orchestration visibility, especially with LangSmith

**Cons:**
- Steep learning curve — requires explicit graph design and manual state management
- Lacks built-in enterprise governance and evaluation tools out of the box
- Large graphs with shared mutable state can lead to unpredictable behavior if not strictly typed

### Weighted Scores (AWS-focused evaluation, max 845)

| Framework | Weighted Score | Avg Score |
|---|---|---|
| **LangGraph** | **716 / 845** | **4.24 / 5** |
| ADK 2.0 Beta | 693 / 845 | 4.10 / 5 |
| ADK 1.x | 649 / 845 | 3.84 / 5 |

**LangGraph wins for:** debugging visibility, memory/persistence, state time travel, AWS deployment fit, cloud agnosticism, model lock-in (freedom), TypeScript support, RAG integration, agentic security & governance, identity/NHI governance, community/maturity.

**ADK wins for:** ease of use, initial build speed, MCP protocol support, eval/testing support (built-in), Gemini Live API / real-time voice, A2A support, prefix/context caching.

**Key questions for final decision:**
- AWS alignment vs. managed governance
- Does the project need LangGraph's explicit state-machine control or ADK's faster LLM-driven delegation?
- Voice implementation: ADK has native Gemini Live API; LangGraph requires custom integration (LiveKit/adapters)
- Accounting auditability: LangGraph "Time Travel" vs ADK event-driven provenance
- Economic strategy: Gemini context caching 90% discount (ADK) vs model-flexibility (LangGraph + LiteLLM)
- Time to market: ADK more batteries-included in Google ecosystem

---

## Langfuse vs LangSmith

### Langfuse

**Description:** Open-source LLM engineering platform for observability, tracing, evaluations, prompt management, and analytics. OpenTelemetry-oriented, can be self-hosted, fits AWS-hosted architecture where Datadog is already used.

**Pros:**
- Strong fit for ADK-first or framework-neutral architectures
- Fits with Datadog and existing OTel-based infrastructure
- Can be self-hosted (data sovereignty, VPC residency, high-compliance financial workflows)
- Attractive cost profile for large teams and high trace volume (unlimited users, usage-based pricing)
- Framework-agnostic; useful if org uses both ADK and LangGraph
- Good for portable prompt governance across frameworks

**Cons:**
- Weaker than LangSmith for LangGraph-native debugging and state visualization
- HITL and LangGraph interrupt-style workflows require more custom handling
- Evaluation workflows more DIY compared to LangSmith's polished annotation flows
- Requires more engineering ownership to create polished enterprise workflow

### LangSmith

**Description:** LangChain's platform for LLM observability, tracing, evaluation, debugging, monitoring. Strongest for LangGraph applications — traces represented as run trees.

**Pros:**
- Best fit for LangGraph-first architectures
- Strong trace quality for node execution, tool calls, run trees, state transitions
- Stronger developer experience for debugging complex agent behavior
- Mature evaluation workflows (datasets, annotation, review loops)
- Good when fast iteration and developer productivity matter more than infrastructure control

**Cons:**
- Less attractive if direction is ADK-first or framework-neutral
- More ecosystem-coupled to LangChain/LangGraph patterns
- Weaker fit for clean OTel-native Datadog integration
- Higher cost risk for large teams and high trace volume (per-seat pricing)
- SaaS/BYOC less straightforward than full self-hosting for strict data sovereignty

### Weighted Scores (AWS-hosted, ADK-compatible, high-compliance accounting)

| Platform | Weighted Score | Interpretation |
|---|---|---|
| **Langfuse** | **8.58 / 10** | Stronger overall fit for AWS-hosted, ADK-compatible, Datadog-aligned, high-compliance system |
| LangSmith | 7.92 / 10 | Strongest if architecture becomes clearly LangGraph-first and deep HITL debugging is dominant priority |

### Pricing Comparison

| Feature | Langfuse (Core/Pro) | LangSmith (Plus) |
|---|---|---|
| User Seats | **Unlimited** ($29–$199/mo) | $39 per user/month |
| Trace Inclusion | 100k included | 10k included per seat |
| Overages | ~$8 per 100k units | ~$50 per 100k traces |
| Deployment | Free self-host or Cloud | SaaS (Enterprise for BYOC/VPC) |

---

## Python vs TypeScript for Agentic Systems

### Language Roles

- **Python ("The Brain")**: Primary runtime for intelligence-heavy tasks — RAG, evaluation harnesses, ML workflows. Native home for most AI research, embedding libraries, data analysis tools.
- **TypeScript ("The Limbs")**: Operational layer — backend service integrations, real-time API contracts, high-concurrency I/O. Standard for MCP servers and real-time streaming interfaces.

### Weighted Decision Matrix (max scores)

| Language | Weighted Total |
|---|---|
| **Python** | **377** |
| TypeScript | 302 |

**Python wins for:**
- Team familiarity (VA team: ~7 Python-native developers vs 1 TypeScript-heavy)
- LangGraph support (Python-first; TypeScript version lags in docs/features)
- Onboarding new devs (larger AI-agent learning ecosystem)
- Tabular/ML integration (pandas, scikit-learn, XGBoost, embeddings)
- RAG/evaluation ecosystem (Ragas, DeepEval, stronger eval workflows)
- Long-term maintainability for agent logic
- State/persistence maturity (LangGraph checkpointing)
- HITL/approval flows (LangGraph maturity)
- Testing/eval automation

**TypeScript wins for:**
- Team familiarity (Shine core web devs)
- I/O performance and concurrency (native non-blocking)
- "Vibe coding" / AI-assisted DX (strong static types reduce generated-code errors)
- Backend service integration (existing Shine backend services are TypeScript)
- Schema/contract safety (Zod-style validation)

**Key architectural question:** Unified runtime vs "Brain and Limbs" hybrid (Python for orchestration/RAG + TypeScript for tool execution/API boundaries via MCP)?

**MCP consideration:** TypeScript was MCP's original home (web tools); Python/FastMCP is becoming the standard for agent-tool development.

**AWS Fargate note:** For agents that block >25% of execution time or exceed 1MB ALB response limit, Fargate is required over Lambda. Memory right-sizing: 512MB+ for long-running Python or TypeScript containers.

### Team Profile (VA team)
- ~7 Python-native developers
- ~1 TypeScript-heavy developer
- LangGraph and ADK: Python is first-class citizen; TypeScript support exists but documentation and features lag
