---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/05-graph-engineering/slides/deck.yaml
cards:
- front: What are the four parts of this lecture, in order?
  back: The first two parts are about execution graphs, the third is about knowledge graphs, and the fourth is where the two meet.
  lesson: ai-engineering/05-graph-engineering/readme
- front: Name four things this lecture teaches you to do with a graph.
  back: You will be able to choose between a loop and a graph, build and run one, and say when a knowledge graph is the memory it coordinates through.
  lesson: ai-engineering/05-graph-engineering/readme
- front: Why does the Airflow-style DAG model break when you apply it to agents?
  back: Graph engineering for agents means cyclic graphs, because retrying and revising need a way back.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: Is moving from a loop to a graph a maturity level you graduate to?
  back: Escalating to a graph is a cost you justify with a specific signal, and not a maturity level you graduate to.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: How do you decide the kind of each node in a graph?
  back: Use code where you can, one LLM call where you must, and an agent only where the path is unknown.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: What is a graph program made of?
  back: A graph program is nodes that return changed keys, plus routers that are ordinary code choosing the next node.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: What must the verifier not see, and what limits the cycle?
  back: A verifier that sees only the task and the output stays independent, and an attempt counter bounds the back-edge.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: How do you make a shared state key safe?
  back: Decide up front who writes each state key, and give any key with several writers a reducer.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: What happens when two parallel branches write one key with no reducer?
  back: Branches in one super-step that write one key with no reducer raise an error in LangGraph and lose work elsewhere.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: How does a graph run one reviewer per changed file when the count is unknown?
  back: Send fans out one reviewer per file at runtime, a reducer merges the results, and a cap on N bounds the cost.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: What single mechanism underlies human-in-the-loop, resume and time travel?
  back: Saving state after every super-step gives one mechanism for human approval, crash recovery and time travel.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Where must a side effect sit relative to interrupt(), and why?
  back: On resume a node reruns from its first line, so any side effect belongs after the interrupt.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Why not put a human approval gate on every node?
  back: Gate only where consequence concentrates, since a gate on every node trains people to approve unread.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: What rule of thumb chooses between shared and isolated context?
  back: Isolate contexts if the cumulative trajectory would pass about half the window; share if no information can be lost.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: Why does choosing a topology also choose what to watch?
  back: Five shapes cover most graphs, and each has a named failure, so choosing a shape also chooses what to watch.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: When does a second agent, such as a reviewer, earn its node?
  back: A reviewer that only rereads text is the same model a second time; it earns a node when it can run something.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: Where does the operating-system analogy for a multi-agent runtime break?
  back: Treat the runtime like an OS, but because agents pass meaning and a message can be misread, every interface needs a contract the receiver can check.
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: Why should a manager pass file paths between agents instead of file contents?
  back: A message carries paths and a task ID, not contents, so a manager can coordinate many workers without holding every file.
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: How does a manager track and stop many parallel agents?
  back: Have agents write their own status to an append-only log, and settle termination races with a lock or idempotent writes.
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: What was the mean multi-agent gain across Kim et al.'s 260 controlled configurations, and what decides it?
  back: Across 260 controlled configurations the mean multi-agent gain was −0.3%, so the task shape decides.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: When does a fan-out graph fail to pay for its extra tokens?
  back: Fan-out pays only for high-value work whose branches are truly independent, so measure your own break-even.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What is the adoption order for moving a loop to a graph?
  back: Adopt a graph by finding real edges, sketching 3 to 5 nodes, and adding nodes one at a time against a baseline.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What should you try before adding nodes when a loop keeps passing bad work?
  back: The most common "we need a graph" is really an overloaded verifier, which you can split inside the existing loop.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: How do you handle cycles, deadlocks and races in a graph?
  back: Wiring failures such as cycles, deadlocks and races have mechanical detectors and fixes, if you let the framework report them.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: Which three bounds does the pre-flight check require on a graph's wiring?
  back: Before running unattended, give every back-edge a counter, every Send a cap, and recursion_limit a chosen value.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: What do most multi-agent failures turn out to be, and what do you fix before rewording prompts?
  back: Most multi-agent failures are structural, so fix topology and verification before you reword prompts.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: What is an anchor, and what happens to a graph that has none?
  back: An anchor is a reference the graph can't edit, such as held-out tests; without one, coupled loops stay self-consistent while drifting from reality.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: How do you attribute and budget cost in a graph?
  back: Carry graph, run and node IDs on every call, and budget per node, per run and per tenant.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: What is n8n's reported design for bounding a workflow builder?
  back: 'n8n''s reported design: per-node bounds, one gate after planning, and a 30K cap on the artifact under construction.'
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: Why does naming edges by meaning matter more than having edges?
  back: A graph whose edges are all RELATED_TO says that things connect but not how, so the edge type holds the knowledge.
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: What are nodes and edges in an agent graph, and in a knowledge graph?
  back: In an agent graph nodes are computation and edges are transitions; in a knowledge graph nodes are entities and edges are typed relationships.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: What makes a Cypher load safe to run twice?
  back: Cypher draws graph patterns in ASCII, and MERGE with a uniqueness constraint makes data loads idempotent.
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: Why is entity resolution the load-bearing step in building a knowledge graph?
  back: Errors compound per hop, so 85% per hop gives 44% over five, which makes entity resolution the load-bearing step.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: Why store mentions and resolution evidence separately?
  back: Storing mentions and resolution evidence separately keeps merges reversible, and a false merge corrupts every path through it.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: What does each of the extract, enhance and expand stages add to the SEC graph?
  back: Start with a minimum viable graph, add document structure, then fuse structured data onto the same entities.
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: What is the default order for adding retrieval modes over a knowledge graph?
  back: Default to vector, then canned traversals, then text-to-Cypher with a validator for the long tail.
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: What did the GraphRAG evaluation actually show?
  back: Going global helps whole-corpus questions; the graph mostly makes it cheaper. That falls short of showing that graphs beat vectors.
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: When does a graph question need no model, and which indexes answer it?
  back: Use a full-text index for names and point distance for places, and keep the model for the long tail.
  lesson: ai-engineering/05-graph-engineering/notes/11a-structured-lookups-and-text-to-cypher
