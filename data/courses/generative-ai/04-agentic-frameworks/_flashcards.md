---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/04-agentic-frameworks/slides/deck.yaml
cards:
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
- front: How do LangGraph's concepts map onto ADK's?
  back: LangGraph and ADK solve the same problems, but ADK runs an agent tree and event stream where LangGraph runs an explicit graph over typed state.
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: How do you cap an ADK agent's loop?
  back: '`RunConfig(max_llm_calls=n)` caps an ADK agent in model calls and raises `LlmCallsLimitExceededError` when the budget runs out.'
  lesson: generative-ai/04-agentic-frameworks/notes/04-google-adk
- front: How does ADK model a pending approval?
  back: ADK turns a pending approval into a long-running function call your application answers, and plugins apply guardrails at the runner across all agents.
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
---
