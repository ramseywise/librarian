---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/04-agentic-frameworks/slides/deck.yaml
cards:
- front: In what order does this lecture build and judge the research agent?
  back: Each step adds one capability to the same agent, and the choice comes after three working builds exist to measure.
  lesson: generative-ai/04-agentic-frameworks/readme
- front: Name four things this lecture teaches you to do with an agent framework.
  back: You will be able to build the same agent on two frameworks, watch it run, and choose between them with measurements.
  lesson: generative-ai/04-agentic-frameworks/readme
- front: Who does what in a ReAct loop?
  back: The model never runs anything itself; it proposes an action and the code around it runs the action and returns the observation.
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: What are the essential parts of a hand-written agent loop?
  back: An agent is a loop that calls a model, runs what it asks for and stops on no action or an exhausted budget.
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: How does the hand-written loop map onto LangGraph?
  back: LangGraph's agent is two nodes and one conditional edge, and its loop guard counts graph steps, so a limit of 9 allows 5 model calls.
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: How does agentic search differ from web search?
  back: Tool output becomes context on every later call, so an agent's search tool should return short scored results, not whole pages.
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: What does adding a checkpointer change?
  back: A checkpointer saves state after every node under a thread id, so a run can pause, resume, survive a crash or rewind without any logic changes.
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: How do interrupt_before and interrupt() differ?
  back: Use interrupt_before to stop at a fixed node and interrupt() to ask only when a specific action is about to happen, resuming with the reviewer's decision.
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: Does rewinding a graph undo external effects?
  back: Rewinding moves the graph's state and keeps its history, but it reruns nodes, so external actions need idempotency keys or they happen twice.
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: Where does long-term memory attach to the graph?
  back: Long-term memory is a store read before the model call and written after it, with a lifetime separate from the thread's checkpoints.
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: What are the three types of long-term memory?
  back: Semantic memory holds facts, episodic holds labelled examples and procedural holds the prompts, and all three live in one namespaced store.
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: What did semantic memory save in the lab?
  back: Semantic memory took a repeat question from 749 to 184 stub tokens for the same user, and namespacing keeps one user's memory away from another's.
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: What goes wrong when an agent trusts its long-term memory unchecked?
  back: Store a source and date with every memory, take the user id from run config, and treat memory writes as untrusted input.
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: How do LangGraph's concepts map onto ADK's?
  back: LangGraph and ADK solve the same problems, but ADK runs an agent tree and event stream where LangGraph runs an explicit graph over typed state.
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: How do you cap an ADK agent's loop?
  back: '`RunConfig(max_llm_calls=n)` caps an ADK agent in model calls and raises `LlmCallsLimitExceededError` when the budget runs out.'
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: How does ADK model a pending approval?
  back: ADK turns a pending approval into a long-running function call your application answers, and plugins apply guardrails at the runner across all agents.
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: Which ADK habits from older tutorials or other frameworks cause failures?
  back: Check tutorials against the installed version, answer every approval request from your own code, and retry around the loop that consumes the events.
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: What does a trace contain?
  back: A trace records each model and tool step as a run in a tree, and framework nesting shows up there too, 19 runs in LangGraph against 9 in ADK for the same work.
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: What does a trace of a stuck run show?
  back: A stuck agent varies its arguments, so exact-duplicate checks miss it, and you detect it by looking for long runs of one tool in the trace.
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: How do datasets and evaluators turn traces into experiments?
  back: Seed datasets from real traces, begin with cheap code evaluators, add LLM judges last, and treat agreement with a stronger model as agreement rather than accuracy.
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: What overhead does each framework add?
  back: With a stub model, framework overhead is milliseconds per run and invisible next to a real model call, so the package count is the cost that matters.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: How many model calls does a stuck agent get by default?
  back: LangGraph's default allows 5,004 model calls on a stuck run and ADK's 500, so set a limit on every invocation and test that it trips.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: How do you confirm a run limit works?
  back: Limits have different units, so write a test that drives a stubborn model into each guard and asserts the number of model calls it allowed.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What does a caller see when each build runs out of budget?
  back: The hand-written build returned None when the budget ran out while both frameworks raised, and in every case the caller has to decide what a stopped run means.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What do the empirical studies say about agent frameworks?
  back: Studies put logic control and version churn among the top agent failures and show stars diverge from adoption, so weigh maintenance above popularity.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: How do you choose an agent framework?
  back: Choose by control flow and durability, not by demo, and keep tools, prompts and eval data neutral so that switching costs stop at the adapter.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What does RunnablePassthrough.assign do?
  back: '`RunnablePassthrough.assign` passes the input through and adds a computed key, so later steps see both the original input and every output so far.'
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: How do you build map-reduce with LCEL?
  back: Map-reduce is a capped batch followed by one invoke, and its limits are that reduce can overflow and map can't see contradictions across documents.
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: How do you run a model-written query plan safely?
  back: Validate a model-written plan for unknown ids and cycles before running it, and move to a graph once the steps are decided at runtime.
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: What rules of thumb summarize agentic frameworks?
  back: Write the loop once, choose by control flow, set every limit and keep your tools and data free of the framework.
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: Where does this pillar lead?
  back: Run the lab first, then follow the course on to post-training, observability and evaluation, and complete applications.
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: What is the minimum an agent needs?
  back: A model call, a tool registry, a loop, and a stop condition. Everything else is convenience or durability
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: What does ReAct mean?
  back: Interleaving reasoning and acting in one transcript, each action's result fed back as an observation
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: Why is a conditional edge better than a regex on model text?
  back: It routes on structured `tool_calls` from the API, so a formatting slip cannot change control flow
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: What does a reducer do?
  back: It defines how a node's partial update merges into shared state. Without one, updates overwrite
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: How do you stop a runaway agent in LangGraph?
  back: '`recursion_limit` in the run config. It counts graph steps and raises `GraphRecursionError`'
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: Why return tool errors instead of raising?
  back: The model can read an error and try something else; an exception ends the run
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: What replaced `create_react_agent`?
  back: '`langchain.agents.create_agent`, per the deprecation notice in LangGraph 1.2.19''s docstring'
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: Why do frameworks matter less than they look for a basic agent?
  back: The loop is short. Frameworks pay off at durability, approval gates, and observability, not at the loop
  lesson: generative-ai/04-agentic-frameworks/notes/01-react-from-scratch-to-langgraph
