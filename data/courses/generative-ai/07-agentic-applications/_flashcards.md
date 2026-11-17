---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/07-agentic-applications/slides/deck.yaml
cards:
- front: In what order does this lecture move from a bounded agent to the person who uses it?
  back: The parts run from a bounded agent to the person who has to trust it, and each adds a stricter check on the answer.
  lesson: generative-ai/07-agentic-applications/readme
- front: Name four things this lecture teaches you to do when you build an agent.
  back: You will be able to decide how much path the model owns, what limits hold, and what check could prove an answer wrong.
  lesson: generative-ai/07-agentic-applications/readme
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
- front: Which three mistakes does the real-time note warn about, and what hides each?
  back: Track tail latency per stage, do not rely on one silence threshold to detect a turn, and report time per task beside any benchmark score.
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
- front: Router node or search tool?
  back: A router gives a fixed, auditable path and a separate prompt for the query. A tool lets the number of searches depend on results. Choose by whether you need bounded behaviour or adaptive behaviour.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: Why write the query in its own node?
  back: Query-writing instructions stay out of the answer prompt, and the query can be logged and improved separately.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: What bounds this agent's cost?
  back: 'The topology: fixed outline length and capped retries give `3 + 2k` to `3 + 4k` model calls. Nothing in the graph can extend a run.'
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: Why clear `search_results`?
  back: With a checkpointer, state persists across turns on a thread, so stale results would leak into the next answer.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: How should a crawler report failure?
  back: Return the error as data so one dead link does not end the run, and keep it out of the prose by marking the section.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: What would you fix first when reusing it?
  back: The retired search API, the brittle parsing, and the fallback that contradicts the "only sources" prompt. Then add evaluation, because `tests/qna.md` is prose only.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: How do you test this offline?
  back: Stub the model and the search client behind the same interfaces and assert on paths and call counts, as the block above does and as the upstream tests do with mocks.
  lesson: generative-ai/07-agentic-applications/notes/01-internet-search-agent
- front: What makes something a deep research agent?
  back: A model-controlled loop of search and reading that decides its own depth, with a long structured report as the output.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: Why return tool errors as messages?
  back: The model can repair the call on the next turn, and the run survives one bad search.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: What is a no-op think tool for?
  back: It makes the model write down a plan or reflection in a described field, and the text stays in context.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: How does compaction work here, and what does it risk?
  back: At 80% of a token estimate, everything after the request becomes a summary. It risks losing recent tool results and URLs, so keep the last k and name what must be preserved.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: What is RACE?
  back: A judge scores the target and a reference report per criterion and per weighted dimension, and the report is `T/(T+R)`, so 0.5 means matches the reference and judge harshness largely cancels.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: What does FACT add?
  back: It checks citations by fetching the pages. RACE judges quality and does not verify sources.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: What did Code Researcher change?
  back: Structured memory of (action, result) pairs filtered before synthesis, and commit search. 48% against 31.5% for SWE-agent on 200 kBenchSyz crashes, under its stated budget.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: How does RLER differ from RULER?
  back: RULER's rubric is fixed. RLER adds rubrics regenerated per step, including negative ones that penalize discovered hacks. Its best-reward run did worse downstream, a warning about judge gaps.
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: How would you evaluate a research agent with no ground truth?
  back: 'Reference-relative judged scores, plus citation verification, plus short-answer benchmarks for retrieval, with several trials. CodeScientist shows the last resort for claims: review the code and replicate.'
  lesson: generative-ai/07-agentic-applications/notes/02-deep-research-bot
