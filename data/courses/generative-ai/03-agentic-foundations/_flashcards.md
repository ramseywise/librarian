---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/03-agentic-foundations/slides/deck.yaml
cards:
- front: What does a plain-code check of the restock order reveal?
  back: Code confirmed the item and found a stockout the model never mentioned, and per-step errors compound quickly over a long run.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What are the parts of an agent?
  back: An agent is a model that chooses actions from its context and uses tools in a loop, and memory or multi-agent designs are ways to manage those parts.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What happens to an agent if you remove its tool results?
  back: An agent can only decide on what is in its context, so every part of the context is load-bearing.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: When should you use a workflow rather than an autonomous agent?
  back: Prefer plain code, then a workflow, and use an autonomous agent only when the path depends on what it finds along the way.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What are the four steps of a tool call?
  back: Advertise, decide, execute and observe repeat until the model answers without a call or a step budget ends the run.
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: What must a minimal agent loop contain besides the model call?
  back: A minimal agent is a capped loop that runs tool calls and feeds back the results, ending in a wrap-up rather than a silent cutoff.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Which failures does chain of thought not fix?
  back: Reasoning helps a model apply a rule it knows, but missing facts and exact arithmetic need tools, so more thinking will not fix them.
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Name four rules for reliable tool calls.
  back: Keep each tool to one job, validate arguments at the boundary, inject known values in code and return errors the model can act on.
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: What are the six prompt-injection design patterns?
  back: A tool result can carry an attacker's instructions, so choose the weakest design pattern that blocks the attack paths your tools open.
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: How does MemGPT treat the context window?
  back: MemGPT treats the context window like an OS treats RAM, so the agent pages facts in and out of larger stores with its own tool calls.
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: What does a self-editing memory do when core memory is full?
  back: A small core plus a searchable archive works only if the agent knows the archive exists, is told when to search, and can phrase the search well.
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Does agent-curated memory beat a verbatim store?
  back: Keep the verbatim record and curate only the index on top, because in Zhou et al. summarizing lost facts that a plain store kept.
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: What four things do you control in a memory agent?
  back: You control a memory agent through its prompts, tools, management policy and starting content, and any saved memory needs a recorded origin.
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: What three stops does a multi-agent conversation need?
  back: End a multi-agent conversation with a semantic stop, a turn cap that escalates and an independent verifier, and restrict who may speak after whom.
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: How does Tree of Thoughts cost scale?
  back: Tree of Thoughts lifted Game of 24 from 4% to 74% with GPT-4, but its calls multiply with depth and width, so try cheaper options first.
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: Which multi-agent topologies are common?
  back: Fewer speakers and restricted edges make a multi-agent system easier to reason about, and handoffs should pass a filtered summary rather than full history.
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: When does a single agent match a multi-agent workflow?
  back: When every role uses one model, a single agent role-playing the steps can keep accuracy at lower cost, so make it the baseline to beat.
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: How do agent frameworks differ?
  back: Frameworks differ in their unit of programming, so write down your control flow first and pick the one that matches, or none if it is a straight line.
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: Why must a side effect not share a node with an interrupt?
  back: On resume an interrupted node runs again from its first line, so put the pause and the side effect in separate nodes.
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: Where does the harness sit across the lifecycle?
  back: The harness is configured in planning, runs during implementation, feeds errors back during testing and is observed in production.
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: What is progressive disclosure?
  back: Progressive disclosure keeps a skill's cost to one line of metadata until a task matches, so the description must carry the whole decision to activate.
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: Why evaluate the trajectory as well as the output?
  back: Output evaluation passes a run that ordered without checking stock, so also evaluate the trajectory, including the order of the steps.
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: What are the four patterns for lowering output risk, from least to most risk?
  back: Ask how much the model needs to write at all, using reviewed templates and assembled facts first, with guardrails as the outer layer.
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: Where should a high-risk tool call be gated?
  back: Rate each tool by what it can undo, default to deny, ask a person for risky calls and keep hard limits that no approval can override.
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: Where do guardrails sit around an agent?
  back: Layer guardrails on inputs including retrieved data, on tool execution and on outputs, because no single check is enough.
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: What rules of thumb summarize agentic foundations?
  back: Compute what you can, bound the loop, distrust tool output, keep the record, start with one agent and enforce limits outside the model.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Which pillar follows agentic foundations?
  back: Next, study LangGraph and ADK in depth, then tracing and scoring, then deployed systems, with the harness discipline in ai-engineering.
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
---