- front: Checkpointer versus store?
  back: A checkpointer is per-thread state at every step. A store holds items that outlive a thread, across threads and users
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: How does human-in-the-loop work in LangGraph?
  back: The graph saves a checkpoint and stops. A later `invoke` on the same thread resumes it, with `Command(resume=...)` for dynamic interrupts
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: Static versus dynamic interrupts?
  back: '`interrupt_before` stops at a node every time. `interrupt()` stops only on the code path that reaches it, with a payload for the reviewer'
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: What happens to code above `interrupt()` on resume?
  back: The node runs again from its top, so that code executes twice
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: Why does `update_state` not duplicate the message?
  back: '`add_messages` replaces any message whose `id` already exists'
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: What is an agent-oriented search tool?
  back: One that returns cleaned, ranked, short results, so no scraping step follows and tokens go to signal
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: Which streaming mode for a chat UI?
  back: '`stream_mode="messages"`, filtering on the node name and on empty content'
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: What does time travel not do?
  back: It does not undo external side effects. It only moves graph state
  lesson: generative-ai/04-agentic-frameworks/notes/02-agentic-search-persistence-streaming
- front: Name the three long-term memory types
  back: Semantic (facts), episodic (past examples), procedural (instructions)
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: Checkpointer or store for user preferences?
  back: Store. A checkpointer is scoped to one thread
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: Hot-path versus background memory writes?
  back: 'Hot path is a tool the model calls: simple but model-dependent and adds latency. Background is deterministic code or a later job: testable, needs a policy for what to keep'
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: How do you stop memory leaking between users?
  back: Namespace with a user id from the run config, set by the server. Never from model output
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: What does episodic memory give you over more rules?
  back: One correction changes behaviour on similar inputs without editing or contradicting a rule set
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: Why version procedural memory?
  back: A rewritten prompt is a deploy with no pull request. You need a diff and a rollback
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: What is the risk of memory in an agent reading the web?
  back: 'Persistent prompt injection: a planted fact survives into later threads'
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: How would you test memory without a model?
  back: Stub the model and assert on tool calls across threads, as this lab does
  lesson: generative-ai/04-agentic-frameworks/notes/03-long-term-memory-with-langgraph