- front: What schema should a text-to-Cypher prompt show, and how should it handle a question it can't answer?
  back: 'Show the model an annotated, filtered schema, and let it return `success: false` instead of inventing a plausible query.'
  lesson: ai-engineering/05-graph-engineering/notes/11a-structured-lookups-and-text-to-cypher
- front: How is text-to-Cypher made reliable in the QA agent?
  back: Text-to-Cypher is a bounded generate-then-verify loop, and listing relationships first reduces invented relationship types.
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: What does each of loop, swarm and graph move out of the agent?
  back: Loops externalise evaluation, swarms externalise search, and a shared graph externalises facts and provenance.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: How should a shared agent graph treat each agent's writes?
  back: A shared graph stores claims with provenance and keeps contradictions, because no agent's write counts as truth.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: Why do workers submit a GraphUpdate and not write to the graph directly?
  back: Workers submit updates to a validator instead of writing directly, which is the reducer idea at database scale.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: What is the gate before adding a swarm to a persistent graph?
  back: Build one measured loop first and add the swarm last, evaluating each layer by its own metric.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: What is the graph ML bottleneck, and what does a false predicted link do?
  back: Features are the graph ML bottleneck, and a false predicted link does what a false merge does to every later traversal.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: What do matrix factorisation, Node2Vec and a GNN have in common?
  back: Matrix factorisation, Node2Vec and GNNs are all an encoder that turns structure into a vector plus a decoder that turns it into a prediction.
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: What are two graph machine-learning mistakes in a shared graph, and the fix for each?
  back: Give the model graph queries as tools and keep unconfirmed predictions out of traversals and training, because a false link is followed as confidently as a true one.
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: What single rule decides when a loop becomes a graph?
  back: Start with a loop, and add a node only when a specific signal forces it.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: What is the first experiment to run on an existing loop?
  back: The cheapest graph experiment is splitting one verifier by criterion and measuring before drawing any node.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What is graph engineering?
  back: 'Designing a multi-agent system''s topology: which nodes exist, which transitions are permitted, and what state they carry across those transitions.'
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: Does graph engineering replace loop engineering?
  back: No. A loop is a directed cyclic graph with one node and an edge to itself, and a graph routing between unreliable loops inherits every loop failure and adds coordination failures.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: How do the failure modes differ?
  back: 'A loop fails by not converging: spinning, quitting early, gaming the scorekeeper. A graph fails by mis-routing, deadlocking, double-writing shared state or losing accountability for a decision.'
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: Why doesn't an Airflow-style DAG fit agents?
  back: A production agent has to go A → B, find that B failed, return to A and only then reach C. A DAG forbids that cycle, so agent graphs are cyclic graphs with bounds.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: What justifies adding a node?
  back: 'One of five signals: distinct specialties, parallel fan-out plus join, per-step model or tool variation, auditable control flow, or an overloaded verifier.'
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: A team's eval pass rate is low and they propose four specialist agents. What do you do first?
  back: Run the decision tree. If one verifier is judging several criteria, split it inside the loop and re-measure, because that is far cheaper than splitting the system.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: How is an agent graph different from a knowledge graph?
  back: Agent graph nodes are computation and its edges are permitted transitions; a knowledge graph's nodes are entities and its edges are typed relationships. They meet when the KG becomes the shared state agents coordinate through.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: Workflow or agent?
  back: 'In Anthropic''s split, a workflow orchestrates models and tools through predefined code paths and an agent directs its own process. A graph can mix them: fixed paths where you know the route, an agent node where you don''t.'
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: What can a node be?
  back: Deterministic code, a router, a single LLM call, an agent with its own tool loop, or a human checkpoint. Each costs differently, and one graph should mix them.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: What does "spend agency per node" mean?
  back: Give each node the least agency that can do its job, since every node that could be code and isn't costs tokens and variance. LangChain's docs agent is a fixed API call, one LLM call with no tools, and one agent node for the open-ended part.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: Where is the important line on the autonomy ladder?
  back: Under level 3. Up to the router a human decides what can happen and the graph is a DAG; from the state machine down, back-edges let the LLM decide when to stop.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: Why is `Literal` in a `TypedDict` not enough for a router?
  back: It is a type hint that nothing checks at runtime, so any other string falls through to the `else` branch without an error. Use a schema, an "unclear" value and a real fallback node.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: A router occasionally gives a confident wrong answer and logs show no errors. Where do you look?
  back: At what its unrecognised labels fall through to, and at the route distribution. Then evaluate the router alone on a labelled set, as a classifier.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: When do you use `Command(goto=, update=)` rather than a separate router?
  back: Use `Command` when the node doing the work is the only one that knows where to go next, and a separate router when the routing logic should be testable on its own.
  lesson: ai-engineering/05-graph-engineering/notes/02-graph-primitives
