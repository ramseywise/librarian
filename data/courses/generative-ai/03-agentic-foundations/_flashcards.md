---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/03-agentic-foundations/slides/deck.yaml
cards:
- front: In what order does this lecture add things to the restock agent?
  back: Each step fixes a failure of the one before it, and the last step is the one that keeps an agent that can spend money inside a limit.
  lesson: generative-ai/03-agentic-foundations/readme
- front: Name four things this lecture teaches you to do with an agent.
  back: You will be able to say how an agent acts, remembers and works with others, and how to keep it inside a limit.
  lesson: generative-ai/03-agentic-foundations/readme
- front: What does a plain-code check of the restock order reveal?
  back: Code confirmed the item and found a stockout the model never mentioned, and per-step errors compound quickly over a long run.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What are the parts of an agent?
  back: An agent is a model that chooses actions from its context and uses tools in a loop, and memory or multi-agent designs are ways to manage those parts.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What happens to an agent if you remove its tool results?
  back: An agent can only decide on what is in its context, so every part of the context is load-bearing.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What must a minimal agent loop contain besides the model call?
  back: A minimal agent is a capped loop that runs tool calls and feeds back the results, ending in a wrap-up rather than a silent cutoff.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: When should you use a workflow rather than an autonomous agent?
  back: Prefer plain code, then a workflow, and use an autonomous agent only when the path depends on what it finds along the way.
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Why does an agent run cost more than its step count suggests?
  back: Each step pays for the whole history again, so total input grows roughly with the square of the steps, and step caps and bounded history are the first levers.
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: What is cost-of-pass?
  back: Cost-of-pass is the cost of one attempt divided by the success rate, and it shows that the most accurate backbone cost 3.6 times more per solved task than the runner-up.
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: In what three ways does an agent learn?
  back: An agent learns in context for one task, in auditable external artifacts across tasks, or in its weights permanently, and editing its own prompts or skills is the riskiest write.
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: Why train an agent on its own successful rollouts?
  back: Keeping only an agent's successful rollouts beat cloning on 2.4 times as many expert trajectories on three tasks, but the gain came from task breadth and lost on SciWorld.
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: What are the four steps of a tool call?
  back: Advertise, decide, execute and observe repeat until the model answers without a call or a step budget ends the run.
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Which failures does chain of thought not fix?
  back: Reasoning helps a model apply a rule it knows, but missing facts and exact arithmetic need tools, so more thinking will not fix them.
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Why put tool names in a plan?
  back: Where the process is known, write the steps and the tool for each in the prompt, because wrong tool choice is the main failure and distractor routines cost GPT-4o about 20 points.
  lesson: generative-ai/03-agentic-foundations/notes/02b-planning-and-tool-use
- front: When does a plan DAG pay?
  back: A dependency graph lets the harness run independent calls together, which buys latency and smaller contexts, but showed no reliable accuracy gain over the strongest sequential baseline.
  lesson: generative-ai/03-agentic-foundations/notes/02b-planning-and-tool-use
- front: Name four rules for reliable tool calls.
  back: Keep each tool to one job, validate arguments at the boundary, inject known values in code and return errors the model can act on.
  lesson: generative-ai/03-agentic-foundations/notes/02c-mcp-code-and-safe-tool-calls
- front: What are the six prompt-injection design patterns?
  back: A tool result can carry an attacker's instructions, so choose the weakest design pattern that blocks the attack paths your tools open.
  lesson: generative-ai/03-agentic-foundations/notes/02c-mcp-code-and-safe-tool-calls
