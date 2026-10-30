---
title: System Design Interview Study Guide
tags: [interview, reference]
summary: Method guide for the ML/LLM/agent system design round — 5-step process, trade-off narration formula, LLM reference architecture, bottleneck table, and failure mode reflexes.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--00-overview.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--03-ml-system-design.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--03-ml-system-design.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--05-ai-product-design.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--05-ai-product-design.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--06-component-cheatsheet.md
  - data/raw/repos/sisyphus/interviewing--guides--9-system-design--06-component-cheatsheet.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--case-interview.md
  - data/raw/repos/sisyphus/interviewing--notes--case-interview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--system-design.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--study-guide.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--study-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--questions.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--questions.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--sources.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--sources.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--README.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--support-agent.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--support-agent.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--forecasting-agent.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--forecasting-agent.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--meeting-processor.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--meeting-processor.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--accounting-assistant.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--accounting-assistant.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--rag-system.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--rag-system.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--agent-system.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--agent-system.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--eval-harness.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--eval-harness.md
  - data/raw/repos/learn-ai-engineering/interviewing--rounds--system-design-round--examples--scaling.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--examples--scaling.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--interviewer-personas.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--README.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--template.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--rag-10m.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--agentic-workflow.md
  - data/raw/repos/sisyphus/interviewing--rounds--system-design-round--walkthroughs--cost-optimization-1m.md
---

# System Design Interview Study Guide

The highest-weight technical round in 2026 AIE/MLE loops. This guide covers the method; domain content lives in [[RAG Interview Study Guide]], [[Agents Interview Study Guide]], and [[Evals and Observability Interview Study Guide]]. That boundary is itself a rule — see [[Durable vs Performative Knowledge Split]].

Between the 5-step process below (abstract) and those domain guides (deep) sits a third layer indexed by situation rather than by component: [[Situation-Indexed Decision Tree]].

Step 1 below — clarify before designing — is a *live-round* rule. It inverts on an async take-home, where the graded behaviour is to state your interpretation and proceed; that round has its own defect list ([[AIE Code-Test Flaw Taxonomy]]) and its own scaling rule ([[Timebox-Scaled Deliverable Bar]]).

## The 5-Step Process (45–55 min, ~8 min/step)

1. **Clarify & scope** — never design against the raw prompt.
   - "Who are the primary users, and what's the top priority — latency, accuracy, cost, safety? That drives every trade-off downstream."
   - "Does the system touch personal/financial data — must it stay on-prem or can we call third-party model APIs?"

2. **Requirements split** — functional (multi-turn? autocomplete vs summarization?) vs non-functional (latency, consistency, scale, security). Write the non-functionals down — they're the trade-off axes.

3. **Design** — components, data flow, APIs; connect every choice back to a requirement, out loud.

4. **Identify shortcomings** — name your design's weaknesses before the interviewer does; propose what you'd do differently under different constraints.

5. **Iterate** — curveballs are deliberate adaptability tests.

The round-day version of the guide replaces step 5 with **close with measurement**
(~5 min): never stop at the diagram. State success metrics with numbers ("p95 under 2s
while holding faithfulness above 0.9") plus a future-improvements list (a distilled model
for the easy 80% of traffic, token-cost dashboards, thumbs-down feedback into the eval set),
and one cost line. Common curveball variants: "now 1M users" (separate what changes, such as
caching, sharding and async, from what doesn't), "half the budget" (degrade deliberately
and name the quality you trade), "what breaks first?", and "how do you know it works?"
(evals and monitoring, stated unprompted). The in-room behaviours graded inside these
steps are in [[System Design Scored Behaviors]].

**Pick the spine during clarification.** Say out loud which kind of system this is. It
looks things up (RAG), takes multi-step actions (agent), predicts or ranks (ML), or
transforms an event stream (pipeline). Most prompts are one spine plus a cameo from another:
a support chatbot is the agent spine with RAG for policy lookup.

## Trade-Off Narration Formula

**Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick.**

("I'd compromise X for optimal Y — here's why that hurts least given the priority.")