- front: What is the difference between state and context?
  back: State is what the graph stores. Context is what you choose to load from it into one node's prompt, so a reviewer sees the draft and the task rather than every key.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: What does a reducer do?
  back: 'It decides how a node''s update combines with what''s there: overwrite with no reducer, append with `operator.add`, append-or-replace by ID with `add_messages`, or anything a custom `(old, new)` function returns.'
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: What is a super-step, and why does it matter for races?
  back: Every node scheduled for the same super-step runs in parallel and their updates apply together at the end, with no checkpoint between them. The reducer alone decides how they combine.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: State the rule for shared keys.
  back: Every key has exactly one writer or an explicit reducer. n8n's builder enforces the same rule by compare-and-swap, rejecting a write that lacks the `versionId` and `expectedChecksum` it read.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: How do `Send` and reducers relate?
  back: '`Send` creates the parallel writers and the reducer makes their writes safe, so without the reducer the fan-out graph raises on its first run with two items.'
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: A customer's internal fields leak through your API although the output schema excludes them. Why?
  back: The output schema filters `invoke`'s return value, not `stream()`. Filter the stream as well, or keep those fields out of state.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: How do you find steps to parallelise?
  back: For each edge, ask whether the next step actually reads the previous step's output. If it doesn't, the ordering is incidental and the step can fan out.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: Why can't a plain loop pause?
  back: Its progress is on the call stack and in an in-memory message list, so there is nowhere to put it when it stops or the process dies.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: What is the one mechanism behind human-in-the-loop, crash recovery and time travel?
  back: A snapshot of the full state at the end of every super-step, keyed by `thread_id`. Each feature is a different use of those checkpoints.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: What happens on resume after `interrupt()`?
  back: The interrupted node runs again from its first line, so anything above `interrupt()` executes twice. Put side effects after it or make them idempotent.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: '`interrupt()` or `interrupt_before`?'
  back: '`interrupt_before` pauses before a node and is useful for debugging. Prefer `interrupt()` in production, because the node can give the human exactly what they need to decide.'
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Where do approval gates go, and why not everywhere?
  back: 'At the edges where consequence concentrates: irreversible actions, trust boundaries and low-confidence routes. A gate everywhere trains people to click approve without reading.'
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: A bad decision at step 6 of a 10-step run wasted an hour. How do you debug it?
  back: Use `get_state_history` to find the checkpoint, `update_state` to change the state there, and invoke from that `checkpoint_id` to fork, so you don't rerun from the start.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: What must a checkpoint hold for a clean resume?
  back: 'Everything the next step needs: the plan, completed steps, intermediate outputs and run metadata such as attempts and budget used. A live connection or a local variable won''t survive.'
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Name the five recurring topologies and how each fails.
  back: Generate-then-verify (the checker agrees with reasoning it can see), supervisor (mis-routing, bottleneck), fan-out (missing reducer, correlated errors), hierarchical (failures hidden inside the subgraph), handoff (status values drift).
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: What is the fix for a supervisor that mis-routes?
  back: 'A schema rather than a firmer prompt: `with_structured_output` over a `Literal` with an `unknown` value, routed to a clarify or escalate node that exists in the graph.'
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: What do you lose building a graph with Claude Code subagents instead of LangGraph?
  back: Typed shared state, reducers and checkpoints. State is whatever the orchestrator passes along, which is a context firewall when you want one and a liability when you need resume.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: When should agents share context and when should it be isolated?
  back: Li's rule is not to share when cumulative context would pass about half the window. Isolated agents then pass paths rather than contents, as threads versus processes would suggest.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: Should you add a second LLM to review the first?
  back: Ask if the collaboration brings in information. Self-review is often neutral or harmful and debate doesn't help much, but a reviewer that can run something gets execution feedback and earns its node.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: A single agent passes 60% of your task set. Does adding a team help?
  back: 'Probably not on those numbers: Kim et al. found negative returns from extra agents above about 45% single-agent performance. Measure on your own tasks before adding any.'
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: Does debate among copies of one model beat a single agent?
  back: Not at matched budgets. On multi-hop QA at matched thinking-token budgets, Tran & Kiela found a single agent best or statistically tied at every budget above 100 tokens. Copies of one model add no new information; execution or tool feedback does.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: Orchestration or choreography?
  back: Orchestration has a conductor, which is a bottleneck and a single point of failure. Choreography removes both and makes the flow harder to see, so it needs a max-handoff guard.
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: Ten parallel workers search and one finds the target. How do the rest stop?
  back: In the parallel-search lab, the finder broadcasts `target_found`; the manager takes a lock, sends `terminate` to the rest and times out any worker after 2 minutes.
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: What is the weak point of a manager with sub-agents?
  back: 'The planner, because a bad plan sinks every worker. Plan-and-Act invests there: it fine-tunes a dedicated planner and replans after every executor step instead of committing to the first plan.'
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: Ten workers share one transcript, or pass file contents in their messages. What do you change?
  back: Pass paths, not contents. Give each agent a private scratchpad, a shared workspace with a lock or a worktree each, and a read-only area for skills, so the manager holds an index rather than the files.
  lesson: ai-engineering/05-graph-engineering/notes/05b-running-multi-agent-systems