- front: How does MemGPT treat the context window?
  back: MemGPT treats the context window like an OS treats RAM, so the agent pages facts in and out of larger stores with its own tool calls.
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: What does a self-editing memory do when core memory is full?
  back: A small core plus a searchable archive works only if the agent knows the archive exists, is told when to search, and can phrase the search well.
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Do skill libraries beat keeping the history in context?
  back: Keeping experience across tasks helped, but skills added nothing over plain history on average, so write a skill for fixed-output procedures and rely on context for judgement calls.
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: What transfers across tasks, trajectories or insights?
  back: Pass@3 rose as memories got more abstract, and raw trajectories hurt where a command that worked in one environment broke in another, so keep the raw record and distil an insight layer on top.
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: Does agent-curated memory beat a verbatim store?
  back: Keep the verbatim record and curate only the index on top, because in Zhou et al. summarizing lost facts that a plain store kept.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: What four things do you control in a memory agent?
  back: You control a memory agent through its prompts, tools, management policy and starting content, and any saved memory needs a recorded origin.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: What three stops does a multi-agent conversation need?
  back: End a multi-agent conversation with a semantic stop, a turn cap that escalates and an independent verifier, and restrict who may speak after whom.
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: Does self-critique beat sampling at equal compute?
  back: At equal tokens a majority vote over independent samples beat self-critique in every comparison, so any design that adds roles should be compared with it first.
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: When has a team beaten the vote?
  back: A team beat the vote only with different models and a learned interaction protocol, and the gap was near zero on a knowledge suite, so say what differs between the agents before adding them.
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: How does Tree of Thoughts cost scale?
  back: Tree of Thoughts lifted Game of 24 from 4% to 74% with GPT-4, but its calls multiply with depth and width, so try cheaper options first.
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: Which multi-agent topologies are common?
  back: Fewer speakers and restricted edges make a multi-agent system easier to reason about, and handoffs should pass a filtered summary rather than full history.
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: When does a single agent match a multi-agent workflow?
  back: When every role uses one model, a single agent role-playing the steps can keep accuracy at lower cost, so make it the baseline to beat.
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
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
- front: What is an agent, in one line?
  back: A model in a loop that chooses actions through tools, with context carrying state between steps, inside a harness that executes those actions and enforces limits
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Who decides the next step in a workflow and in an agent?
  back: Your code in a workflow; the model in an agent. Most production systems mix the two (orchestrated autonomy)
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: When is an agent the wrong choice?
  back: When inputs vary little and the path is known. Plain code, a workflow or RAG is cheaper, faster and easier to test
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Why do long agent runs fail more often?
  back: 'Per-step errors compound: at 95% per step, 10 steps is about 60% and 100 steps is under 1%, assuming independent failures'
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: What are the exit conditions of the loop?
  back: A final-output tool, a reply with no tool calls, an unrecoverable error, or the round cap. The cap needs a wrap-up call
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Why do token costs grow quadratically with run length?
  back: The whole trajectory is re-sent on each turn, so the input grows with every step and is paid for every time
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Where does a permission belong?
  back: Below the model, in credentials and tools. A prompt can be edited or overridden (07)
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: How should you pick a model?
  back: Evaluate on your own tasks, weigh price against quality per role, and treat speed as latency, since rounds run in sequence
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Where do production systems sit on the autonomy spectrum?
  back: 'Nearly every one sits in the middle, which Koenigstein calls orchestrated autonomy: the model chooses freely inside regions you designed, but it can''t redesign its control graph or invent new topologies.'
  lesson: generative-ai/03-agentic-foundations/notes/01-agent-fundamentals
- front: Why does agent cost grow faster than step count?
  back: Each step re-reads the whole context, so total input grows roughly with the square of the steps.
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: Which agent component matters most for cost per success?
  back: The backbone. In Efficient Agents (GAIA), Claude 3.7 Sonnet scored 61.8% at $3.54 per solved task against GPT-4.1's 53.3% at $0.98.
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: Does step-level best-of-N pay?
  back: 'Not there: N=4 moved accuracy 53.3% → 53.9% and raised cost-of-pass from $0.98 to $1.28.'
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: Is summarising history a cheap memory?
  back: Not by default. Plain history scored 56.4% at $0.74 per success; model-summarised memory scored 51.5% at $1.52.
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: How should you compare two agent designs on cost?
  back: Check both still work, then compare cost at matched quality or quality at a matched budget.
  lesson: generative-ai/03-agentic-foundations/notes/01b-what-an-agent-costs
- front: What did RL change about tool calling?
  back: It moved the decision (when, which tool, which arguments, whether to continue) into the model. The tool and its execution stay outside the weights.
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: Why does a stronger model need more harness, not less?
  back: It owns more decisions, so a wrong one costs more. Constraint, verification and correction get finer-grained.
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: What are the three ways an agent learns?
  back: Context (this task only), external artifacts such as prompts, skills and code (across tasks, auditable), and parameters (permanent, via post-training).
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: Which memory write is riskiest?
  back: 'Procedural: it changes the agent''s own prompts, skills or weights. Episodic and semantic writes are safer.'
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: What is the usual recipe for training on trajectories?
  back: Behavioral cloning on expert trajectories, then reward-filtered training on the agent's own successful rollouts.
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: Why clone the thoughts too?
  back: The plan is visible, so a monitor can halt a forbidden action, and the agent learned faster, at least in the BabyAI grid world.
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: When is it cheaper to train the tool than the agent?
  back: 'When the agent is frozen and the tool learns from its feedback (T2): s3 matched Search-R1''s accuracy with about 70× less data.'
  lesson: generative-ai/03-agentic-foundations/notes/01c-model-as-agent-and-how-agents-learn