Trade-offs live between non-functionals: latency↔accuracy, cost↔quality, consistency↔availability, full-automation↔safety, read↔write throughput, storage↔caching.

If told your trade-off was wrong: adapt visibly ("with that requirement, option B's consistency guarantee wins"). No points for stubbornness.

If you hit a knowledge gap: "my understanding there is superficial" — buys credibility and redirects time to areas you're strong in.

## LLM-System Reference Architecture

```
Client
  → API gateway (authn, rate limits, quotas)
  → orchestration (workflow/agent graph)
  → {retrieval: query rewrite → hybrid search → rerank}
  + {generation: prompt assembly → streaming LLM with fallback chain}
  → output validation/guardrails
  → response

Sidecars: caches (prefix + semantic), state store (session/checkpointer),
          trace/observability, eval pipeline, HITL queue
```

For each box: know its failure mode and its scaling story.

## Bottleneck Table

The five bottlenecks, their causes, and mitigations are durable infrastructure knowledge —
they live in [[LLM System Bottleneck Table]]. Know the table cold; the exam cue is that
naming the *cause* is what makes the mitigation follow, rather than reciting a list.

Cost questions attached to this round ("why is this expensive, how would you cut it?")
resolve to the prefill/decode split in [[LLM Inference Economics]].

## Three-Layer Walkthrough