- front: How do you decide if work is too fluid for a graph?
  back: Ask if you can name the nodes before the run starts, or if `Send` can derive them from a step you know. If neither, use a harness with a good loop.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What does fan-out cost, per Anthropic?
  back: In their write-up, agents use about 4× the tokens of a chat interaction and multi-agent systems about 15×, so it pays only for tasks whose value justifies that.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What did Kim et al. add to that?
  back: '260 configurations across six benchmarks showed an enormous spread: a centralized team scored 80.8% above a single agent on Finance Agent, where work decomposes, and extra agents had negative returns once a single agent passed about 45%.'
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: A vendor says fan-out breaks even at a 50% pass rate. How do you treat that?
  back: As a shape to test, not a constant. Run the same task set through the loop and the graph, and compare tokens, wall-clock time and pass rate.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: Your verifier is failing. Do you add a node?
  back: First split it into per-criterion checks in the loop, make what can be code into code, and measure. A criterion that still fails because it needs a different model, tools or context has earned a node.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What does a premature graph cost besides tokens?
  back: More prompts that can drift, state synchronisation, coordination latency and harder debugging, since a wrong answer now has N places it could have come from.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: How do you adopt a graph once it is justified?
  back: Find the bottleneck, mark which edges are real, sketch 3–5 nodes, baseline the loop against the graph, and add nodes one at a time, each with a signal.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What are the two families of graph failure?
  back: Mechanical failures come from wiring (cycles, races, unbounded fan-out, mis-routing) and the framework mostly catches them. Control failures come from interacting feedback loops, and nothing catches them unless you design for it.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: Why are N agreeing workers weak evidence?
  back: They usually share a model, prompt template and index, so their errors correlate. In the note's simulation, a nine-worker majority at 70% each falls from about 90% to 70% as sharing goes from none to total.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: What should a verifier see?
  back: The task and the output, not the generator's reasoning, because a verifier that sees the reasoning tends to ratify it.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: Why are agent failures Byzantine rather than crash faults?
  back: A worker that hallucinates still returns a well-formed summary, so timeouts and retries see nothing. Only cross-validation, independent voting and deterministic checks catch it.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: How much does topology change error spread?
  back: Kim et al. measured trace-level errors at 17.2× a single agent for independent agents merged without cross-checks, and 4.4× with a validating orchestrator, across six benchmarks.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: A team's ChatDev-style system keeps failing and they want to rewrite the prompts. What do you say?
  back: MAST found prompt and role fixes gave only +15.6% on ChatDev, and that most failures are structural, so look at topology and verification first.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: What is an anchor, and why can't it be tunable?
  back: An external fixed node the machinery is forbidden to rewrite, such as a held-out test set. Without one a graph can be self-consistent while drifting away from reality, and a tunable anchor eventually gets tuned.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: Which identifiers should every call carry, and why?
  back: '`graph_id` to compare and roll back topology versions, `run_id` or `thread_id` to group and resume a run, and `node_id` for per-node cost, latency and error rate.'
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: Why record the actual runtime work graph?
  back: With `Send` and conditional edges, the graph that ran isn't the one you drew. Traces are the only record of which nodes ran, how many times and in what order.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: At what levels do you budget, and what does each guard against?
  back: Per node for one node looping or fanning out, per run for a whole run going wrong, per tenant for one customer consuming shared budget.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: Why can't the framework enforce a tenant budget?
  back: The limit must hold across many concurrent runs, and a run-scoped framework only sees one. TrueFoundry's answer, which is also what it sells, is a gateway rule keyed on a virtual account or metadata tag.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: A tenant budget is checked on every call and still overspends. Why?
  back: The check and the write sit either side of an await, so concurrent runs all pass the same check. Reserve the worst case atomically before the call and settle after it.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: Why filter by tenant in the query rather than after it?
  back: After it, the top-k is already spent, so small tenants starve, and any step before the filter has seen foreign text. Over-fetching eases the first and worsens the second.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: What does a model alias buy you?
  back: A model change becomes a config change you can roll out and roll back per node, rather than a code edit.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: What is the transferable lesson from n8n's context budget?
  back: Compaction starts at 75% of the window (150K of 200K), and the artifact under construction is capped at 30K tokens, so the agent can't fill its context with what it is editing. These come from a third-party teardown.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: A run's cost doubled overnight. How do you find out why?
  back: Group the trace by `node_id` and compare it with the prior `graph_id`. Without `node_id` on every call, you only learn that the run was expensive.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: What makes a knowledge graph more than a graph database?
  back: 'The chapter''s four pillars: evolution (it is never done), semantics (types and relationship names carry meaning), integration (several sources fused onto shared entities) and learning (the structure supports inference and graph ML).'
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: LPG or RDF?
  back: 'Choose by goal: RDF and OWL when standard ontologies, interchange and formal inference are the point; LPG when you want properties on edges and fast traversal, as with `since` or `source`.'
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: Why put provenance on edges?
  back: Fields such as `source`, `run_id` and `extracted_at` let you audit a fact and roll one back. Note 12's shared memory depends on them.
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: A `MERGE` import created duplicates. What are the likely causes?
  back: Writers racing with no uniqueness constraint, or `MERGE` on a non-key property such as a name spelled two ways. Add the constraint, `MERGE` on the key, then `SET` the rest.
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: Why does the rare-disease graph keep two IDs for type 1 diabetes?
  back: It is a disease (`OMIM:222100`) and a phenotypic feature of other syndromes (`HP:0100651`), and which applies depends on the role. Merging them would blur the ranking.
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: Should you quote "typed edges improve accuracy 18%"?
  back: 'No. That is an unsourced vendor claim. The principle holds without it: a query can only filter on distinctions the schema keeps.'
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
- front: Why is entity resolution the load-bearing step?
  back: Each hop of a traversal multiplies the error per edge, and a false merge creates paths that don't exist, which later agents follow confidently.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: NLP pipeline or LLM extraction?
  back: scispaCy-style pipelines are cheap and deterministic where a domain model exists; LLMs handle domains without one and equivalences with no surface pattern, and need temperature 0 plus stability tests.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: Why write a mention per page, and not merge?
  back: Nothing is deleted, so the KG can be rebuilt from mentions when the resolution changes. That is what makes resolution reversible.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: How does graph-based ER decide on a canonical entity?
  back: Write `META_SIMILAR` where the evidence is strong, run weakly connected components, name each after its longest name, and send borderline clusters to a person.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: You have budget for 100 labels. How do you evaluate?
  back: Label a gold set of 50–100 mentions and report precision, recall and F1 per type, plus false-merge and false-split rates, weighting merges more heavily.
  lesson: ai-engineering/05-graph-engineering/notes/10-building-kgs-with-llms