- front: Why does a voice agent feel slow even when the LLM is fast?
  back: The serial sum (VAD silence wait + ASR + TTFT + TTS, about 1 to 2 s), multiplied by queueing at load. Fix it with streaming, speculative generation, semantic turn detection or full-duplex.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: End-to-end or cascade for a support line that must capture order numbers exactly?
  back: Content-determined, so a (self-)cascade with structured transcripts is as accurate and debuggable. Go end-to-end when tone and emotion drive the outcome.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: How do you add deep reasoning without adding latency?
  back: Use a fast foreground model with a background reasoner on a text or status channel. Hand it the full context, never let the fast model claim completion early, and resolve contradictions in favour of the slow model *before* speaking.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: How do you observe an end-to-end voice model?
  back: Log the input audio, the event tokens and the inner-monologue or text stream. Run self-cascade replays to localize errors to perception or reasoning.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: DOM indexing or pure vision for Computer Use?
  back: Index when structure exists, fall back to SoM or coordinates on canvas, and keep both paths. Pick the route per model.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: Action chunking versus sudden change?
  back: Use shorter chunks near contact, re-plan on visual anomaly triggers, and blend overlapping chunks.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: What did SeeAct show about GUI agents?
  back: With oracle grounding GPT-4V completed 51.1% of live-site tasks, with a large gap to real grounding. Finding the element, rather than choosing the action, was the bottleneck at that time.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: Is human-level OSWorld performance the end of the story?
  back: No. Agent S3's 72.6% used 10 rollouts at a 100-step budget, roughly 10× the cost and, run in parallel, about 1.7× the wall-clock of one rollout (the paper's cost and time figures are for GPT-5 alone, while the 72.6% run mixed in Opus 4.5). Measure time per task and steps per task alongside the success rate.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: Does "click first, look later" apply to every action?
  back: No. It needs a gate for anything you cannot undo, and what appears on the screen is untrusted input too, since a page can carry instructions for the agent.
  lesson: generative-ai/07-agentic-applications/notes/03-real-time-multimodal-agents
- front: What makes coding different from other agent applications?
  back: The environment returns a cheap, fast verdict, the tests, and the tools carry real risk. So design around getting that verdict early and gate completion on it.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: What is an agent-computer interface, and why does it matter?
  back: The commands and the output format the model works through. On SWE-bench Lite the same model went from 11.0% with a shell to 18.0% with a designed interface (Yang et al.).
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Why not show the whole file?
  back: SWE-agent's full-file viewer scored 12.7% against 18.0% with a 100-line window. Too much output crowds out the relevant lines; too little (30 lines, 14.3%) hides context.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: How should the edit tool work?
  back: Exact unique string, required prior read, stale-read refusal, parse or lint check before writing, and a refusal message that names the next action.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Is path confinement a sandbox?
  back: 'No. It limits tools. Tests run the agent''s code with your rights, so real isolation is an OS-level boundary: container or VM, no network, no credentials, only the workspace mounted.'
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Why is a green test suite not enough?
  back: Overfit and wrong patches can pass it. 52.0% of SWE-agent's analysed failures were incorrect or overly specific implementations. SWE-bench scores on tests the agent never saw.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: How do you detect a stuck agent?
  back: Fingerprint the call together with the file state over a window; warn, then halt. Execution halts are stronger than injected text. Include state or test-edit-test looks like a loop.
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: How tight should the budget be?
  back: 'Failed runs consume most of it: median successful SWE-agent run 12 steps and $1.21, mean failed run 21 steps and $2.52. A tight budget loses little and saves a lot, so measure on your task.'
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: What does a scripted model test?
  back: 'The harness: limits, refusals, end states, message shape. It cannot tell you how capable a real model is with those tools. That needs a benchmark.'
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: What is the risk to the people using these agents?
  back: In one small RCT, AI help lowered later quiz scores by about two grade points without a significant time saving, most of all on debugging. Delegation patterns scored worst (Shen & Tamkin, preprint).
  lesson: generative-ai/07-agentic-applications/notes/04-coding-agent
- front: Why is a data agent harder to trust than a coding agent?
  back: Tests fail loudly. A wrong analysis returns a plausible number. The harness has to supply its own check.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: What does execution accuracy miss?
  back: It compares against a reference query, so it assumes a precise question. It says nothing about definitions, coverage, confidence or the prose written around the number.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: What is TAG, and what does it claim?
  back: Synthesize a query, execute it, generate from the result. Databases do exact computation and models do semantic reasoning. Biswal et al. measured hand-written pipelines at 55% against baselines at no more than 20% on adapted BIRD questions.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: How do you make SQL read-only?
  back: 'Below the text: a read-only role, or SQLite''s authorizer, with a statement timeout and row cap. String filters lose to comments and unusual syntax.'
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: How would you stop metric drift?
  back: 'A semantic layer: named metrics a person has defined, with claims required to cite one. Which definition is correct is a business decision, so the data cannot settle it.'
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: How does the validator work?
  back: It takes a structured claim, recomputes through independent code on the source data, and rejects with reasons. It does not ask the model.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: What should it reject?
  back: Value mismatch, a wrong winner, a small group without its n, a null population without coverage, a lead whose interval spans zero, numbers with no source, and causal language on observational data.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: Why a bootstrap here?
  back: No distribution assumption, a few lines of code, and it works for means of ratios. Its result is a statement about noise, which is the thing a ranked table hides.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: Why a narrow chart tool?
  back: Numbers come from the query, axes start at zero, and there is no general Python tool to sandbox. It gives up flexibility to rule out misleading charts.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: What are the limits of the validator?
  back: Only claim shapes it understands. Open "why" questions and repeated exploration across many cuts need review, and query logs make that possible.
  lesson: generative-ai/07-agentic-applications/notes/05-data-analysis-agent