- front: What is the main structural difference between ADK and LangGraph?
  back: ADK's unit is an agent driven by a runner that emits events. LangGraph's is a node in a graph you draw
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: What replaced `SequentialAgent` and `LoopAgent`?
  back: '`Workflow`, a graph with `edges`. The old shells are deprecated at 2.13.0. `Workflow` cannot yet be an `LlmAgent` sub-agent'
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: What are the state prefixes?
  back: None for the session, `user:` across a user's sessions, `app:` across the app, `temp:` for one invocation
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: How does human approval work?
  back: '`FunctionTool(fn, require_confirmation=True)` emits an `adk_request_confirmation` call. You resume by sending a function response with `confirmed`'
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: Where do you put a guardrail that must always apply?
  back: In a `BasePlugin` passed to `Runner(plugins=[...])`, which covers every agent and tool the runner drives
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: What does `tool_trajectory_avg_score` catch that response scoring misses?
  back: A good answer reached by a wrong or looping route
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: Can ADK run non-Gemini models?
  back: 'Yes: `BaseLlm` is a small interface. `AnthropicLlm` calls Claude directly, and `LiteLlm` reaches others'
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: What is a trace, in one sentence?
  back: A tree of runs for one invocation, each with a type, inputs, outputs, error and timing
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: Why is tracing more important for agents than for ordinary services?
  back: The common failures, such as logic control and termination, raise no exception at the step that goes wrong, so only the sequence of steps shows them
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: How does LangSmith attach to LangGraph?
  back: Through LangChain's callback system. `LANGSMITH_TRACING=true` is enough, with no code change
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: How does it attach to ADK?
  back: '`configure_google_adk()` patches the runner, agent, model flow and tools. `RunTree` in a plugin is the manual route'
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: How do you test tracing without an account?
  back: Pass a client that stores runs, as `CaptureClient` does, through `tracing_context` or `LangChainTracer`. `evaluate()` also takes `upload_results=False`
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: What is `dotted_order`?
  back: A sort key built from the ancestors' start times and ids. It rebuilds the tree when runs arrive out of order
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: What are the cheap evaluators to start with for a research agent?
  back: Exact match on citations, and a route check on the tools used. Add LLM judges only for what those cannot express
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: Why is agreement with GPT-4 not accuracy?
  back: The labels may be wrong, so a model that is right can score as wrong. Spot-check the reference labels first
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: LangSmith or Langfuse?
  back: LangSmith for the tightest LangChain and LangGraph fit, hosted. Langfuse for open source and self-hosting. See note 06
  lesson: generative-ai/04-agentic-frameworks/notes/05-langsmith
- front: When do you not need a framework?
  back: 'One model, a few tools and no pause or resume: a loop over the provider''s tool calling is enough'
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What does a framework actually buy you?
  back: Durable execution, HITL, replay, tracing hooks and an eval harness, at the price of indirection and dependencies
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: How do you compare two frameworks fairly?
  back: Same tools, same prompts, same dataset, same graders and one trace schema, with the framework name in the metadata
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What does a stub model let you measure?
  back: 'Framework overhead alone: cold start, per-run cost and control behaviour, with no network or inference in the numbers'
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What is the most common failure class in agent frameworks?
  back: Logic control, more than a third of failures in Wang et al., and termination is the biggest part of it
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What happens by default when a LangGraph or ADK agent never stops?
  back: LangGraph 1.2.19 raises `GraphRecursionError` after 5,004 model calls, and ADK 2.13.0 raises `LlmCallsLimitExceededError` after 500. Set both explicitly
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: Are GitHub stars a good selection signal?
  back: No. Stars and adoption diverge in Wang et al. Check maintenance, issue resolution and real dependents
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: How do you reduce lock-in?
  back: Plain-function tools, prompts in files, neutral eval data, OTEL traces and an export of each run to plain rows
  lesson: generative-ai/04-agentic-frameworks/notes/06-framework-selection
- front: What is LCEL for?
  back: Composing runnables with `|` so that streaming, batching and tracing come for free across prompt, model and parser
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: What does `RunnablePassthrough.assign` do?
  back: Passes the input through and adds a computed key, so later steps see both
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: When is sequential better than parallel?
  back: When a step needs what the previous one produced. The book's scenes each get a summary of the last scene
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: How do you stop `.batch()` causing rate-limit errors?
  back: '`max_concurrency` in the config'
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: Name three routes to structured output
  back: Output parser with format instructions, tool calling with `PydanticToolsParser`, and `with_structured_output`, the default
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: What do you do about hallucinated tool arguments?
  back: Validate in code before acting, and return the validation error as an observation
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: How do you execute a query plan safely?
  back: Check for unknown ids and cycles, then run in topological waves, each wave in parallel
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: What are map-reduce's two failure modes?
  back: The reduce step can overflow, and a map step can't see anything that spans documents
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
- front: When should a chain become a graph?
  back: When the steps are chosen at runtime, or you need retries with state, checkpoints or human approval
  lesson: generative-ai/04-agentic-frameworks/notes/07-lcel-composition-in-practice
---
