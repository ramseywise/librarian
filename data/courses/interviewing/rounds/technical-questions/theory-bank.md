---
imported_hash: e14753ef3fee2f6e
title: Theory bank
summary: 38 AI-engineering theory questions reported in real loops, grouped by topic.
order: 107
kind: reading
section: Technical questions
source: sisyphus/interviewing/rounds/technical-questions/theory-bank.md
---

# Theory bank

38 AI-engineering theory questions reported in real loops, grouped by topic. Ask yourself
the question, answer out loud, *then* open the reference. Follow-ups are what the interviewer
pushes on next; exercises are small builds that make the answer stick.

Source: [ai-engineering-gym](https://github.com/alexeygrigorev/ai-engineering-gym) `content/theory/`, converted 2026-10-29. Answers are
general technical knowledge with the gym's citations kept — not claims about you.

## agents

### How would you build an agent that reviews code and suggests improvements?

`agents-code-review-agent` · medium

<details><summary>Hints</summary>

- What should you feed the reviewer: the whole repository, or just the change?
- Which checks are better done by deterministic tools than by the LLM?
- How do you keep the review useful instead of a wall of nitpicks?

</details>

<details><summary>Reference answer</summary>

Trigger on a pull request and give the agent the diff plus enough context (the changed files, related tests, and the team's style/guidelines) so it reviews the change, not the whole repo. Combine deterministic tools with LLM reasoning: run cheap static analysis, linters, SAST, and the test suite first to catch obvious issues, cut cost, and reduce false positives, then have the LLM reason about correctness, security, performance, and readability. Optionally split into focused checks/sub-agents (bugs, security, style, perf). Post a structured PR summary plus line-level comments, each grounded in the code and citing the rule or reason, and suppress nitpicks. Keep a human as the approver, integrate it as a CI step, and evaluate it on comment precision (useful vs. noisy) and false-positive rate.

Key points:

- Trigger on the PR/diff and scope context to changed files + tests + guidelines: review the diff, not the whole repo
- Hybrid: run linters/static analysis/SAST/tests first (cheap, deterministic), then LLM reasoning over what's left
- Cover multiple aspects (correctness/bugs, security, performance, style) optionally via focused sub-agents
- Output a structured summary + line-level comments grounded in the code and citing the rule/why, and avoid nitpicks
- Human stays the approver, ship as a CI step, and evaluate on comment precision and false-positive rate

</details>

**Follow-ups**

- How do you keep the false-positive/nitpick rate low?
- Where does static analysis end and LLM reasoning begin?
- How would you evaluate the reviewer's usefulness over time?
- Should the agent ever block a merge, or only comment?

**Check yourself**

1. What context should the code-review agent primarily work from?
   - a) The PR diff plus related files, tests, and style guidelines
   - b) The entire repository history on every run
   - c) Only the commit message
   - d) A random sample of files in the repo

   <details><summary>Answer</summary>a — Scoping to the diff and directly relevant context keeps the review focused, cheaper, and more accurate.</details>

2. Why run linters and static analysis before the LLM step?
   - a) They cheaply and deterministically catch obvious issues, cutting cost and false positives
   - b) They replace the need for any LLM reasoning
   - c) They increase the model's temperature
   - d) They make the diff larger

   <details><summary>Answer</summary>a — A hybrid pipeline lets deterministic tools handle what they do best, so the LLM focuses on higher-level reasoning at lower cost.</details>

**Exercises**

- Order the code-review agent workflow
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [PromptLayer — The Agentic System Design Interview](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- [Sourcegraph — 13 Best Automated Code Review Tools in 2026 (AI and Static Analysis Compared)](https://sourcegraph.com/blog/automated-code-review-tools)
- [Anthropic — Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)

</details>

### What are the essential components of an agent beyond an LLM?

`agents-essential-components` · easy

<details><summary>Hints</summary>

- Think about what a person needs to finish a multi-step task, not just to answer a question.
- Group the pieces into planning, memory, and tools, then ask what runs the loop.
- Recall Lilian Weng's 'brain + planning + memory + tool use' and OpenAI's 'instructions + tools + guardrails'.

</details>

<details><summary>Reference answer</summary>

The LLM is only the "brain." Around it, a working agent needs planning (decompose the goal into subtasks and reflect/self-correct) and memory (short-term context/scratchpad plus long-term storage, often a vector store, to keep state across steps). It also needs tools (APIs, code execution, retrieval) that let it act on and sense the world. Gluing them together is an orchestration loop that runs the perceive→act→observe cycle, plus guardrails and stop conditions that keep it bounded and safe. OpenAI frames the same triad as instructions, tools, and guardrails.

Key points:

- LLM as the reasoning core / 'brain', necessary but not sufficient on its own
- Planning: decompose the goal into subtasks, plus reflection and self-critique to correct course
- Memory: short-term (context window / scratchpad) plus long-term (external store, often vectors) for state across steps
- Tools: APIs, code execution, retrieval (how the agent acts on and senses the environment)
- Orchestration loop + guardrails/stop conditions to run the cycle, keeping it safe and bounded

</details>

**Follow-ups**

- What's the difference between short-term and long-term memory in an agent?
- Why is reflection/self-critique part of planning?
- Which component most often causes agent failures?
- How do guardrails fit into this picture?

**Check yourself**

1. In Lilian Weng's framing, which three components surround the LLM 'brain'?
   - a) Planning, memory, and tool use
   - b) Fine-tuning, quantization, and distillation
   - c) Embeddings, chunking, and reranking
   - d) Prompt, temperature, and top-p

   <details><summary>Answer</summary>a — Weng describes an agent as an LLM brain plus planning, memory, and tool use.</details>

2. Why isn't an LLM alone enough to be an agent?
   - a) It can reason but can't retain state across steps or act on the world without memory and tools
   - b) It is too small to hold instructions
   - c) It cannot generate text without retrieval
   - d) It always needs to be fine-tuned first

   <details><summary>Answer</summary>a — The LLM supplies reasoning; memory holds state across steps and tools let it take actions — those are what make it agentic.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} lets the agent retain state across steps; {1} let it act on and sense the world.', 'blanks': ['Memory', 'Tools'], 'chips': ['Memory', 'Tools', 'Temperature', 'Embeddings']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Lilian Weng — LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [Chip Huyen — Agents](https://huyenchip.com/2025/01/07/agents.html)
- [OpenAI — A Practical Guide to Building Agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

</details>

### How do you explain agentic systems to non-technical stakeholders?

`agents-explain-to-stakeholders` · easy

<details><summary>Hints</summary>

- Use an everyday analogy rather than architecture terms.
- Contrast 'answers questions' with 'takes actions to finish a job'.
- Anticipate the control/safety question by mentioning guardrails and human approval.

</details>

<details><summary>Reference answer</summary>

Use the "digital coworker" analogy: you give the agent a goal, it figures out the steps on its own, uses the same apps and systems a person would (its tools), and reports back. A chatbot, by contrast, only answers questions. Draw the autonomy-vs-automation line: automation follows a fixed script, an agent chooses what to do within guardrails. Then reassure on control: guardrails on what it may touch, human-in-the-loop approval for high-stakes actions (sending money, emails, deleting records), and oversight (who the agents are, what they can connect to, and what they're allowed to do). Anchor it to one concrete business outcome and its ROI, not jargon.

Key points:

- Analogy: an agent is like a digital coworker (give it a goal, it plans, uses tools, and reports back)
- Contrast with a chatbot: a chatbot answers questions, while an agent takes actions in your systems to finish a task
- Autonomy vs. automation: automation follows a fixed script, an agent decides what to do within limits
- Reassure on control: guardrails, human-in-the-loop approval for high-stakes actions, logging and oversight
- Ground it in a concrete use case and business outcome/ROI, avoiding jargon

</details>

**Follow-ups**

- How would you explain the risk of autonomy without scaring them off?
- How do you set expectations about reliability and human oversight?
- What one-sentence definition would you give a CFO?
- How do you tie an agent to measurable ROI?

**Check yourself**

1. What is the clearest one-line contrast to give a non-technical audience?
   - a) A chatbot answers questions; an agent takes actions in your systems to complete a task
   - b) An agent uses a transformer and a chatbot does not
   - c) An agent has a larger context window
   - d) An agent is fine-tuned and a chatbot is not

   <details><summary>Answer</summary>a — The action-taking distinction lands without jargon; architecture details don't help a non-technical stakeholder.</details>

2. Which point best reassures stakeholders worried about control?
   - a) Guardrails plus human-in-the-loop approval for high-stakes actions
   - b) The model has billions of parameters
   - c) It runs in the cloud
   - d) It uses vector search

   <details><summary>Answer</summary>a — Guardrails and human approval for high-stakes actions directly address the control/safety concern.</details>

**Exercises**

- {'kind': 'fill', 'template': 'Automation follows a fixed {0}; an agent decides what to do within {1}.', 'blanks': ['script', 'guardrails'], 'chips': ['script', 'guardrails', 'embeddings', 'prompts']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [MIT Sloan — Agentic AI, explained](https://mitsloan.mit.edu/ideas-made-to-matter/agentic-ai-explained)
- [Knight First Amendment Institute — Levels of Autonomy for AI Agents](https://knightcolumbia.org/content/levels-of-autonomy-for-ai-agents-1)
- [OpenAI — Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)

</details>

### How do you detect and stop infinite planning loops in an agent?

`agents-infinite-loops` · medium

<details><summary>Hints</summary>

- Should the model be trusted to decide when to stop? What external checks can you add?
- Think about how you'd notice the agent repeating the exact same action or making no progress.
- Consider the cost: why is an unbounded loop dangerous?

</details>

<details><summary>Reference answer</summary>

Don't trust the model to decide when to stop, so wrap it in external, deterministic guardrails. Put a hard cap on steps (max_iterations) and a budget on tokens, cost, and wall-clock time per run. Detect repetition by hashing each (tool, arguments) call and breaking when the same action recurs k times. Detect stalls with no-progress checks: if the agent's state hasn't advanced in k steps, fire a "stuck" handler. Make the "done" signal explicit in the prompt and ensure the termination check can actually return true. When a guard trips, fail gracefully (stop, return best-effort, or escalate to a human) and log it for later evaluation. Runaway loops burn real money fast, so these limits aren't optional.

Key points:

- Hard caps: max_iterations/step limit plus token, cost, and wall-clock budgets per run
- Repetition detection: hash each (tool, args) call and break if the same action repeats k times
- No-progress detection: if state hasn't changed in k steps, trigger a 'stuck' handler
- Explicit 'done' signal in the prompt and a termination check that can actually return true
- On trip: fail gracefully (stop / best-effort / escalate to human) and log for eval. Loops burn cost fast

</details>

**Follow-ups**

- What do you do when a loop guard trips: retry, stop, or escalate?
- How do you tell 'stuck in a loop' apart from 'legitimately doing many steps'?
- How is stopping a loop different from a general termination condition?
- How would you surface loop incidents in monitoring?

**Check yourself**

1. Which is the most reliable way to guarantee an agent stops?
   - a) An external, deterministic max-iteration / time / cost cap that overrides the agent
   - b) Trusting the LLM to decide when it's finished
   - c) A larger context window
   - d) A lower temperature setting

   <details><summary>Answer</summary>a — External deterministic guards override faulty internal logic; the model deciding for itself is exactly what fails.</details>

2. How would you detect the agent repeating the same action forever?
   - a) Hash each (tool, arguments) call and break if it recurs k times
   - b) Increase the number of tools available
   - c) Raise top-p sampling
   - d) Add more few-shot examples

   <details><summary>Answer</summary>a — Action deduplication — hashing (tool, args) and counting repeats — catches loops that hard caps alone would let run to the limit.</details>

**Exercises**

- {'kind': 'recall', 'front': 'Name three guardrails that stop an agent from looping forever.', 'back': "A hard step/iteration cap (plus token/cost/time budget), action deduplication by hashing (tool, args), and no-progress 'stuck' detection — then fail gracefully or escalate."}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Inkog — AI Agent Infinite Loop Detection & Prevention](https://inkog.io/glossary/infinite-loop-ai-agent)
- [Anthropic — Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI — A Practical Guide to Building Agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

</details>

### How do you sandbox tool execution safely?

`agents-sandbox-tool-execution` · hard

<details><summary>Hints</summary>

- Ask where the code runs: is anything untrusted touching the host machine?
- Think in terms of isolation strength: plain container vs. microVM vs. userspace kernel.
- Beyond isolation, what privileges, resources, and lifetime should the sandbox have?

</details>

<details><summary>Reference answer</summary>

Never run untrusted or LLM-generated code (or high-impact tools) on the host. Isolate execution in a strong sandbox: a container hardened with a userspace kernel (gVisor/Kata) or, better, a microVM (Firecracker/E2B). Standard containers share the host kernel, so one runtime bug can compromise the host. Apply least privilege: default-deny network and filesystem, then allowlist only the egress the tool needs. Hand it scoped, short-lived, revocable credentials. Bound resources with CPU/memory/time quotas and kill switches. Make sandboxes ephemeral: a fresh, disposable environment per run with no persistent secrets. Risk-rate tools and require human approval for high-impact actions (write, spend, delete), and log every action for audit.

Key points:

- Isolate: run untrusted/generated code in containers hardened by userspace kernels (gVisor/Kata) or microVMs (Firecracker/E2B), not on the host
- Standard containers share the host kernel. A single runtime CVE can escape to the host, so prefer stronger isolation
- Least privilege: default-deny network + filesystem, allowlist egress, scoped short-lived revocable credentials
- Resource limits: CPU/memory/time quotas and kill switches to bound runaway or abusive execution
- Ephemeral, disposable envs per run. Risk-rate tools, require human approval for high-impact actions, and log everything

</details>

**Follow-ups**

- Why isn't a plain Docker container enough for untrusted code?
- How do you scope credentials so a compromised tool can't do much?
- Which tool actions warrant a human approval step?
- How does sandboxing relate to prompt-injection defense?

**Check yourself**

1. Why is a standard container often insufficient for running untrusted, LLM-generated code?
   - a) It shares the host kernel, so one runtime vulnerability can escape to the host
   - b) It cannot run Python
   - c) It has no filesystem
   - d) It is slower than running on the host

   <details><summary>Answer</summary>a — Containers share the host kernel; stronger isolation (microVMs, userspace kernels) shrinks the escape surface.</details>

2. Which combination best reflects least-privilege sandboxing?
   - a) Default-deny network/filesystem, allowlist egress, and scoped short-lived credentials
   - b) Full network access and the host's root credentials for convenience
   - c) A long-lived shared secret reused across all runs
   - d) No resource limits so tasks never fail

   <details><summary>Answer</summary>a — Least privilege means denying by default, allowlisting only what's needed, and using scoped, revocable, short-lived credentials.</details>

**Exercises**

- {'kind': 'recall', 'front': 'List the layers of a safe tool-execution sandbox.', 'back': 'Strong isolation (microVM/userspace kernel, not the host), least-privilege default-deny network/filesystem with scoped short-lived credentials, resource quotas + kill switches, ephemeral per-run envs, and human approval + logging for high-impact actions.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [ARMO — AI Agent Sandboxing & Progressive Enforcement Guide](https://www.armosec.io/blog/ai-agent-sandboxing-progressive-enforcement-guide/)
- [Northflank — Best code execution sandbox for AI agents (2026)](https://northflank.com/blog/best-code-execution-sandbox-for-ai-agents)
- [OpenAI — A Practical Guide to Building Agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)

</details>

### What are the biggest security risks with tool-using agents?

`agents-security-risks` · hard

<details><summary>Hints</summary>

- What happens if a document the agent reads contains hidden instructions?
- Think about which permissions the agent's tools hold and what an attacker could do with them.
- No single control is enough, so what layered defenses would you stack?

</details>

<details><summary>Reference answer</summary>

The headline risk is prompt injection, especially indirect injection. Malicious text in a retrieved document, web page, or tool output is treated as trusted instructions and triggers unintended tool calls (OWASP LLM01). It gets dangerous when three conditions combine, often called the "lethal trifecta." Together, private-data access, exposure to untrusted content, and the ability to exfiltrate are enough to steal data. Excessive agency and over-permissioned tools amplify the blast radius: too much autonomy or broad write access turns a small mistake or injection into real damage. Then there's unsafe tool execution (code execution, SQL/command injection, or SSRF through tools), plus sensitive-data leakage into logs. Defend in depth with least-privilege tools, input/output filtering, human approval for high-risk actions, sandboxing, and adversarial testing.

Key points:

- Prompt injection, especially indirect (from retrieved/tool content), makes the agent follow attacker instructions and fire unintended tools (OWASP LLM01)
- The 'lethal trifecta': private-data access + untrusted content + exfiltration ability = data theft
- Excessive agency / over-permissioned tools amplify damage: too much autonomy or write access on a mistake or injection
- Unsafe tool execution: code execution, SQL/command injection, SSRF via tools, plus sensitive-data leakage into logs
- Defense in depth: least-privilege tools, input/output filtering, human approval for high-risk actions, sandboxing, adversarial testing

</details>

**Follow-ups**

- What's the difference between direct and indirect prompt injection?
- What's the 'lethal trifecta' and how do you break it?
- How does least privilege limit the blast radius of an attack?
- Where should human-in-the-loop approvals sit in the defense?

**Check yourself**

1. Why is indirect prompt injection especially dangerous for tool-using agents?
   - a) Malicious text in retrieved content or tool output is treated as trusted instructions and can trigger unintended tool calls
   - b) It makes the model's responses longer
   - c) It only affects the temperature setting
   - d) It prevents the agent from using any tools

   <details><summary>Answer</summary>a — In RAG/tool/agent setups the model may treat external content as instructions, so injected text can drive real actions.</details>

