---
title: Wiki Index
tags: [meta, reference]
summary: Auto-generated table of contents for every page in data/wiki/, grouped by domain directory.
updated: 2026-08-04
sources:
  - data/wiki/
---

# Wiki Index

Canonical list of all wiki pages, grouped by domain (the primary retrieval axis).
Regenerate after every ingest. `data/wiki/private/` is deliberately excluded.

**270 pages** across 17 domains.

## Foundations

- [[Batch Normalization]] — Batch Normalization (Ioffe & Szegedy, 2015) normalizes layer inputs using mini-batch statistics during training to reduce internal covariate shift — enables higher learning rates, reduces sensitivity to initialization, and acts as a regularizer. Rethinking BatchNorm (Wu & Johnson, 2021) exposes pitfalls with EMA population statistics, train/inference inconsistency, and domain shift.
- [[Bradley-Terry Preference Model]] — The pairwise-comparison model that converts human choices between two responses into a scalar reward — the shared formal core underneath RLHF reward models, DPO, and RLAIF preference models.
- [[Constitutional AI and RLAIF]] — Anthropic's two-phase replacement for human preference labels — critique-and-revise SL-CAI followed by RLAIF against a written constitution — plus what AI feedback provably matches and where it still underperforms humans.
- [[Data Engineering Foundations]] — The six stages of data engineering as a pipeline discipline — ingest, transform, orchestrate, warehouse, monitor, feature-serve — where each stage's job is to prepare data for the next, plus the modern-stack tools (DuckDB, Polars, Iceberg, Dagster) missing from Zoomcamp-era material.
- [[Data Science Curriculum Layers]] — The tree-shaped ML curriculum — statistical foundations, then supervised learning branching to model evaluation and independently to unsupervised/ensembles/Bayesian — plus the six-layer analytics progression that precedes it and the branching decision that ends it.
- [[Dialogue Transformers — TED Policy]] — Transformer Embedding Dialogue (TED) policy (Rasa, 2020) applies self-attention at the discourse level — over dialogue turns rather than tokens — outperforming LSTM-based policies on sub-dialogue handling while being simpler and faster than REDP.
- [[DIET Architecture]] — Dual Intent and Entity Transformer (Rasa, 2020) — a multi-task NLU architecture for joint intent classification and entity recognition that outperforms fine-tuned BERT while being 6x faster to train, using plug-and-play pre-trained embeddings with sparse features.
- [[Dilated Causal Convolutions]] — Convolutions with exponentially increasing dilation factors that preserve temporal causality while growing the receptive field exponentially with depth — the key architectural innovation in WaveNet for modeling long-range audio dependencies efficiently.
- [[Git Branch Triage]] — Deciding what to do with in-flight work before switching context — the branch health check that separates merged from unmerged commits, the WIP-branch-versus-stash choice, and reading a stash diff before trusting it.
- [[HDBSCAN with KMeans Fallback]] — Clustering selection strategy that tries density-based HDBSCAN first and falls back to KMeans when silhouette drops below 0.25 — plus the diagnostic discipline that treats a fallback as a feature-quality signal rather than a resolved choice.
- [[Multi-Agent Reinforcement Learning]] — MARL, the non-stationarity problem it exists to solve, CTDE as the dominant answer, the value-decomposition and central-critic algorithm families, and the five challenges — including the ~10–20 agent scalability wall.
- [[Neural Probabilistic Language Model]] — Bengio et al. (2003) introduced the idea of learning distributed word representations (embeddings) jointly with a neural network language model — fighting the curse of dimensionality by mapping words to a continuous vector space where semantically similar words have nearby representations.
- [[Notebook Dependency Staleness]] — Migration maps for the three library breaks that strand old ML notebooks — sklearn 0.20→1.4, TensorFlow 1.x→2.x, PyMC3→PyMC 5 — plus the two-phase triage that distinguishes a mechanical import swap from a genuine rewrite.
- [[Open-Domain Dialogue Systems]] — Survey of frameworks for open-domain conversation — retrieval-based (score candidates), generation-based (seq2seq/PLM), and hybrid methods — with two key goals (informative via knowledge grounding, controllable via persona/strategy/safety).
- [[Positional Encoding]] — Sinusoidal or learned position signals injected into Transformer input embeddings — required because self-attention is permutation-invariant and has no inherent notion of sequence order.
- [[Preference Optimization Algorithms]] — The PPO → DPO → GRPO → KTO/IPO/ORPO family — what each removes from the stage before it, the five-algorithm decision table, and why the field shifted from choosing an algorithm to designing a reward structure.
- [[RLHF Pipeline]] — The three-stage InstructGPT pipeline — SFT, then a Bradley-Terry reward model on ~33k comparisons, then PPO with a KL penalty against the SFT policy — and why all three stages are load-bearing.
- [[Reinforcement Learning Foundations]] — The MDP tuple (S, A, P, R, γ), the Markov property that makes RL tractable, the four algorithm families, and the exploration/exploitation tension — with how each maps onto LLM training and agentic tool use.
- [[Reward Hacking and Overoptimization]] — The three failure modes of optimizing against a learned reward proxy — reward hacking, the inverse-U overoptimization curve against KL distance, and the ~15% alignment tax on academic NLP benchmarks.
- [[Self-Attention Mechanism]] — Self-attention (intra-attention) relates different positions of a single sequence to compute a representation — the core primitive enabling Transformers to model long-range dependencies in O(1) path length.
- [[Transformer Architecture]] — The Transformer model architecture (Vaswani et al., 2017) — encoder-decoder stacks of self-attention and feed-forward layers that replaced RNNs/CNNs for sequence transduction, enabling parallelized training and constant-length dependency paths.
- [[TypeScript any Escapes]] — The three ways out of an `any` — a real type, `unknown` with narrowing, or a generic — plus why types files are the highest-leverage place to fix them and how exhaustive-deps catches stale closures rather than style violations.
- [[WaveNet — Autoregressive Audio Generation]] — WaveNet (van den Oord et al., 2016) is a deep autoregressive generative model for raw audio waveforms using dilated causal convolutions — achieved state-of-the-art TTS naturalness (MOS >4.0) and demonstrated multi-speaker conditioning, music generation, and speech recognition from raw audio.

## Patterns