- front: Why is assembly deterministic when extraction isn't?
  back: The model's judgement stops at resolution. After that, `MERGE` on a shared key under a constraint means the same input gives the same graph, and you can replay it.
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: Where do `value` and `shares` go in the SEC graph, and why?
  back: On the ownership edge, since a value belongs to a manager's stake in a quarter. The quarter is part of the edge's identity.
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: You are merging a second source. What is your validation?
  back: Map onto shared codes before `MERGE`, label provenance per source, then check counts, orphans and degree distributions after each load.
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: Why is DWPC better than path count?
  back: It damps paths through hubs. For celiac disease, T cell costimulation (10 paths) outranks a generic immune process (21 paths) with DWPC 0.0335 vs 0.0272.
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: How do you handle a request to delete a user's data?
  back: If every fact links to its source document, you can remove what came from it. The book connects traceability to privacy for this reason.
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: What keeps running after deployment?
  back: 'Four pipelines: updates as sources change, assessment of every write, cleaning for outdated or legally removed facts, and access control.'
  lesson: ai-engineering/05-graph-engineering/notes/10b-assembling-and-maintaining-kgs
- front: Name failures of vector RAG that a graph helps with.
  back: 'Context fragmentation, embedding compression, and misses on aggregate questions: similarity optimises closeness, not coverage.'
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: What did Edge et al. actually show?
  back: LLM-judged wins over vector RAG on comprehensiveness and diversity (62–81%), with no ground truth. Map-reduce over raw chunks did about as well; the graph mostly cuts tokens.
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: What do triples lose?
  back: Conditions and nuance, so the beach-trip plan loses "if it rains". Extraction errors also contaminate the graph, so keep the source text.
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: A question needs to know how two entities connect. What do you retrieve?
  back: 'A path, restricted by rule or by shortest paths, because the number of paths grows exponentially with length. Return the smallest unit that answers: node, triplet, path, then subgraph.'
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: How do you make text-to-Cypher reliable before retries?
  back: 'An LLM-ready schema with value annotations, a query-writing prompt allowing `success: false`, the question restated last, and an `information` slot for the error on retry.'
  lesson: ai-engineering/05-graph-engineering/notes/11a-structured-lookups-and-text-to-cypher
