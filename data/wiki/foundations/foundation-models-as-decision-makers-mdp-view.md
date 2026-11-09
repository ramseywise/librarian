---
title: Foundation Models as Decision Makers (MDP View)
tags: [foundations, agents, concept]
summary: "A 2023 survey frames dialogue, prompting and tool use by a foundation model as sequential decision problems in a Markov decision process, with the model as policy and tools, humans or the world as environment; it reports no experiments, only framing and cited numbers."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-yang-2023-foundation-models-decision-making.md
---

# Foundation Models as Decision Makers (MDP View)

A survey and position paper from March 2023. Its organising idea is that actions produced by a foundation model and feedback from an external entity (a human, a tool, a simulated or physical world) recur in a loop, and that this loop is a Markov decision process with states, actions, rewards, a transition function, an initial distribution and a discount. It treats the fully observable case; partial observability appears only in a footnote.

## How the three language-model settings map

- **Dialogue.** The conversation so far is the state, the reply is the action, and the person talking is the environment. RLHF is presented as three stages: tune on dialogue data, fit a preference model to human rankings, then tune the policy against that model with a policy gradient.
- **Prompting.** The prompt provider acts as the agent and the language model as the environment, with reward 1 when the output reaches the goal answer and 0 otherwise. Prompting schemes can be read as coarse actions (for instance decomposing, ranking, denoising, paraphrasing, summarizing, pruning and searching) that nest inside one another, and with external memory a model could be programmed through prompts like a computer.
- **Tool use.** Calling an API is framed as a sequential decision, much as dialogue is, with the API's replies acting as feedback. Beyond dialogue the agent also decides when to call a tool, which one, and how to reformulate a query when the result is unhelpful. The survey notes that supervised finetuning needs heavy annotation of API calls, that prompting needs hand-written prompts per tool and is format-sensitive, and that a rule-based parser is usually needed.

## Arguments the survey makes

- The survey argues that signals from tools are a cheaper and steadier remedy for out-of-date facts, hallucination and weak arithmetic than gathering human feedback on each of those.
- Seeing browsers and search engines as environments an agent can act in opens web navigation and retrieval to reinforcement learning and search, and grounding in environment feedback is said to avoid the Dichotomy of Control problem.
- Agents can reach search engines, databases and compilers cheaply online, and the authors call for infrastructure in which software tools are environments, remote procedure calls are interactions and foundation models are policies.
- Without RL finetuning, good behaviour can also be drawn out through chain-of-thought steps and by modelling sequences of improvement; corrective re-prompting feeds error information from the environment back as context.
- Decision making calls for long context and outside memory, yet a transformer's context is limited.

Numbers in the survey are all cited from other work: a generalist agent trained on over 40 Atari games, one on over 700 real-world robot tasks, one on over 600 tasks of varying modality, and a from-scratch Atari agent needing 7 GPU days for one game.

## Limits

- The survey runs no experiments, so nothing is measured; each figure is borrowed from other papers.
- Dated March 2023: it predates function calling as common practice, standard agent frameworks and long-context models. Its claim that no earlier work has a tool-using agent improve from tool feedback reflects that date. It does not define an agent as a model plus context plus tools.
- The extraction notes that most of the paper (the sections on reinforcement learning, imitation learning, robotics and the equations) is not about LLM agent engineering, and that the authors concede gaps in data, environment diversity, context length, physical grounding and the lag of text-based agents behind task-specific game solvers.

## See Also
- [[Reinforcement Learning Foundations]] — prerequisite-for
- [[Agent Fundamentals]] — prerequisite-for
- [[ReAct Pattern]] — related (tool calls as actions with observations as feedback)
- [[Post-Training for Agents]] — related