- [[ACI (Agent-Computer Interface)]] — Tool design discipline for agents — the interface between agent and tools, analogous to HCI for humans. Good ACI determines whether the agent uses tools correctly or hallucinates parameters.
- [[Agent Orchestration Patterns]] — Four levels of agent logic structure — single prompt, single agent + tools, multi-step graph, multi-agent — ordered by control and complexity, with a decision shortcut and the governing rule to start simple and escalate only on demonstrated need.
- [[Agent Quality Review Checklist]] — Nineteen agent-system-specific review checks across six families — prompt/LLM smells, tool safety, workflow state, retrieval/context, memory write-back, and accountability — of which "safeguard in prose only" is named the highest-value finding.
- [[Agent Scaffolding Skill Layers]] — A three-layer Claude Code skill design for scaffolding agents — a generic parallel-subagent factory (L1), standalone capability add-skills that read the target before generating (L2), and a domain-specific bundle that orchestrates L2 skills in sequence (L3).
- [[Agentic Workflow Patterns]] — Anthropic's five composable workflow patterns for LLM agents — when to use each, and the ACI principle for tool design.
- [[AI Project Archetypes]] — Four archetypes — Information Retrieval, Document Generation, Workflow Automation, Conversational Interface — that cover most nonprofit AI projects, each with a complexity floor, disambiguating questions, and a mapping to concrete scaffold parameters.
- [[AI Project Template Scaffold]] — A generic, framework-agnostic starter repo pattern for standing up new AI agent projects — modeled on a mature reference project's skills/docs/infra layout plus a conventional data-science project skeleton (`.github`, `project_init.sh`, `.vscode`, `data/`, `docs/`, `infrastructure/`), kept as its own repo rather than nested under the reference project.
- [[Asked vs Derived Scaffold Variables]] — A scaffold interview that splits ~20 template variables into six asked out loud, eight derived-then-confirmed, and the rest left silently defaulted — with the split decided by blast radius of a wrong guess, not by how many variables exist.
- [[Block Attribute Inversion]] — Turning a list of unanswerable design questions into per-component metadata — when each architectural block ships with its own failure mode, scaling limit, and cost driver, the design's weak points are generated from the assembly rather than interrogated from a user who cannot answer.
- [[Branch Naming Convention Pattern]] — Ticket-linked, type-prefixed branch naming (`type-TICKET-slug`) with per-repo type taxonomies and a `hotfix` escape hatch for production-blocking bugs.
- [[Callable-By Integration Contract]] — When a project needs to work with an external hosted service, the scaffoldable unit is not the service but the contract that makes your system reachable from it — a plain HTTP endpoint plus a signed-webhook receiver for the reverse direction.
- [[Capability Parity Audit]] — A method for deciding what a shared template should absorb next — classify every requested capability as have / partial / gap against the template's *verified* current state, then prioritize by how many consumers share the gap rather than by how loudly any one asked.
- [[Capability Runtime-Coupling Tiers]] — Sorting agent capabilities into runtime-coupled (T1), runtime-adjacent (T2), and runtime-independent (T3) — because cross-runtime parity is a meaningful goal for T1/T2 and a category error for T3.
- [[Chain of Thought]] — Inference-time technique where the LLM is prompted to show its reasoning before answering — improves accuracy on multi-step logic, arithmetic, and routing decisions with no training cost.
- [[Complexity Floor]] — The minimum viable complexity of a project shape — a constraint that makes capacity a selection criterion rather than a schedule, forcing archetype reframing rather than scope-thinning when the team can't reach the floor.
- [[Copier Re-Entry as Capability Path]] — Treating `.copier-answers.yml` as durable scaffold state so that flipping a template answer and re-rendering is the *only* sanctioned way a component enters a generated repo — which turns "scaffold the MVP now, add later" into a real guarantee rather than advice.
- [[Copier Upstream Update Workflow]] — Pulling template changes into an already-scaffolded project — a clean-tree gate, a mandatory `--pretend --diff` preview, impact-categorized change review, and conflict resolution that preserves local intent over template defaults.
- [[Corrective Follow-Up Dispatch]] — Gated subagents that a signal-detection pass failed to trigger get dispatched in a second round when always-on subagents report out-of-dimension signal — treating reviewer observations as a recovery path for missed conditional dispatch.
- [[Data Pipeline Pattern Selection]] — Four ways data reaches an AI system — batch ingest, event-driven, streaming, hybrid — chosen by one question about where the data comes from, with hybrid treated as a phase-2 evolution rather than a phase-1 option.
- [[Deferred Decision Status]] — A three-value status for design decisions — Resolved / Open / Deferred(trigger) — where a deferral must name the concrete event that reopens it, and a triggerless deferral silently degrades to Open so it still blocks the gate.
- [[Derived-and-Hidden Design Decisions]] — A scaffold variable marked `when: false` ships the code correctly and prevents the design conversation entirely — the failure mode where observability and guardrails exist as files nobody chose, distinguished from legitimate derivation by whether a silent default has an irreversible failure mode.
- [[Design-Before-Infrastructure Sequencing]] — The decision to make design scoping a standalone skill that runs before the scaffold interview rather than a wrapper around it — because design and build are separate phases that may be months apart, and merging them makes the combined skill unusable for anyone who already designed.
- [[DESIGN.md Artifact]] — The six-section design record every scaffolded project ships — problem, actors, C4 system context, MVP scope, key decisions, and non-functional constraints — shipped as a placeholder stub when unfilled so the skipped conversation stays visible.
- [[Deterministic Review Substrate]] — Review steps that are mechanical (diff scoping, dedup clustering, schema validation, report rendering) are pushed into a CLI the agent shells out to, so the only work left to LLM judgment is the part that actually needs judgment.
- [[Evidence Classification Model]] — A four-state classification (verified / supported / hypothesis / question) every review finding must carry before it is returned, with self-verification assigned to the producing subagent rather than the orchestrator.
- [[Integration Pattern Selection]] — Five ways an AI system connects to external services — MCP tools, Composio connectors, direct httpx clients, webhook receivers, n8n glue — and the single discriminating question that picks each one.
- [[Merge Impact and Evidence State]] — A two-axis finding schema that separates how much a problem matters (merge_impact) from how sure the reviewer is (evidence_state) — so an uncertain critical finding and a certain trivial one stay distinguishable.
- [[Multi-Agent Role Specialization]] — Multiple agents with distinct roles and tool sets coordinated by an orchestrator — the highest-complexity orchestration, justified only when quality genuinely requires different modes of thinking, and explicitly never a starting point.
- [[Multi-Repo Claude Organization]] — How to organize .claude/, .agents/, and docs/ across related repos — avoiding skill sprawl, maintaining canonical sources, and sharing context between parallel workspaces.
- [[Multi-Step Graph Orchestration]] — A directed graph of processing nodes with explicit transitions, where the LLM executes within nodes but you control flow between them — the pattern for branching, human gates, and retry loops, with a concrete refactor trigger for when to adopt it.
- [[Parallel Dimension Scanner Architecture]] — Code review decomposed into independent single-concern scanner agents dispatched in parallel — each owns one dimension, one ID prefix, and one severity mapping — so review breadth scales by adding agents rather than lengthening one prompt.
- [[Payload Security Defects at Canon]] — When a code-gen payload is about to be mirrored into every scaffolded project, its defects must be fixed in the canonical copy first — a mirror multiplies a single-source bug into every downstream consumer, and the fix window closes once copies exist.
- [[Project Discovery Conversation]] — A guided pre-design conversation that turns a volunteer's pain point into a Project Profile — deliberately withholding all technology vocabulary so the artifact commits to outcomes and constraints, not framework choices.
- [[ReAct Pattern]] — Reasoning + Acting loop — the foundational single-agent pattern where the LLM alternates thought and tool calls until it has enough information to answer. Implemented via create_react_agent in LangGraph.
- [[Read-Only by Default with Explicit Authorization]] — A review agent's safety model built from an enumerated safe-command allowlist plus a single authorization gate placed at the write boundary — so subagents get real shell access for verification while every mutating action, including writing a draft the system itself produced, stops at proposing.
- [[Scope-Gated Reporter Dispatch]] — Sizing a review to the change by declaring a scope up front, then recording each reporter's skip with its reason in the verdict — so "not run" is visible evidence rather than an absent section a reader mistakes for a clean pass.
- [[Scope-POC Design Interview]] — A five-tier system-design interview that produces a DESIGN.md answering *what* to build — idempotent over its own output, ratifying rather than adopting inherited decisions, and treating "I don't know" as a recordable answer instead of a blocker.
- [[Shared Context Brief]] — A structured brief the orchestrator fills in exactly once and passes to every dispatched subagent, so N parallel reviewers share one grounding pass instead of each re-deriving repository context from the same diff.
- [[Silent Fallthrough in String-Keyed Discovery]] — When a tool finds its working target by grepping a literal string, renaming that string doesn't crash — it selects a different target with no error, making the rename a flag-day change whose only defence is a call-site checklist.
- [[Single Agent With Tools]] — One agent with a tool set, where the LLM chooses which tools to call and when to stop — the level most real projects need, and the recommended default before any graph or multi-agent escalation.
- [[Single Prompt Baseline]] — One LLM call with no tools, state, or framework — the simplest orchestration, correct for classification/extraction/summarization, and the baseline any agent must beat to justify its complexity.
- [[Six-Pillar Agent Engineering Assessment]] — A rubric scoring agent codebases across six engineering pillars — prompt, context, harness, loop, graph, evaluation — with each pillar's requirements tiered Must/Should/Nice so a coverage percentage separates "missing the foundation" from "not yet mature.
- [[Skill Preloading via Agent Definition]] — A skill file is inert until an agent definition names it in a `skills:` field — the two-file split (`.claude/skills/<name>/SKILL.md` plus `.claude/agents/<name>.md`) is what turns checklist content into context actually loaded at subagent startup.
- [[Source Severity vs Merge Impact]] — When a review aggregates findings from external tools, each tool's native severity is preserved unrewritten and a separate merge-impact field answers the different question of whether this particular PR should merge.
- [[Specification by Example]] — The classical practice (ATDD/SBE) of expressing a requirement as a concrete example rather than prose, producing an executable specification that cannot drift from the code.
- [[Sync as Render, Not Copy]] — When one canonical source ships into a second tree that addresses it differently, the sync must transform link targets and variable names rather than mirror bytes — a byte-for-byte copy cannot serve both contexts, and hand-copied files drift backwards.
- [[TDD as Coding-Agent Harness]] — Using a failing test to constrain the agent that writes code — the clearest goal you can give it — plus the guardrail neither popular source addresses: an agent that writes both test and implementation can satisfy itself.
- [[Template Floor Raising]] — Prioritizing scaffold work by cross-portfolio gap frequency rather than by any single project's needs — the template's job is to make the weakness every existing repo shares impossible to inherit, so new projects start above the portfolio's floor.
- [[Template Migrations for Structural Moves]] — A file-level merge cannot express "this module moved" — template `_migrations` supply the missing structural edit, and degrade to a loud WARN rather than a silent overwrite when the file being moved was hand-edited.
- [[Track2Vec Playlist Co-Occurrence Embeddings]] — Item2vec-style technique — treat playlists as "sentences" and item IDs as "words", train Word2Vec over co-occurrence to get dense embeddings that capture human curation intent rather than content similarity.
- [[Verified Runtime Capability Constraint]] — A design rule that a control may only be specified if the runtime demonstrably enforces it — three separate Parallax mechanisms (a timeout budget, a cost cap, a submodule-vendored skill) were dropped on discovering the harness had no way to make them real.
- [[Wander — Question-Generating Review Agent]] — A review agent that produces 3–5 pointed questions instead of findings — surfacing intent, edge cases, walked-past decisions, blast radius, and the conspicuously absent thing — as the "yin" complement to defect scanners.
- [[Webhook Handler Idempotency]] — Every inbound webhook handler must tolerate the same event arriving more than once — at-least-once delivery is the sender's contract, so deduplication is unambiguously the receiver's responsibility.