2. Which best mitigates 'excessive agency' in a tool-using agent?
   - a) Least-privilege tools plus human approval for high-risk actions
   - b) Giving every tool full write access for flexibility
   - c) Increasing the context window
   - d) Turning off logging to avoid leaks

   <details><summary>Answer</summary>a — Scoping tool permissions and gating high-risk actions behind human approval limits how much damage an over-eager or hijacked agent can do.</details>

**Exercises**

- {'kind': 'recall', 'front': 'Name the top security risks for tool-using agents and the core defense.', 'back': 'Prompt injection (esp. indirect), the lethal trifecta (private data + untrusted content + exfiltration), excessive agency/over-permissioned tools, and unsafe tool execution — defended with defense-in-depth: least privilege, I/O filtering, human approval, sandboxing, adversarial testing.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [OWASP — LLM Prompt Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html)
- [Mend — 2025 OWASP Top 10 for LLM Applications: a quick guide](https://www.mend.io/blog/2025-owasp-top-10-for-llm-applications-a-quick-guide/)
- [ARMO — AI Agent Sandboxing & Progressive Enforcement Guide](https://www.armosec.io/blog/ai-agent-sandboxing-progressive-enforcement-guide/)

</details>

### How would you design an agent to analyze customer support tickets, draft responses, and escalate complex issues?

`agents-support-ticket-agent` · medium

<details><summary>Hints</summary>

- Break the job into stages. What has to happen before a reply can be drafted?
- Decide what the agent sends on its own versus what a human must approve.
- Don't forget how you'd measure whether it's actually working in production.

</details>

<details><summary>Reference answer</summary>

Model it as a triage pipeline with a human-in-the-loop, not a fully autonomous responder. Ingest the ticket, then classify it (intent, category, priority, sentiment). Retrieve context using RAG over the knowledge base plus read-only account/order data from the CRM. Draft a reply grounded in that context, then run a confidence/quality self-check. Above threshold, send it or queue it for a quick human approve/edit. Below threshold, or for high-stakes, angry, or high-value tickets, escalate to a human with the full context attached. Give it least-privilege tools (KB retrieval, read-only CRM), log every action, and keep writes gated. Finally, evaluate and monitor on resolution rate, escalation accuracy, CSAT, and draft faithfulness or hallucination, then iterate.

Key points:

- Pipeline: ingest → classify/triage (intent, category, priority, sentiment) → retrieve context → draft → self-check → send or escalate
- Human-in-the-loop: draft-and-approve, where a confidence threshold decides autonomous send vs. escalate
- Tools with least privilege: KB retrieval (RAG) and read-only CRM/account lookups. Log every action and gate writes
- Escalation logic: route complex / low-confidence / angry / high-value tickets to a human with full context and SLA rules
- Evaluate + monitor: resolution rate, escalation accuracy, CSAT, and draft faithfulness/hallucination, then iterate

</details>

**Follow-ups**

- How do you set the confidence threshold for auto-send vs. escalate?
- How do you keep drafted replies grounded and avoid hallucinated policies?
- What context do you attach when escalating to a human?
- Which metrics tell you the agent is helping, not just deflecting?

**Check yourself**

1. What decides whether the agent sends a reply itself or escalates to a human?
   - a) A confidence/quality threshold, with complex or high-stakes tickets routed to a human
   - b) Whichever is cheaper in tokens
   - c) The alphabetical order of the customer's name
   - d) The current server load

   <details><summary>Answer</summary>a — A confidence threshold plus risk/complexity routing is the standard human-in-the-loop escalation control.</details>

2. Why give the agent read-only CRM access rather than full write access?
   - a) Least privilege limits damage from mistakes or prompt injection
   - b) Read-only access is faster to type
   - c) Write access would improve draft grammar
   - d) It removes the need for evaluation

   <details><summary>Answer</summary>a — Least-privilege tools shrink the blast radius; writes should be gated behind approval.</details>

**Exercises**

- Order the support-ticket agent pipeline
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [PromptLayer — The Agentic System Design Interview](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
- [DevRev — AI support ticket triaging: the enterprise playbook (2026)](https://devrev.ai/blog/ai-support-ticket-triaging)
- [OpenAI — Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)

</details>

### How do you implement termination conditions in long-running agents?

`agents-termination-conditions` · medium

<details><summary>Hints</summary>

- List every way a run could legitimately end, not just 'it finished'.
- Separate 'we succeeded' from 'we ran out of budget' from 'something went wrong'.
- Think about where a human should be able to pause or approve.

</details>

<details><summary>Reference answer</summary>

Define explicit exits for every way a run can end (success, budget, and failure), and enforce them outside the model. A success exit is a completion check (verifiable criteria or a validator, optionally with the model's self-assessment) that marks the goal met. Budget exits (max steps, max tokens/cost, and max wall-clock time) bound how long it may run. Failure or abort exits (repeated errors, an unrecoverable tool failure, or a guardrail violation) stop the run and escalate. For high-stakes actions, a human-in-the-loop approval gate pauses the run until approved or rejected. Prefer external, deterministic checks over trusting the model to stop on its own, and always log why it stopped.

Key points:

- Success exit: an explicit completion check (verifiable criteria/validator, optionally + model self-assessment)
- Budget exits: max steps, max tokens/cost, and max wall-clock time
- Failure/abort exits: repeated errors, unrecoverable tool failure, or guardrail violation → stop and escalate
- Human-in-the-loop approval gates pause the run for high-stakes actions until approved/rejected
- Enforce externally and deterministically, not by trusting the model, and log the reason it stopped

</details>

**Follow-ups**

- How do you verify a run met its goal rather than the model claiming it did?
- How is a termination condition different from loop detection?
- Where do you insert human approval gates?
- How do you log and monitor why runs terminate?

**Check yourself**

1. Which set best covers the ways a long-running agent should be able to terminate?
   - a) Goal-satisfied, budget exhausted (steps/tokens/time), and failure/abort
   - b) Only when the user closes the browser tab
   - c) Only when the model outputs the word 'done'
   - d) Only when the API rate limit is hit

   <details><summary>Answer</summary>a — Robust agents define success, budget, and failure exits — not a single condition, and not solely the model's say-so.</details>

2. For a high-stakes action like sending a payment, the right termination-related control is:
   - a) A human-in-the-loop approval gate that pauses the run until approved or rejected
   - b) Raising the temperature so the model is more careful
   - c) Removing all step limits so it can retry freely
   - d) Letting the model auto-approve to save latency

   <details><summary>Answer</summary>a — Approvals pause the run for high-stakes tool calls; the model may still request the action but a human confirms it.</details>

**Exercises**

- {'kind': 'fill', 'template': 'Bound a run with a max {0} count and a max {1} budget, and stop on unrecoverable failures.', 'blanks': ['step', 'cost'], 'chips': ['step', 'cost', 'vector', 'prompt']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [OpenAI — A Practical Guide to Building Agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [OpenAI — Guardrails and human review](https://developers.openai.com/api/docs/guides/agents/guardrails-approvals)
- [Inkog — AI Agent Infinite Loop Detection & Prevention](https://inkog.io/glossary/infinite-loop-ai-agent)

</details>

### How do you handle tool failures, retries, and idempotency in an agent?

`agents-tool-failures-retries` · medium

<details><summary>Hints</summary>

- What should the agent see when a tool call fails, so it can try something smarter?
- Which failures should you retry, and how do you space those retries?
- If a retried 'create order' call runs twice, how do you stop a duplicate order?

</details>

<details><summary>Reference answer</summary>

Feed the failure back to the agent as an observation (the error message plus valid options). Then the model can reason about it and self-correct by retrying with fixed arguments. Pick the retry policy by error type. Rate limits (429) and transient 5xx get exponential backoff with jitter. A bad-argument error lets the model correct and retry. An unrecoverable failure stops and notifies. Make writes idempotent so retries don't double-act. Attach an idempotency key / unique requestId that the downstream API dedupes (a GET is safe to retry, a POST isn't by default). Cap it all with retry budgets and circuit breakers that open after N failures with a cooldown and alert on error-rate thresholds. Watch for context contamination: a failure preserved in history can make the agent repeat the same bad call, so sometimes prune or reset.

Key points:

- Return the error to the model as an observation so it can reason and self-correct the tool call
- Retry by error type: 429/5xx → exponential backoff + jitter, bad args → let the model fix, hard failure → stop/notify
- Idempotency: attach an idempotency key / unique requestId so downstream dedupes retried writes (GET safe, POST not by default)
- Retry budgets + circuit breakers: cap retries per turn, open after N failures with a cooldown, alert on error rate
- Beware context contamination: a preserved failure can make the agent repeat the bad call, so prune/reset when needed

</details>

**Follow-ups**

- Which HTTP errors should you retry and which should you fail fast on?
- How do idempotency keys prevent duplicate side effects?
- How do you keep retries from blowing the token/cost budget?
- What's context contamination and how do you mitigate it?

**Check yourself**

1. How do you make a write tool safe to retry after a timeout?
   - a) Attach an idempotency key / unique requestId the downstream API uses to dedupe
   - b) Retry immediately as fast as possible
   - c) Switch the call from POST to GET
   - d) Increase the model temperature

   <details><summary>Answer</summary>a — An idempotency key lets the downstream service recognize and drop a duplicate retried write, avoiding double side effects.</details>

2. The right retry strategy for an HTTP 429 (rate limit) is:
   - a) Exponential backoff with jitter
   - b) Immediate tight-loop retries
   - c) Never retry; fail the whole run
   - d) Retry only after a human approves

   <details><summary>Answer</summary>a — 429s are transient; exponential backoff with jitter spaces retries so you don't flood the API.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} keys make a write safe to retry; {1} backoff spaces out retries after rate limits.', 'blanks': ['Idempotency', 'Exponential'], 'chips': ['Idempotency', 'Exponential', 'Embedding', 'Linear']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Motomtech — AI Agent Retries and Idempotency: Tool Failure Patterns](https://www.motomtech.com/blog-post/ai-agent-retries-idempotency-tool-failures/)
- [Chanl — How to Build Idempotent Tool Calls for AI Agents](https://www.channel.tel/blog/idempotent-tool-calls-agent-retry-safety)
- [Chip Huyen — Agents](https://huyenchip.com/2025/01/07/agents.html)

</details>

### How do agents decide which tool to use?

`agents-tool-selection` · medium

<details><summary>Hints</summary>

- Think about what information the model actually sees about each tool before it picks one.
- Recall the ReAct loop, where reasoning is interleaved with the choice of action.
- Consider what goes wrong when many tools have overlapping or vague descriptions.

</details>

<details><summary>Reference answer</summary>

Each tool is exposed to the model with a name, a natural-language description, and a typed parameter schema (function/tool calling). The model matches the current task to the best-fitting tool from those descriptions and emits a structured call. In ReAct, the model interleaves reasoning ("thought") with actions. It thinks, picks a tool, observes the result, then re-decides whether to reuse the same tool with new args, switch tools, or finish. With many tools, a router/dispatcher LLM call first narrows to a specialized tool or sub-agent. Selection quality hinges on clear, non-overlapping descriptions and a minimal tool set, since bloated or ambiguous tools are a top cause of wrong choices.

Key points:

- Tools are described to the model with names, descriptions, and typed parameter schemas (function/tool calling)
- ReAct: interleave reasoning and acting (thought → action → observation → re-decide)
- Pure function calling emits a structured tool call directly, with the reasoning internal to the model
- Router/dispatcher for large tool sets: a first call routes to a specialized tool or sub-agent
- Selection quality depends on clear, non-overlapping tool descriptions and a minimal viable tool set

</details>

**Follow-ups**

- How do you handle an agent that has 100+ tools available?
- What do you do when the agent keeps picking the wrong tool?
- How would you force or constrain a specific tool choice?
- How do you evaluate tool-selection quality?

**Check yourself**

1. What does the model primarily rely on to choose a tool?
   - a) The tool's name, description, and parameter schema
   - b) The tool's source-code line count
   - c) The order tools were registered, alphabetically
   - d) The temperature setting alone

   <details><summary>Answer</summary>a — Tools are surfaced via names, descriptions, and typed schemas; the model matches the task to the best-described tool.</details>

2. A common cause of poor tool selection is:
   - a) A bloated set of tools with overlapping or ambiguous descriptions
   - b) Using typed parameter schemas
   - c) Giving each tool a clear, distinct description
   - d) Keeping the tool set small

   <details><summary>Answer</summary>a — Anthropic notes bloated, ambiguous tool sets create unclear decision points; a curated minimal set improves reliability.</details>

**Exercises**

- Order one ReAct tool-use cycle
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [APXML — LLM Agent Tool Selection Methods](https://apxml.com/courses/building-advanced-llm-agent-tools/chapter-3-llm-tool-selection-orchestration/agent-tool-selection)
- [Anthropic — Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Chip Huyen — Agents](https://huyenchip.com/2025/01/07/agents.html)

</details>

### What makes an AI system agentic?

`agents-what-makes-agentic` · easy

<details><summary>Hints</summary>

- Ask who's in control of the next step: hard-coded application code, or the LLM?
- Contrast a single prompt→response with something that loops, plans, and calls tools toward a goal.
- Recall Anthropic's workflow-vs-agent distinction and the perceive→reason→act→observe loop.

</details>

<details><summary>Reference answer</summary>

An AI system is agentic when the LLM drives the control flow. It decides what to do next, which tools to call, and when the task is done, instead of following a fixed, hard-coded path. Anthropic frames it as a spectrum: workflows orchestrate LLMs and tools through predefined code paths, while agents let the model dynamically direct its own process. The hallmarks are autonomy, goal-directedness, and tool use to act on the world. It runs in an iterative perceive → reason/plan → act → observe loop until a goal or stop condition is met. Autonomy is what you gain, and predictability is what you trade away.

Key points:

- Autonomy: the model chooses the next step and its own tool use, not a fixed script
- Goal-directed: given an objective it plans and decomposes into subtasks, not one prompt→one answer
- Tool use: it acts on and senses the environment (APIs, code, databases) and reacts to results
- Runs in a loop: perceive → reason/plan → act → observe, iterating until done
- It's a spectrum: workflow (predefined paths) → agent (open-ended, model-driven), and autonomy trades away predictability

</details>

**Follow-ups**

- Where exactly is the line between a workflow and an agent?
- Is a single LLM call with one tool already an agent?
- What do you give up as you make a system more autonomous?
- What are the core components an agent needs beyond the LLM?

**Check yourself**

1. What most distinguishes an agentic system from a fixed LLM pipeline?
   - a) The LLM dynamically directs the control flow and its own tool use
   - b) It uses a larger model with a bigger context window
   - c) It always retrieves documents before answering
   - d) It never calls any external tools

   <details><summary>Answer</summary>a — Anthropic's definition: agents let the model dynamically direct its own process and tool use, versus workflows that follow predefined code paths.</details>

2. Which is NOT a hallmark of an agentic system?
   - a) Every step is hard-coded by the developer in advance
   - b) Goal-directed planning and task decomposition
   - c) Tool use to act on the environment
   - d) An iterative act-then-observe loop

   <details><summary>Answer</summary>a — Hard-coding every step is a workflow. Agents decide steps at runtime; the other options are agentic hallmarks.</details>

**Exercises**

- Order one turn of an agent's core loop
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Anthropic — Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [Lilian Weng — LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [Google Cloud — What are AI agents?](https://cloud.google.com/discover/what-are-ai-agents)

</details>

### When is an agent the wrong solution?

`agents-when-not-to-use` · medium

<details><summary>Hints</summary>

- Ask whether you could write down the exact steps in advance. If yes, do you even need an agent?
- Think about how errors compound when each step feeds the next.
- Weigh the cost of re-calling a large model at every decision point.

</details>

<details><summary>Reference answer</summary>

An agent is the wrong tool when the task has a known, fixed path. A deterministic workflow or pipeline is more predictable, cheaper, and easier to test and debug. Agents are also wrong when error tolerance is low: reliability doesn't average across steps, it multiplies, so one early mistake propagates downstream. And they're wrong when cost or latency is tight, because each autonomous turn re-calls a large model. The same task can cost several times a plain workflow. Anthropic recommends using the simplest thing that passes your eval, and reserving agents for open-ended tasks where you can't hardcode the path but can still verify progress.

Key points:

- Known, fixed path → use a workflow/pipeline: more predictable, cheaper, easier to test
- Low error tolerance → agents are risky: reliability multiplies across steps, early mistakes propagate
- Cost/latency-sensitive → each autonomous turn re-calls a large model (can be several× a plain workflow)
- Anthropic: use the simplest solution that passes eval, and add autonomy only when needed
- Reserve agents for open-ended tasks you can't hardcode but can still verify progress on

</details>

**Follow-ups**

- What's a concrete task where a workflow beats an agent?
- How do you decide where on the workflow→agent spectrum to sit?
- How does multiplying (not averaging) reliability change your design?
- How would you justify not building an agent to a stakeholder who wants one?

**Check yourself**

1. Which situation most argues AGAINST using an agent?
   - a) The task has a known, fixed sequence of steps and low error tolerance
   - b) The task is open-ended and can't be scripted in advance
   - c) You can verify progress but not hardcode the path
   - d) The path changes unpredictably with each input

   <details><summary>Answer</summary>a — A known fixed path with low error tolerance is exactly where a deterministic workflow wins; the others favor agents.</details>