- front: 'Chatbot, collaborative editor or ambient: how do you choose?'
  back: By concurrency, meaning who works when. Help on demand is a chatbot, a kept artifact is collaborative editing, and slow work nobody is waiting on is ambient.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: What is the hardest part of each?
  back: Safe write access to the canvas; merging the agent's edits with the user's; defining "interesting" and keeping reflection from drifting.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: Why not rewrite the whole document?
  back: It cannot be merged with concurrent edits. Emit targeted operations against anchors that survive them, and stream small intermediate edits.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: When would you still use an intent classifier?
  back: With few, known intents and tight cost or latency, as a front door. DIET matched BERT fine-tuned inside it (within one standard deviation) and trained about six times faster on the NLU-Benchmark.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: Do explanations make human review safer?
  back: Not by themselves. In Bansal et al.'s crowd studies, none gave a significant gain over showing confidence, and on two of three tasks the Explain-Top-1 condition lowered accuracy when the AI was wrong. Showing checkable evidence is the design inference; the study did not test it.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: Why does reflection need anchors?
  back: An agent that edits its own definition of interesting can silence an alert class, and no one sees alerts that were not sent. Fix a must-surface list and log rule changes.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: What does a new domain cost on a well-built engine?
  back: A corpus and new goals, if the registry and ingestion are generic. Rothman moved from legal to marketing that way, but his evidence is single runs and one pitch that outran its sources.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: A blend of small models beat ChatGPT on retention. What do you conclude?
  back: For that platform and audience, engagement did not follow model size. Measure the product's own outcome with an A/B test, and do not generalize to tasks with a correct answer.
  lesson: generative-ai/07-agentic-applications/notes/06-application-patterns
- front: How do you scope an AI product?
  back: User, problem, metric, constraint, in that order, with a kill criterion written first. Then cost, ROI, build or buy, and a phased rollout
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: How do you estimate cost per request?
  back: 'Count model calls per task, and what each resends: prefix, history and new input. Then add tool tokens, retries and evals'
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: Why does input dominate output in an agent?
  back: Every call resends the growing context. Here it's 21,048 input to 770 output, so output was only 15% of cost despite the 5× price
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: When does prompt caching pay?
  back: When a large prefix gets read many times. A prefix read across tickets saved 51% here; history read twice saved a further 5%
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: What usually decides an AI product's ROI?
  back: Uplift and use rate, not the model bill. A 30% miss on use moved value by four times the whole bill
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: What is the evidence on productivity uplift?
  back: Mixed. +14% in a support field study, with most of it among novices. A trial of experienced developers measured them 19% slower while they felt faster
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: Why not ask users whether it saves time?
  back: In that trial, self-estimates had the wrong sign. Use a holdout or a timed comparison
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: When is time saved worth money?
  back: Only when hiring, backlog or volume changes. Otherwise it's capacity, not cash
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: Build or buy?
  back: Compare over a horizon with fixed engineering against per-seat fees, and find the break-even. Then ask whether the integration or eval set is your advantage
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: When do you self-host?
  back: When volume is high enough for fixed compute to beat flat per-token API pricing, or privacy or control requires it. Include the people
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: Why keep shadow mode if it earns nothing?
  back: It's the cheapest look at real tokens, latency and quality before anyone depends on it
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
- front: How do you read adoption?
  back: As a funnel with an owner per step, over time. Adherence can rise with exposure, so week one is a poor reading
  lesson: generative-ai/07-agentic-applications/notes/07-scoping-an-ai-product
---