## Prompting

- [[Prompt Engineering]] — The pillar hub — prompt ⊂ context ⊂ harness, the "colleague with minimal context" golden rule, and the nine techniques with their authority hierarchy.
- [[Few-Shot Prompting]] — Zero-shot versus few-shot, the three properties good examples need (relevant, diverse, structured) with the failure mode for each, and few-shot CoT.
- [[XML Prompt Structuring]] — Tagging inputs so the model can tell instructions from data — the technique that addresses misattribution, which is the mechanism behind injection.
- [[Structured Output]] — A structured-output prompt is a request, not a guarantee; always pair with harness-side schema validation and prefer constrained decoding where available.
- [[Prompt Templates and Variables]] — The fixed-skeleton/variable split makes prompts versionable, evaluable, and — most importantly — makes the injection boundary explicit.
- [[Long-Context Prompting]] — Longform data at the top (up to 30% quality improvement when the query appears last), XML tags for multi-document inputs, and grounding responses in extracted quotes.
- [[Prompt Chaining]] — Why decomposition beats one large prompt (split attention, contamination), what it costs, and where chains cross into harness territory.
- [[Prompt Injection]] — Instructions and data share one channel with no structural separation — the attack surface, Best-of-N power-law scaling, and defences ordered with least privilege first.

## Context

- [[Context Engineering]] — The pillar hub — the minimization objective, the four levers (Write → Select → Compress → Isolate) applied in order, and the four context types.
- [[Why Context Is Finite]] — Attention divides a fixed budget across n² token pairs, so added tokens thin attention rather than expanding capacity; the marginal return curve turns negative, not merely flat.
- [[Context Anatomy]] — What goes in the window and in what order — system-prompt altitude, the five layers organized by stability, and stable-before-dynamic ordering for cache prefix matching.
- [[Context Retrieval Strategies]] — The shift from pre-computed retrieval to just-in-time context, the hybrid default with the ≥80%-of-turns test, and pre-retrieval pipeline ordering.
- [[Context Compaction]] — Transforming interaction history into a continuation state — retention priority, why tool-result clearing is the highest-value move, and why state extraction is what makes compaction safe.
- [[Memory as Context]] — Memory is the mechanism by which context outlives a window: episodic→semantic distillation, structured note-taking, index-plus-detail, and hygiene rules.
- [[Multi-Agent Context]] — Sub-agent isolation is the highest-cost lever — the discarded window is the feature, orchestrator-holds-plan is the default, and isolation doubles as a security boundary.
- [[Context Failure Modes]] — Five distinct failures (rot, poisoning, distraction, clash, injection) with separate mechanisms and fixes, plus the diagnostic flow.

## Harness

- [[Harness Engineering]] — The pillar hub — Agent = Model + Harness, the four parts (acceptance baseline, execution boundary, feedback signals, rollback), why reliability compounds negatively, and the ratchet.
- [[Harness Anatomy]] — The nine harness components in three groups, why the filesystem is the foundational primitive, the layered mental model, and the causal build order.
- [[Tool Design as Harness Surface]] — Tools as a harness contract rather than a context cost — ACI over API, the five-section tool spec, the four gating questions, and write-operation safety.
- [[Execution Boundaries and Guardrails]] — Sandboxes, hooks, and permission gates — encode constraints rather than documenting them, trust zones, rollback, and why a role label is not a sandbox.
- [[Canary Testing for Permission Boundaries]] — Deny rules are untested code — run each destructive route unguarded then guarded, and require a structured denial event, because a surviving file proves nothing.
- [[Verification Loops]] — Two distinct failures needing two distinct fixes: a forced verification pass and an external evaluator — three kinds of reflection, asymmetric QA, and when a verifier is worth deleting.
- [[Agent Retry Taxonomy]] — Which failures are retryable and which never are, retry at both call and node level, and feeding the error back as the move that makes a retry a re-plan.
- [[Loop Detection and the Two-Retry Rule]] — The doom loop, per-file edit-count detection that forces re-planning rather than repair, and the reasoning sandwich.
- [[Long-Horizon Execution]] — Coherence decay and context anxiety — state externalization makes the loop re-entrant, plans as first-class artifacts, context reset vs compaction, and Ralph loops.
- [[Harness Orchestration]] — Subagents as a context firewall before they are an architecture — role separation, graph-based orchestration, the four multi-agent failure modes, and when not to go multi-agent.
- [[Harness Maturity and Failure Modes]] — The five-stage maturity ladder, the six-stage per-task pipeline with its Approve gate, and the five ways teams fool themselves.
- [[Production Reliability Primitives]] — Per-step checkpointing, cross-provider model fallback, fail-fast on ambiguity, and confidence-routed quarantine as the shape of HITL at volume.
- [[Iterative Harness Simplification]] — Components encode assumptions about what the model can't do; when models improve those assumptions expire — strip one at a time and re-run the eval.
- [[Agentic Engineering and the New SDLC]] — The vibe-coding-to-agentic-engineering stakes spectrum, per-phase SDLC transformation, the conductor/orchestrator split, the 80% problem, and the CapEx/OpEx case for the harness.