2. Why does step count matter for agent reliability?
   - a) Errors multiply across steps — each step's output feeds the next, so one early mistake propagates
   - b) More steps always make the model more accurate
   - c) Reliability averages out over many steps
   - d) Latency is unaffected by the number of steps

   <details><summary>Answer</summary>a — Agent reliability multiplies rather than averages; an early error poisons everything downstream.</details>

**Exercises**

- {'kind': 'recall', 'front': "Give Anthropic's rule of thumb for when to reach for an agent.", 'back': "Use the simplest solution that passes your eval; reserve agents for open-ended tasks where you can't hardcode the path but can still verify progress."}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Anthropic — Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)
- [OpenAI — A Practical Guide to Building Agents (PDF)](https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf)
- [Chip Huyen — Agents](https://huyenchip.com/2025/01/07/agents.html)

</details>

## evaluation

### How do you ensure the output from an LLM is consistent and accurate?

`eval-consistent-accurate-output` · medium

<details><summary>Hints</summary>

- Think about the two axes separately: consistency (variance) and accuracy (correctness).
- What can you constrain about the output shape, and what deterministic checks run after generation?
- Temperature, structured outputs + validators/retries, self-consistency, a calibrated LLM-judge, and a regression eval set in CI.

</details>

<details><summary>Reference answer</summary>

You treat consistency and accuracy as engineering problems, not free properties. LLM decoding is non-deterministic, so lower temperature (temperature=0 / greedy) to shrink variance, but don't expect bit-identical output. Batching and floating-point still cause drift. Constrain the output surface with structured outputs or function calling so the structure is guaranteed. Then add deterministic validators (schema/business rules) with bounded retries on failure. Improve accuracy with prompt engineering, retrieval grounding, and self-consistency (sample N, take the majority) for high-stakes calls. Verify with an LLM-as-judge that has been calibrated against human labels. Lock everything in with a versioned regression eval set in CI so prompt- and model-version changes can't silently degrade quality.

Key points:

- LLM decoding is non-deterministic, and temperature=0 reduces variance but doesn't guarantee identical output (batching, floating-point, no stable seed)
- Constrain the output surface: structured outputs / JSON-schema-constrained decoding or function calling guarantees the structure
- Add deterministic post-processing: schema and business-rule validators with bounded retries / re-ask on failure
- Raise accuracy with prompt engineering, retrieval grounding, and self-consistency (sample N, majority vote) for high-stakes answers
- Verify content with an LLM-as-judge that's validated against human labels and kept as a binary decision
- Lock it in with evals in CI: a versioned regression dataset that gates prompt and model-version changes

</details>

**Follow-ups**

- Temperature 0 still produced two different answers in production. Why, and how would you mitigate it?
- How do you validate that your LLM-as-judge is correct, and stop it drifting when you swap the underlying model?
- Structured outputs guarantees valid JSON, but the content was wrong. Which layers catch that?

**Check yourself**

1. Setting temperature=0 makes an LLM's output...
   - a) Lower-variance / more repeatable, but not guaranteed bit-identical
   - b) Perfectly deterministic and always identical across calls
   - c) More accurate on every task by definition
   - d) Immune to prompt changes

   <details><summary>Answer</summary>a — Greedy decoding shrinks variance, but batching, floating-point, and provider routing still cause drift, and low temperature does not fix correctness.</details>

2. Structured outputs (schema-constrained decoding) primarily guarantees...
   - a) The shape/format of the output (valid JSON matching the schema)
   - b) That the facts in the output are correct
   - c) That the model never refuses
   - d) Lower token cost

   <details><summary>Answer</summary>a — Schema constraints guarantee a valid shape; semantic correctness still needs validators, grounding, and evals on top.</details>

**Exercises**

- Order a reliability pipeline for an LLM feature, from generation to release gate
- {'kind': 'fill', 'template': 'Sampling N answers and taking the majority is called {0}; grounding answers in retrieved context is called {1}.', 'blanks': ['self-consistency', 'RAG'], 'chips': ['self-consistency', 'RAG', 'quantization', 'distillation']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [OpenAI — Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs)
- [Hamel Husain — Using LLM-as-a-Judge for Evaluation: A Complete Guide](https://hamel.dev/blog/posts/llm-judge/)
- [Hamel Husain & Shreya Shankar — LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- [Chip Huyen — Building LLM applications for production](https://huyenchip.com/2023/04/11/llm-engineering.html)

</details>

### How do you debug a RAG chatbot giving confident but wrong answers?

`eval-debug-rag-confident-wrong` · hard

<details><summary>Hints</summary>

- Two components could be at fault. Which two, and how do you tell them apart?
- There's a quick controlled experiment that isolates one of them.
- Inject known-good context (isolation test): correct now = retrieval fault, still wrong = generation fault. Then use context recall/precision vs faithfulness, add citations, and trace on a golden set.

</details>

<details><summary>Reference answer</summary>

Decompose the pipeline first: the same confidently-wrong output can come from a retrieval failure (wrong or missing chunks) or a generation failure (right context, but the model ignored or misused it). These have different fixes. Run the isolation test: manually inject known-good context and re-run generation. A correct answer means retrieval is the culprit, still wrong means generation/prompt is. Diagnose retrieval with context recall (whether the needed evidence was retrieved at all) and context precision (whether the top-k is mostly relevant). Common root causes are bad chunking, weak or mismatched embeddings, and missing reranking. Diagnose generation with faithfulness / groundedness (whether every claim is entailed by the retrieved context or hallucinated) and answer relevance. Low faithfulness on good context points at the prompt or model behavior. Add citations/attribution so you can instantly see whether the answer traces to a retrieved span. Confident-but-wrong with no supporting span is a hallucination, and with a wrong span it's retrieval. Instrument every stage (query → embeddings → retrieved chunks → prompt → answer) with tracing, and run a labeled golden set so you localize where failures concentrate instead of debugging anecdotally.

Key points:

- Decompose first: a confidently-wrong answer is either a retrieval failure (wrong/missing chunks) or a generation failure (good context ignored)
- Isolation test: inject known-good context and re-run. Correct now = retrieval fault, still wrong = generation/prompt fault
- Diagnose retrieval with context recall and precision. Common causes are bad chunking, weak/mismatched embeddings, and missing reranking
- Diagnose generation with faithfulness/groundedness and answer relevance. Low faithfulness on good context means a prompt/model problem
- Add citations/attribution: no supporting span = hallucination, wrong span = retrieval problem
- Instrument each stage with tracing and use a labeled golden set to localize failures instead of debugging anecdotally

</details>

**Follow-ups**

- Retrieval recall is fine but faithfulness is low. Walk me through the prompt- and generation-side fixes you'd try, in order.
- How would you build the golden/eval set to attribute failures to retrieval vs generation, and what do you label?
- The correct chunk is retrieved but ranked #8 and truncated out of the prompt. How do you detect and fix that (reranking, chunk size, top-k, context ordering)?

**Check yourself**

1. A RAG bot gives a confident, wrong answer. What is the fastest way to tell whether retrieval or generation is at fault?
   - a) Inject known-good context and re-run — correct now means retrieval was the problem
   - b) Increase the temperature and see if the answer changes
   - c) Switch to a bigger model and re-ask
   - d) Delete the vector index and rebuild it blindly

   <details><summary>Answer</summary>a — The isolation test controls for retrieval: if a correct answer appears once the right context is supplied, retrieval was failing; if it's still wrong, generation is.</details>

2. The right context WAS retrieved, but the answer still contradicts it. Which metric captures this, and what's the likely fix area?
   - a) Low faithfulness/groundedness — fix the prompt or model behavior
   - b) Low context recall — fix the embeddings
   - c) High latency — fix the index
   - d) Low precision — fix the chunk size

   <details><summary>Answer</summary>a — Faithfulness measures whether claims are entailed by the retrieved context; low faithfulness on good context is a generation-side (prompt/model) problem.</details>

**Exercises**

- Order the steps to debug a confidently-wrong RAG answer
- {'kind': 'fill', 'template': 'If the answer cites no supporting span it is a {0}; if the top-k chunks are irrelevant it is a {1} failure.', 'blanks': ['hallucination', 'retrieval'], 'chips': ['hallucination', 'retrieval', 'latency', 'tokenization']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Ragas — List of available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)
- [Evidently AI — A complete guide to RAG evaluation](https://www.evidentlyai.com/llm-guide/rag-evaluation)
- [Deepchecks — Retrieval Quality vs. Answer Quality: Why RAG Evaluation Fails](https://deepchecks.com/retrieval-vs-answer-quality-rag-evaluation/)
- [Confident AI (DeepEval) — RAG Evaluation Metrics: Answer Relevancy, Faithfulness, and More](https://www.confident-ai.com/blog/rag-evaluation-metrics-answer-relevancy-faithfulness-and-more)

</details>

### How do you detect and mitigate hallucinations?

`eval-detect-mitigate-hallucinations` · medium

<details><summary>Hints</summary>

- Start by defining it: faithfulness vs factuality, intrinsic vs extrinsic.
- Separate detection from mitigation, since detection is a portfolio of signals, not one tool.
- Detect with LLM-judge/NLI entailment, self-consistency (SelfCheckGPT), log-prob uncertainty. Mitigate with RAG grounding, citations, 'I don't know', low temperature, and a verification pass.

</details>

<details><summary>Reference answer</summary>

First define what you mean: intrinsic hallucination contradicts the source, extrinsic can't be verified against it. Faithfulness means grounded in the provided context, factuality means true about the world, and they need different tests. Detection is a portfolio, not one tool: an LLM-as-judge / faithfulness score, NLI entailment of each claim against evidence, self-consistency sampling (SelfCheckGPT: sample N and check the facts agree), retrieval-grounded groundedness checks, and cheap token-level uncertainty flags from log-probs or entropy. The most effective mitigation is grounding: RAG puts facts in the prompt so the model conditions on evidence instead of recalling from weights, and requiring inline citations makes every claim auditable. Add prompt and decoding controls (explicitly permit "I don't know", instruct "use only the provided context", lower temperature), an output-side verification pass that vetoes ungrounded claims, and human review for high-stakes outputs. Fine-tuning helps but nothing fully eliminates hallucination, so measure the residual rate with an eval set.

Key points:

- Distinguish intrinsic (contradicts source) from extrinsic (unverifiable) hallucination, and faithfulness (grounded) from factuality (true). They need different tests
- Detection is a portfolio: LLM-as-judge/faithfulness scoring, NLI entailment of claims, self-consistency sampling (SelfCheckGPT), groundedness checks, log-prob/entropy uncertainty
- Grounding is the most effective mitigation: RAG conditions the answer on retrieved evidence rather than parametric recall
- Require inline citations so every claim is auditable and retractable
- Prompt/decoding controls: allow 'I don't know', restrict to provided context, extract verbatim quotes, lower temperature
- Add an output-side verification pass and human-in-the-loop for high-stakes outputs. Fine-tuning helps but never fully eliminates it, so measure the residual rate

</details>

**Follow-ups**

- How would you build an automated eval to measure hallucination rate before/after a mitigation, and what's your ground truth?
- The LLM-as-judge is also an LLM. How do you keep the judge from hallucinating, and calibrate it against human labels?
- When is token-level uncertainty a reliable hallucination signal, and when does it fail (e.g. confidently wrong on memorized-but-false facts)?

**Check yourself**

1. What is the difference between faithfulness and factuality?
   - a) Faithfulness = grounded in the provided context; factuality = true about the world
   - b) They are two names for the same metric
   - c) Faithfulness applies only to code, factuality only to text
   - d) Factuality measures latency; faithfulness measures cost

   <details><summary>Answer</summary>a — An answer can be faithful to a wrong source (grounded but not factual) or factual but not grounded in the given context — different failure modes.</details>

2. How does SelfCheckGPT detect hallucinations without an external knowledge base?
   - a) It samples multiple responses and checks whether the facts stay consistent across them
   - b) It queries a search engine for every claim
   - c) It fine-tunes the model on the fly
   - d) It counts the number of tokens in the answer

   <details><summary>Answer</summary>a — Self-consistency sampling assumes factual content is stable across samples while hallucinations diverge/contradict — a zero-resource, black-box signal.</details>

**Exercises**

- Order a hallucination detect-and-mitigate workflow, from grounding to sign-off
- {'kind': 'fill', 'template': "A hallucination that contradicts the source is {0}; one that can't be verified against the source is {1}.", 'blanks': ['intrinsic', 'extrinsic'], 'chips': ['intrinsic', 'extrinsic', 'factual', 'faithful']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Ji et al. — Survey of Hallucination in Natural Language Generation (arXiv:2202.03629)](https://arxiv.org/abs/2202.03629)
- [Manakul et al. — SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection (arXiv:2303.08896)](https://arxiv.org/abs/2303.08896)
- [Anthropic — Reduce hallucinations (Claude docs)](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [Huang et al. — A Survey on Hallucination in LLMs: Principles, Taxonomy, Challenges (arXiv:2311.05232)](https://arxiv.org/abs/2311.05232)

</details>

### How do you evaluate a chatbot?

`eval-evaluate-a-chatbot` · medium

<details><summary>Hints</summary>

- Think about two splits: offline vs online, and single-turn vs whole-conversation.
- What's the one outcome that matters most, and how would you phrase the judgment?
- Offline golden conversations in CI (LLM-judge) + online A/B tests and CSAT. Turn-level and conversation-level, goal completion as pass/fail, support bots add containment/escalation KPIs.

</details>

<details><summary>Reference answer</summary>

Split evaluation into offline and online, and score at two granularities. Offline, run curated golden conversations in CI, judged by an LLM-as-judge plus reference answers or rubrics. Online, use A/B tests, thumbs up/down, CSAT, and implicit signals like escalation and retry rate. Evaluate turn-level quality (relevance, correctness, tone/safety of a single response given prior context) and conversation-level quality (goal completion, coherence across turns, role/persona adherence, knowledge retention). The primary outcome metric is task success / goal completion (did the conversation resolve the user's intent), expressed as a binary judgment, not a fuzzy 1-5. Start with error analysis: sample real transcripts, open-code failure modes, then turn frequent failures into targeted evals. LLM-as-judge is the scalable workhorse but degrades on long transcripts and must be aligned to human labels. For support bots, translate quality into business KPIs (containment/deflection, escalation, first-contact resolution, cost per conversation, CSAT), and gate release on safety/tone guardrails.

Key points:

- Separate offline eval (golden conversations in CI, LLM-judge + references) from online eval (A/B tests, thumbs/CSAT, escalation/retry signals)
- Evaluate at two granularities: turn-level (relevance, correctness, tone/safety) and conversation-level (goal completion, coherence, role adherence, knowledge retention)
- The primary outcome is task success / goal completion, expressed as a binary pass/fail rather than a fuzzy 1-5
- Do error analysis first: sample transcripts, open-code failure modes, then build targeted evals from frequent failures
- LLM-as-judge scales scoring but degrades on long conversations and must be aligned to human labels before you trust it
- For support bots, translate quality into business KPIs (containment/deflection, escalation, first-contact resolution, CSAT) and gate on safety/tone guardrails

</details>

**Follow-ups**

- Your LLM judge gives high scores but users are unhappy. How do you debug the gap between offline scores and online satisfaction?
- How would you design an A/B test to prove a new chatbot version is better, and what guardrail metrics would you watch?
- How do you build and maintain a golden multi-turn test set without it going stale as the product changes?

**Check yourself**

1. What is the single most important outcome metric for a task-oriented chatbot?
   - a) Task success / goal completion — did it resolve the user's intent
   - b) Average number of tokens per reply
   - c) How grammatically fluent each reply is
   - d) The model's parameter count

   <details><summary>Answer</summary>a — A fluent, on-topic bot that never resolves the user's goal has failed; goal completion is the north-star outcome, ideally scored as pass/fail.</details>

2. For a customer-support bot, 'containment rate' measures...
   - a) The share of conversations resolved by the bot without human escalation
   - b) The number of tokens stored in the context window
   - c) How often the bot repeats itself
   - d) The embedding similarity between turns

   <details><summary>Answer</summary>a — Containment/deflection rate is the business KPI for how many conversations the bot handles end-to-end; escalation rate is its complement.</details>

**Exercises**

