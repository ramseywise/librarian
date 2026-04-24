2.1: Agent System Design (MVP)

Core job (1 sentence)
Provide a single chat ADK agent that answers user requests and manages conversation context efficiently.

Core behaviour
Provide a chat agent that reliably handles user requests with a consistent persona, and support for feedback and escalation.

Scope (what it includes)
Manage context via prefix caching to reuse stable parts of the prompt.
Summarize long conversations when near the token limit to maintain coherence.
Handle skills for our domains.
Escalation to a human supporter.
Support human-in-the-loop/interruption and confirmation before executing critical tool calls.
Trace a conversation and identify issues
See PO requirements for features
Short term session management
(Security?) Prevent user unlimited query size

Excludes
Routing and multi‑agent orchestration.
Automated failure detection.
Other features like multi‑agent transfers.
Semantic caching to reuse answers for similar queries
Long term memory / DBs
Artefact store

Success
Fulfil users request if in domain (resolution rate)
Task completion
Friction less conversation
Low latency for simple task
Gain trust

Tasks (owned work)
	Define the system prompt and persona guidelines.
	Implement prefix caching strategies.
	Add compaction logic to summarise conversation history.
	Integrate escalation triggers (Trigger tokens).
	Set up session memory.
Define ADK evalsets
Create a python server for the agent

Dependencies (required for MVP)
LLM provider supporting context caching.
Memory service for short‑term storage and retrieval.
Client UI protocol
DataDog for monitoring and tracing
OTelemetry tracing / Evaluation: Langsmith, Langfuse, DeepEvals, DataDog?

Missing / Needs to be created (no clear owner yet)
Finalised prompt and tone guidelines.
Caching and compaction thresholds and configurations.
Definition of the escalation workflow.

Spikes (investigate)
Evaluate summarisation prompts for compaction.
Evaluate voice integration providers for quality and latency when using skills.
LangGraph vs ADK (vs Semantic Kernel) for the orchestration loop — state management, MCP support, observability out of the box
Prefix/context caching behaviour in practice across ADK, LangGraph (and Semantic Kernel) 
Voice agent session compatibility — can the same session store handle text and voice turn structures?

Decisions (align)
Select the storage back end for short term memory.
Decide UI protocol.

Constraints (guardrails)
Maintain a single consistent persona; avoid multiple identities.
Keep prompts within the model’s token limit using compaction.
Comply with safety policies; do not make high‑impact decisions based on sensitive data.
2.2: Short-term memory & context window (MVP)

Core job
Bridge the gap between stateless LLMs and multi-turn interactions by managing session history, intermediate tool results, and context assembly

Core behavior
Capture, store, and format user/assistant messages and tool outputs into a coherent context window for each LLM call

Scope
Session storage, 
context assembly, 
basic compaction strategies, 

Excludes
Long-term memory persistence, 
Complex compaction strategies, 
Cross-session retrieval, 
User preference storage
artefact reference injection (non MVP)

Success
Tool outputs from turn 1 are available as context in turn 2
Agent maintains operational coherence across 5+ turns
Token overflows handled via defined compaction policy without crashing

Tasks (owned work)
Define the short-term memory schema: 
{session_id, conversation_history[], tool_results[], agent_state, artefact_refs[], turn_count}
Build storage layer (in-memory / Redis / SQL)
Build context formatter — converts stored turns into gateway-ready payload
Integrate token counter to track budget per turn
Implement compaction trigger and chosen strategy (pending spike decision)
Propagate trace_id through every stored turn

Dependencies (required for MVP)
LLM gateway (context is assembled for it)
Token counter tool
Session identifier — upstream system must provide consistent session_id
Artefact store interface — referenced by key, not stored inline
trace_id propagation standard agreed across components

Missing / needs to be created (no clear owner yet)
Standardised memory schema — needs to be a shared artifact owned by one team before any agent builds against it
Agreed trace_id propagation convention across all agents and tools

Spikes (investigate)
Compaction strategy: summarise vs truncate vs sliding window — cost-to-performance ratio under real session length distributions
Massive tool output handling — when a tool returns a large dataset, what is the prioritisation and truncation strategy before it enters the context window?