A component cheat sheet frames the round as *software system design with LLM-specific
components*: the LLM is one service. Walk three layers — **application** (gateway, auth, rate
limits on requests/tokens/cost per day, orchestrator, business logic), **AI** (models, RAG,
memory, tools, planning, evaluation), **infrastructure** (inference, queues, caches, databases,
vector store, monitoring, autoscaling) — and never start the diagram at the LLM. Three
reminders from it that recur in answers: **memory ≠ RAG** (retrieval answers "what is
relevant?", memory answers "what should this agent remember?"), store each memory kind by its
access pattern rather than in one database, and the application validates every tool call
before executing it. The generic substrate under the infrastructure layer is
[[Backend Scaling Fundamentals]]; the interface step is [[API Design Fundamentals]].

## Round Variants

- **ML-flavoured round** — the biggest mistake is opening with a model ("I'd use XGBoost").
  Order: business problem → requirements → scope the ML task (inputs, outputs, objective) →
  data (source, labels, freshness, privacy, bias) → approach → evaluation → deployment →
  monitoring. For GenAI the approach fork is base model vs fine-tune vs RAG; RAG is usually
  preferred because it changes the *context*, not the model, so knowledge stays current
  without retraining. Fine-tune only when the model's behaviour itself must change.
- **AI-product round** — the layer above the architecture. Chain every solution as **pain →
  capability → model behaviour → guardrail → UI**, never pain → feature. Separate mission (why)
  from goals (what); segment users on capability, need, risk, and frequency before picking one;
  choose 1–3 metrics tied to goals across business, quality, and healthy-behaviour families
  rather than optimising engagement alone; name a mitigation for every AI-specific risk
  (over-engagement, emotional dependency, false authority, injection). Consistency is chosen per
  domain: strong for money, bids, inventory, bookings; eventual for feeds, search, analytics.
  See [[Product and Delivery Interview Study Guide]].

## Failure Mode Reflexes

In the closing phase, give each failure mode as a triple: the failure, the **signal that detects it** (index-update lag, truncation rate, reviewer override rate, queue depth), and the **degradation path** (abstain, smaller model, shorter context, defer to async review). Naming a failure without its detection signal is the common miss ([[AI System Design Walkthroughs]]).

- Prompt crashes model → detect known patterns
- Irrelevant retrieval → thresholds, metadata filters
- Mid-stream failure → graceful fallback to full response
- Hallucination → grounding scores, double-pass validation

## Worked Examples: the Lesson Each Teaches

Rehearse systems you have actually built, because they beat memorized generic designs. For the canonical public prompts (RAG at 10M documents, chat at scale, coding copilot, moderation, fraud), see [[AI System Design Walkthroughs]]. To run any of them as a scored mock round, see [[AI System Design Interviewer Rubric]].
Each walkthrough follows the five steps against a 40-minute timer. What each one is meant
to teach:

| Prompt | The transferable call |
|---|---|
| Help-centre support agent with citations | Enforce citations structurally instead of detecting hallucinations afterwards. Make escalation a typed output field, not a fallback string ([[Safeguards Architecture — Five Protection Layers]]) |
| Regulated-domain assistant (tax/accounting) | Split knowledge by retrieval type. Prose how-tos go to hybrid RAG. Exact rates and rules go to deterministic structured or graph lookup, because embedding similarity can't guarantee "25%". Use one agent with intent routing, not one agent per layer, so cross-layer questions still work |
| Self-learning forecasting system | Classical models forecast, and the LLM only routes, explains and runs a planner→forecaster→evaluator→learner loop that writes lessons back into the planner's context. Update the knowledge graph in the same transaction as training, or explanations go stale |
| Meeting-intelligence lifecycle agent | The agent is the *sole writer* of the lifecycle stage, using its own attributable credential. Transitions need a confidence threshold *and* a matching extracted-fact type, otherwise they go to human review. Keep the fact-type enum small, since every type needs its own precision/recall grading. Build tenancy in from migration one |
| Code-review agent | One agent with structured passes, not several agents. Risk-tier files for context budget. Fast model triages and escalates low-confidence findings to a larger one |
| Document-QA under data residency | RAG over fine-tuning when the corpus changes and citations are required. Fine-tune only for style |
| Eval pipeline | Start the gate strict and tune toward under 10% false alarms. A gate that cries wolf gets bypassed. 100 curated cases reviewed quarterly beat 1000 stale ones |
| Scale RAG 100× | Scale per component. Stay on pgvector + HNSW until p95 breaches the SLA. Prefix cache plus semantic cache, invalidated on corpus update |

## See Also
- [[LLM System Bottleneck Table]] — prerequisite-for (the durable table this round examines)
- [[LLM Inference Economics]] — prerequisite-for (the cost mechanism under the trade-off questions)
- [[RAG Interview Study Guide]] — extends
- [[Agents Interview Study Guide]] — extends
- [[System Design — Shared Code-Index Service]] — instance-of
- [[System Design — Serverless Agent Backends]] — instance-of
- [[System Design — Unified Eval Harness]] — instance-of
- [[Block Attribute Inversion]] — instance-of (this rubric relocated into per-component metadata)
- [[Situation-Indexed Decision Tree]] — extends (situation index over the §3 component table)
- [[Durable vs Performative Knowledge Split]] — prerequisite-for (why method and domain live apart)
- [[AIE Code-Test Flaw Taxonomy]] — alternative-to (the shipping round vs. the design round)
- [[Timebox-Scaled Deliverable Bar]] — complements (async ambiguity protocol inverts step 1)
- [[AI-Assisted Take-Home Playbook]] — alternative-to (the take-home build-and-present counterpart to the live round)
- [[AI Role Interview Loop Map]] — prerequisite-for (where this round sits in each role's loop, and when it is not the top round)
- [[Backend Scaling Fundamentals]] — prerequisite-for (the generic substrate the round assumes)
- [[API Design Fundamentals]] — prerequisite-for (the five-minute API step)
- [[Product and Delivery Interview Study Guide]] — extends (the AI-product variant)
- [[Context Engineering and Cost Interview Study Guide]] — extends (cost/latency trade-offs)
- [[Security and Safety Interview Study Guide]] — extends (governance layers in regulated designs)
- [[Data Engineering and MLOps Interview Study Guide]] — extends (pipeline spine substrate)
- [[ML Foundations Interview Study Guide]] — extends (ML spine metrics and framing)
- [[System Design Scored Behaviors]] — extends (the in-room behaviours graded inside the five steps)
- [[Technical Breadth Round Playbook]] — alternative-to (the verbal breadth round)
- [[AI System Design Interviewer Rubric]] — extends (the grader-side rubric and personas for mock rounds)
- [[AI System Design Walkthroughs]] — extends (nine public prompts on the same board layout)