- Order a practical chatbot evaluation workflow
- {'kind': 'fill', 'template': 'Judging a single reply given prior context is {0} evaluation; judging goal completion across the whole dialogue is {1} evaluation.', 'blanks': ['turn-level', 'conversation-level'], 'chips': ['turn-level', 'conversation-level', 'offline', 'reference-based']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Confident AI (DeepEval) — LLM Chatbot Evaluation Explained](https://www.confident-ai.com/blog/llm-chatbot-evaluation-explained-top-chatbot-evaluation-metrics-and-testing-techniques)
- [Hamel Husain — Multi-Turn Chat Evals](https://hamel.dev/notes/llm/officehours/evalmultiturn.html)
- [Eugene Yan — Evaluating the Effectiveness of LLM-Evaluators (LLM-as-Judge)](https://eugeneyan.com/writing/llm-evaluators/)
- [Decagon — What is Chatbot Containment Rate?](https://decagon.ai/glossary/what-is-chatbot-containment-rate)

</details>

### How do you evaluate agent performance? What metrics matter (tool selection quality, action advancement, context adherence)?

`eval-evaluate-agent-performance` · hard

<details><summary>Hints</summary>

- An agent is more than its final answer, so think about levels of evaluation.
- Consider outcome, each step, and the whole path, then add efficiency and safety.
- Final-response (goal completion) + single-step (tool selection/arguments) + trajectory (LLM-judge over the trace). Plus action advancement, context adherence, and steps/latency/cost.

</details>

<details><summary>Reference answer</summary>

Evaluate an agent at three complementary levels. First, final-response / outcome eval: did it accomplish the goal (task / goal completion rate). Second, single-step eval: was the right tool chosen with correct parameters (tool selection quality plus argument correctness and tool-error rate). Third, trajectory eval: was the whole sequence of steps sound. Because multiple valid paths usually exist, score trajectories with exact / in-order / any-order matching against a reference OR an LLM-as-judge over the full trace rather than brittle exact match, and count incorrect steps so near-misses beat total deviations. Action advancement (does each step make progress) and action/task completion (did it achieve all goals in the session) capture progress at trace vs session level. Context adherence measures whether outputs stay grounded in provided/retrieved context, the agent analog of RAG groundedness, catching closed-domain hallucinations. Track efficiency and cost as first-class metrics (number of steps, latency, tokens/dollars per run, and looping/convergence stability), since an agent that succeeds in 30 steps and $5 may be worse than one that succeeds in 5. And include error recovery / robustness plus safety guardrails, because agents take real actions.

Key points:

- Use three complementary levels: final-response/outcome (goal completion rate), single-step (tool selection + arguments), and trajectory (whole step sequence)
- Tool selection quality decomposes into: right tool chosen, correct arguments/parameters, and successful execution (tool-error rate)
- Score trajectories with exact/in-order/any-order match OR LLM-as-judge over the trace, since multiple valid paths make brittle exact match unfair. Count incorrect steps
- Action advancement = progress per step (trace-level). Action/task completion = achieving all goals (session-level)
- Context adherence = outputs stay grounded in provided/retrieved context, the agent analog of RAG groundedness, catching closed-domain hallucinations
- Track efficiency and cost as first-class (steps, latency, tokens/$ per run, convergence stability), plus error recovery and safety guardrails since agents take real actions

</details>

**Follow-ups**

- Your agent reaches the correct final answer but takes a wildly inefficient path. How do you catch and score that, and does it matter?
- There are multiple valid trajectories for a task. How do you evaluate the path without over-fitting to one golden sequence?
- How would you evaluate an agent's ability to recover from a tool that returns an error or malformed output?

**Check yourself**

1. Why is exact-match trajectory scoring often a poor way to evaluate an agent?
   - a) Multiple valid step sequences can solve the task, so exact match unfairly penalizes correct alternatives
   - b) Trajectories are impossible to record
   - c) Agents never use tools
   - d) It is the only metric that ignores the final answer

   <details><summary>Answer</summary>a — Real tasks have many valid paths; use any-order matching or an LLM-as-judge over the trace, and count incorrect steps rather than demanding one exact sequence.</details>

2. 'Context adherence' for an agent is most analogous to which RAG metric?
   - a) Groundedness / faithfulness — outputs stay grounded in provided context
   - b) Retrieval latency
   - c) Chunk size
   - d) Embedding dimension

   <details><summary>Answer</summary>a — Context adherence checks the agent's outputs against provided/retrieved context, catching closed-domain hallucinations — the agent version of RAG groundedness.</details>

**Exercises**

- Match each agent metric to what it measures
- {'kind': 'fill', 'template': 'Judging whether the right tool was called with correct parameters is {0} evaluation; judging the whole sequence of steps is {1} evaluation.', 'blanks': ['single-step', 'trajectory'], 'chips': ['single-step', 'trajectory', 'final-response', 'offline']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [LangChain — LangSmith: Agent evaluation approaches](https://docs.langchain.com/langsmith/evaluation-approaches)
- [Galileo — A Deep Dive into AI Agent Metrics](https://galileo.ai/blog/ai-agent-metrics)
- [Databricks — What is AI Agent Evaluation?](https://www.databricks.com/blog/what-is-agent-evaluation)
- [Ragas — Agent / tool-use metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)

</details>

### How do you evaluate a RAG pipeline?

`eval-evaluate-rag-pipeline` · medium

<details><summary>Hints</summary>

- A RAG system has two stages, so evaluate them separately to know which one failed.
- Name the metrics for each stage, and recall the reference-free triad.
- Retrieval: context precision/recall, recall@k, MRR, nDCG. Generation: faithfulness, answer relevance, correctness. The RAG triad (context relevance, groundedness, answer relevance) is reference-free.

</details>

<details><summary>Reference answer</summary>

Evaluate retrieval and generation separately so you can localize failures. A bad answer is either a retrieval problem (the right information wasn't surfaced) or a generation problem (it was surfaced but ignored or hallucinated over). For retrieval, use rank-unaware metrics (hit rate / recall@k, precision) and rank-aware ones (MRR, nDCG), plus LLM-graded context precision (are retrieved chunks relevant) and context recall (does the context contain everything needed). For generation, use faithfulness / groundedness (every claim traceable to context), answer relevance (does it address the question), and answer correctness (matches a reference when you have one). The RAG triad (context relevance, groundedness, answer relevance) is reference-free, so it runs both offline in CI and on live production traffic. The failing leg points at the component to fix. Build a golden dataset of {question, ground-truth context, reference answer}, and do component eval (unit-test the retriever with IR metrics) alongside end-to-end eval so improving one stage doesn't silently regress the whole pipeline.

Key points:

- Evaluate retrieval and generation separately so you can localize whether a bad answer is a retrieval or a generation failure
- Retrieval metrics: rank-unaware (recall@k / hit rate, precision) and rank-aware (MRR, nDCG), plus context precision and context recall
- Generation metrics: faithfulness/groundedness, answer relevance, and answer correctness (when a reference exists)
- The RAG triad (context relevance, groundedness, answer relevance) is reference-free, so it runs offline and on live traffic. The failing leg points at the fix
- Build a golden dataset of {question, ground-truth context/chunks, reference answer}. Reference-based metrics need it, triad metrics don't
- Do component eval (unit-test the retriever in isolation) AND end-to-end eval to catch both regressions and interaction effects

</details>

**Follow-ups**

- End-to-end answer quality is low but faithfulness is high. How do you diagnose whether it's retrieval or the question set?
- How do you construct a golden dataset for RAG, and how do you handle questions with multiple valid supporting chunks?
- Faithfulness and answer-relevance are both LLM-judged, so how do you validate that the judge is trustworthy?

**Check yourself**

1. Why evaluate retrieval and generation separately in a RAG pipeline?
   - a) To localize a bad answer to either the retriever or the generator
   - b) Because retrieval and generation use the same metric
   - c) So you never need a golden dataset
   - d) To reduce the embedding dimension

   <details><summary>Answer</summary>a — A confidently-wrong answer can stem from missing context (retrieval) or ignoring good context (generation); separate metrics tell you which to fix.</details>

2. Which property of the RAG triad lets it run on live production traffic without labels?
   - a) It is reference-free (no ground-truth answer required)
   - b) It only uses BLEU score
   - c) It requires a fine-tuned judge
   - d) It ignores the retrieved context

   <details><summary>Answer</summary>a — Context relevance, groundedness, and answer relevance are all judged from the query, context, and answer alone — no reference answer needed.</details>

**Exercises**

- Match each RAG metric to the component it evaluates
- {'kind': 'fill', 'template': '{0} measures whether every claim in the answer is grounded in retrieved context; {1} rank-aware metrics like MRR and nDCG measure retrieval ordering.', 'blanks': ['Faithfulness', 'Retrieval'], 'chips': ['Faithfulness', 'Retrieval', 'Latency', 'Toxicity']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Ragas — List of available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)
- [Ragas — Faithfulness](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [TruLens — The RAG Triad](https://www.trulens.org/getting_started/core_concepts/rag_triad/)
- [Es et al. — RAGAS: Automated Evaluation of Retrieval Augmented Generation (arXiv:2309.15217)](https://arxiv.org/abs/2309.15217)

</details>

### How do you build a golden dataset for evaluation?

`eval-golden-dataset` · medium

<details><summary>Hints</summary>

- Where should the examples come from so they match what users actually do?
- Think about who labels the expected outputs, and how you cover edge cases and failure modes.
- Real production traces + error analysis for coverage, expert-labeled expected outputs/rubrics, inter-annotator agreement, plus versioning and no train/eval leakage.

</details>

<details><summary>Reference answer</summary>

A golden dataset is a curated, versioned set of representative examples with expected outputs (or pass/fail rubrics) that you evaluate against. Source examples from real production queries, logs, and traces so the distribution matches what users actually ask, sampling both typical and problematic (low-score) cases. Deliberately cover edge cases and known failure modes via error analysis (open-code real traces into a failure taxonomy) and aim for coverage/saturation rather than a magic number (100+ traces is a practical start). Attach expected outputs or reference answers written by domain experts. Where a single gold string is impossible, store a rubric. Default to one principal domain-expert labeler, and when you need several, write annotation guidelines and measure inter-annotator agreement (Cohen's kappa). Fill coverage gaps with dimension-based synthetic data, but avoid it for high-stakes or niche cases. Version the set, prevent train/eval leakage, and keep updating it as new failure modes appear in production.

Key points:

- Source examples from real production queries/logs/traces so the eval distribution matches real usage. Sample typical AND problematic cases
- Cover edge cases and known failure modes via error analysis (open/axial coding into a failure taxonomy). Aim for coverage/saturation (~100+ traces)
- Attach expected outputs / reference answers or pass-fail rubrics, authored by domain experts
- Default to one domain-expert labeler. With multiple annotators, write guidelines and measure inter-annotator agreement (Cohen's kappa)
- Use dimension-based synthetic data to fill gaps, but avoid it for high-stakes, niche, or underrepresented cases
- Version the dataset, prevent train/eval leakage, and continually update it as new production failure modes surface

</details>

**Follow-ups**

- How large should the golden set be, and how do you know it's big enough and representative?
- How do you prevent leakage between your eval set and your prompts or fine-tuning data, and detect it if it happened?
- Two annotators disagree on many examples. How do you diagnose and fix it, and how would you quantify the problem?

**Check yourself**

1. What is the best primary source of examples for a golden eval dataset?
   - a) Real production queries, logs, and traces (including problematic ones)
   - b) Only synthetic examples generated by the model itself
   - c) The model's public training benchmarks
   - d) A single hand-picked happy-path example

   <details><summary>Answer</summary>a — Real production traffic matches the true input distribution; synthetic data supplements coverage but shouldn't be the sole source.</details>

2. When multiple people label eval examples, what should you measure?
   - a) Inter-annotator agreement (e.g. Cohen's kappa)
   - b) The average response latency
   - c) The model's token cost
   - d) BLEU score between labels

   <details><summary>Answer</summary>a — Agreement metrics like Cohen's kappa reveal ambiguous items and unclear guidelines; low agreement means the labels aren't trustworthy yet.</details>

**Exercises**

- Order the steps to build a golden evaluation dataset
- {'kind': 'fill', 'template': 'Generating extra examples to fill coverage gaps is {0} data; keeping eval examples out of prompts and fine-tuning avoids {1}.', 'blanks': ['synthetic', 'leakage'], 'chips': ['synthetic', 'leakage', 'reference', 'drift']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Hamel Husain & Shreya Shankar — LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)
- [Hamel Husain — How many people should annotate my LLM outputs?](https://hamel.dev/blog/posts/evals-faq/how-many-people-should-annotate-my-llm-outputs.html)
- [Databricks — Build evaluation datasets (MLflow)](https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/build-eval-dataset)
- [LangChain — LangSmith Evaluation](https://docs.langchain.com/langsmith/evaluation)

</details>

### What metrics do you consider when evaluating LLM performance?

`eval-llm-metrics` · easy

<details><summary>Hints</summary>

- Metrics depend on the task, so start by grouping by task type (classification, retrieval, generation).
- Don't forget the non-quality axes an interviewer wants to hear about.
- Task metrics (F1/exact-match, recall@k/MRR/nDCG), generation (BLEU/ROUGE/BERTScore, LLM-as-judge), RAG (faithfulness, context precision/recall), plus latency, cost, and safety.

</details>

<details><summary>Reference answer</summary>

Pick metrics by task type, and always cover quality, operations, and safety. For classification/extraction use accuracy, precision/recall, F1, exact match. For ranking/retrieval use recall@k, MRR, nDCG. For generated text, reference-based overlap metrics (BLEU, ROUGE, METEOR) are cheap but weak because they measure n-gram overlap, not meaning. BERTScore adds semantic similarity but still needs a reference. For open-ended output, use a reference-free LLM-as-judge (e.g. G-Eval), which correlates far better with humans, but validate it against human labels. RAG needs decomposed metrics: faithfulness and answer relevance for generation, context precision and context recall for retrieval. Always add operational metrics (latency p50/p95, cost per request, throughput) and safety metrics (toxicity, bias, hallucination rate), and keep human eval as the calibration gold standard.

Key points:

- Choose metrics by task: accuracy/precision/recall/F1/exact-match for classification-extraction, and recall@k, MRR, nDCG for retrieval/ranking
- Reference-based text metrics (BLEU, ROUGE, METEOR) measure n-gram overlap, not meaning. BERTScore adds semantic similarity but still needs a reference
- For open-ended output use reference-free LLM-as-judge (G-Eval), which correlates better with humans, but validate the judge against human labels
- RAG needs decomposed metrics: faithfulness + answer relevance (generation) and context precision + context recall (retrieval)
- Always include operational metrics: latency (p50/p95), cost per request/token, throughput
- Include safety metrics (toxicity, bias, hallucination rate) and keep human eval as the calibration gold standard

</details>

**Follow-ups**

- BLEU/ROUGE are high but users say the answers are wrong. What's happening, and what would you measure instead?
- Your RAG answer-relevance is high but faithfulness is low. What does that tell you, and where do you fix it?
- How do you trade off answer quality against latency and cost when choosing a production model?

**Check yourself**

1. Why are BLEU and ROUGE weak metrics for open-ended LLM generation?
   - a) They measure n-gram overlap with a reference, not semantic meaning
   - b) They require a GPU to compute
   - c) They only work for classification tasks
   - d) They cannot be computed without human annotators

   <details><summary>Answer</summary>a — BLEU/ROUGE reward surface overlap with a reference; a correct paraphrase can score low and a wrong answer can score high.</details>

2. Which metric set is appropriate for the RETRIEVAL half of a RAG system?
   - a) Context precision and context recall (recall@k, MRR, nDCG)
   - b) BLEU and ROUGE
   - c) Faithfulness and answer relevance
   - d) Latency and cost per token

   <details><summary>Answer</summary>a — Retrieval quality is measured with context precision/recall and ranking metrics; faithfulness/answer-relevance measure the generation half.</details>

**Exercises**

- Match each metric to what it measures
- {'kind': 'fill', 'template': '{0} metrics compare against a gold reference; {1} metrics (like an LLM-as-judge) need no reference and suit open-ended output.', 'blanks': ['Reference-based', 'Reference-free'], 'chips': ['Reference-based', 'Reference-free', 'Operational', 'Statistical']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Ragas — List of available metrics](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/)
- [Confident AI (DeepEval) — LLM Evaluation Metrics: The Ultimate Guide](https://www.confident-ai.com/blog/llm-evaluation-metrics-everything-you-need-for-llm-evaluation)
- [Eugene Yan — Evaluation & Hallucination Detection for Abstractive Summaries](https://eugeneyan.com/writing/abstractive/)
- [Chip Huyen — Building LLM applications for production](https://huyenchip.com/2023/04/11/llm-engineering.html)

</details>

### How would you prevent factual errors in a summarization system?

`eval-summarization-factual-errors` · hard

<details><summary>Hints</summary>

- The property you care about is faithfulness of the summary to its source, not overlap with a reference.
- Think about a design lever (extractive vs abstractive) plus purpose-built consistency metrics.
- Prefer extractive/quote-constrained + citations, and measure with NLI-based (SummaC, FactCC) and QA-based (QAGS) consistency. Constrain to source, then human review.

</details>

<details><summary>Reference answer</summary>

The core objective is faithfulness / groundedness of the summary to its source, which is distinct from ROUGE-style overlap or general "quality". A fluent summary can still invent facts. Extractive vs abstractive is a design lever: extractive or heavily quote-constrained summaries are far less prone to fabrication, while abstractive gains fluency at the cost of hallucination risk. Measure factual consistency explicitly with purpose-built metrics: NLI-based checks (SummaC, FactCC) that verify each summary sentence is entailed by the source, and QA-based checks (QAGS, QuestEval) that verify the same questions get the same answers from summary and source. An LLM-as-judge for faithfulness scales this, but validate it against human labels and the classic benchmarks. Constrain generation to the source (instruct the model to use only the provided text, add citations/attribution back to source spans, lower temperature). Add a post-hoc verification pass that flags or removes unsupported claims, handle long documents with chunking plus hierarchical/map-reduce summarization, and keep human review for high-stakes summaries.

Key points:

- The objective is faithfulness/groundedness of the summary to its source, distinct from ROUGE overlap or fluency
- Extractive / quote-constrained summaries fabricate far less, while abstractive trades fluency for hallucination risk
- Measure factual consistency explicitly: NLI-based entailment (SummaC, FactCC) and QA-based agreement (QAGS, QuestEval)
- Use an LLM-as-judge for faithfulness to scale, but validate it against human labels and benchmark datasets
- Constrain generation to the source: 'use only the provided text', add citations to source spans, lower temperature, add a post-hoc unsupported-claim filter
- Handle long documents with chunking + hierarchical/map-reduce summarization, and keep human review for high-stakes cases

</details>

**Follow-ups**

- The summarizer must compress and paraphrase. How do you tell legitimate abstraction apart from a hallucinated fact when scoring faithfulness?
- How do you evaluate faithfulness when the source exceeds the model's (or the judge's) context window?
- What about factual errors that are in the source. Should the summary faithfully repeat them, and how does that interact with factuality vs faithfulness?

**Check yourself**

1. Why is ROUGE a poor guard against factual errors in a summary?
   - a) It rewards n-gram overlap with a reference, not whether claims are entailed by the source
   - b) It requires a GPU to compute
   - c) It measures latency instead of quality
   - d) It only works on extractive summaries

   <details><summary>Answer</summary>a — A summary can overlap heavily with a reference yet still assert a fact the source never supports; you need entailment- or QA-based consistency checks.</details>