## Loop

- [[Loop Engineering]] — The fourth layer of the stack — designing the cycle that re-prompts, checks, and stops an agent when nobody is watching, replacing yourself as the person who prompts it.
- [[Loop Termination Design]] — Stop rules are layered and independent — success verifier, iteration cap, budget cap, stall detector, escalation path — and the cap is the backstop, never the primary exit.
- [[Loop Autonomy Ladder]] — Four rungs of handoff — tool approval, stop condition, trigger, session — climbed one at a time, each earned with a verifier that has been observed catching a real failure.
- [[Evolve Loop]] — A slow loop pointed at a fast one that rewrites files rather than weights — four edit targets, a 5–10 run cadence, and the anti-busywork rule that makes "no change needed" a first-class success.
- [[Recursive Self-Improvement]] — Level 4 at the frontier — the write boundary is the load-bearing design decision, a 3% hit rate is fine when attempts are cheap, and automating generation shifts the bottleneck onto verification.

## Graph

- [[Graph Engineering]] — The fifth layer of the stack — designing which nodes exist, which transitions are permitted, and how the runtime work graph mutates, so multi-agent work has an organizational structure rather than just more agents.
- [[Graph Topology Primitives]] — Nodes, edges, state, durable execution, and typed edges — the agency budget per node, conditional edges as where control lives, and reducers as the concurrency primitive.
- [[Loop-to-Graph Escalation]] — A loop is a graph with one node and an edge back to itself; escalation is a cost you justify with five specific signals, not a maturity level you graduate to.
- [[Graph Governance and Attribution]] — Once work fans out across nodes, "the graph did it" is not an acceptable audit answer — identity propagation, per-node cost attribution, and approval gates placed where consequence concentrates.
- [[Knowledge Graph Retrieval]] — Vector search finds things that sound like your question; graphs find things that are connected to your answer — but traversal depth compounds error, which makes entity resolution the load-bearing sub-problem.
- [[Knowledge Graph as Shared Agent Memory]] — Loop → swarm → graph as three capacity unlocks: parallel workers rediscover the same findings because nothing connects them, and a typed KG turns fan-out from re-derivation into accumulation.
- [[n8n AI Workflow Builder]] — A shipped supervisor-pattern LangGraph with published operational constants — five specialist subgraphs, prompt-only specialization, per-node iteration bounds, and an agent never allowed to fill its own context with the artifact it is editing.

## RAG

- [[Bedrock KB vs LangGraph Decision]] — Decision framework for Bedrock Knowledge Bases vs. LangGraph CRAG pipeline — quality, observability, cost, and migration path analysis.
- [[Agentic RAG — Advanced Patterns]] — Self-RAG vs CRAG distinction, Adaptive RAG complexity tiers, GraphRAG for relationship traversal, HyDE for lexical gap, Multi-Query RAG-Fusion, agentic latency budgets, A2A protocol mapping to LangGraph, and the production-readiness gate.
- [[RAG Architecture Selection]] — The nine named RAG architectures as one selection space — what each buys and costs, the decision cheat-sheet, and Fusion RAG over heterogeneous sources (distinct from multi-query RAG-Fusion).
- [[Conversation Repository Pattern]] — Two-table PostgreSQL schema for persisting multi-turn conversation state — conversations table for sessions, messages table for turns with JSONB trace and sources columns enabling trace-linked retrieval debugging.
- [[CRAG Retry Logic]] — The confidence-gated conditional back-edge in a CRAG pipeline that re-enters retrieval when the reranker's top score falls below threshold — preventing low-confidence answers from reaching the user.
- [[Embedder Warmup]] — Force-loading the embedding model during application startup (before the first request) to prevent a 3–8s cold-start spike on the first query in production.
- [[GCP Vertex AI Search vs AWS Bedrock KB]] — Head-to-head comparison of GCP Discovery Engine and AWS Bedrock Knowledge Bases as managed RAG backends — covering search semantics, session state, answer ownership, and when to consider switching.
- [[Librarian RAG Architecture]] — The five-agent Librarian pipeline — Plan, Retrieval, Reranker, Generation, and Eval agents wired by a LangGraph StateGraph with CRAG retry loop.
- [[RAG API Design Patterns]] — Three design patterns for exposing a RAG service cleanly — multi-query surface (LLM sends 2-3 query variants), fingerprint-based global deduplication, and typed Pydantic response contract at the HTTP boundary.
- [[RAG Evaluation]] — Three-tier evaluation architecture for RAG pipelines — golden datasets, LLM-as-judge, failure clustering, ragas vs deepeval, and retrieval lift measurement.
- [[RAG Knowledge Preparation]] — The process of transforming human-readable documentation into machine-retrievable knowledge units — chunking, metadata tagging, rewriting for self-containment, and enforcing consistency.
- [[RAG Reranking]] — Reranking strategies for RAG pipelines — cross-encoder vs LLM listwise, confidence scoring, and when each is appropriate.
- [[RAG Retrieval Strategies]] — Comprehensive reference for chunking, embedding, vector store, and hybrid search strategies — component choices, tradeoffs, and swap paths used in the Librarian pipeline.
- [[RL for Retrieval Policies]] — Modelling RAG as a sequential decision process — the five decision points and their reward signals, the three optimization patterns (online RL, per-subtask modules, Self-RAG), and why reward sparsity makes end-to-end RAG RL hard.
- [[Reciprocal Rank Fusion (RRF)]] — Score-free fusion algorithm that combines multiple ranked lists by position — the standard method for merging BM25 and dense vector retrieval results, and for amplifying cross-query agreement in multi-query retrieval.
- [[Semantic Cache for RAG Agents]] — Zero-retrieval-cost path for RAG agents — embed the query, cosine-match against a grader-validated golden seed, and short-circuit the full CRAG pipeline on high-similarity hits.
- [[VA vs HCA Retrieval Evaluation]] — Benchmarking results comparing VA, HCA (Bedrock), and local RAG baselines across 935 Danish support questions — VA outperforms HCA on all dimensions (MRR 0.286 vs 0.248), but 47% corpus ceiling means data-ops fixes dominate model-level improvements.
- [[Vector Database Comparison]] — Side-by-side of vector stores used across RAG pipelines — DuckDB (embedded local), ChromaDB, pgvector, OpenSearch (Bedrock), Pinecone, GCP Discovery Engine — with when-to-use guidance and migration notes.

## LangGraph

