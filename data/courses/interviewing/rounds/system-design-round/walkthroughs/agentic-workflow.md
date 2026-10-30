---
imported_hash: d81517a80dc4e21f
title: Design a multi-step agentic workflow (e.g. meeting scheduling, code review, or an email campaign)
summary: agentic-workflow-walkthrough · agentic · hard
order: 91
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/agentic-workflow.md
---

# Design a multi-step agentic workflow (e.g. meeting scheduling, code review, or an email campaign)

`agentic-workflow-walkthrough` · agentic · hard

## 1. clarify

**Interviewer:** First question to answer: does this even need an agent? Clarify the task, autonomy, and constraints.

<details><summary>Reference</summary>

The senior signal here is NOT reaching for agents because they're exciting. Clarify
whether the task genuinely needs autonomy. If the steps are predictable, a fixed
WORKFLOW (LLM calls orchestrated through predefined code paths) is more reliable and
cheaper; reserve AGENTS (the model dynamically directs its own steps and tool use) for
OPEN-ENDED problems where you can't predict how many steps are needed. Then clarify:
(1) the goal and what "done" means; (2) which tools/systems it acts on (calendar,
email, repo) and their side effects; (3) which actions are IRREVERSIBLE and need human
approval; (4) permissions — whose authority does the agent act under; (5) latency and
cost budget, since agents are token-hungry; (6) failure tolerance. State assumptions
and confirm. [anthropic-agents, igotanoffer]

</details>

## 2. high-level

**Interviewer:** Sketch the architecture. Which agent topology, and where does the control flow live?

<details><summary>Reference</summary>

Use an ORCHESTRATOR-WORKERS topology: a lead/orchestrator agent decomposes the goal,
delegates sub-tasks to specialized worker agents (each with a focused role prompt and
a curated tool set), and synthesizes their results — the subtasks are decided at
runtime, not hard-coded, which is the point of agents. Crucially, the CONTROL FLOW
(looping, sequencing, when to stop, when to escalate) lives in the ORCHESTRATOR CODE,
not buried inside prompts. Around the agents: a tool layer (function calling) with
per-tool auth, a shared memory/state store for the run, guardrails, human-in-the-loop
checkpoints before writes, and tracing/observability. Start as SIMPLE as possible and
add agents only when it demonstrably helps. [anthropic-agents, anthropic-multi-agent, igotanoffer]

</details>

## 3. deep-dive

**Interviewer:** Planning & orchestration: how does the agent decompose the task and decide the next step?

<details><summary>Reference</summary>

The orchestrator plans: break the goal into sub-tasks (e.g. 'find common free slots' ->
'propose times' -> 'send invite'), then loop — observe state, pick the next action or
tool, act, observe the result, repeat (a plan-and-execute / ReAct-style loop) until
done or a stop condition. Grade decomposition quality: interviewers explicitly look
for clear sub-task breakdown and logical flow between steps. Bound the loop with an
explicit STEP LIMIT and budget so it can't spin forever. Where sub-tasks are
independent (e.g. checking several calendars, researching several sources), run
workers in PARALLEL — Anthropic's multi-agent research cut time up to 90% that way.
Keep run STATE durable so a long run can resume after a failure. [promptlayer, anthropic-multi-agent, anthropic-agents]

</details>

## 4. deep-dive

**Interviewer:** Tools & permissions: how do agents act on the world safely?

<details><summary>Reference</summary>

Tools (function calling) are the agent's hands, and they need as much prompt-
engineering care as the main prompt — clear names, schemas, and descriptions. Apply
LEAST PRIVILEGE: each agent gets only the specific tools/endpoints it needs (Doctolib's
data-retriever agent could call only a curated allow-list). Agents INHERIT the
requesting user's permissions and act under the user's authority, never with broader
access — enforce this at the service boundary, not in the prompt. Reads can be
autonomous; anything that WRITES or is irreversible (send the email, book the meeting,
merge the PR) goes through a human-in-the-loop confirmation. In Doctolib's design the
LLM never directly executes the sensitive action — a deterministic node re-fetches
fresh data and the final change stays in the user's hands. [doctolib, anthropic-agents, igotanoffer]

</details>

## 5. deep-dive

**Interviewer:** Reliability: how do you handle errors, retries, and keep a long run consistent?

<details><summary>Reference</summary>

Agents run long and call many tools, so failures are normal, not exceptional. Handle
them: retries with backoff on transient tool errors, RECONCILIATION for partial
progress (if the invite was sent but the calendar write failed, detect and repair
rather than double-book), idempotency keys on side-effecting calls, and timeouts /
circuit breakers per tool. Keep durable run state so you can resume after a crash
instead of restarting. Add a deterministic FACT-CHECK / validation step before acting
on model output. Interviewers specifically reward showing error handling and edge
cases, and IGotAnOffer lists retries, reconciliation, and failure recovery as expected
topics. [anthropic-multi-agent, doctolib, promptlayer, igotanoffer]

</details>

## 6. deep-dive

**Interviewer:** Evaluation & observability: how do you know the agent actually works?

<details><summary>Reference</summary>

You can't ship an agent you can't see. Add FULL TRACING of every step: the plan, each
tool call and result, and the decision path — Anthropic emphasizes production tracing
to understand agent decision patterns. Evaluate TASK COMPLETION, not just per-response
quality: Doctolib scores an "achievement" level (did it accomplish the goal), plus
end-to-end latency and NUMBER OF STEPS (a proxy for efficiency/looping). Build a suite
of representative tasks and run them as regression evals. Add online signals (success
rate, human-override rate, escalations). Meaningful evaluation metrics are an explicit
interview grading criterion. [anthropic-multi-agent, doctolib, promptlayer]

</details>

## 7. tradeoffs

**Interviewer:** What's the cost/latency reality of agents, and how do you keep it bounded?

<details><summary>Reference</summary>

Agents are EXPENSIVE and SLOW. Anthropic found agents use ~4x the tokens of chat and
multi-agent systems ~15x, and token usage alone explains ~80% of performance variance
— so more capability literally means more tokens. Multi-agent is only worth it for
high-value tasks with heavy parallelization, context that exceeds one window, or many
complex tools; it's a poor fit for tightly coupled tasks that must share context (like
most coding edits). Bound cost/latency with step/budget caps, parallelizing
independent work, routing easy sub-tasks to cheaper models, caching, and — again —
preferring a fixed workflow when the task doesn't truly need autonomy. [anthropic-multi-agent, anthropic-agents]

</details>

## 8. tradeoffs

**Interviewer:** What breaks, how do you detect it, and how does the system fail safe?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) Infinite loops / no progress: detect via step
count and repeated states; cap steps and escalate to a human. (2) Wrong or harmful
action: prevent with least-privilege tools + human approval on writes; detect via the
override/rollback rate. (3) Prompt injection through tool outputs (a malicious calendar
entry or email steering the agent): sanitize/verify tool inputs, keep control flow in
code, scope permissions. (4) Cost/latency blowup: monitor tokens and step count per
run; cap budgets, downshift models. (5) Partial-failure inconsistency: reconciliation
plus idempotency. Fail SAFE — when uncertain, stop and ask a human rather than act. Close
with the biggest risks (safety of write actions, cost) and what you'd harden first.
[igotanoffer, anthropic-agents, doctolib]

</details>

## Sources

- [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [PromptLayer — The Agentic System Design Interview](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- [Doctolib — Building an Agentic AI System for Healthcare Support](https://medium.com/doctolib/building-an-agentic-ai-system-for-healthcare-support-a-journey-into-practical-ai-implementation-0afd28d716e6)
- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