2. Which design choice most directly reduces fabricated facts in summaries?
   - a) Prefer extractive / quote-constrained generation grounded in source spans
   - b) Raise the temperature for more creative phrasing
   - c) Remove citations to keep summaries short
   - d) Optimize purely for ROUGE

   <details><summary>Answer</summary>a — Extractive or quote-constrained summaries pull text directly from the source, sharply limiting invented content; abstractive fluency raises hallucination risk.</details>

**Exercises**

- Order a faithfulness-first summarization pipeline
- {'kind': 'fill', 'template': '{0}-based checks like SummaC test whether each summary sentence is entailed by the source; {1}-based checks like QAGS compare answers drawn from summary and source.', 'blanks': ['NLI', 'QA'], 'chips': ['NLI', 'QA', 'ROUGE', 'BLEU']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Laban et al. — SummaC: Re-Visiting NLI-based Models for Inconsistency Detection in Summarization (arXiv:2111.09525)](https://arxiv.org/abs/2111.09525)
- [Wang, Cho, Lewis — Asking and Answering Questions to Evaluate Factual Consistency of Summaries (QAGS, arXiv:2004.04228)](https://arxiv.org/abs/2004.04228)
- [Eugene Yan — Evaluation & Hallucination Detection for Abstractive Summaries](https://eugeneyan.com/writing/abstractive/)
- [Kryściński et al. — Evaluating the Factual Consistency of Abstractive Text Summarization (FactCC, arXiv:1910.12840)](https://arxiv.org/abs/1910.12840)

</details>

## llm-practice

### What is the context window and what happens when you exceed it? How do you handle long documents?

`llm-context-window` · medium

<details><summary>Hints</summary>

- Think of it as the model's working memory measured in a specific unit. What unit, and what does it include besides the prompt?
- Two different failure modes when you go over: a hard one from the API and a quiet one from the tooling. And even under the limit, position matters.
- It's the max tokens (input + output) the model attends to. Exceed it → error or silent truncation. Even below it, 'lost in the middle' hurts. Handle long docs with RAG, summarization/compression, and deliberate truncation.

</details>

<details><summary>Reference answer</summary>

The context window sets the maximum amount of text, measured in tokens, that an LLM can attend to at the same time, covering both the input (prompt, system message, history, retrieved docs) and the tokens it generates. It's the model's working memory: nothing outside it exists to the model. When you exceed it, what happens depends on the tool. The API returns an error, or the input is silently truncated (usually dropping the oldest tokens), so the model loses earlier instructions or context and quality degrades. Even below the hard limit, long contexts show the "lost in the middle" problem. The model attends best to the start and end but can miss facts buried in the middle, and attention cost grows roughly quadratically. To handle long documents you don't just cram everything in: (1) chunk and use RAG to retrieve only the relevant passages at query time. (2) Summarize or compress (hierarchically / map-reduce for long docs). (3) Truncate deliberately, keeping the parts that matter. (4) Roll up conversation history into a running summary. RAG is the default for corpora far larger than any window.

Key points:

- Context window = max tokens the model can process in a single pass, spanning input + output
- It's the model's working memory, and anything outside it is invisible to the model
- Exceed it → API error or silent truncation (oldest tokens dropped), losing earlier context and degrading quality
- Even within the limit, long context degrades: 'lost in the middle', higher latency/cost (attention scales ~quadratically)
- Handle long docs with RAG (chunk + retrieve only relevant parts), the default when the corpus exceeds any window
- Also: summarize/compress (hierarchical/map-reduce), deliberate truncation, and rolling conversation summaries

</details>

**Follow-ups**

- Why does a 1M-token window not make RAG obsolete?
- What's the 'lost in the middle' problem and how do you mitigate it?
- How do you decide chunk size and overlap when splitting a long document?
- How do you manage a long multi-turn conversation that keeps growing past the window?

**Check yourself**

1. What does the context window measure?
   - a) The maximum number of tokens (input + output) the model can consider at once
   - b) The number of parameters (weights) in the model
   - c) How many documents are stored in the vector database
   - d) The model's maximum requests per minute

   <details><summary>Answer</summary>a — The context window is a token budget covering prompt, history, retrieved context, and generated output — the model's working memory. It's unrelated to parameter count or rate limits.</details>

2. A user pastes a document longer than the model's context window. What is a common consequence?
   - a) The input is truncated (or the API errors), so earlier content is dropped and quality degrades
   - b) The model automatically grows its window to fit the document
   - c) The extra tokens are stored as long-term memory for future calls
   - d) Nothing changes; models handle any length equally well

   <details><summary>Answer</summary>a — Beyond the limit you get an error or silent truncation (usually of the oldest tokens), so instructions or context get lost. Models don't auto-expand the window or persist overflow.</details>

**Exercises**

- Order a RAG-style pipeline for answering questions over documents too large for the context window
- {'kind': 'fill', 'template': 'The context window is measured in {0}; when input exceeds it, the tooling typically {1} the oldest content.', 'blanks': ['tokens', 'truncates'], 'chips': ['tokens', 'truncates', 'parameters', 'caches']}
- {'kind': 'recall', 'front': 'Name three ways to handle documents that exceed the context window.', 'back': 'RAG (chunk + retrieve only relevant passages), summarization/compression (e.g. hierarchical/map-reduce), and deliberate truncation that keeps the important parts. For growing chats, roll history into a running summary.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [IBM — What is a context window?](https://www.ibm.com/think/topics/context-window)
- [Agenta — Top techniques to manage context length in LLMs](https://agenta.ai/blog/top-6-techniques-to-manage-context-length-in-llms)
- [IBM Research — Why larger LLM context windows are all the rage](https://research.ibm.com/blog/larger-context-window)

</details>

### How do LLMs work?

`llm-how-llms-work` · easy

<details><summary>Hints</summary>

- Start from the single training objective. What's the model actually asked to output at each step?
- Think about the pipeline: how does raw text become something the network consumes, and what does the last layer emit?
- It's an autoregressive next-token predictor built on transformer self-attention, trained self-supervised with cross-entropy, then aligned with instruction tuning/RLHF.

</details>

<details><summary>Reference answer</summary>

An LLM is a large neural network (almost always a transformer), trained to predict the next token given all the tokens before it. Text is split into tokens (words or word-pieces). Each token becomes a vector, and stacked self-attention layers let every position read from earlier positions to build up context. The final layer outputs a probability distribution over the whole vocabulary for the next token. Training is self-supervised: run over trillions of tokens of text. For each position, penalize the model (cross-entropy loss) when it assigns low probability to the token that actually came next. Doing this at scale forces the model to internalize grammar, facts, style, and reasoning patterns. At inference the model is autoregressive: predict a token, append it, feed it back in, repeat. Base models are then aligned with instruction tuning and RLHF so they follow instructions instead of just continuing text.

Key points:

- Core objective: predict the next token given the preceding context (autoregressive language modeling)
- Architecture is a transformer: self-attention lets each token attend to earlier tokens to build context
- Text → tokens → embeddings → transformer layers → probability distribution over the vocabulary
- Training is self-supervised on huge corpora with cross-entropy loss and needs no manual labels
- Generation is iterative: sample/pick a token, append it, feed back in, repeat
- Instruction tuning + RLHF turn a raw next-token predictor into a helpful assistant

</details>

**Follow-ups**

- What's the difference between a base (pretrained) model and an instruction-tuned/chat model?
- If it just predicts the next token, how does it appear to reason?
- How does sampling (temperature, top-p) change what token gets produced?
- Why do LLMs hallucinate if they're trained to predict likely text?

**Check yourself**

1. What is the fundamental training objective of a modern LLM?
   - a) Predict the next token given the preceding tokens
   - b) Classify each sentence into a fixed set of topics
   - c) Compress the training corpus into a lookup table
   - d) Translate every input into a canonical embedding and store it

   <details><summary>Answer</summary>a — LLMs are trained with a self-supervised next-token prediction objective; everything else (facts, style, reasoning) is a side effect of doing this well at scale.</details>

2. Which neural architecture underpins essentially all current LLMs?
   - a) The transformer, using self-attention
   - b) A convolutional neural network (CNN)
   - c) A decision-tree ensemble
   - d) A recurrent LSTM with no attention

   <details><summary>Answer</summary>a — Transformers with self-attention let every token attend to earlier tokens in parallel, which is what made large-scale language modeling practical.</details>

**Exercises**

- Order the steps an LLM takes to generate the next token
- {'kind': 'fill', 'template': 'An LLM is trained with a {0} objective and generates text {1}, feeding each new token back in.', 'blanks': ['next-token prediction', 'autoregressively'], 'chips': ['next-token prediction', 'autoregressively', 'classification', 'all at once']}
- {'kind': 'recall', 'front': 'In one sentence, how does an LLM work?', 'back': 'It is a transformer trained self-supervised to predict the next token from context, and it generates text autoregressively by repeatedly sampling a token and feeding it back in.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [IBM — What Are Large Language Models (LLMs)?](https://www.ibm.com/think/topics/large-language-models)
- [Sebastian Raschka — How does next-token prediction train an LLM?](https://sebastianraschka.com/faq/docs/next-token-prediction.html)

</details>

### How do you do memory management and context management with LLMs?

`llm-memory-management` · medium

<details><summary>Hints</summary>

- Start from a key property of the model: does a plain LLM call remember anything from the last one?
- Two layers: one lives inside the context window right now, the other lives somewhere else and gets pulled in when needed.
- Short-term/working memory = curated context (recent turns + summaries), long-term memory = external store retrieved on demand (RAG). Context management is choosing what enters the finite window each turn.

</details>

<details><summary>Reference answer</summary>

LLMs are stateless (each call only knows what's in its context window), so "memory" is something you engineer around the model. Split it into two layers. Short-term (working) memory is what you fit into the context this turn: the system prompt, recent conversation, and retrieved snippets. Because the window is finite and stuffing it degrades quality, you manage it: keep the last N turns verbatim, and compress older history into a running summary (summarization), or truncate/drop the least relevant parts. Long-term memory is persistent state kept outside the model (a database or vector store) that survives across sessions: user preferences, facts, past decisions. You don't feed all of it in. You extract salient memories, store them, and at query time retrieve only the relevant ones (RAG-style) back into the context. This is often organized as semantic (facts/knowledge), episodic (past interactions), and procedural (learned how-to) memory. Context management is the discipline of deciding, each turn, exactly what goes into the limited window (recent history + retrieved long-term memories + tools), so the model has what it needs and nothing that pollutes it. Watch for staleness and contradictory memories, and prune/update them over time.

Key points:

- LLMs are stateless, so memory is engineered around them, not stored in the weights
- Short-term / working memory = what fits in the context window this turn (system prompt, recent turns, retrieved snippets)
- Manage short-term memory by keeping recent turns verbatim and summarizing/compressing or truncating older history
- Long-term memory = persistent external store (DB / vector store) surviving across sessions: preferences, facts, past events
- Retrieve long-term memory on demand (RAG-style): store salient items, fetch only the relevant ones back into context
- Memory types: semantic (facts), episodic (past interactions), procedural (learned procedures)
- Context management = curating what enters the finite window each turn. Prune stale/contradictory memories

</details>

**Follow-ups**

- How do you decide what goes into long-term memory versus what you discard?
- What breaks when the running summary loses an important detail, and how do you guard against it?
- How do conflicting or stale memories cause bad behavior, and how do you handle them?
- How is this different from just using a bigger context window?

**Check yourself**

1. Why do LLM applications need an explicit memory layer at all?
   - a) The model is stateless — a call only sees its context window, so persistence must be handled outside it
   - b) Because the model stores every past conversation in its weights automatically
   - c) Because temperature resets memory between calls
   - d) Only fine-tuned models can read the context window

   <details><summary>Answer</summary>a — LLMs don't retain anything between calls; whatever isn't in the current context is gone. Memory is engineered around the model with external storage plus retrieval.</details>

2. Which best describes long-term memory in an LLM agent?
   - a) Persistent state in an external store (e.g. vector DB), retrieved into context when relevant
   - b) The recent messages currently sitting in the context window
   - c) Extra parameters added to the model at runtime
   - d) A larger temperature setting that improves recall

   <details><summary>Answer</summary>a — Long-term memory persists outside the model across sessions; you retrieve only the relevant pieces back into the window. Recent in-window messages are short-term/working memory.</details>

**Exercises**

- Order how an agent uses long-term memory across a conversation
- {'kind': 'fill', 'template': '{0} memory is the curated content inside the context window this turn; {1} memory is persistent state kept in an external store.', 'blanks': ['Short-term', 'Long-term'], 'chips': ['Short-term', 'Long-term', 'Parametric', 'Frozen']}
- {'kind': 'recall', 'front': 'How do you keep a long conversation from overflowing the context window while retaining what matters?', 'back': 'Keep the last N turns verbatim, compress older history into a running summary (and/or truncate the least relevant parts), and push durable facts to a long-term store you retrieve from on demand.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [APXML — Memory mechanisms for LLM agents (short- & long-term)](https://apxml.com/courses/multi-agent-llm-systems-design-implementation/chapter-2-architecting-agents-defining-roles/memory-mechanisms-llm-agents)
- [Redis — Build smarter AI agents: manage short-term and long-term memory](https://redis.io/blog/build-smarter-ai-agents-manage-short-term-and-long-term-memory-with-redis/)
- [mem0 — AI memory management for LLMs and agents](https://mem0.ai/blog/ai-memory-management-for-llms-and-agents)

</details>

### What is temperature and top-p sampling? How do they affect outputs?

`llm-temperature-top-p` · medium

<details><summary>Hints</summary>

- Both act at decoding time on the next-token probability distribution: one reshapes it, the other trims it.
- One is a knob on the whole distribution's sharpness, and the other is a cutoff on cumulative probability mass. Which does which, and which direction means 'more creative'?
- Temperature scales logits (low = focused/deterministic, high = diverse). Top-p keeps the smallest set of tokens summing to probability p and samples from it, dropping the tail. Tune one, not both.

</details>

<details><summary>Reference answer</summary>

Both are decoding controls that decide how the model picks the next token from its probability distribution, changing randomness, not the model's weights. Temperature rescales the logits before the softmax. Low temperature (→0) sharpens the distribution so the top token dominates: focused, repetitive, near-deterministic output. That's good for extraction, classification, and code. High temperature (>1) flattens the distribution so unlikely tokens get a real chance: diverse, creative, but riskier output. Temperature 0 is effectively greedy decoding. Top-p (nucleus sampling) instead truncates the distribution: it keeps the smallest set of most-probable tokens whose cumulative probability reaches p (e.g. 0.9). Then it samples from only that set, dropping the long tail of junk tokens. So top-p adapts how many candidates are considered to how confident the model is at that step. They interact: temperature is applied first, so a low temperature shrinks the nucleus. Common advice (OpenAI) is to tune one, not both. Use low temperature and low-ish top-p for factual and deterministic tasks, and higher settings for brainstorming and creative writing.

Key points:

- Both are decoding-time sampling controls that change randomness, not the model weights
- Temperature rescales logits before softmax: low → sharper/more deterministic, high → flatter/more diverse
- Temperature ≈ 0 is greedy decoding (always the most likely token)
- Top-p (nucleus) keeps the smallest set of tokens whose cumulative probability ≥ p and samples from it, cutting the low-probability tail
- Top-p adapts the candidate set size to the model's confidence at each step. Top-k fixes a constant count instead
- They stack (temperature applied first), and common advice is to tune one, not both
- Low settings for factual/extraction/code, higher settings for creative/brainstorming tasks

</details>

**Follow-ups**

- How does top-p differ from top-k sampling?
- If you need reproducible outputs, what settings do you use and is that enough?
- Why might temperature 0 still not be perfectly deterministic in practice?
- You want deterministic JSON extraction. What decoding settings do you choose and why?

**Check yourself**

1. You need consistent, near-deterministic answers for a data-extraction task. What temperature do you pick?
   - a) A low temperature (near 0)
   - b) A high temperature (above 1)
   - c) Temperature has no effect on determinism
   - d) Exactly 1.0, always

   <details><summary>Answer</summary>a — Low temperature sharpens the distribution toward the most likely token, giving focused, near-deterministic output — what you want for extraction and classification.</details>