- [[Orchestration Architecture Decision]] — Three architecture options for the Librarian service deployment — full Bedrock, full LangGraph, or polyglot — with tradeoffs and the recommended migration path.
- [[Deep Agents Framework]] — Opinionated agent harness built on LangChain/LangGraph — create_deep_agent() wraps planning, file management, subagent delegation, and HITL into configurable middleware with no boilerplate.
- [[Deep Agents Memory Backends]] — Pluggable backend system for Deep Agents file operations and memory — StateBackend (ephemeral), StoreBackend (cross-thread), FilesystemBackend (local disk), and CompositeBackend (routing).
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] — Decision guide for choosing between LangChain, LangGraph, and Deep Agents — layered frameworks where higher layers add planning, memory, and middleware on top of lower ones.
- [[HistoryCondenser]] — LangGraph node that rewrites the latest user query into a self-contained form given prior turns — prevents retrieval degradation on coreference-heavy multi-turn conversations.
- [[LangChain Dependency Management]] — Package structure and version policy for the LangChain ecosystem — langchain/langchain-core/langgraph/langsmith as the required core, provider/tool packages installed a la carte, and the langchain-community non-semver trap.
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]] — LangChain 1.0's core agent-building primitives — the create_agent() loop, the @tool decorator, checkpointer-based persistence, and structured output — the foundation layer beneath LangGraph and Deep Agents.
- [[LangChain Agent Middleware]] — LangChain's create_agent() middleware API — HumanInTheLoopMiddleware for tool-call approval, wrap_tool_call/before_model/after_model hooks for custom logic, and Command-based resume — the mechanism Framework Selection means when it says "LangGraph has no middleware.
- [[LangChain RAG Implementation Patterns]] — LangChain-specific RAG implementation surface — document loaders, RecursiveCharacterTextSplitter, vector store classes (Chroma/FAISS/Pinecone), similarity/MMR search, metadata filtering, and wrapping a retriever as an agent tool; the API layer beneath the conceptual choices in RAG Retrieval Strategies.
- [[LangGraph Advanced Patterns]] — Advanced LangGraph patterns beyond the basics — subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints/interrupts, error handling, and Plan-and-Execute.
- [[LangGraph BaseStore]] — LangGraph's cross-thread persistent key-value store with optional vector search — the standard backend for episodic, semantic, and procedural agent memory.
- [[LangGraph CRAG Pipeline]] — The Corrective RAG pattern implemented as a LangGraph StateGraph — deterministic graph with conditional retry loop, confidence gating, and typed state schema.
- [[LangGraph State Reducers]] — Functions that define how parallel node outputs merge into shared state — preventing collisions when multiple nodes write to the same field simultaneously.
- [[Runtime Topology and Checkpointer Alignment]] — Critical rule — checkpointer backend must match runtime hosting model. MemorySaver fails silently in Lambda and multi-worker deployments. Covers trigger patterns, observability tool choice (LangSmith vs Langfuse/GDPR), and key production signals.
- [[Send API Fan-out]] — LangGraph's Send API enables dynamic map-reduce parallelism — fan out to N workers at runtime without knowing N at graph compile time.
- [[Summarization Node]] — A LangGraph node that compresses conversation history when it exceeds a trigger threshold — keeps context window usage bounded while preserving conversational continuity.

## Google ADK

- [[ADK Context Engineering]] — How the ADK samples repo manages context — SKILL.md pattern, three skill-loading strategies, static vs dynamic instruction, and history compaction.
- [[ADK Deployment Patterns]] — ADK deployment targets (Agent Engine vs Cloud Run vs GKE), CI/CD with WIF, service account architecture, event-driven triggers, and Terraform patterns.
- [[ADK Eval Guide]] — ADK evaluation methodology — the eval-fix loop, 8 built-in criteria, evalset schema, tool trajectory gotchas, multimodal eval, user simulation, and Vertex AI managed pointwise/pairwise eval.
- [[HITL and Interrupt Patterns]] — Six HITL patterns for LangGraph agents — static breakpoints, dynamic interrupt(), clarification loop (budget-bounded), scheduler confirmation gate, tool approval for irreversible actions, and time-travel/replay/fork.
- [[ADK JS TypeScript Patterns]] — Google ADK TypeScript SDK (@google/adk 0.5.0) — LlmAgent, FunctionTool, structured Zod output, streaming NDJSON, and pitfall patterns for Next.js agent integration.
- [[ADK Observability]] — Four-tier observability for ADK agents — Cloud Trace (always-on), prompt-response logging, BigQuery Agent Analytics plugin, and third-party platforms (AgentOps, Phoenix, MLflow, etc.).
- [[ADK Python API Reference]] — Quick reference for the Google ADK Python SDK — agent types, tools, state, callbacks, plugins, artifacts, memory, context caching, and context compaction.
- [[ADK Scaffold Patterns]] — Agent Starter Pack CLI patterns for scaffolding ADK agent projects — templates, deployment options, prototype-first workflow, DESIGN_SPEC.md contract, and development phase guidelines.
- [[ADK User Simulation Eval]] — Dynamic conversation testing in ADK using ConversationScenario and a user simulator LLM — replaces static turn sequences when agent response order is unpredictable.
- [[ADK vs LangGraph Comparison]] — Side-by-side mental model comparison of Google ADK and LangGraph — primitive mappings, weighted scoring (LangGraph 716/845 for AWS/ADK-compatible context), VA team production findings, and the recommended vocabulary alignment approach.
- [[ADK vs LangGraph Decision]] — Decision to keep Librarian on LangGraph — ADK's strengths don't address Librarian's core requirements; vocabulary alignment (Level 1) is the right refactor scope.
- [[ADK Workflow Agents]] — ADK's three deterministic workflow agents — Sequential, Parallel, and Loop — which provide control flow without LLM orchestration.
- [[Multi-Agent Orchestration Patterns]] — Multi-agent architecture patterns — supervisor/handoff/parallel swarm trade-offs, try-agent history for fallback routing, tool count budget, and the [client] ADK POC selection rationale.
- [[Multi-Modal Agent Response]] — Agent response pattern where output can include text, data visualizations, interactive UI components, and full task surfaces — moving beyond chat to structured elicitation and guided execution.
- [[Plan and Execute Pattern]] — Separating planning from execution for multi-step agent tasks — Planner, Executor, Replanner, and Responder nodes with HITL confirmation gate.
- [[SKILL.md Pattern]] — ADK skill declaration format — YAML frontmatter listing tools + natural language instruction body, enabling dynamic skill loading without hardcoding capabilities into the system prompt.
- [[System Design — Serverless Agent Backends]] — Interview-format system design writeup of running agent systems on serverless (Vercel Functions / Next.js API routes) — stateless invocations, session state in Postgres, streaming within platform timeouts, and the designed handoff to a stateful phase 2.
- [[VA Product Design Patterns]] — Product design patterns for embedded VA agents — three interaction levels, structured output as UI contract, page context awareness, escalation triggers, and tool count budget for routing quality.
- [[Voice Agent Patterns]] — Patterns for real-time voice agents — hard latency constraints, BIDI streaming session management, ADK Strategy C preloading, LangGraph flat tool node, and mandatory history pruning.

## Memory

