---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/05-graph-engineering/slides/deck.yaml
cards:
- front: Why does the Airflow-style DAG model break when you apply it to agents?
  back: Graph engineering for agents means cyclic graphs, because retrying and revising need a way back.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: Is moving from a loop to a graph a maturity level you graduate to?
  back: Escalating to a graph is a cost you justify with a specific signal, and not a maturity level you graduate to.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: What should you try before adding nodes when a loop keeps passing bad work?
  back: The most common "we need a graph" is really an overloaded verifier, which you can split inside the existing loop.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What was the mean multi-agent gain across Kim et al.'s 260 controlled configurations, and what decides it?
  back: Across 260 controlled configurations the mean multi-agent gain was −0.3%, so the task shape decides.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: When does a fan-out graph fail to pay for its extra tokens?
  back: Fan-out pays only for high-value work whose branches are truly independent, so measure your own break-even.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
- front: What is the adoption order for moving a loop to a graph?
  back: Adopt a graph by finding real edges, sketching 3 to 5 nodes, and adding nodes one at a time against a baseline.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
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
- front: What is the true-dependency test for deciding whether steps can run in parallel?
  back: To tell a real edge from an incidental one, ask whether the next step reads the previous output. If not, fan out.
  lesson: ai-engineering/05-graph-engineering/notes/03-state-and-reducers
- front: What single mechanism underlies human-in-the-loop, resume and time travel?
  back: Saving state after every super-step gives one mechanism for human approval, crash recovery and time travel.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Where must a side effect sit relative to interrupt(), and why?
  back: On resume a node reruns from its first line, so any side effect belongs after the interrupt.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Why not put a human approval gate on every node?
  back: A gate on every node trains people to approve without reading, so gate only where consequence concentrates.
  lesson: ai-engineering/05-graph-engineering/notes/04-durable-execution-and-interrupts
- front: Why does choosing a topology also choose what to watch?
  back: Five shapes cover most graphs, and each has a named failure, so choosing a shape also chooses what to watch.
  lesson: ai-engineering/05-graph-engineering/notes/05-topology-patterns
- front: What rule of thumb chooses between shared and isolated context?
  back: Isolate contexts if the cumulative trajectory would pass about half the window; share if no information can be lost.
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
  back: Without an anchor the graph can't edit, it stays perfectly self-consistent while drifting far from reality.
  lesson: ai-engineering/05-graph-engineering/notes/07-failure-modes-at-scale
- front: How do you attribute and budget cost in a graph?
  back: Carry graph, run and node IDs on every call, and budget per node, per run and per tenant.
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: What is n8n's reported design for bounding a workflow builder?
  back: 'n8n''s reported design: per-node bounds, one gate after planning, and a 30K cap on the artifact under construction.'
  lesson: ai-engineering/05-graph-engineering/notes/08-governance-and-production
- front: What are nodes and edges in an agent graph, and in a knowledge graph?
  back: An agent graph is execution topology and a knowledge graph is a data structure; they share only a name until agents share memory.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: Why does naming edges by meaning matter more than having edges?
  back: A graph whose edges are all RELATED_TO says that things connect but not how, so the edge type holds the knowledge.
  lesson: ai-engineering/05-graph-engineering/notes/09-kg-fundamentals-and-cypher
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
- front: What did the GraphRAG evaluation actually show?
  back: Going global helps whole-corpus questions; the graph mostly makes it cheaper. That falls short of showing that graphs beat vectors.
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: What is the default order for adding retrieval modes over a knowledge graph?
  back: Default to vector, then canned traversals, then text-to-Cypher with a validator for the long tail.
  lesson: ai-engineering/05-graph-engineering/notes/11-kg-rag-and-text-to-cypher
- front: When does a graph question need no model, and which indexes answer it?
  back: Answer a fixed question shape with a canned query by name or place, and keep the model for the long tail.
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
- front: Why do workers submit a GraphUpdate and not write to the graph directly?
  back: Workers submit updates to a validator instead of writing directly, which is the reducer idea at database scale.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: How should a shared agent graph treat each agent's writes?
  back: A shared graph stores claims with provenance and keeps contradictions, because no agent's write counts as truth.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: What is the graph ML bottleneck, and what does a false predicted link do?
  back: Features are the graph ML bottleneck, and a false predicted link does what a false merge does to every later traversal.
  lesson: ai-engineering/05-graph-engineering/notes/13-graph-ml-and-gnns
- front: What do matrix factorisation, Node2Vec and a GNN have in common?
  back: Every method is an encoder plus a decoder, and on the book's two runs the heaviest model, GAT, never beat GraphSAGE.
  lesson: ai-engineering/05-graph-engineering/notes/13b-representation-learning-and-gnns
- front: What is the gate before adding a swarm to a persistent graph?
  back: Build one measured loop first and add the swarm last, evaluating each layer by its own metric.
  lesson: ai-engineering/05-graph-engineering/notes/12-kg-as-shared-agent-memory
- front: What single rule decides when a loop becomes a graph?
  back: Start with a loop, and add a node only when a specific signal forces it.
  lesson: ai-engineering/05-graph-engineering/notes/01-graph-vs-loop
- front: What is the first experiment to run on an existing loop?
  back: The cheapest graph experiment is splitting one verifier by criterion and measuring before drawing any node.
  lesson: ai-engineering/05-graph-engineering/notes/06-when-not-to-build-a-graph
---
