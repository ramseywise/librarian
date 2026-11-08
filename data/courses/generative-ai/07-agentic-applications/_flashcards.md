---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/07-agentic-applications/slides/deck.yaml
cards:
- front: In the internet search agent, what does the workflow graph do, in order, and what bounds its cost?
  back: A router node and a fixed plan keep search bounded and debuggable, for one extra classifier call.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: What ends the minimal agent loop in the deep-research bot, and what must you add to it for long runs?
  back: An open research agent is a capped loop with compaction, so the code is small and the risks are in the run.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: What did TTD-DR, Open Deep Search and SFR-DeepResearch each change about the loop, and how far do you trust the numbers?
  back: New research agents mostly change one part of the same loop, and CodeScientist shows how far raw output is from verified results.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: How does RACE score a report, and why is an LLM judge in the training loop risky?
  back: Judge a report relative to a reference on weighted criteria, and remember that a judge you train against becomes a target.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: Which stages make up the latency of a cascaded voice response, and which is usually largest?
  back: Voice latency is a serial sum led by the silence wait, so a faster LLM alone will not fix it.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: Why can a voice server not run hot, and what does the latency formula leave out for VAD?
  back: With queueing a fast voice stack hits two seconds at 70% load, so capacity planning is a latency decision.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: In a fast/slow architecture, what rule protects the user, and where must it live?
  back: Keep a voice responsive with a fast foreground and a slow worker, and enforce the no-false-done rule in code.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: What did SeeAct show about grounding, and what did Agent S3 trade for its OSWorld score?
  back: Grounding was the early bottleneck for GUI agents, and later scores come from spending more tries and more time.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: What arc did SWE-agent's trajectories show, and why is reproducing first valuable?
  back: Reproducing first gives the agent a verdict, and interface choices move results a lot on the same model.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: What is the agent-computer interface, and how much did it matter in SWE-agent?
  back: The agent-computer interface, meaning the commands the model can issue and what comes back, is a design decision worth several points on the same model.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: What should stop a coding agent's loop, and what counts as success?
  back: Count only evidence as done, cap the budget because runs that fail, fail slowly, and halt repeats by fingerprinting the call together with the state of the files.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Which lab layer stops an agent from editing tests to pass them, and what does no file-tool check stop?
  back: A file-tool check is a promise about the tool and a process limit a promise about the code, so state what each misses.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: In the coding-agent lab, what does the guards scenario show, and which scenario shows the limit of the sandbox?
  back: You can test a harness with no model at all, by scripting the bad behaviour and checking that limits hold.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Why did the overfit scenario pass visible tests, and what did the Shen and Tamkin trial add to the supervision question?
  back: Hold tests back from the agent, and keep the debugging skill that human review depends on.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Why does the data agent agree a metric before querying, and why doesn't the validator ask the model?
  back: Put the metric before the query and the recomputation after it, so that a check never shares the agent's reasoning.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: How does the validator decide whether a claimed lead between two groups is real?
  back: Bootstrap the difference between groups, and refuse an unhedged lead when the interval includes zero.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: What does the narrow chart tool enforce, and what does the chart still fail to show?
  back: Give the agent one narrow chart tool with enforced defaults, and still state the sample size in words.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: Name three limits of the data agent's validator.
  back: A validator checks only the claims it has a shape for, so log the search and keep a person on open questions.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: What differs between chatbot, collaborative and ambient patterns, and what is hardest in each?
  back: The patterns differ in concurrency and get harder in that order, and each has one problem to solve first.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: When is a small intent-and-slot model in front of the agent still sensible?
  back: With few known intents, a small router or workflow graph can beat an LLM on cost and testability.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: What did Bansal et al. find about explanations, and what should a confirmation show instead?
  back: Explanations also persuade when the AI is wrong, so show checkable evidence at the point of approval.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: Why does an ambient agent need a must-surface list and a change log?
  back: An ambient agent can silence itself unnoticed, so keep events it must surface and log each rule change.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: What did moving the Context Engine to marketing take, and what is wrong with the chapter's key success?
  back: A good engine moves to a new domain with a new corpus, but check grounding claim by claim, since a fluent pitch is no proof.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: Why decide what would kill an AI project before the work starts?
  back: Narrow from user to constraint in that order, and write the kill criterion first, or a failing project gets a further phase and not a decision.
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: Why does input dominate an agent's bill even when output costs 5 times as much per token?
  back: Cost an agent per call, since each resends the growing context, so input dominates and caching the shared prefix saves about half.
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: In the worked example, why measure how often people use the draft before working on the model bill?
  back: At a 14% uplift a 30% miss on use moves value by $9,549 a month, over four times the $2,204 model bill, so measure use first.
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: When does building an AI feature beat buying it, in the note's hypothetical?
  back: Buy when the task is common, build when the eval set or workflow is your advantage or the vendor is ruled out, and keep the eval set yourself either way.
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: What are the rules of thumb for agentic applications?
  back: For every agent, decide who owns the path and what limits are enforced, and name the check that could prove it wrong.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: Which pillars and labs come after agentic applications?
  back: You have seen what an agent can do, so next learn the engineering layer that makes it reliable.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
---