- [[Agent Memory Types]] — Three-tier memory taxonomy (semantic/episodic/procedural) with storage patterns, context window strategies, reflection pattern, and SQLite preference store for VA agents — backed by LangGraph BaseStore.
- [[Memory Architecture for VA Agents]] — Three-tier cognitive memory model (semantic/episodic/procedural), SQLite implementation pattern, context window management strategies, and self-improving reflection pattern for VA agents.
- [[Self-Learning Agents]] — Four-level improvement stack for production agents — inference-time (ReAct, CoT, self-critique), session-time (reflection, procedural memory), operational (learning loop, HITL), and training-time (DPO). Most agents need the first three; DPO is a late-stage investment.
- [[Memory Lifecycle]] — Five stages — represent, store, retrieve, use, update/forget — with the fifth being the one production systems skip, and consolidation designed so a failed merge can roll back instead of losing history.
- [[Memory Decay Weighting]] — Exponential recency decay as a retrieval scorer — Memoria weights memories by e^(-alpha*age), which resolves stale-vs-current facts by ranking rather than by an explicit conflict-resolution step.
- [[Memory-Augmented Conversational RAG]] — Multi-turn retrieval breaks because the query is under-specified — the fixes are query rewriting against history, a when-to-retrieve policy, and asking a clarifying question instead of retrieving on an ambiguous turn.

## MCP

- [[A2A Agent Protocol]] — Google's Agent-to-Agent open specification for inter-agent communication — task lifecycle, agent cards, and how it maps to LangGraph primitives.
- [[Agent Interoperability Protocol Stack]] — The five open protocols standardizing agent integration — MCP, A2A, A2UI, AP2, UCP — partitioned by what sits on the other end of the boundary: data, agent, human, or money.
- [[MCP Protocol]] — Model Context Protocol — how it separates tool definitions from agents, enabling independent deployment and runtime tool discovery; includes AWS Bedrock AgentCore deployment pattern from the Hypernova PoC.
- [[MCP Server Security Patterns]] — Security patterns for MCP servers — read-only invariant, sandbox isolation, secrets handling, and what to never expose over MCP.
- [[Tool Design as Context Engineering]] — Tools consume context twice — definitions sit in the window permanently, results enter per call — so token-efficient results, unambiguous boundaries, and terse routing descriptions are context decisions, not API aesthetics.

## Evaluation

- [[Agentic KPI Trees]] — KPI tree pattern for agentic products — goal completion rate, no-touch rate, and transaction match accuracy as the primary success metrics for VA, document processing, and reconciliation agents.
- [[Anthropic Three-Tier Eval Taxonomy]] — Practical agent evaluation framework from Anthropic — three tiers (unit/trajectory/e2e) mapped to cost, determinism, and failure coverage. Unit covers ~70% of regressions cheaply; trajectory checks routing paths; e2e is sparingly used for quality gates.
- [[Conversational Test Fixture Design]] — How to author a fixture for a pipeline whose input is dialogue — the volunteer's verbatim words as the input unit, the full expected artifact as the oracle, and a short "key validation points" list naming the specific wrong answers the scenario exists to catch.
- [[Copilot Learning Loop]] — The operational process for improving agent systems over time — signal capture from real usage, knowledge refinement workflows, and controlled autonomy expansion. Not automatic: requires deliberate instrumentation and tooling.
- [[Direct Preference Optimization]] — Training-time technique that fine-tunes a model on human preference pairs (preferred vs rejected responses) without a reward model — replaces PPO/RLHF for preference alignment. Not applicable to API-only models.
- [[Eval-Driven Development (EDD)]] — Writing the eval suite before the agent exists — ATDD reconstructed for non-deterministic systems, where first-ness buys honesty rather than design pressure.
- [[RAG Eval Gate Contract]] — Eight-gate ownership contract for RAG evaluation pipelines — each gate answers a distinct question about corpus quality, retrieval, generation, and grader calibration, with strict handoff contracts between gates.
- [[Eval Harness Anatomy]] — The vocabulary of agent evaluation — task, trial, grader, trajectory, outcome — plus the separation that makes it work: the evaluation harness treats the agent harness as the system under test, and capability evals want low pass rates while regression evals want ~100%.
- [[Eval Maturity Ladder]] — Five levels of what eval infrastructure exists — vibes, deterministic gates, separated evaluator, eval sets plus tracing, continuous sampling with drift alerts — where most builders sit at 0 and production demands 3+, with trajectory-over-outcome and cost-per-success as the metrics that expose thrashing.
- [[Eval Non-Determinism]] — Why one trial is an anecdote — pass@k when a single success suffices, pass^k when consistency is the product, and the arithmetic that makes a "75% reliable" agent pass three consecutive trials only 42% of the time.
- [[Eval Suite Maintenance]] — Fix the evaluation system before changing the agent, read traces rather than scores, and treat a saturated suite as a stopped learning signal — paired regression and rolling-discovery sets keep the frontier moving.
- [[Eval Ladder]] — A four-rung progression — manual review, golden-set grading, LLM-judge, user feedback — sequenced so each rung's failures supply the next rung's test cases, with an explicit "most POCs reach rung 2–3 and that's sufficient" stopping point.
- [[Eval vs Test Distinction]] — A test tells you your code is broken; an eval tells you your product got worse — two different instruments with different targets, graders, cadences, and failure semantics.
- [[Experiment Tracking Schemas]] — The metadata contract that makes an eval run reproducible and diffable — base trace fields, ExperimentRun/RagConfig/BedrockConfig/ChunkRecord, the instrumentation asymmetry between a custom pipeline and a managed KB, and the log-only-then-promote policy for grounding checks.
- [[Forecast Grader Thresholds]] — The pass/fail contract for time-series forecast evaluation — MASE against a naïve baseline, SMAPE, directional accuracy, and prediction-interval coverage — with the diagnostic each failure points to and the drift ratio that triggers retraining.
- [[Golden Set Mechanics]] — The shape of a golden case (input/expected/metadata), sizing by purpose (20–50 at spec time, 100–1000 for CI), sourcing priority, and the anti-staleness practices that keep a set measuring.
- [[Grounding Claim Methodology]] — Claims-based grounding — the "yellow highlighter" approach to RAG verification, where the agent extracts verbatim supporting quotes from retrieved documents before writing the final answer, creating a verifiable paper trail.
- [[Heuristic Pipeline Metrics]] — Automated measurement of operational health — latency, error rate, token usage, retrieval recall — that runs alongside every eval rung and is explicitly never sufficient alone, since a fast cheap wrong answer still fails.
- [[HITL Annotation Pipeline]] — Human-in-the-loop annotation workflow for conversation data — two-queue structure (random + edge case), inter-annotator agreement as quality gate, and feedback routing to eval dataset vs failure taxonomy.
- [[Human-Participant Skill Test Protocol]] — Usability-testing a conversational skill with real first-time users — pre-registered facilitator expectations, scripted plus real scenarios, non-intervention rules, and a severity-sorted friction log that feeds fixes back before the next session.
- [[LightGBM vs CatBoost Comparison]] — Methodology for comparing calibrated GBM rerankers head-to-head — fixing train/inference feature-distribution mismatch before comparing, native categorical handling, and Brier score/log-loss as the metrics that matter for calibrated probability scores.
- [[LLM-as-Judge Evaluation]] — A separate LLM scoring outputs against a rubric — the approach for subjective quality where exact matching fails, requiring calibration against human grades and recommended as a complement to golden-set grading rather than a replacement.
- [[LLM Grader Calibration Insights]] — Calibration evidence for LLM-as-judge graders in the project-g eval pipeline — custom v3 grader outperforms DeepEval defaults (+0.214 score delta vs +0.086), domain-shift is the main failure pattern, passage context is required for grounding accuracy. Grounding cross-check vs DeepEval shows near-zero agreement until article text is wired in.
- [[Manual Review as Eval Bootstrap]] — Human eyeballs on 10–20 real queries as the deliberate first eval rung — zero setup, doesn't scale, and valuable precisely because its failure patterns become the criteria every automated approach above it needs.
- [[Observability & Evaluation Glossary]] — Canonical vocabulary for agent observability and evaluation — the observability/tracking/tracing/monitoring/alerting hierarchy, offline vs online evaluation modes, heuristic vs LLM-judge metric types, dataset terminology, and rank-based retrieval metrics (MRR/precision@k/recall@k/ndcg@k/hit@k).
- [[Online Eval Sampling]] — Score 10–20% of production traces by rule rather than at random — negative feedback, high-cost dialogues (cost as a thrashing proxy), fixed time windows as the control group, and a full 48-hour review after any model or prompt change — with human labels calibrating an LLM judge that would otherwise drift.
- [[project-g Eval Architecture]] — Routing vs domain eval distinction (Strand A/E/F), grader interface contract, three-tier eval coverage, calibration methodology for the project-g HC agent eval pipeline, and ADK vs LangGraph parallel evaluation approach.
- [[RAG Eval Metrics Suite]] — Eight-metric RAG evaluation framework covering stakeholder quality (faithfulness, naturalness, completeness, relevance), retrieval quality (contextual relevance, recall, document precision), and system calibration — split between runtime-compatible and offline-only metrics.
- [[Skill Eval Pipeline (Blind Comparison + Grading)]] — Three-agent pipeline for A/B testing Claude Code skills — a blind comparator scores two outputs on a rubric without knowing which skill produced them, a grader checks explicit expectations pass/fail with cited evidence, and a post-hoc analyzer unblinds the result to explain why the winner won and suggest concrete improvements to the loser.
- [[Skill Pipeline Dryrun Testing]] — Regression-testing a chain of conversational skills by simulating a user through fixed scenarios with unambiguous expected outcomes — asserting not only what the pipeline produces but which questions it correctly skips and which it must still ask.
- [[Synthetic Dataset Generation for RAG Eval]] — Four-mode pipeline for generating and maintaining a versioned synthetic test dataset from a knowledge base — article fingerprinting drives incremental refresh, stable content-derived IDs make Langfuse upserts idempotent, and four query categories cover the full quality surface.
- [[System Design — Unified Eval Harness]] — Interview-format system design writeup of playground's eval harness — golden set → heuristic graders → LLM judges → gate, shared across three agent implementations, with HTML reporting and threshold governance.
- [[User Feedback Loops]] — Explicit ratings or implicit usage signals from deployed users — the only eval source that catches "technically correct but unhelpful", slow and sparse and biased, whose real payoff is converting thumbs-down cases into permanent golden-set entries.
- [[VA Eval Harness]] — Agent evaluation harness for VA agents — four eval suites (routing, quality, behavioral, error handling), JSON evalset schema, tool_trajectory_avg_score metric, LLM-as-judge, Makefile flow, and CI regression gate. Production golden dataset: ~100 questions from 700-question Intercom set, Langfuse pipeline live, CS agent validated.