- front: Would you use text-to-Cypher for "firms near Palo Alto"?
  back: 'No, if it is a known question: a fixed query with a parameter and `point.distance` in metres is cheaper and more reliable.'
  lesson: ai-engineering/05-graph-engineering/notes/11a-structured-lookups-and-text-to-cypher
- front: What failure should you expect in L7?
  back: Filtering `value` on the wrong node, which runs without any error from the database. A validator catches it.
  lesson: ai-engineering/05-graph-engineering/notes/11a-structured-lookups-and-text-to-cypher
- front: Why does the retry edge go to `text_to_cypher` and not to schema extraction?
  back: The schema doesn't change between attempts, only the query, which now has the database's error in the prompt's `information` slot.
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: What can't the retry loop catch?
  back: A query that runs and returns nothing, because only `ClientError` is caught. Semantic errors need a validator before execution.
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: What are the steps of a validator?
  back: '`EXPLAIN` to parse and plan, check labels, relationship types and `var.prop` against the schema, reject unbounded paths, then route failures back; execute only as a read-only user.'
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: Why do you summarise when the user can see the result?
  back: The summary complements the view, pointing out what isn't visible, such as a detail in a `description`. `results_analysis` makes the choice to analyse easy to monitor.
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: Why does the five-step investigation work without restating anything?
  back: Each turn can point at the nodes selected in the last one, so "the selected crime" resolves from the UI selection.
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: What would you measure in production?
  back: First-pass validity and validity after retries, which tell you whether the prompt or the retry edge does the work.
  lesson: ai-engineering/05-graph-engineering/notes/11b-text-to-cypher-qa-agent