- front: Who executes a tool call?
  back: The client. The model only emits name and arguments
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Does ReAct always beat CoT?
  back: No. Observations help when the task needs facts the model lacks. On HotpotQA the original ReAct scored below CoT (27.4 against 29.4 EM with PaLM-540B), and the best result combined the two. Decide per task, or per step, when to call out
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Why put a caller and an executor in different agents?
  back: Approval, sandboxing and auditing sit between them
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Why does CoT not fix a knowledge gap?
  back: 'Reasoning cannot supply a missing fact: the steps stay plausible and the answer stays wrong. Give the agent a tool or the data'
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Why group tool results in one message?
  back: A single turn can carry several parallel calls, and each result must answer its `tool_use_id`. Results for one turn belong together
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: Why return errors as tool results?
  back: So the model can correct itself, which it can do only if the error says what was wrong and what is valid
  lesson: generative-ai/03-agentic-foundations/notes/02-tool-use-and-react
- front: What does restating state buy?
  back: On Blocksworld, GPT-4 went from 35% (CoT) to 82% with AoT+, and the ablation showed the restatement, not the search examples, carried the gain.
  lesson: generative-ai/03-agentic-foundations/notes/02b-planning-and-tool-use
- front: Why scope each subtask's context?
  back: Smaller contexts and local replanning. TDP used 70–82% fewer output tokens than Plan-and-Act, but didn't beat ReAct where feedback is immediate.
  lesson: generative-ai/03-agentic-foundations/notes/02b-planning-and-tool-use
- front: How do you handle hundreds of tools?
  back: Retrieve a few candidates by embedding, then let the model choose. Learned retrieval on 837 unseen tools still reached only 10.4% top-1 at 7B.
  lesson: generative-ai/03-agentic-foundations/notes/02b-planning-and-tool-use
- front: How do you improve a tool description?
  back: Call the tool, keep calls that work, and use them as examples and as a test set for rewriting the description. Play2Prompt gained 2.5–7 points on BFCL.
  lesson: generative-ai/03-agentic-foundations/notes/02b-planning-and-tool-use
- front: When would you choose code execution over tools?
  back: Open-ended computation or a DSL; when many calls would chain
  lesson: generative-ai/03-agentic-foundations/notes/02c-mcp-code-and-safe-tool-calls
- front: What does MCP add over function calling?
  back: 'A protocol: tools live in a separate server any client can use'
  lesson: generative-ai/03-agentic-foundations/notes/02c-mcp-code-and-safe-tool-calls
- front: Does MCP let the model use context without a tool round trip?
  back: No. MCP tools are still `tools/call` round trips; resources and prompts are separate primitives the client chooses to load
  lesson: generative-ai/03-agentic-foundations/notes/02c-mcp-code-and-safe-tool-calls
- front: You have 40 tools and selection accuracy drops. What do you do?
  back: Retrieve the few relevant tools per query and bind only those; measure that the extra latency pays off
  lesson: generative-ai/03-agentic-foundations/notes/02c-mcp-code-and-safe-tool-calls
- front: What is the MemGPT analogy?
  back: Context = RAM, databases = disk, the LLM pages for itself with tools
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Core vs archival vs recall?
  back: Always in context and small; vector store of facts and documents; full message history
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: What is a heartbeat?
  back: A flag on a tool call asking for another LLM step without user input
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Why is "every output a tool call" useful?
  back: One uniform loop; replying is just another action the agent chooses
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: What does agentic RAG change?
  back: The agent decides when and what to retrieve, and can retrieve again
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Why give core memory a hard size limit?
  back: It is always in context, so it costs tokens on every call. An error at the limit makes the agent decide what to keep
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Should a memory agent summarize what it stores?
  back: 'Often not: curate the index and keep the facts. Zhou et al. found that verbatim stores hold up well against curated ones'
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: Why does the agent not search when it should?
  back: Tools let it manage memory but do not teach it when. Put memory stats in context, instruct it, and test that behavior
  lesson: generative-ai/03-agentic-foundations/notes/03-memory-as-an-operating-system