2. What does top-p = 0.9 actually do?
   - a) Samples from the smallest set of tokens whose cumulative probability reaches 0.9
   - b) Always keeps exactly 90 candidate tokens
   - c) Multiplies every logit by 0.9 before softmax
   - d) Discards the 90% most likely tokens

   <details><summary>Answer</summary>a — Top-p (nucleus) sampling keeps the smallest set of most-probable tokens whose probabilities sum to p and samples from that nucleus, discarding the low-probability tail. Keeping a fixed count is top-k.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} rescales the logits to control randomness; {1} keeps the smallest set of tokens whose cumulative probability reaches a threshold.', 'blanks': ['Temperature', 'Top-p'], 'chips': ['Temperature', 'Top-p', 'Top-k', 'Beam search']}
- {'kind': 'recall', 'front': 'Higher temperature does what to the output distribution and the resulting text?', 'back': 'It flattens the distribution so lower-probability tokens are more likely to be chosen, producing more diverse/creative but less predictable text. Low temperature sharpens it toward focused, deterministic output.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [IBM — What is LLM temperature?](https://www.ibm.com/think/topics/llm-temperature)
- [Holtzman et al. — The Curious Case of Neural Text Degeneration (nucleus/top-p sampling)](https://arxiv.org/abs/1904.09751)
- [PromptEngineering.org — Guide to Temperature and Top-p](https://promptengineering.org/prompt-engineering-with-temperature-and-top-p/)

</details>

## ml-fundamentals

### What is the bias-variance tradeoff? How does it relate to overfitting and underfitting?

`ml-bias-variance-tradeoff` · medium

<details><summary>Hints</summary>

- Break the error into two competing sources: one from being too simple, one from being too sensitive to the exact data.
- One source shows up as bad-everywhere, the other as great-on-train-but-bad-on-test. Match each to underfitting vs overfitting.
- Bias = wrong/simple assumptions → underfitting (bad on train and test). Variance = fitting noise → overfitting (big train-test gap). More complexity trades bias for variance, so minimize total error on held-out data.

</details>

<details><summary>Reference answer</summary>

Total prediction error on unseen data decomposes into bias, variance, and irreducible noise. Bias is error from wrong or overly simple assumptions. The model is too rigid to capture the true signal (e.g. fitting a line to a curve). Variance is error from sensitivity to the specific training set. The model swings a lot if you resample the data because it's chasing noise. The tradeoff: making a model more complex (more features, depth, capacity) lowers bias but raises variance, while making it simpler does the opposite. High bias shows up as underfitting: poor performance on both training and test data. High variance shows up as overfitting: great on training, poor on test, with a big train-test gap. You don't try to zero out either one. You find the complexity that minimizes total error on held-out data. You navigate it with regularization, more data, cross-validation, and simpler-vs-richer models, trading a little bias for a lot less variance (or vice versa).

Key points:

- Expected test error = bias² + variance + irreducible error
- Bias: error from overly simple/wrong assumptions, so the model can't capture the true signal
- Variance: error from over-sensitivity to the training set, so the model fits noise and swings under resampling
- High bias → underfitting: poor on both train and test
- High variance → overfitting: great on train, poor on test (large train-test gap)
- More complexity lowers bias but raises variance, and vice versa. Pick the complexity that minimizes total held-out error
- Levers: regularization, more data, cross-validation, feature selection, model capacity

</details>

**Follow-ups**

- How does adding more training data affect bias versus variance?
- Which direction does regularization move you on the tradeoff?
- How would you diagnose whether a model is underfitting or overfitting from its learning curves?
- Do ensembles like random forests reduce bias, variance, or both?

**Check yourself**

1. A model scores 99% on training data but 70% on the test set. What is happening?
   - a) High variance — the model is overfitting
   - b) High bias — the model is underfitting
   - c) Irreducible error dominates
   - d) The model is perfectly balanced

   <details><summary>Answer</summary>a — A large gap where training performance far exceeds test performance is the signature of high variance / overfitting — the model has fit noise specific to the training set.</details>

2. You increase model complexity (more parameters/features). What typically happens to bias and variance?
   - a) Bias decreases, variance increases
   - b) Bias increases, variance decreases
   - c) Both decrease with no cost
   - d) Both increase

   <details><summary>Answer</summary>a — More capacity lets the model fit finer structure (lower bias) but makes it more sensitive to the specific training data (higher variance). That's the tradeoff.</details>

**Exercises**

- {'kind': 'fill', 'template': 'High {0} causes underfitting (poor on train and test); high {1} causes overfitting (great on train, poor on test).', 'blanks': ['bias', 'variance'], 'chips': ['bias', 'variance', 'noise', 'latency']}
- {'kind': 'recall', 'front': 'What is the bias-variance tradeoff in one sentence?', 'back': 'Reducing bias (simplistic-model error) tends to increase variance (data-sensitivity error) and vice versa, so you choose the model complexity that minimizes total error on unseen data.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [IBM — What is the bias-variance tradeoff?](https://www.ibm.com/think/topics/bias-variance-tradeoff)
- [GeeksforGeeks — Underfitting and Overfitting in Machine Learning](https://www.geeksforgeeks.org/machine-learning/underfitting-and-overfitting-in-machine-learning/)

</details>

### What is regularization, and what's the difference between L1 (Lasso) and L2 (Ridge)?

`ml-l1-l2-regularization` · medium

<details><summary>Hints</summary>

- Both add a term to the loss that punishes big weights. The difference is how they measure 'big'.
- One measures with absolute values, the other with squares. That single choice is why one zeroes coefficients out and the other just shrinks them.
- L1/Lasso = sum of absolute values → sparse, does feature selection. L2/Ridge = sum of squares → smooth shrinkage, keeps all features. λ tunes strength.

</details>

<details><summary>Reference answer</summary>

Regularization fights overfitting by adding a penalty on model complexity to the loss, so the optimizer is discouraged from learning large weights that fit noise. You minimize (training loss + λ · penalty), where λ controls the strength: too small does nothing, too large underfits. L1 (Lasso) penalizes the sum of the absolute values of the coefficients. Its geometry (a diamond-shaped constraint with corners on the axes) tends to push some coefficients to exactly zero. So L1 performs automatic feature selection and yields sparse models, which is great when you have many features and suspect most are irrelevant. L2 (Ridge) penalizes the sum of the squared coefficients. It shrinks all weights smoothly toward zero but rarely to exactly zero, spreading weight across correlated features and stabilizing the solution, which is good when many features are useful or highly correlated. In short: L1 → sparsity/selection, L2 → smooth shrinkage/stability. Elastic Net combines both. Either way you regularize to trade a bit of bias for a meaningful drop in variance.

Key points:

- Regularization adds a complexity penalty to the loss to reduce overfitting: minimize (loss + λ · penalty)
- λ (regularization strength) tunes the tradeoff: too high underfits, too low doesn't help
- L1 (Lasso): penalizes sum of |coefficients| → drives some to exactly zero → sparsity + feature selection
- L2 (Ridge): penalizes sum of coefficients² → shrinks all weights smoothly toward (not to) zero
- L1 is good with many irrelevant features. L2 is good with correlated/useful features and stabilizes the solution
- Elastic Net blends L1 and L2, and conceptually you trade a little bias for lower variance

</details>

**Follow-ups**

- Why does L1's geometry produce exactly-zero coefficients while L2 doesn't?
- You have thousands of features and suspect most are noise. Which penalty and why?
- How do you choose λ in practice?
- What's Elastic Net and when would you use it over pure L1 or L2?

**Check yourself**

1. Which regularizer tends to drive some coefficients to exactly zero, effectively selecting features?
   - a) L1 (Lasso)
   - b) L2 (Ridge)
   - c) Neither — both only shrink coefficients slightly
   - d) Both zero out coefficients equally

   <details><summary>Answer</summary>a — L1's absolute-value penalty has corners on the axes, so the optimum often lands with some coefficients at exactly zero — automatic feature selection. L2 shrinks smoothly but keeps them non-zero.</details>

2. What is the primary purpose of adding a regularization penalty to the loss?
   - a) Reduce overfitting by discouraging overly large/complex weights
   - b) Speed up training by using fewer epochs
   - c) Increase model capacity to fit the training data better
   - d) Guarantee the model reaches zero training error

   <details><summary>Answer</summary>a — Regularization penalizes complexity to lower variance and improve generalization — the opposite of maximizing training fit.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} regularization adds the sum of absolute values and yields sparse models; {1} regularization adds the sum of squares and shrinks weights smoothly.', 'blanks': ['L1', 'L2'], 'chips': ['L1', 'L2', 'Dropout', 'L0']}
- {'kind': 'recall', 'front': 'L1 vs L2: which gives sparsity and which gives smooth shrinkage?', 'back': 'L1 (Lasso) penalizes absolute values and drives some coefficients to exactly zero → sparsity and feature selection. L2 (Ridge) penalizes squares and shrinks all weights smoothly toward zero without eliminating them.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Built In — L1 and L2 Regularization Methods, Explained](https://builtin.com/data-science/l2-regularization)
- [Towards Data Science — Understanding L1 and L2 Regularization](https://towardsdatascience.com/understanding-l1-and-l2-regularization-93918a5ac8d0/)

</details>

### What's the difference between precision and recall, and when do you optimize for each?

`ml-precision-vs-recall` · medium

<details><summary>Hints</summary>

- Both focus on the positive class but count different mistakes: one cares about false positives, the other about false negatives.
- Ask 'of what I flagged, how much was right?' (precision) versus 'of all the real positives, how many did I catch?' (recall).
- Precision = TP/(TP+FP), penalizes false positives. Recall = TP/(TP+FN), penalizes false negatives. Optimize recall when misses hurt (fraud/disease), precision when false alarms hurt (spam). F1 balances both.

</details>

<details><summary>Reference answer</summary>

Both come from the confusion matrix and answer different questions about the positive class. Precision = TP / (TP + FP): of everything the model flagged positive, what fraction was correct, punishing false positives. Recall (sensitivity) = TP / (TP + FN): of all the actual positives, what fraction did the model catch, punishing false negatives. There's a tradeoff: pushing the decision threshold to catch more positives (higher recall) usually lets in more false alarms (lower precision), and vice versa. Which you optimize depends on the cost of each error type. Optimize recall when missing a positive is expensive (disease screening, fraud detection, security). You'd rather tolerate false alarms than miss a real case. Optimize precision when a false positive is costly or annoying (spam filtering, recommending content, flagging accounts for suspension). You don't want to wrongly act on negatives. When you need one number that balances both, use the F1 score (harmonic mean of precision and recall). It's far more informative than accuracy on imbalanced data, where a majority-class baseline can look "accurate" while catching none of the minority class.

Key points:

- Precision = TP / (TP + FP): correctness of positive predictions, penalizing false positives
- Recall = TP / (TP + FN): coverage of actual positives, penalizing false negatives
- Precision-recall tradeoff: moving the threshold trades one for the other
- Optimize recall when false negatives are costly (disease, fraud, security)
- Optimize precision when false positives are costly (spam, recommendations, account suspension)
- F1 = harmonic mean of precision and recall, one balanced number
- On imbalanced data, accuracy is misleading, so precision/recall/F1 are the right lens

</details>

**Follow-ups**

- How does moving the classification threshold change precision and recall?
- When would you use the F1 score versus AUC-ROC versus PR-AUC?
- Why is accuracy a bad metric for a 99%-negative dataset?
- What's the difference between recall and specificity?

**Check yourself**

1. A cancer-screening model must avoid missing sick patients, even at the cost of some false alarms. Which metric do you prioritize?
   - a) Recall
   - b) Precision
   - c) Raw accuracy
   - d) Training loss

   <details><summary>Answer</summary>a — A missed sick patient (false negative) is the costly error, so you maximize recall — catching as many true positives as possible, tolerating extra false positives.</details>

2. Precision is defined as:
   - a) TP / (TP + FP) — of predicted positives, the fraction actually positive
   - b) TP / (TP + FN) — of actual positives, the fraction caught
   - c) (TP + TN) / total — overall correctness
   - d) FP / (FP + TN) — the false-positive rate

   <details><summary>Answer</summary>a — Precision measures how many flagged positives were correct: TP / (TP + FP). TP / (TP + FN) is recall.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} = TP / (TP + FP) and penalizes false positives; {1} = TP / (TP + FN) and penalizes false negatives.', 'blanks': ['Precision', 'Recall'], 'chips': ['Precision', 'Recall', 'Accuracy', 'Specificity']}
- {'kind': 'recall', 'front': 'When do you optimize for recall over precision?', 'back': 'When a false negative (a missed positive) is more costly than a false alarm — e.g. disease screening, fraud, security. Optimize precision instead when false positives are the expensive error (spam filtering, recommendations).'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Google for Developers — Classification: Accuracy, recall, precision, and related metrics](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall)
- [DataCamp — F1 Score: A Balanced Metric for Precision and Recall](https://www.datacamp.com/tutorial/f1-score)

</details>

### What's the difference between supervised and unsupervised learning?

`ml-supervised-vs-unsupervised` · easy

<details><summary>Hints</summary>

- The whole distinction hinges on one property of the training data.
- If every example comes with the 'right answer', you're in one regime. If you only have raw inputs and must find patterns yourself, you're in the other.
- Supervised = labeled data, predict a target (classification/regression). Unsupervised = unlabeled data, find structure (clustering, dimensionality reduction).

</details>

<details><summary>Reference answer</summary>

The difference is whether the training data has labels. Supervised learning trains on labeled examples (each input paired with the correct output). It learns a mapping from inputs to outputs so it can predict labels for new data. Its two main tasks are classification (discrete labels, e.g. spam/not-spam) and regression (continuous values, e.g. house price). You can measure accuracy directly because you have ground truth. Unsupervised learning trains on unlabeled data and looks for hidden structure, with no target to predict. Its main tasks are clustering (group similar points, e.g. customer segments), dimensionality reduction (compress features, e.g. PCA), and anomaly detection. Evaluation is fuzzier because there's no ground-truth label to check against. Use supervised learning when you have labels and a clear prediction target. Use unsupervised learning to explore, segment, or reduce data when labels are unavailable or expensive. (Semi-supervised and self-supervised sit in between, using a little labeled data or labels derived from the data.)

Key points:

- Core difference: supervised uses labeled data, unsupervised uses unlabeled data
- Supervised goal: learn input→output mapping to predict labels on new data
- Supervised tasks: classification (discrete) and regression (continuous)
- Unsupervised goal: discover hidden structure with no target variable
- Unsupervised tasks: clustering, dimensionality reduction, anomaly detection
- Supervised is easy to evaluate against ground truth, but unsupervised evaluation is harder (no labels)
- Semi-supervised / self-supervised are middle grounds

</details>

**Follow-ups**

- Give an example task for each and the algorithm you'd use.
- How do you evaluate an unsupervised model without labels?
- Where does self-supervised learning (as in LLM pretraining) fit in?
- What's semi-supervised learning and when is it useful?

**Check yourself**

1. You have 50,000 emails each tagged 'spam' or 'not spam' and want to classify new emails. What kind of learning is this?
   - a) Supervised learning (classification)
   - b) Unsupervised learning (clustering)
   - c) Reinforcement learning
   - d) Dimensionality reduction

   <details><summary>Answer</summary>a — The data is labeled and the goal is to predict a discrete label for new inputs — that's supervised classification.</details>

2. Which task is a classic example of unsupervised learning?
   - a) Clustering customers into segments with no predefined labels
   - b) Predicting tomorrow's temperature from labeled historical data
   - c) Classifying images as cat or dog using a labeled training set
   - d) Forecasting a house's sale price from past sales

   <details><summary>Answer</summary>a — Clustering discovers structure in unlabeled data with no target variable. The other options all have labels/targets, making them supervised.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} learning trains on labeled data to predict a target; {1} learning finds structure in unlabeled data.', 'blanks': ['Supervised', 'Unsupervised'], 'chips': ['Supervised', 'Unsupervised', 'Reinforcement', 'Federated']}
- {'kind': 'recall', 'front': "Supervised vs unsupervised — what decides which one you're doing?", 'back': 'Whether your data is labeled. Labeled + predicting a target = supervised (classification/regression). Unlabeled + finding hidden structure = unsupervised (clustering, dimensionality reduction, anomaly detection).'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [IBM — Supervised vs. Unsupervised Learning: What's the Difference?](https://www.ibm.com/think/topics/supervised-vs-unsupervised-learning)
- [Google Cloud — Supervised vs. unsupervised learning](https://cloud.google.com/discover/supervised-vs-unsupervised-learning)

</details>

## rag

### How do you handle citations and source attribution in a RAG system?

`rag-citations-source-attribution` · medium

<details><summary>Hints</summary>

- Provenance has to start before generation. What must you attach to a chunk the moment you index it?
- Think of two jobs: making the model emit citations, and checking those citations are real. Watch out for an answer that looks cited but isn't actually supported.
- Index-time metadata + stable chunk IDs -> instruct the model to cite each claim (inline [id] or post-hoc attribution) -> verify the cited span entails the claim to avoid 'citation-shaped hallucination' -> render clickable links to page/section.

</details>

<details><summary>Reference answer</summary>

Citations are what turn a plausible answer into a verifiable one, so build them into the pipeline rather than bolting them on. Start at ingestion: attach metadata to every chunk (source document, URL/title, page, section) and keep a stable chunk ID through retrieval so you always know where a passage came from. At generation, give the model the chunks tagged with those IDs and instruct it to attach a citation to each claim, ideally with a verbatim evidence span. Two broad strategies: simultaneous (the model emits [id] markers inline as it writes) or post-hoc (generate the answer, then attribute each sentence back to the best-supporting chunk, e.g. with an NLI/entailment check). Then verify. The dangerous failure is "citation-shaped hallucination", where the answer looks grounded (has quotes/links) but the cited source doesn't actually support the claim. Check that the cited span entails the statement. In the UI, render citations as resolvable links back to the exact page/section so users can click through and audit.

Key points:

- Preserve provenance at index time: per-chunk metadata (source, page, section) + stable chunk IDs kept through retrieval
- Prompt the model to cite each claim, tagging chunks with IDs, and prefer verbatim evidence spans
- Two strategies: simultaneous inline [id] markers vs post-hoc attribution (map each sentence to its supporting chunk)
- Verify against 'citation-shaped hallucination': confirm the cited span actually entails the claim (e.g. NLI check)
- Render citations as resolvable links to the exact page/section for user audit

</details>

**Follow-ups**

- How do you detect a citation that looks valid but doesn't support the claim?
- What are the trade-offs of inline citations while generating vs attributing after the fact?
- How do you cite when an answer synthesizes several chunks?

**Check yourself**

1. Where does reliable source attribution have to begin?
   - a) At ingestion — attach source/page/section metadata and a stable chunk ID to every chunk
   - b) Only at generation — the model can infer sources on its own
   - c) After deployment, by manually labeling answers
   - d) In the embedding model's weights

   <details><summary>Answer</summary>a — You can only cite what you tracked. Provenance metadata and stable IDs must be captured at index time and carried through retrieval to generation.</details>