## Infrastructure

- [[Agent Management Layer]] — The six systems a production agent needs beyond the agent itself — evaluation frameworks, fallback/escalation, drift monitoring, HITL checkpoints, audit logging, and a defined handoff protocol — argued as 60% of the deployment, with HITL corrections doubling as the training-data pipeline only if they are logged.
- [[Observability — LangFuse vs LangSmith Decision]] — Decision to use LangFuse first for RAG observability — native ragas/deepeval integrations, self-hostable, GDPR-friendly, and highest weighted score (8.58/10) for [client]'s AWS-hosted, high-compliance context.
- [[Cloud Run + Cloud SQL Pattern]] — Single-container Cloud Run service (FastAPI + SPA) connected to Cloud SQL via the built-in Auth Proxy unix socket — no public IP, no SSL config, private GCP-internal networking by default.
- [[Cloud Service Deployment]] — A long-running 24/7 hosted service — the same container as single-service plus monitoring, health checks, and env management, chosen when the system must be available without anyone starting it.
- [[Deployment Topology Ladder]] — Five deployment topologies (local → single service → cloud service → split service → serverless) ordered by who can access the system, with cost and ops-complexity as the selection axes rather than technical capability.
- [[Input Guardrails Pipeline]] — 7-stage deterministic safety pipeline (normalise → size check → domain classify → injection detect → PII redact → XML envelope → advisory) that runs before every LLM call — LLM-free by design.
- [[Langfuse ADK Tracing Patterns]] — Two-layer Langfuse instrumentation for ADK agents — OpenTelemetry auto-instrumentation plus manual @observe decorators produce a single unified trace tree; session grouping, RAG path tagging, and first-class Scores are the critical operational additions.
- [[Langfuse Platform]] — Langfuse is an open-source LLM engineering platform for tracing, prompt management, and evaluation — chosen by [client]'s AI teams as the observability standard, with SSO and governance pending before production rollout. Instrumentation patterns vary by framework (lf.trace() for ADK, CallbackHandler for LangGraph, @observe for FastAPI).
- [[LangSmith Platform]] — LangSmith mechanics — auto-instrumentation for LangGraph vs manual @traceable wiring for ADK, datasets, evaluator functions as thin adapters over your own graders, annotation queues, and experiment comparison.
- [[Local-Only Deployment]] — The zero-infrastructure rung — the AI runs on a developer's machine with no hosting and no external access, chosen when the only user is the developer and iteration speed matters more than availability.
- [[Observability and Runtime Patterns]] — Observability tool choice (LangSmith vs Langfuse), tracing architecture, runtime topology and checkpointer alignment rules, trigger patterns, and key signals to monitor for VA agents.
- [[PGVector Migration Pattern]] — Migrating a vector store from in-memory NumPy arrays to PostgreSQL + pgvector — preserving the public API, using cosine distance operator, adding an IVFFlat index, and moving embeddings to Cloud SQL without re-embedding.
- [[PII Masking Approaches]] — Regex vs LLM-based vs hybrid PII masking for conversation data pipelines — contextual PII is the hard problem; compliance sign-off is a hard gate before data moves.
- [[Prefix Caching]] — Claude's automatic KV cache reuse for repeated prompt prefixes — cuts latency and cost by 90% for static system prompts and long tool schemas.
- [[Presidio PII Redaction for Langfuse]] — Presidio orchestration layer with spaCy fr_core_news_lg + CamemBERT NER + custom regex recognizers for French financial PII — wired into Langfuse via the SDK mask hook as a single interception point before traces leave the process.
- [[Production Hardening Patterns]] — Checklist of production hardening fixes for the Librarian service — P0/P1/P2 issues, async I/O safety, SQL injection prevention, CORS, and Docker packaging.
- [[Production Readiness Backlog]] — The pre-launch gap checklist for a RAG service going to managed cloud hosting — auth, CORS, structured logging, tests, CI gate, staging separation, probes, retries, migrations — each stated as current-state vs required.
- [[Safeguards Architecture — Five Protection Layers]] — Five-layer runtime safety pipeline for production agents — input guardrails, routing confidence, retrieval quality (CRAG), post-generation grounding check, and escalation routing — each with distinct latency cost and failure mode.
- [[Serverless Deployment]] — Functions that spin up on demand and shut down after execution — an off-ladder alternative chosen on traffic shape (bursty, stateless, sub-30s) rather than audience size, paying cold starts and timeout limits for zero idle cost.
- [[Single Service Deployment]] — One container running the AI backend, reachable by a small internal team — the rung where deployment first exists but auth, frontends, and independent scaling deliberately do not.
- [[Split Service Deployment]] — Separately deployed frontend and backend sharing identity through a common auth provider — the only rung that supports external users and multi-tenancy, at roughly double the operational burden.
- [[Streaming Output Scrubbing]] — Scrubbing secrets from a streamed LLM response in transit via a TransformStream with a carry window — the only seam that preserves streaming while guaranteeing scrubbed bytes are the only bytes the caller sees.
- [[System Design — Shared Code-Index Service]] — Interview-format system design writeup of the DSSG shared indexer — centralized indexer + query API with MCP as a thin read-only client, DuckDB single-writer risk, and the pgvector escape hatch.