Decisions (align)
Update policy: append-only vs overwrite for intermediate tool results — recommendation is append-only with a turn index, overwrite loses debuggability
Privacy/security: at what point is sensitive data masked or redacted within the short-term buffer — before storage or before assembly into the payload?
Shared vs partial: in multi-agent flows, do agents share one session pool or maintain private partial memories? Needs to be decided before coordinator is built

Constraints (guardrails)
Schema must be defined and frozen before any agent writes to it — retrofitting is expensive
Compaction must write raw turns to cold storage (S3) before discarding — needed for GDPR audit trail and FBL golden trace recovery
trace_id is non-negotiable on every turn — without it the feedback loop and observability are blind
Sensitive data must never enter the LLM payload unredacted — redaction happens at assembly time, not storage time

2.3: Long-term memory

Core Job (1 sentence)
Persist and apply durable memory so the agent can recall past context, respect user and system preferences, and improve personalization over time.

Core behaviour
Store, retrieve, and update different memory types across sessions: episodic memory for past interactions, semantic memory for facts and preferences, and procedural memory for rules and workflows.

Scope
Long-term memory across sessions.
Growing personalization from repeated interactions and feedback.
Support episodic, semantic, and procedural memory patterns.
Use the right database by memory type.
ADK session state
User preference memory.
System preference memory.

Excludes
?

Success
The agent recalls relevant past context across sessions.
User preferences are applied consistently.
System defaults are applied consistently.
Personalization improves over time without becoming rigid or wrong.
Memory storage matches the data type and access pattern.

Tasks (owned work)
Define memory types and schema.
Define what gets stored and when.
Implement storage, retrieval, and update flows.
Map each memory type to the right database.
Apply memory in runtime behaviour.
Support correction, overwrite, and deletion.

Dependencies (required for MVP)
Memory storage back end.
Retrieval interface.
Preference store.
Summarization / memory creation logic.
Feedback signals for personalization.
Database strategy for each memory type.

Missing / Needs to be created (no clear owner yet)
Memory schema.
Promotion rules from session/history to memory.
Confidence rules for inferred preferences.
Retention, decay, and deletion policy.
Database access patterns.

Spikes (investigate)
Vector DB vs relational DB split.
Whether graph DB is needed for relational knowledge.
How to validate inferred preferences.
How growing personalization should work safely.
How memory retrieval affects response quality.

Decisions (align)
What qualifies as durable memory.
What is explicit vs inferred preference.
What belongs in user preference vs system preference.
When personalization signals are promoted to saved memory.
Which database is used for which memory type.

Constraints (guardrails)
Do not store unnecessary sensitive data.
User preferences must be editable and overridable.
System preferences must be centrally governed.
Personalization must be reversible and based on strong enough signals.
Memory design should stay simple for first implementation.
2.4 Artefact store

Core Job (1 sentence)
Store large files and generated outputs outside the prompt so the agent can reference, load, and reuse them without bloating context.

Core behavior
Save, retrieve, and reference artifacts such as files, documents, generated outputs, and tool results for later use by the agent or UI.

Scope
Store files and generated artifacts.
Return artifact references/metadata to the agent and UI.
Load artifacts when needed for a task.
Support artifact reuse across a session.

Excludes
?

Success
Large outputs do not need to be kept in the prompt.
The agent can reliably save and reload artifacts when needed.
Artifacts can be referenced from the UI and traced to a session/task.

Tasks (owned work)
Define artifact schema and metadata.
Implement save/load/delete APIs.
Define how artifacts are referenced in agent context.
Connect artifact store to UI and agent runtime.
Set retention and access rules.

Dependencies (required for MVP)
Artifact storage backend.
Metadata store.
Agent runtime support for artifact references.
UI support for displaying or downloading artifacts.

Missing / Needs to be created (no clear owner yet)
Artifact schema.
Retention policy.
Access control model.
Reference pattern between agent, session, and artifact.

Spikes (investigate)
S3/object store setup.
Metadata indexing approach.
How artifacts should be loaded into context safely.
Limits on file size and artifact types.

Decisions (align)
What counts as an artifact.
Where metadata lives.
How long artifacts are retained.
Who can access which artifacts.

Constraints (guardrails)
Do not store sensitive data without proper access control.
Artifacts must not be inserted into prompt by default.
Large files should be referenced, not copied into context.
Retention and deletion must be supported.