2. What is a 'citation-shaped hallucination'?
   - a) An answer that looks grounded (quotes/links) but the cited source doesn't actually support the claim
   - b) A citation formatted in the wrong style guide
   - c) A missing citation on a correct answer
   - d) A duplicate citation on the same sentence

   <details><summary>Answer</summary>a — The claim is unsupported or distorted even though a source marker is present — which is why you verify that the cited span actually entails the statement.</details>

**Exercises**

- {'kind': 'fill', 'template': 'Attach provenance {0} at index time, then verify that each cited {1} actually supports the claim.', 'blanks': ['metadata', 'span'], 'chips': ['metadata', 'span', 'temperature', 'embedding']}
- {'kind': 'recall', 'front': 'How do you guard against fake-looking citations in RAG?', 'back': 'Verify grounding: confirm the cited evidence span actually entails the claim (e.g. an NLI/faithfulness check), not just that a source marker is present. Pair this with index-time provenance and clickable source links.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Tensorlake — Citation-Aware RAG: fine-grained citations in retrieval and response synthesis](https://www.tensorlake.ai/blog/rag-citations)
- [Henry Ruiz — Building Trustworthy RAG Systems with In-Text Citations](https://haruiz.github.io/blog/improve-rag-systems-reliability-with-citations)
- [DEV Community — Unlocking Advanced RAG: Citations and Attributions](https://dev.to/experilearning/unlocking-advanced-rag-citations-and-attributions-59lk)

</details>

### What are the key tradeoffs when designing a RAG system?

`rag-design-tradeoffs` · hard

<details><summary>Hints</summary>

- Most answers collapse into one triangle. What three things are you constantly trading against each other in retrieval?
- Go knob by knob (chunk size, top-k, reranking, retrieval method, index type) and for each say what you gain and what you pay.
- It's quality vs latency vs cost (plus freshness/complexity). Small vs large chunks, high vs low top-k, rerank or not, keyword/vector/hybrid, exact vs ANN index, re-index often or not. No universal optimum, so tune to the product and validate with eval.

</details>

<details><summary>Reference answer</summary>

Almost every RAG design decision is a knob on the same triangle: retrieval quality (recall/precision) vs latency vs cost, with freshness and complexity as extra axes. Chunk size: small chunks give precise retrieval but fragment context and inflate the index. Large chunks preserve context but add noise, tokens, and cost. Top-k: retrieving more raises recall but stuffs the prompt, raising latency, token cost, and distraction. Too few risks missing the answer. Reranking: a cross-encoder reranker sharply improves precision but adds a compute/latency step. It's worth it for high-value queries, overkill for cheap ones. Retrieval method: keyword is cheap and exact, vector captures meaning, hybrid is best quality but more moving parts. Index type: exact search is accurate but doesn't scale, ANN is fast but trades some recall, and heavy compression saves memory at recall cost. Freshness vs cost: frequent re-indexing keeps answers current but costs compute. Advanced tricks (contextual retrieval, hierarchical chunking) lift accuracy but add ingestion cost and latency. There's no globally right setting. You tune to the product's quality bar, latency budget, and cost ceiling, and validate with eval.

Key points:

- Central tension: retrieval quality (recall/precision) vs latency vs cost. Freshness and complexity are extra axes
- Chunk size: small = precise but fragmented + bigger index, large = more context but noisier + costlier
- Top-k: more = higher recall but more tokens/latency/distraction, fewer = risk of missing the answer
- Reranking: big precision gain, extra latency/compute, worth it for high-value queries
- Retrieval method (keyword/vector/hybrid) and index (exact vs ANN vs compressed) trade accuracy against speed/scale/memory
- Freshness vs cost: re-indexing frequency. No universal optimum, tune to quality bar, latency budget, cost ceiling, and eval it

</details>

**Follow-ups**

- You have a strict latency budget, so which knobs do you turn first?
- When is reranking not worth the added latency?
- How does chunk size interact with top-k and the context window?

**Check yourself**

1. What's the trade-off of increasing top-k (retrieving more chunks per query)?
   - a) Higher recall, but more prompt tokens, latency, cost, and model distraction
   - b) Higher recall with no downside at all
   - c) It fine-tunes the model on the retrieved chunks
   - d) It reduces the index size

   <details><summary>Answer</summary>a — More chunks raise the chance the answer is present (recall) but stuff the context window — increasing tokens, latency, cost, and the risk the model is distracted by irrelevant passages.</details>

2. Which best describes the chunk-size trade-off?
   - a) Small chunks = precise retrieval but fragmented context; large chunks = more context but noisier and costlier
   - b) Larger chunks always retrieve more precisely
   - c) Chunk size has no effect on retrieval quality
   - d) Smaller chunks always reduce total cost

   <details><summary>Answer</summary>a — Small chunks localize the match but can split key context and bloat the index; large chunks keep context together but add noise and tokens. It's a balance, not a strict better/worse.</details>

**Exercises**

- Match each RAG knob to its main trade-off
- {'kind': 'recall', 'front': 'The one sentence that frames RAG design trade-offs?', 'back': "Nearly every knob (chunk size, top-k, reranking, retrieval method, index type, re-index frequency) trades retrieval quality against latency and cost — there's no universal optimum, so tune to the product's quality bar and budget and validate with eval."}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [The New Stack — Eliminating the Precision-Latency Trade-Off in Large-Scale RAG](https://thenewstack.io/eliminating-the-precision-latency-trade-off-in-large-scale-rag/)
- [Atlan — Chunking Strategies for RAG: Methods, Trade-offs & Best Practices](https://atlan.com/know/chunking-strategies-rag/)
- [Ragie — The Architect's Guide to Production RAG](https://www.ragie.ai/blog/the-architects-guide-to-production-rag-navigating-challenges-and-building-scalable-ai)

</details>

### What are common RAG failure points, and how do you debug them?

`rag-failure-points-debugging` · hard

<details><summary>Hints</summary>

- Before naming failures, split the pipeline in half: retrieval vs generation. That framing is what interviewers want.
- Walk each stage: is the answer even in the corpus? indexed but ranked too low? retrieved but dropped from context? in context but ignored by the model? Each is a different fix.
- Reference the seven failure points (missing content, missed top-k, not in context, not extracted, wrong format, wrong specificity, incomplete). Debug by logging retrieved chunks: wrong chunk = fix retrieval, right chunk + wrong answer = fix prompt/model. Validate continuously in operation.

</details>

<details><summary>Reference answer</summary>

Debug RAG by splitting it into retrieval failures and generation failures, then isolating which stage broke. Barnett et al.'s "seven failure points" is a good map: (1) missing content: the answer isn't in the corpus at all. (2) missed top-k: it's in the index but ranked too low to be retrieved. (3) not in context: retrieved but dropped during consolidation/reranking or truncated by the context window. (4) not extracted: present in context but the model didn't use it (often noise/distraction). (5) wrong format: ignored a requested output format. (6) incorrect specificity: too vague or too detailed. (7) incomplete: misses parts even though the info was retrieved. To debug, instrument each stage: log the retrieved chunks and look at them independently of the LLM. If the right chunk isn't retrieved, the problem is upstream: chunking, embeddings, or the index (fix chunk size, try hybrid search, add a reranker). If the right chunk was retrieved but the answer is still wrong, it's a generation/prompt problem: context stuffing/order, prompt instructions, or the model. A key insight from the paper: RAG robustness can only be validated in operation, so you need continuous eval, not a one-time design.

Key points:

- Split failures into retrieval-side vs generation-side and isolate the broken stage
- Seven failure points (Barnett et al.): missing content, missed top-k ranking, not in context (consolidation/window), not extracted, wrong format, incorrect specificity, incomplete
- Debug retrieval first: log and look at retrieved chunks independently of the LLM
- Wrong chunk retrieved -> fix chunking, embeddings, hybrid search, reranking
- Right chunk retrieved but wrong answer -> prompt/context ordering/model problem
- RAG robustness is validated in operation -> continuous evaluation, not one-time design

</details>

**Follow-ups**

- How do you tell a retrieval failure apart from a generation failure in production?
- The right chunk is retrieved but the model ignores it. What do you try?
- What would a RAG eval suite measure to catch these before users do?

**Check yourself**

1. The correct chunk IS in the retrieved context, but the model's answer is still wrong. Where do you look first?
   - a) Generation side — prompt instructions, context ordering, or the model
   - b) The embedding model — retrieval clearly failed
   - c) The chunk size — it must be too small
   - d) The vector index — it returned nothing useful

   <details><summary>Answer</summary>a — If the right chunk was retrieved, retrieval succeeded. A wrong answer then points to generation: the model didn't extract/use it (noise, ordering, prompt), not the retriever.</details>

2. A user's answer exists in the corpus and is indexed, but never shows up in results. Which failure point is this?
   - a) Missed top-k — it ranked too low to be retrieved
   - b) Missing content — it isn't in the corpus
   - c) Wrong format — the output format was ignored
   - d) Incomplete — the answer left parts out

   <details><summary>Answer</summary>a — It's present and indexed but ranked below the cutoff — the 'missed top-k' failure. Fixes: better embeddings, hybrid search, reranking, or a larger k.</details>

**Exercises**

- Order a debugging workflow for a wrong RAG answer
- {'kind': 'recall', 'front': 'First question when debugging a wrong RAG answer?', 'back': 'Was the correct chunk actually retrieved? Inspect the retrieved context directly. If no -> retrieval problem (chunking/embeddings/index/reranking). If yes -> generation problem (prompt/ordering/model).'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Barnett et al. — Seven Failure Points When Engineering a Retrieval Augmented Generation System (arXiv:2401.05856)](https://arxiv.org/abs/2401.05856)
- [ACM/IEEE CAIN 2024 — Seven Failure Points When Engineering a RAG System](https://dl.acm.org/doi/10.1145/3644815.3644945)
- [Sahin Ahmed (Medium) — The Common Failure Points of LLM RAG Systems and How to Overcome Them](https://medium.com/@sahin.samia/the-common-failure-points-of-llm-rag-systems-and-how-to-overcome-them-926d9090a88f)

</details>

### How would you stop a model from hallucinating when no information is found in the retrieved context?

`rag-hallucination-empty-context` · medium

<details><summary>Hints</summary>

- The core mindset shift: what should the model be allowed to say when it genuinely has nothing?
- Attack it at two points: before generation (was anything relevant even retrieved?) and after (is every claim actually grounded?).
- Instruct 'answer only from context, else say you don't know' + a retrieval relevance threshold that short-circuits on weak hits + mandatory citations + a faithfulness/verification check. Abstaining or escalating is a valid outcome.

</details>

<details><summary>Reference answer</summary>

Make "I don't know" a first-class, rewarded answer instead of letting the model fill the gap. Do it in layers. Prompt/instruction: explicitly tell the model to answer only from the provided context and to say it can't find the answer when the context doesn't support one. Retrieval gating: put a relevance/similarity threshold (and ideally a reranker score) on retrieval. If the top chunks don't clear it, treat retrieval as empty and short-circuit to a graceful "I couldn't find that" rather than passing weak context to the model. Grounded generation: require citations so every claim is tied to a retrieved span. An uncited claim is a red flag. Verification: optionally add a self-check/faithfulness pass (LLM-as-judge or NLI) that checks the answer is entailed by the context and suppresses or flags unsupported answers. And design the UX so abstaining, asking a clarifying question, or escalating to a human is an acceptable outcome.

Key points:

- Make abstention a valid answer: instruct the model to answer only from context and to say 'I don't know' when it can't
- Retrieval gating: similarity/rerank threshold. If nothing clears it, short-circuit instead of feeding weak context
- Grounded generation with mandatory citations, since uncited claims are suspect
- Verification pass (faithfulness / NLI / LLM-as-judge) to catch answers not entailed by context
- Fallback UX: clarifying question or human escalation beats a confident fabrication

</details>

**Follow-ups**

- How do you set the similarity threshold without rejecting good answers?
- How do you evaluate whether the model actually abstains when it should?
- What's the difference between a faithfulness check and a relevance check?

**Check yourself**

1. The retriever returns only low-similarity chunks for a query. What's the best behavior?
   - a) Short-circuit and tell the user you couldn't find the answer
   - b) Pass the weak chunks in and let the model answer confidently anyway
   - c) Answer from the model's parametric memory without saying so
   - d) Silently return the single closest chunk verbatim as the answer

   <details><summary>Answer</summary>a — A relevance threshold should gate retrieval: below it, treat context as empty and abstain gracefully rather than inviting a fabrication from weak or off-topic context.</details>

2. Which measure most directly makes hallucinated answers detectable after generation?
   - a) Requiring citations and checking every claim is entailed by the retrieved context
   - b) Increasing the model's temperature
   - c) Removing the system prompt
   - d) Returning more tokens per answer

   <details><summary>Answer</summary>a — Grounded generation with citations plus a faithfulness/entailment check ties claims to sources; uncited or unentailed claims flag likely hallucinations. Higher temperature increases them.</details>

**Exercises**

- {'kind': 'fill', 'template': "Instruct the model to answer only from {0}; if nothing clears the relevance {1}, it should say it doesn't know.", 'blanks': ['context', 'threshold'], 'chips': ['context', 'threshold', 'temperature', 'weights']}
- {'kind': 'recall', 'front': 'What single instruction most reduces gap-filling in RAG?', 'back': "Tell the model to answer only from the provided context and to explicitly say it can't find the answer when the context doesn't support one — backed by a retrieval relevance threshold and grounded, cited generation."}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [K2view — RAG hallucination: what it is and how to avoid it](https://www.k2view.com/blog/rag-hallucination/)
- [Atlan — LLM Hallucinations: Why They Happen and How to Reduce Them](https://atlan.com/know/llm-hallucinations/)
- [Sharvari Raut (Medium) — How to Stop LLM Hallucinations in RAG](https://sharur7.medium.com/how-to-stop-llm-hallucinations-in-retrieval-augmented-generation-rag-5ef2894f9cd6)

</details>

### You're building a system over huge PDF reports. How would you process them?

`rag-process-large-pdfs` · hard

<details><summary>Hints</summary>

- Where do most RAG systems actually fail on messy documents: the model, or the step before it?
- Think about the pipeline order and what makes PDFs hard specifically: multi-column layout, tables, section hierarchy, huge length.
- Layout-aware parse (keep structure, tables as tables) -> structure-aware chunking with metadata -> embed/index (hybrid) -> retrieve + rerank -> generate with page/section citations. Consider parent-child retrieval for long reports.

</details>

<details><summary>Reference answer</summary>

Big PDFs are a data-engineering problem before they're a retrieval problem. Most RAG failures trace back to ingestion, not the LLM. First, parse layout-aware: use a parser (LlamaParse, Unstructured, a layout model) that distinguishes body text from headings, tables, figures and captions, and keeps section hierarchy, not raw PyPDF2 text dumps that scramble multi-column pages. Handle tables specially: extract them as structured markdown/HTML rather than flattening them into plain text, which retrieves poorly. Then chunk semantically along structural boundaries (sections/subsections, ~300-800 tokens with overlap) rather than by blind fixed length, and attach metadata to every chunk (source file, page number, section heading) for filtering and citations. Embed the chunks, then index them (hybrid keyword + vector helps for report jargon and figures). At query time, retrieve top-k, optionally rerank, and generate with citations back to page/section. For long reports also consider hierarchical / parent-child retrieval so you can retrieve a precise child chunk but hand the model the wider parent context.

Key points:

- Ingestion is the bottleneck: parse quality decides retrieval quality, not the LLM
- Layout-aware parsing (LlamaParse/Unstructured/layout model): keep headings, sections, hierarchy. Don't raw-dump multi-column text
- Extract tables as structured markdown/HTML, not flattened text
- Semantic/structure-aware chunking (~300-800 tokens, overlap) beats blind fixed-size splits
- Attach metadata per chunk: source, page, section (for filtering and citations)
- Hierarchical / parent-child retrieval gives precise match + wider context for long reports

</details>

**Follow-ups**

- How would you handle scanned PDFs or images/charts inside the report?
- How do you pick a chunk size, and why does it matter here?
- How do you cite the exact page and section a claim came from?

**Check yourself**

1. Why prefer a layout-aware parser over PyPDF2/pdfminer raw text for big report PDFs?
   - a) It preserves headings, sections, and tables instead of scrambling multi-column layout
   - b) It fine-tunes the LLM on the PDF automatically
   - c) It removes the need to chunk or embed the documents
   - d) It is always faster than any other parser

   <details><summary>Answer</summary>a — Layout-aware parsers keep document structure (sections, tables, hierarchy), which is what raw text extractors destroy on complex PDFs. They don't replace chunking/embedding or touch model weights.</details>