- front: How is a KG different from graph state?
  back: State lasts one run, in one process, and mistakes die with it. A KG lasts across runs, any agent reads it, and mistakes persist and spread.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: What are the non-negotiables of the write path?
  back: Complete provenance, reversible entity resolution, and claims stored as claims rather than truths.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: Why isn't a swarm enough?
  back: Without shared state, workers re-derive the same findings. Publishing to a shared typed graph turns that redundancy into accumulation.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: What does Claude Code's workflow limit tell you about cost?
  back: Third-party write-ups report 16 concurrent and 1,000 total sub-agents per run, and Anthropic reports about 15× tokens for its multi-agent system. Topology makes spend tractable, not cheap.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: How do you test if the graph is earning its place?
  back: Fan out 5–10 workers over one corpus with and without shared memory, compare redundancy, tokens and quality, and gate against flat retrieval too.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: A right answer came from an unsupported path. Is that a pass?
  back: No. Evaluate path validity as well as correctness, because a right answer reached through a wrong path is luck.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: Why are graph tasks semi-supervised?
  back: Training sees the whole graph, unlabelled nodes included; only their labels are missing, and their neighbourhoods still inform the model.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: Homophily or structural equivalence?
  back: Homophily says connected nodes are alike, and structural equivalence says nodes with similar neighbourhoods play similar roles even when far apart. They need different features.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: Why isn't community detection K-means?
  back: K-means needs *k* up front and treats records as independent points, while Louvain and label propagation use the graph directly and need no training.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: Why write features by hand at all?
  back: 'They are explainable, they work on small graphs, and they set a baseline: karate club got 0.93 from homophily against 0.64 from untuned Node2Vec, on 14 test nodes.'
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: What does DWPC fix, and what doesn't it let you do?
  back: It discounts hubs in path counts, but scores compare only within one metapath and one exponent.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: You are predicting links on a changing graph. What is the hard rule?
  back: Featurisation at prediction time must be exactly the one used at training time.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: Why negative sampling?
  back: 'Scoring all pairs is hopeless: a million nodes means about a trillion candidates, nearly all absent. Each true triple is scored against a few corrupted ones.'
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: What distinguishes KG embedding decoders?
  back: 'The patterns they represent: symmetric, asymmetric, inverse, compositional. DistMult is symmetric in head and tail, and RESCAL''s matrix per relation is expressive and parameter-heavy.'
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: What are message edges and supervision edges?
  back: Message edges carry information and supervision edges are what the model predicts. If they overlap, the model can see the answer and training metrics mean nothing.
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: Your AML model has 0.97 weighted F1. Ship it?
  back: Not on that number. With 90% licit nodes, weighted F1 stays high while only 68–83% of illicit nodes are caught, so look at per-class recall and false positives.
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: GCN, GAT or GraphSAGE?
  back: On the book's runs, GAT had the most parameters and never beat SAGE. SAGE caught most AML (83%) with fewest false links (5.4%), and GCN found most links (78.6%).
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: How can LLMs and GNNs combine?
  back: 'As predictor, encoder, aligner or labeller: an LLM can embed node text for the GNN, or label nodes zero-shot, or narrate a structural result without deciding it.'
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: What do you do with a predicted edge?
  back: Write it through `GraphUpdate` flagged, with confidence and `run_id`, keep it out of default traversals, and watch false positives, since a false link acts like a false merge.
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
---