- front: 'What transfers across tasks: trajectories or insights?'
  back: Insights. Pass@3 rose from 0.523 with no memory to 0.534 with raw trajectories and 0.560 with one-line insights, and trajectories hurt where commands no longer applied (Memory Transfer Learning).
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: When should raw records be kept?
  back: Always, as the source of truth. Answer same-conversation questions from them, and distil a fact-preserving or insight layer on top for reuse.
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: Why gate skill promotion on evidence?
  back: Skills distilled from a single run overfit and are invoked in the wrong context. MSCE requires two episodes and a positive gain, and retires skills whose pass rate drops.
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: Should memory go to the planner or the executor?
  back: The planner. In MIA, memory given to the executor cost 0.4 points, and the same memory given to a planner added 3.5.
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: How do you know a memory system is worth its cost?
  back: Compare it against no memory, history in context, and the same tokens spent on retries. ArcMemo's gain shrank as retries grew, and several published memory systems scored below no memory.
  lesson: generative-ai/03-agentic-foundations/notes/03b-learning-from-experience
- front: What are the four levers on a memory agent?
  back: Prompts, tools, memory management (block sizes, eviction, summarizing) and memory content (persona, preloaded archive).
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: Should the agent curate its memory?
  back: Mostly not. Verbatim or per-session stores matched or beat agent-curated ones on four benchmarks; curation left stale preferences standing.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: What is the safe curation?
  back: Edit the index (keywords, tags, links) and leave content untouched, as A-MEM does.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: Where do you spend model strength?
  back: On the reader. A stronger searcher helped; a stronger builder did not.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: Raw records or distilled guidance?
  back: 'Match it to the executor: logs helped a stronger executor, distilled guidance a smaller one. Keep the raw record regardless.'
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: Why do tools not make a good memory manager?
  back: They give the ability, not the judgment of when to save or search. That has to be instructed, measured or trained.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: Can a small model be a memory manager?
  back: With RL, yes in one benchmark (mem-agent, 0.39 to 0.75), but the benchmark is small and handmade.
  lesson: generative-ai/03-agentic-foundations/notes/03c-designing-a-memory-agent
- front: Name Ng's four agentic patterns
  back: Reflection, tool use, planning, multi-agent collaboration
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: What is a nested chat for?
  back: Running a sub-conversation (reviewers, a tool executor) behind one agent's reply
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: How do you stop a group chat from derailing?
  back: Speaker-transition rules, turn caps, a human approver
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: Why does a reflection node swap human and AI roles?
  back: Dialogue-tuned models expect alternating turns; the critic must see the draft as user input, and the generator must see the critique as user feedback
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: What stops a two-agent conversation?
  back: A semantic signal, a turn cap that escalates, and ideally a verifier that is neither agent
  lesson: generative-ai/03-agentic-foundations/notes/04-multi-agent-design-patterns
- front: What is the fair baseline for a multi-agent system on a task with checkable answers?
  back: 'Self-consistency: the best single model sampled several times at the same token budget, with a majority vote.'
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: Why can adding models to a vote hurt?
  back: Strong models get the same questions right, and their errors are only weakly correlated. Weaker models mostly add wrong votes (Marjanovic et al., 23 models).
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: What does a hierarchy do to a brainstorming team?
  back: 'It collapses diversity: collaborators echo the leader. Flat groups and drafting alone first keep ideas apart (Chen et al.).'
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: How do you check that a second agent is pulling its weight?
  back: Ablate its turns and see whether the final answer changes. Under multi-turn GRPO, one agent can learn to contribute nothing.
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: When does routing among model sizes pay?
  back: When cheap models handle most tasks and a strong model takes the hard ones. SALE beat always-32B by 2.7–3.5 points at 25–42% lower cost, but still over-escalated.
  lesson: generative-ai/03-agentic-foundations/notes/04b-when-more-agents-pay