## Interview Prep

- [[Agents Interview Study Guide]] — Exam-prep reference for agent architecture questions — workflow vs agent distinction, composable patterns, ACI tool design, harness engineering, long-horizon reliability, and memory taxonomy.
- [[AIE Code-Test Flaw Taxonomy]] — The eleven recurring defects in LLM take-home submissions — context overflow, naive chunking, missing retry/timeout, ungrounded generation, JSON drift, swallowed exceptions — each with its detection cue and the minimal fix that fits inside a one-hour timebox.
- [[Durable vs Performative Knowledge Split]] — One test — "is this true regardless of whether I'm being interviewed?" — sorts study material into durable technical knowledge and interview-performance technique, which decay at different rates and need different revision cadences.
- [[Evals and Observability Interview Study Guide]] — Exam-prep reference for eval and observability questions — vocabulary, grader types, three-tier taxonomy, pass@k vs pass^k, and the tracing-first discipline.
- [[LLM Fundamentals Interview Study Guide]] — Exam-prep reference for LLM theory questions — transformer architecture, training pipeline, adaptation menu, inference economics, and failure modes.
- [[RAG Interview Study Guide]] — Exam-prep reference for RAG architecture questions — component choices, architecture variants, production judgment, measured benchmarks, and terminology traps.
- [[Situation-Indexed Decision Tree]] — Replacing a flat component table (answers indexed by noun) with a branching tree indexed by situation — one memorized trunk fork into four system spines, each node carrying a discriminator question and a rehearsable sentence.
- [[System Design Interview Study Guide]] — Method guide for the ML/LLM/agent system design round — 5-step process, trade-off narration formula, LLM reference architecture, bottleneck table, and failure mode reflexes.
- [[Timebox-Scaled Deliverable Bar]] — Test coverage, file organisation, and observability expectations are a dial set by the assignment window rather than a constant — the one-hour "don't write tests" advice inverts at three hours, and the async ambiguity protocol inverts the live-round clarify-first reflex.

## Meta

- [[AI Engineering Curriculum Structure]] — The two-wave model of the learn-ai-engineering corpus — generative-ai as the application wave (seven pillars) and ai-engineering as the discipline wave (six foundations) — plus the dependency ordering behind the pillar sequence.
- [[Agile Workflow Definitions]] — Definition of Ready, Definition of Done, WIP limits, weekly cadence, and ceremony-to-skill mapping for the Claude Code workflow system.
- [[Claude Code Hook Architecture]] — Claude Code lifecycle hooks — PreToolUse/PostToolUse events, exit-code protocol (0=pass, 2=block), and the hook suite pattern used to enforce code quality automatically without mid-task reminders.
- [[Claude Workflow System]] — Personal Claude Code harness — global skills, PreCompact hook, phase checkpoints, and session notes — that automates context management across multi-phase engineering workflows.
- [[Code Review Drill — SANYI]] — Code-review interview drill using a real SANYI review as the worked example — a two-line diff that lints clean but violates the change contract, and the reviewing method that catches it.
- [[Documentation Boundary — Machine vs Human Docs]] — Who writes what — machine-consumed docs (CLAUDE.md, skills, plans) vs human-consumed docs (READMEs, wiki, design docs), with the akira dao exception.
- [[Karpathy LLM Wiki Pattern]] — The compiler analogy for personal knowledge bases — raw sources in, LLM compiles them into structured interlinked wiki pages, no vector infra needed.
- [[No-Placeholder Plan Discipline]] — A plan handed to an implementing agent carries every file's content in full, and a gap is treated as a defect in the plan rather than license for the agent to invent — with verification steps that check structure, not behavior, when the deliverable is markdown.
- [[Plan-Doc Status Enum]] — Nine-member Status enum for plan docs (7 in-flight, 2 terminal) with a forbid-and-relocate suffix policy — the Status line carries exactly one token, everything else moves to named fields.
- [[Puffin Consciousness Development Skills]] — A chained Claude Code skill family in the `guacamayo` project (renamed from `puffin` 2026-07-17) (genesis → wake → grow → reflect → synthesize → dream) that walks a user and Claude through a staged, multi-session self-development process — grounded in "user seed material" collected from prior conversations.
- [[SANYI Change-Contract System]] — Three-layer change-contract system (变易/简易/不易) for agent architectures — classifies every component into ever-changing, simple, or invariant, then enforces cross-layer discipline via init/review/audit modes.
- [[Session Insights]] — Compiled insights from 42 facet-analyzed Claude Code sessions — friction patterns, recurring themes, skill candidates, and learning outcomes.
- [[Session Knowledge Capture Patterns]] — Patterns for capturing, enriching, and classifying session knowledge — output type taxonomy, pre-compact enrichment, and the session-as-source-of-truth approach.
- [[Skill-Knowledge Information Flow]] — How knowledge flows between the four parallel systems — global skills, ai-project-template, learn-ai-engineering, and the librarian wiki — and the sync contracts between them.

## Projects

- [[Atlas Project]] — Time-series forecasting and customer-segmentation agent system — Planner/Forecaster/Evaluator/Learner loop over ARIMA and Chronos models, an HDBSCAN-with-KMeans-fallback segmentation pipeline, and a Neo4j knowledge graph linking customers to segments and merchants.
- [[Change-Contracts Rollout]] — 2026-07-17 decision record — SANYI promoted to the global skills reservoir, SANYI.md contracts drafted for playground/librarian/atlas, contract checks wired into review skills, template seeds contracts at scaffold time; akira rollout blocked on hardcoded scan paths.
- [[NYC-DSSG Project]] — NYC Data Science for Social Good — platform engineering for a nonprofit serving 600+ nonprofits via 300 volunteers; building knowledge base, project templates, and PM agent.
- [[Librarian Graph Explorer]] — Local React Flow wiki graph explorer — multi-dimensional edge types (wikilink/semantic/tag-shared), UMAP semantic layout, and agent chat with graph highlighting and wikilink write-back. Addresses the gap where Obsidian cannot do multi-edge toggling or embedding-based spatial layout.
- [[Librarian KB — Build Plan]] — Phased build plan for the Librarian KB — Phases 1–5 complete, Phase 6 (connectors) active, Phase 8A+B (React Flow UI) done, Phases 9–15 future.
- [[Librarian Project]] — The Librarian service — a LangGraph CRAG-based RAG pipeline for knowledge retrieval, deployed as a Python FastAPI service with evaluation harness.
- [[Listen-Wiseer Project]] — Spotify recommendation agent with ENOA taste-map personalisation — LangGraph ReAct + Chainlit UI, LightGBM classifiers, DuckDB vss RAG, and three-tier eval harness.
- [[Parallax]] — An evidence-driven PR review system that combines multiple review perspectives into one explainable merge decision — the judging third of the Akira/SANYI/Parallax triad, deliberately optimizing against comment count.