2. What's the recommended way to handle tables inside the reports?
   - a) Extract them as structured markdown/HTML and keep them intact
   - b) Flatten each table into a sentence of prose before embedding
   - c) Drop all tables — they never contain useful information
   - d) Store tables only as images and never index them

   <details><summary>Answer</summary>a — Tables embedded as flattened prose retrieve poorly; keeping them structured preserves the row/column relationships that make them answerable.</details>

**Exercises**

- Order an ingestion pipeline for large PDF reports
- {'kind': 'recall', 'front': 'What is the single most important lever for quality when ingesting huge PDFs?', 'back': 'Parsing/chunking quality. Most RAG failures come from ingestion, not the LLM: layout-aware parsing that keeps structure and tables, then structure-aware chunking with metadata, sets the ceiling on retrieval quality.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [LlamaIndex — Mastering PDFs: extracting sections, headings, paragraphs and tables](https://www.llamaindex.ai/blog/mastering-pdfs-extracting-sections-headings-paragraphs-and-tables-with-cutting-edge-parser-faea18870125)
- [Koreadeep — Layout-Aware Chunking for RAG: Why Document Structure Decides Retrieval](https://koreadeep.com/en/blog/layout-aware-chunking-rag)
- [PremAI — Building Production RAG: Architecture, Chunking, Evaluation & Monitoring](https://blog.premai.io/building-production-rag-architecture-chunking-evaluation-monitoring-2026-guide/)

</details>

### How do you scale a RAG system to 10M+ articles?

`rag-scaling-10m-articles` · hard

<details><summary>Hints</summary>

- First, why can't you just do the same thing you'd do for 10k docs? What breaks at 10 million?
- Think along three axes: the index algorithm (exact vs approximate), the machine topology (one box vs many), and the retrieval funnel (how many candidates each stage touches).
- ANN index (HNSW/IVF) instead of brute force + product quantization for memory + sharding/replication across nodes + a two-stage retrieve-then-rerank funnel + metadata filters and caching. It's a recall/latency/cost/memory trade-off you eval continuously.

</details>

<details><summary>Reference answer</summary>

At 10M+ documents (often 100M+ chunks) brute-force similarity is impractical, so scaling is about the index, the topology, and a staged retrieval funnel. Index: use an approximate nearest neighbor (ANN) index (HNSW for high recall/low latency, IVF for memory-efficient clustering) instead of exact search. Both trade a little recall for a huge latency win. Memory: 10M+ high-dimensional vectors is terabytes of RAM, so compress with product quantization (PQ) to cut memory ~an order of magnitude at some recall cost. Topology: shard the index across nodes (partition the vectors, query all shards in parallel, aggregate the top results) and replicate shards to handle query volume and stay available. Retrieval funnel: do cheap high-recall ANN to pull a few hundred candidates, then an expensive high-precision reranker (cross-encoder) on just those. You don't rerank 10M docs, only the shortlist. Add metadata filtering to prune the search space (recency, source, ACLs), a semantic cache for repeated queries, and asynchronous/batched ingestion so the index stays fresh without blocking. Throughout it's a recall-vs-latency-vs-cost-vs-memory trade-off, so you need continuous eval to know where you sit.

Key points:

- Use ANN indexes (HNSW / IVF), not exact search, trading a little recall for large latency gains
- Compress with product quantization (PQ): 10M+ high-dim vectors is terabytes of RAM
- Shard the index across nodes (parallel query + aggregate) and replicate for throughput/availability
- Two-stage funnel: cheap high-recall ANN -> rerank only the shortlist with a cross-encoder
- Metadata filtering (recency/source/ACL) to prune search space, semantic cache for repeated queries
- Async/batched ingestion to keep the index fresh, continuous eval on recall-latency-cost-memory trade-offs

</details>

**Follow-ups**

- HNSW vs IVF vs IVF-PQ: how do you choose for 10M vectors at low latency?
- How do you keep the index fresh as new articles arrive without downtime?
- Why rerank only a shortlist instead of the whole corpus?

**Check yourself**

1. Why switch from exact nearest-neighbor search to an ANN index (HNSW/IVF) at 10M+ vectors?
   - a) Exact search is too slow at that scale; ANN trades a little recall for a large latency win
   - b) ANN indexes are always more accurate than exact search
   - c) Exact search cannot represent embeddings above 512 dimensions
   - d) ANN removes the need for a vector store entirely

   <details><summary>Answer</summary>a — Brute-force exact search scans everything and doesn't scale to millions; ANN approximates neighbors for millisecond latency, accepting a small, tunable recall drop.</details>

2. In a two-stage retrieval funnel at scale, what does the reranker operate on?
   - a) Only the small shortlist of candidates from the fast ANN stage
   - b) All 10M+ documents on every query
   - c) The raw query string before embedding
   - d) The full index, replacing the ANN stage

   <details><summary>Answer</summary>a — The cheap high-recall ANN stage narrows to a few hundred candidates; the expensive cross-encoder reranker only scores that shortlist — reranking the whole corpus would be prohibitively slow.</details>

**Exercises**

- Order a scaled retrieval funnel for a 10M+ article RAG
- {'kind': 'fill', 'template': 'Use an {0} index instead of brute force, and compress vectors with product {1} to fit memory.', 'blanks': ['ANN', 'quantization'], 'chips': ['ANN', 'quantization', 'keyword', 'temperature']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [DesignGurus — System Design for RAG: Vector Databases, Chunking, and Re-ranking](https://www.designgurus.io/blog/system-design-for-rag)
- [Milvus — Strategies to scale the vector store for a large RAG knowledge base](https://milvus.io/ai-quick-reference/what-strategies-could-be-used-to-scale-the-vector-store-component-for-a-rag-system-dealing-with-a-very-large-knowledge-base-or-high-query-volume-sharding-indexing-optimizations-etc)
- [Towards Data Science — HNSW at Scale: Why Your RAG System Gets Worse as the Vector Database Grows](https://towardsdatascience.com/hnsw-at-scale-why-your-rag-system-gets-worse-as-the-vector-database-grows/)

</details>

### What is semantic caching?

`rag-semantic-caching` · easy

<details><summary>Hints</summary>

- Contrast it with an ordinary cache: what has to match for a normal cache to hit, and why does that almost never happen with natural-language questions?
- It's embeddings plus a similarity threshold. What do you compare, and what do you return on a hit?
- Embed the incoming query, similarity-search it against past query embeddings. If the nearest is above a threshold, return the stored response instead of calling the LLM. Saves cost/latency, but too-loose a threshold causes false hits.

</details>

<details><summary>Reference answer</summary>

Semantic caching is a cache that matches queries by meaning instead of exact string. A normal cache only hits when a new request is byte-for-byte identical to a past one. That almost never happens with natural language, where "reset my password" and "how do I change my password?" are the same intent worded differently. A semantic cache embeds each incoming query into a vector, compares it (usually cosine similarity) against the vectors of previously seen queries, and if the closest one is above a similarity threshold, returns the stored response instead of calling the LLM (or re-running retrieval) again. Components: an embedding model, a vector store for cached query embeddings, a response store, and a tunable similarity threshold. The payoff is big cost and latency reduction on repeated/similar traffic. A too-loose threshold serves a cached answer to a subtly different question (a false hit), so you tune the threshold, and often scope or invalidate the cache when the underlying data changes.

Key points:

- Matches queries by semantic meaning, not exact string, so paraphrases hit the cache
- Mechanism: embed query -> similarity search vs cached query embeddings -> return stored answer if above threshold
- Components: embedding model, vector store (cached queries), response store, similarity threshold
- Benefit: large cost and latency savings on repeated/similar queries
- Risk: threshold too loose -> false hits (right-looking answer to a slightly different question), tune it and invalidate on data change

</details>

**Follow-ups**

- How do you set the similarity threshold, and what breaks if it's too loose or too strict?
- How is a semantic cache invalidated when the underlying documents change?
- Where does the cache sit: in front of the LLM, the retriever, or both?

**Check yourself**

1. How does a semantic cache differ from a traditional exact-match cache?
   - a) It returns a cached response when a new query is semantically similar, not just identical
   - b) It stores responses on disk instead of in memory
   - c) It caches the model weights rather than responses
   - d) It only works when two queries are byte-for-byte identical

   <details><summary>Answer</summary>a — Semantic caching uses embedding similarity to match meaning, so paraphrased queries hit; exact-match caching requires identical strings, which rarely occurs in natural language.</details>

2. What is the main risk of setting the similarity threshold too low (loose)?
   - a) False cache hits — serving a stored answer to a subtly different question
   - b) The cache will never return any result
   - c) Embeddings stop being computed
   - d) It doubles the LLM's token cost

   <details><summary>Answer</summary>a — A loose threshold treats not-quite-the-same queries as matches, returning a cached answer that doesn't actually fit — the classic false-hit failure. Too strict, and you miss valid hits.</details>

**Exercises**

- {'kind': 'fill', 'template': 'A semantic cache embeds the query, does a {0} search against cached queries, and returns the stored answer if above a {1}.', 'blanks': ['similarity', 'threshold'], 'chips': ['similarity', 'threshold', 'keyword', 'temperature']}
- {'kind': 'recall', 'front': 'One-line definition of semantic caching?', 'back': 'A cache keyed by meaning: embed the query, similarity-search past queries, and return the stored response when the match clears a threshold — avoiding a redundant LLM call and cutting cost/latency.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Kuldeep Paul (DEV) — Reducing LLM Cost and Latency Using Semantic Caching](https://dev.to/kuldeep_paul/reducing-llm-cost-and-latency-using-semantic-caching-3bn9)
- [GPT Semantic Cache: Reducing LLM Costs and Latency via Semantic Embedding Caching (arXiv:2411.05276)](https://arxiv.org/abs/2411.05276)
- [PyImageSearch — Semantic Caching for LLMs: FastAPI, Redis, and Embeddings](https://pyimagesearch.com/2026/04/27/semantic-caching-for-llms-fastapi-redis-and-embeddings/)

</details>

### Text vs vector search — when would you use each?

`rag-text-vs-vector-search` · medium

<details><summary>Hints</summary>

- Think about the two things a query can be about: exact tokens versus meaning.
- One is great for SKUs, error codes, and names, while the other is great for synonyms and paraphrases. Which is which, and what's each one's blind spot?
- Keyword/BM25 = exact match, weak on vocabulary mismatch. Vector = semantic meaning, weak on exact strings. Most production RAG runs both and fuses scores (hybrid search).

</details>

<details><summary>Reference answer</summary>

Text (keyword/lexical) search, usually BM25, matches the exact tokens in the query. It's fast, cheap, needs no embedding model, and is unbeatable for exact identifiers: product SKUs, error codes, names, acronyms, legal citations. Its weakness is vocabulary mismatch: it misses relevant content that uses different words. Vector (semantic) search embeds the query and documents into a shared space and retrieves by cosine similarity, so it finds content by meaning even when wording differs (synonyms, paraphrases, cross-lingual). Its weakness is exact matches: it can drift on rare tokens and precise strings. Use keyword for "where is that exact thing?", vector for "what did the user mean?". In practice most production RAG uses hybrid search: run both and fuse the scores (e.g. reciprocal rank fusion) to get keyword precision plus semantic recall.

Key points:

- Text/keyword search (BM25): exact-token matching. Fast, cheap, no embeddings. Best for IDs, codes, names, rare terms
- Keyword weakness: vocabulary mismatch, missing relevant docs that use different words
- Vector/semantic search: embed query + docs, retrieve by similarity, finds meaning across synonyms/paraphrase
- Vector weakness: can miss exact strings and rare identifiers
- Hybrid search fuses both (e.g. reciprocal rank fusion) and is the usual production default

</details>

**Follow-ups**

- How would you combine the two scores: what's reciprocal rank fusion?
- Your users search by part numbers and error codes, so which do you rely on, and why?
- When does pure vector search actively hurt retrieval quality?

**Check yourself**

1. A user searches for the exact error code 'ERR_0x8004'. Which retrieval method is most reliable?
   - a) Keyword/BM25 search — it matches the exact token
   - b) Vector search — embeddings capture the code's meaning best
   - c) Neither; error codes cannot be retrieved
   - d) Vector search, because it is always more accurate than keyword search

   <details><summary>Answer</summary>a — Exact identifiers like error codes are keyword search's strength and vector search's weakness — embeddings can drift on rare, meaningless-to-semantics tokens.</details>

2. Why is hybrid search common in production RAG?
   - a) It combines keyword precision with semantic recall by fusing both rankings
   - b) It removes the need for a language model
   - c) It is always cheaper than either method alone
   - d) It guarantees 100% retrieval recall

   <details><summary>Answer</summary>a — Hybrid fuses lexical and semantic scores (e.g. reciprocal rank fusion) to cover each method's blind spot; it isn't cheaper or a correctness guarantee.</details>

**Exercises**

- {'kind': 'fill', 'template': '{0} search matches exact tokens (good for IDs); {1} search matches meaning via embeddings (good for synonyms).', 'blanks': ['Keyword', 'Vector'], 'chips': ['Keyword', 'Vector', 'Fuzzy', 'Graph']}
- {'kind': 'recall', 'front': 'When do you pick keyword search over vector search?', 'back': 'When exact-token precision matters — identifiers, codes, names, rare terms — or when you need cheap, embedding-free retrieval. Vector search wins on semantic/meaning-based matching; hybrid gets both.'}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Redis — Hybrid search explained: full-text meets vector search](https://redis.io/blog/hybrid-search-explained/)
- [Meilisearch — Understanding hybrid search RAG for better AI answers](https://www.meilisearch.com/blog/hybrid-search-rag)
- [MongoDB — Hybrid Search Explained With An In-Depth Guide](https://www.mongodb.com/resources/products/capabilities/hybrid-search)

</details>

### What's RAG? Explain the complete process

`rag-what-is-rag` · medium

<details><summary>Reference answer</summary>

RAG (Retrieval-Augmented Generation) makes an LLM answer from your own data instead of only its frozen training weights. Offline, you chunk your documents, embed each chunk into a vector, and store those vectors in an index. At query time you embed the user's question, retrieve the top-k most similar chunks, paste that context into the prompt, and let the LLM generate a grounded answer, often with citations. The model's weights never change, only what's in the context window. This reduces hallucinations and lets you serve fresh, domain-specific knowledge.

Key points:

- Retrieval augments the prompt with external context, and the model's weights are unchanged (not fine-tuning)
- Offline/ingestion path: chunk documents, embed chunks, store vectors in an index
- Online/query path: embed the query, retrieve top-k similar chunks, augment the prompt, generate
- Grounding the answer in retrieved context reduces hallucination and enables source citations
- Lets the LLM use fresh and private/domain data without retraining

</details>

**Follow-ups**

- How do you handle it when nothing relevant is retrieved?
- How do you chunk documents, and why does chunk size matter?
- When would you fine-tune instead of (or in addition to) using RAG?
- How do you evaluate a RAG pipeline's retrieval and generation quality?

**Check yourself**

1. How does RAG change the language model itself?
   - a) It doesn't — RAG adds retrieved context to the prompt; the weights are unchanged
   - b) It fine-tunes the model on your documents at query time
   - c) It retrains the base model nightly on retrieved chunks
   - d) It replaces the model's tokenizer with your vocabulary

   <details><summary>Answer</summary>a — RAG augments the prompt with retrieved context. No weights change — that's what distinguishes it from fine-tuning.</details>

2. What is the main benefit of grounding generation in retrieved context?
   - a) Reduces hallucination and lets the model cite sources
   - b) Guarantees the model never makes a mistake
   - c) Removes the need for a language model entirely
   - d) Makes the model smaller on disk

   <details><summary>Answer</summary>a — Grounding answers in retrieved passages reduces hallucination and enables source attribution; it doesn't make the model perfect or unnecessary.</details>

**Exercises**

- Order the RAG pipeline from raw documents to a grounded answer
- {'kind': 'fill', 'template': '{0} search finds exact tokens; {1} search finds meaning via embeddings.', 'blanks': ['Keyword', 'Vector'], 'chips': ['Keyword', 'Vector', 'Fuzzy', 'Graph']}
- {'kind': 'explain'}

<details><summary>Sources</summary>

- [Databricks — What is Retrieval Augmented Generation (RAG)?](https://www.databricks.com/blog/what-is-retrieval-augmented-generation)
- [NVIDIA — RAG 101: Demystifying Retrieval-Augmented Generation Pipelines](https://developer.nvidia.com/blog/rag-101-demystifying-retrieval-augmented-generation-pipelines/)
- [AWS — What is RAG (Retrieval-Augmented Generation)?](https://aws.amazon.com/what-is/retrieval-augmented-generation/)

</details>