- front: Why do multi-agent systems fail?
  back: Bad specs, misaligned agents, weak verification (Cemri 2025)
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: Messages vs shared memory?
  back: Messages for requests; shared blocks for facts every agent needs
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: Supervisor, hierarchical or swarm?
  back: Supervisor for small teams (bottleneck, but no deadlocks); hierarchical for many teams (harder to debug); swarm for peer back-and-forth (needs careful handoffs)
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: Does a role-play software team beat one model?
  back: Not cleanly. MetaGPT's HumanEval gain over a well-parsed single GPT-4 call is under a point before its test-and-debug loop, and on Paper2Code both MetaGPT and ChatDev lost to one call given the full paper
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: Decomposition-first vs interleaved planning?
  back: Up-front plans can't correct mid-run errors; interleaved plans adapt but can run long and costly on hard problems
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: What does Tree of Thoughts cost?
  back: 'Calls per level grow with width × thoughts: 41 calls and 93 seconds in Lakshmanan and Hapke''s depth-4 example. Try a reasoning model first'
  lesson: generative-ai/03-agentic-foundations/notes/04c-planning-architectures-and-failure
- front: CrewAI vs LangGraph?
  back: Roles and tasks with implicit flow vs an explicit state graph
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: What is code-as-action?
  back: The model writes Python that calls tools, instead of one JSON call per step
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: MCP vs A2A?
  back: Tools for a model vs tasks between agents
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: Why does AutoGen 0.2 code look different from current AutoGen?
  back: 0.4 rewrote it as event-driven; Microsoft Agent Framework is the successor
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: What should a tool return on failure?
  back: A status and a readable error, so the model can recover
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: Why must side effects not share a node with `interrupt()`?
  back: On resume the node re-runs from the start, so the side effect would run twice
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: Two ways to add a LangGraph subgraph?
  back: As a node directly when keys are shared, or via a wrapper that transforms state when schemas differ
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: When would you use no framework?
  back: When the loop is simple and you need neither checkpoints nor multi-agent routing. Many teams build directly on provider APIs
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: What do you get from a framework that a loop does not give you?
  back: Durable state and resume, human approval, tracing and routing primitives. You pay in abstraction and in churn
  lesson: generative-ai/03-agentic-foundations/notes/05-framework-survey
- front: Tests vs evals?
  back: 'Tests check deterministic behavior; evals check non-deterministic behavior: trajectory, tool choice and answer quality'
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: Name six types of context
  back: Instructions, knowledge, memory, examples, tools, guardrails
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: What is a harness?
  back: 'Everything around the model: instructions, tools, sandboxes, orchestration, guardrails, hooks, observability'
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: Conductor vs orchestrator?
  back: Real-time direction for hard or unfamiliar work; asynchronous delegation for well-defined work
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: Skills vs MCP vs agent.md?
  back: How to do a task; what can be reached; what is always true
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: Do skills replace multi-agent systems?
  back: Where agents differ only in instructions, yes. Not for parallelism, context isolation, reviewer independence or separate permissions
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: What is the 80% problem?
  back: Agents generate most of a feature fast; edge cases and integration need the expertise. The figure is a rule of thumb
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: Why talk about total cost of ownership?
  back: Agents cut build cost, but running, fixing and maintaining remain, and they can dominate
  lesson: generative-ai/03-agentic-foundations/notes/06-google-adk-intensive
- front: What are the positions for guardrails?
  back: Input, retrieval, tool parameters and execution, and output. Layer them, since no single one suffices
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: How do you reduce hallucination risk before filtering?
  back: 'Move risky content out of the model''s reach: reviewed templates (P29), then assembled facts it only rephrases (P30)'
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: Does low token probability mean an answer is wrong?
  back: No. It flags uncertainty among alternatives, some valid. Use it as a review signal
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: Why is a prompt restriction not a permission?
  back: Whoever edits the prompt changes it, and injected data can override it. Use read-only credentials and tools that cannot perform the action
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: When do you escalate to a human?
  back: Past a failure threshold, and before irreversible or high-cost actions, at least until reliability is proven
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: What does a parallel guardrail save?
  back: Latency, but not the cost of the model call, which still runs
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: How do you evaluate guardrails?
  back: A dataset of attacks and benign look-alikes, tracking misses, false blocks and added latency
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: What must an agent tell its user?
  back: Capabilities and limits, planned actions, progress, side effects, and whether the goal was attained
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
- front: How autonomous are agents today?
  back: By Gao et al.'s levels, Raieli and Iuculano judge none beyond Level 1, a research assistant. Design for orchestrated autonomy
  lesson: generative-ai/03-agentic-foundations/notes/07-guardrails-and-autonomy
---
