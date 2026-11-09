---
title: "Agentic vs Agentive: Agent Model Position"
tags: [foundations, concept]
summary: "A position paper separates agentic systems, whose competence sits in scaffolding and harnesses, from agentive ones that carry goals, identity and self-regulation inside the model, and proposes a Goal-Identity-Configurator architecture; it has no experiments, only theorems under stated assumptions."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xing-2026-critique-agent-model.md
---

# Agentic vs Agentive: Agent Model Position

This 2026 position and theory paper (no experiments, no tables, no benchmark numbers) defines an agent model as a policy that maps the current state to an action given goals and identity, kept distinct from a world model, which is the learned dynamics of the environment. Its central distinction is between agentic systems, whose competence resides in workflows and harnesses, and agentive ones, whose competence is internalised. The authors call current LLM agents agentic and say much of their behaviour is closer to a software pipeline than to an autonomous agent.

## The argument

- **Five axes of agency**: goals, identity, decision-making, self-regulation and learning, each running from set by someone outside to maintained by the agent itself. A sixth, coordination, treats most multi-agent systems as one scaffolded system, not a society.
- **Critique of harness practice.** Identity is typically a hand-written system prompt listing role, tools and constraints. The authors name MCP, Agent Skills and harness engineering as the criticised practice, while granting that good interfaces are valuable.
- **Chain-of-thought is not planning.** The paper holds that reasoning tokens give a story that sounds plausible and no grounded dynamics, so extra tokens can just add confident guesses. The claim rests on argument and cited work, not a new experiment.
- **Theorems.** Four standard-bound results: planning with an accurate world model can be added to any baseline without loss (Theorem 2); an always-on lookahead horizon grows with the precision required (Theorem 3, though only logarithmically, so the extraction calls the paper's "unsustainable" label rhetoric); fast identity updates beat slow-only learning if they are better than random (Theorem 1, whose assumption, the extraction notes, largely restates its conclusion); mixing simulated and real experience is bounded by world-model error (Theorem 4).
- **Proposal.** GIC combines a belief encoder, goal decomposer, identity evolver, a configurator that picks the mode, a simulative planner, an actor, a critic, plus a world model trained apart from the rest, evaluated by performance, efficiency and growth. It is not implemented here.

## Limits

- No empirical support; evidence is deferred to the authors' own companion manuscripts, which the extraction did not read, so no performance number should be cited from this paper.
- Agentive has no operational test. The theorems presuppose a world model whose error bound is known, and the extraction notes that nobody shows that attainable in open domains.
- The authors promote their own world-model line and criticise rival approaches. The claim that harm falls to goal misspecification in a well-trained modular system is, the extraction notes, an unsupported assertion, and the paper concedes it offers no definitive answers.
- It gives no standard model-loop-tools-memory definition of an agent; read it as a counter-definition.

## See Also
- [[Agent Fundamentals]] — prerequisite-for
- [[Harness Engineering]] — related (the practice the paper critiques)
- [[World Knowledge Model for Agent Planning]] — related
