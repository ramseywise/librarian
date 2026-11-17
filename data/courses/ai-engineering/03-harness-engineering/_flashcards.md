---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/03-harness-engineering/slides/deck.yaml
cards:
- front: What are the six parts of this lecture, in order?
  back: The lecture runs from why a demo fails, through tools, boundaries, checks, long runs and more agents, to the repo a fresh session reads.
  lesson: ai-engineering/03-harness-engineering/readme
- front: Name four things this lecture teaches you to do with an agent.
  back: You will be able to restate a failure as harness, constrain tools, make done checkable and keep an agent going across sessions and agents.
  lesson: ai-engineering/03-harness-engineering/readme
- front: What separates a production harness from a demo?
  back: Context plus tools is the demo, while constrain, verify and correct make up the production harness.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: Where do the constraint, correction and verification for a refund tool live, and why there?
  back: Put limits, retries and confirmation in code around the tool call, where the model cannot talk its way past them.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: What did Agashe et al. change to take a small model above frontier models on OSWorld?
  back: Changing only the interfaces around a fixed small model can overtake frontier models, at a fraction of the cost per task.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: What should you restate every agent failure as, and why?
  back: Every agent failure should be restated as a missing piece of harness, because that restatement is a build task.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: What four parts must every harness have?
  back: A system missing any of acceptance, boundary, feedback or rollback is a prompt with tools attached, not a harness.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: What is the harness ratchet?
  back: A harness grows by encoding each real failure as a check, so it cannot recur.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: 'An agent is confidently wrong rather than stuck: which subsystem has the gap?'
  back: Agents are rarely stuck, often confidently wrong, which points at a feedback gap.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: What do you build on Monday morning, and what comes after?
  back: Start with a tool loop, sandbox, filesystem, plan file, one verification gate and traces, then add constraints as failures show up.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: 'A tool is misused: what do you check first?'
  back: When a tool is misused, check the tool description before questioning the model.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: What did adding invocation examples buy in Li's measurement?
  back: Adding one to five invocation examples moved tool-call accuracy from about 72% to 90% in Li's measurement.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Which tool actions deserve a gate?
  back: Gate only the irreversible, because gating reversible actions is the most common way to make an agent useless.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Why discover tool definitions on demand instead of loading them all up front?
  back: Eagerly loaded tool definitions can take a large share of the window, so discover them on demand and append new ones.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Why should a skill description read like a routing rule rather than a summary?
  back: Only a skill's name and description stay resident, so the description's job is deciding when the skill fires.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: How do you defend against a poisoned MCP tool description?
  back: Treat a tool description as untrusted code, pin and diff descriptions, and break the lethal triad (private data, untrusted content, an exfiltration channel).
  lesson: ai-engineering/03-harness-engineering/notes/03b-mcp-write-safety-and-async-tools
- front: Why must a write tool without an idempotency key never be auto-retried?
  back: A tool with no idempotency key must never be auto-retried, because one timeout can become three charged invoices.
  lesson: ai-engineering/03-harness-engineering/notes/03b-mcp-write-safety-and-async-tools
- front: How should you design a tool call that takes minutes?
  back: Name a slow tool for its initiation, return a task ID at once, and report completion as an event.
  lesson: ai-engineering/03-harness-engineering/notes/03b-mcp-write-safety-and-async-tools
- front: Which constraints belong in a hook or permission rather than a sentence?
  back: An instruction is a request and a hook is a rule.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Why is a virtualenv not a sandbox?
  back: A virtualenv isolates dependencies and not effects, so real isolation starts at the OS level and pairs every rung with quotas.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Why should a hook be silent on success?
  back: A hook that speaks only on failure teaches within one step, while one that announces every pass trains the model to skim.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: How should you treat model-written tool inputs?
  back: Treat model-written tool inputs as semi-trusted, and validate them against the schema as you would an external request.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: When may a later termination layer run, and what does skipping a required one mean?
  back: Do not run a later layer while an earlier one fails, and treat skipping a required layer as not done.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Why must generation and evaluation be separate agents, and what does the evaluator actually do?
  back: A generator judging itself agrees with itself, so a separate evaluator that drives the running app does the checking.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: What did the Minecraft run's false Ender Eye announcement show about agent reports?
  back: An agent's report is only a claim, so verification compares it against the recorded state of the world.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: What goes in a sprint contract, and what does it prevent on each side?
  back: Agreeing scope, verification and exclusions before work starts stops both the builder and the judge from moving the goalposts.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Name four ways a verification step quietly fails.
  back: A check fails when the agent can bypass it, when it sees too little, when it flags good work, or when it measures capability and not reliability.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Which failures should be retried and which never?
  back: Classify a failure before retrying, because a model refusal repeats itself while a transient error deserves backoff.
  lesson: ai-engineering/03-harness-engineering/notes/05b-recovery-and-termination
- front: What must every recovery path have, and why?
  back: Each recovery path needs a ceiling set from data, since an unbounded retry loop fails repeatedly and expensively.
  lesson: ai-engineering/03-harness-engineering/notes/05b-recovery-and-termination
- front: Why re-test compaction versus context reset on each model upgrade?
  back: Resets beat compaction on Sonnet 4.5 and later models need them less, so re-test the choice on each model upgrade.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What sections does a good session handoff have, and why not just a generated summary?
  back: A handoff keeps verified work apart from assumptions, which a generated summary blurs together.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: How does a Ralph loop deal with an agent that wraps up too early?
  back: A hook that re-injects the prompt on exit lets a fresh context carry on, until a verification gate says the work is done.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What let the Minecraft agents keep making progress through 605 deaths and 6 restarts?
  back: A 27-hour unattended run worked because what the team knew lived outside any single agent's context window.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: Name four mistakes that make a long-running agent drift.
  back: Long runs drift when a session's start, its reasons and its mess go unrecorded, so each gets its own artifact.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What is the main reason to use a subagent, and what should it return?
  back: The best reason for a subagent is to absorb exploration, returning a condensed result and not the exploration itself.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: What should a subagent's prompt and return value contain?
  back: A handoff needs a typed schema that labels each source and declares what was not done, because handoffs break more often than models.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: 'Components pass, end-to-end fails: suspect what?'
  back: When components pass and the end-to-end run fails, suspect a handoff bug, and evaluate at both levels.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: What are the components of a plan-execute multi-agent engine?
  back: A plan-execute engine turns a goal into a JSON plan of registered agents, then runs and traces each step in order.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: Where in the six-stage pipeline does the human gate go, and why?
  back: Reviewing a wrong plan takes minutes while reviewing the code from a wrong plan takes an hour, so the human gate goes on the plan.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: What is the honest test of whether a team really has verification?
  back: The honest maturity test is whether you can point to the code that runs verification on every task without a human remembering.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: How do you decide which harness components to delete after a model upgrade?
  back: Harness components encode assumptions about model weakness, so disable each in turn on every upgrade and delete what no longer pays.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: What happens to each question a fresh session cannot answer?
  back: Every question a fresh session cannot answer gets guessed, and every new session guesses again.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: What goes in AGENTS.md, and where do the hard constraints go?
  back: The entry file should route to topic docs and keep hard constraints at its edges, so dead rules can be audited and deleted.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: How do WIP = 1 and script-owned feature states stop overreach and under-finishing?
  back: With one active feature and a script that flips the state, an agent cannot overreach or mark its own work as passing.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: Name four ways a feature list stops being a gate.
  back: A feature list gates completion only when the harness reads it, the agent cannot edit the check, it names behaviour a user sees, and each item fits one session.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: What do you do when an agent fails?
  back: When an agent fails, change the system around it, then make sure that failure cannot recur.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: Which pillar covers the loops a harness runs?
  back: Loop engineering runs the harness again, against a goal, until a scorekeeper says stop.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: What is a harness?
  back: 'Everything around the model that isn''t the model: `Agent = Model + Harness`, where the harness informs, constrains, verifies and corrects.'
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: Your agent is 90% reliable per step over five steps. What end-to-end success do you expect, and what changes it most?
  back: About 59%, from 0.9^5. Harness structure changes it most, because it sets how many steps must succeed in a row and what happens when one doesn't; a better model only moves per-step accuracy a few points.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: What are the four parts of a harness, and which do teams miss?
  back: Acceptance baseline, execution boundary, feedback signals and rollback. Rollback is most often missing, and the baseline is most often faked with a "looks good".
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: Give evidence that the harness matters as much as the model.
  back: LangChain DeepAgents went from 52.8% to 66.5% on Terminal Bench 2.0 with a fixed model. Agent S4 evolved only interfaces and took Qwen3.8-27B from 5.6% to 21.3% on OSWorld V2, above GPT-5.5 at 13.0% and Opus 4.8 at 20.6%.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: An agent keeps failing and a stakeholder wants the newest model. What do you do?
  back: Run, attribute the failure to one subsystem, fix only that one, and re-run the same task on the fixed model. Swapping first hides which part was missing, so the failure returns under the next model.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: How do framework, runtime and harness differ?
  back: 'A framework gives abstractions and integrations, a runtime gives durable execution, streaming, HITL and persistence, and a harness is batteries-included: predefined tools, prompts, a to-do planner, a virtual filesystem, subagents and history summarization.'
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: What are the five subsystems of a harness?
  back: Instructions, tools, environment, state and feedback. Every failure can be attributed to one of them, which is why this cut is for diagnosis while the nine components describe what ships.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: What are the gulfs of execution and evaluation, and which do agents hit more?
  back: Execution is knowing what to do but being unable to act, a tools or environment gap. Evaluation is acting but being unable to tell if it worked, a feedback gap; agents usually fail here, confidently wrong rather than stuck.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: Why does the filesystem matter so much in a harness?
  back: 'It lets state outlive one context window, so the loop becomes re-entrant, and it gives large tool output a home: a 2,000-line log can leave only its head, tail and a path in the window.'
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: Where do you put the current branch and recent commits, and why?
  back: At the end of the context, before each inference. In the system prompt the changing values would break the KV cache.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: Bash or typed tools?
  back: Start with bash, and promote when you need a gate, a rendered result, an audit record, parallelism or a retry policy. Bash is maximally capable and dangerous, so pair it with a sandbox and hooks.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: A requirement must hold on every run. Which layer does it go in?
  back: The deterministic shell, because reliability requirements move outward. Otherwise use the innermost layer that can hold it, because a sentence is cheap and reversible while a subagent tier multiplies tokens and loses shared context.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: Give evidence that the interface matters independently of the model.
  back: 'SWE-agent: the same GPT-4 Turbo resolved 18.0% of SWE-bench Lite through a purpose-built interface and 11.0% through a plain shell.'
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Typed catalog or bash for a strong current model?
  back: Mak et al. found bash alone beat a typed catalog by 21.8–24.5 pp on TheAgentCompany and 4.8–7.4 pp on APEX-Agents with Opus-4.8 and GPT-5.5, using fewer tokens. Keep typed tools for steps needing a gate, an audit record or a retry policy.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: What are the four gating questions?
  back: Reversible, idempotent, observable, parallel-safe. Failing them means, in order, a confirmation gate, no retry without an idempotency key, undebuggable, and serialized execution.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Why are negative boundaries in a description worth writing?
  back: Positive descriptions leave the model to infer the boundary between similar tools. WHEN NOT TO USE and DO NOT USE FOR disambiguate `search`, `grep` and `read`, and each entry should come from observed misuse.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Your agent has about 100 tools and picks wrongly. What are your options?
  back: Merge overlapping tools, namespace the rest, and stop loading every definition up front. Use progressive disclosure or discovery, keeping dynamic content out of the cached prefix.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: Dedicated tool or Skill plus a general executor?
  back: Use a Skill plus executor when parameters are complex, the procedure changes often, or the model is strong enough to compose it. Use a dedicated tool when the call is frequent, parameters are simple, or a smaller model must get it right every time.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: How do you make tool parameters error-proof?
  back: Prefer enums over free strings, absolute paths over relative ones, and required parameters over optional ones with surprising defaults, so the mistake is harder to make.
  lesson: ai-engineering/03-harness-engineering/notes/03-tool-design
- front: A payment tool timed out and the customer was charged three times. What went wrong?
  back: A non-idempotent write was auto-retried. Tools without idempotency keys must not be auto-retried, and the fix is a key on the call plus a query-before-mutate check.
  lesson: ai-engineering/03-harness-engineering/notes/03b-mcp-write-safety-and-async-tools
- front: When do you choose MCP over an in-process tool?
  back: When several callers need it, a security boundary must be crossed, it deploys independently, discovery matters or it holds its own state. Otherwise default to in-process.
  lesson: ai-engineering/03-harness-engineering/notes/03b-mcp-write-safety-and-async-tools
- front: How do you design a tool that takes minutes?
  back: Name the initiation (`initiate_phone_call`), return a task ID at once, give it `get_status` and `cancel`, and deliver completion as a later event.
  lesson: ai-engineering/03-harness-engineering/notes/03b-mcp-write-safety-and-async-tools
- front: Rank the isolation options.
  back: OS-level (Seatbelt, seccomp, Landlock), then container, then microVM such as Firecracker, each with quotas on CPU, memory, disk, network and wall-clock time. A `venv` isn't on the ladder.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Why not just tell the model not to touch production?
  back: Instructions change what the agent tries, not what it is allowed to do. Enforce the rule in the runtime; STOP saw GPT-4 remove its own sandbox flag in 0.42% of 10,000 attempts.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Where do you place human approval, and what goes wrong otherwise?
  back: On irreversible actions only, with a timeout and declared default. Gating reversible steps makes the agent useless and causes alert fatigue, so people click through the approval that matters.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Why does `$(echo rm) -rf /` matter?
  back: It shows shell composition defeats keyword blacklists. A production gate parses each command's flags and arguments to find its real effect.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Proposer-Reviewer or Sidecar for a risky tool? Give the trade-off.
  back: Proposer-Reviewer runs in series with the conversation, suits high-stakes, low-frequency actions and has higher injection exposure. Sidecar sees only structured call fields and runs in parallel at low latency, so it suits every call to a risky tool class. Either way, use a different model family and a circuit breaker.
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: What makes autonomy affordable?
  back: 'Rollback: git branch-per-agent, sandbox snapshots and editable memory. An agent that can act but not be undone forces a human gate on every action.'
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: What does persistent memory add to the lethal triad?
  back: 'It is a fourth amplifier: an injected instruction can lie dormant in `MEMORY.md` and fire sessions later. So content written to memory deserves the same trust review as external input.'
  lesson: ai-engineering/03-harness-engineering/notes/04-execution-boundaries
- front: Why not let the agent decide when it is done?
  back: It finishes confidently on broken work. The harness intercepts the exit and forces a check, so the agent can only request done.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Why are unit tests not enough?
  back: 'Isolation and mocks make them blind to boundary defects: interface mismatch, state propagation, resource lifecycle and environment. The fix is the static, runtime and system layers.'
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Is a separate evaluator worth paying for?
  back: 'Usually. Anthropic''s DAW run spent $10 of $124.70 on QA, and it caught core features that were presentational only. The cost argument is often whether you get a working result at all: $9 broken against $200 working.'
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Pass@k or Pass^k?
  back: Pass@k asks whether it can ever do the task, and Pass^k whether it does so every time. Use the first for capability and ship on the second.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: A verifier is blocking good work. When do you delete it?
  back: When its false positives cost more than the defects it catches. PRINCE deleted its LLM SQL reviewer because it kept flagging valid queries, adding cost and latency with no accuracy gain.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: Both the eval and the agent look broken. Which do you fix first?
  back: The eval system. If it is broken, fix it before touching the agent, because you should never steer on a distorted signal.
  lesson: ai-engineering/03-harness-engineering/notes/05-verification-loops
- front: How do you stop an agent stuck on the same bug?
  back: Track per-file edit counts or a `hash(tool, args)` fingerprint and prompt "reconsider your approach" after N. After two failed retries, assume a bad spec. A hard stop alone doesn't force re-planning.
  lesson: ai-engineering/03-harness-engineering/notes/05b-recovery-and-termination
- front: Why is a retry budget per invocation?
  back: Otherwise five tools with three retries each become fifteen attempts. Add a circuit breaker after 5 consecutive failures, with a 60s cooldown, then fail fast.
  lesson: ai-engineering/03-harness-engineering/notes/05b-recovery-and-termination
- front: An agent edits the same file a dozen times. Is a hard stop the fix?
  back: No. A hard stop ends the run without a new plan. Count edits per file and inject a "reconsider your approach" prompt, so the agent re-plans instead of repairing.
  lesson: ai-engineering/03-harness-engineering/notes/05b-recovery-and-termination
- front: What is context anxiety, and why is it hard to spot?
  back: 'As the window nears its limit, models prematurely wrap up. It doesn''t fail loudly: the agent finishes early and confidently, so the fix is a harness mechanism to continue.'
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What is lost at a session boundary?
  back: The why behind decisions, which work is already done, which tests passed and failed, and the match between the agent's picture and the real repo, which drifts. That's why you measure rebuild cost and keep state in files.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: Compaction or context reset?
  back: Compaction summarizes in place, suits a single long session and risks summary drift. A reset clears the window and hands off through state, suits multi-day work and loses anything not written down.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What does Phase 0 do, and why separate it?
  back: It sets up the repo, including `init.sh`, and writes no feature code. Implementation maximizes verified features and initialization maximizes the reliability of later sessions; combined, the agent drifts toward visible output.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What makes a session finished?
  back: 'The task passes verification and the clean-state check passes: build, all tests including older ones, progress recorded, no stale artifacts, and a standard startup that works.'
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: Why does a handoff separate verified from assumed?
  back: A generated summary blurs them, so the next session either trusts unverified work or redoes all of it.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: A tool returns a 2,000-line log. What should the harness do?
  back: Keep the head and tail tokens of any output above a threshold, offload the full result to the filesystem, and leave a path the model can read if it needs more. Cost stays bounded and nothing is destroyed.
  lesson: ai-engineering/03-harness-engineering/notes/06-long-horizon-execution
- front: What is a subagent's main value?
  back: Context isolation, as a firewall. A search that reads 40 files and finds 3 returns the 3 in a summary of about 1,000–2,000 tokens, so the parent stays coherent longer.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: Why define protocols before parallelism?
  back: Parallelism on an undefined task structure produces collision, not speed. Use natural language inside tasks and protocols between them.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: Name four orchestration failures and their fixes.
  back: 'Loop oscillation: iteration counters. Context pollution: boundary schemas, returning summaries only. Concurrency collision: per-branch state ownership and JoinNode barriers. Consensus deadlock: a tie-break or arbiter.'
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: Why was Rothman's measured latency so far above the estimate?
  back: The estimate was about 10.7 s and measured three-step runs took 148 s and 151 s with gpt-5 from Colab, with generation calls dominating. The levers are parallel independent calls, caching and smaller models.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: Does the Minecraft run prove agents can self-coordinate?
  back: 'It shows emergent coordination can hold for a day: 229 messages across 2,783 programs. It was one run, one game, on Easy, so don''t extrapolate to domains where a wrong note is costly.'
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: When do you stay with one agent?
  back: When tasks don't need separate tools, trust levels or context isolation, because coordination overhead can exceed the parallel gain. Find the single-agent limit first.
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: One agent's invention reaches the final answer of a multi-agent run. How do you catch it and find the culprit?
  back: 'Cross-validate claims that cross a handoff. Evaluate each component and the end-to-end result separately: if end-to-end fails while every component passes, the bug is in a handoff; if one component fails, you know which agent to fix.'
  lesson: ai-engineering/03-harness-engineering/notes/07-orchestration
- front: What are the maturity stages, and where does most production value land?
  back: Ad-hoc, Basic, Verified, Observability-first and Self-healing, numbered 0 to 4, with value concentrated at 2→3. Stage 4 is still emerging, so treat it as direction rather than a target.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: Which pipeline stage do teams skip, and why does it pay?
  back: Approve, the human gate on the plan in Preflight → Plan → Approve → Tasks → Verify → Finish. Reviewing a wrong plan takes minutes, while reviewing code from a wrong plan takes an hour.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: Do you cut cost or raise accuracy first?
  back: Accuracy. PRINCE accepted high inference costs early, because a system not good enough to adopt has no usage worth optimizing and cheap-and-wrong burns adoption.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: Runtime or process observability?
  back: Runtime answers what the system did, through logs and traces. Process answers why a change should be accepted, through contracts and rubrics. You need both, and the harness collects them, not the agent.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: A new model is out. What do you do to the harness?
  back: List components with the weakness each mitigates, disable one, run the eval suite, then delete it if quality holds. Opus 4.6 allowed Anthropic to remove sprint decomposition.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: What is the meta-failure among the five?
  back: 'Skipped harness: claiming Stage 2 while at Stage 0, which hides the other four. Ask for the code that runs verification on every task with no human remembering.'
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: What can a coding agent actually see?
  back: The system prompt and task, file contents in the repo, and tool output. Slack, Jira and whiteboard decisions don't exist for it.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: What is the fresh session test?
  back: Open a new session with no verbal context and ask what this is, how it's organized, how to run it, how to verify it and where things stand. Every miss is guessed again in every later session.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: Why does a long `AGENTS.md` hurt?
  back: 'Budget crowding, lost in the middle, flat priority, and decay with contradiction. The fix is progressive disclosure: an index, plus topic docs of 50–150 lines read on demand.'
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: How long should the entry file be?
  back: 'Sources disagree: Osmani under ~60 lines, OpenAI about 100, *learn-harness-engineering* 50–200. They agree that everything there is read on every task, so each line has to earn it.'
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: An agent keeps importing across layers despite the docs. What do you do?
  back: Add a lint rule, import-graph test or CI script for that boundary, with an error message saying how to fix it. Docs state rules, and a check makes them hold.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: Why is a stale doc worse than none?
  back: It sends the agent the wrong way while it believes it's on track. Update docs with the code and keep one truth.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: What are overreach and under-finish?
  back: Overreach is more tasks active than a session can finish, and under-finish is too few of them passing end-to-end verification. They feed each other, and the tell is lines written rising while verified features stay flat.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: What is verified completion rate?
  back: Verified features divided by activated features. Under WIP = 1 it sits at 1.0 between features, and a harness can refuse to activate a new one below that.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: Why is a feature list a primitive rather than a memo?
  back: 'Other parts of the harness read it: the scheduler, verifier, handoff reporter and progress tracker. A document can be ignored, while a primitive works like a database check.'
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: What's in a feature entry?
  back: 'The triple: behavior as user-visible behavior, verification as executable steps or a command, and state. Evidence such as a commit or test output is added once it passes.'
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: How does a feature get to `passing`?
  back: Only by a successful run of its own verification, ideally through a script that flips the state. The agent requests verification rather than editing the status.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
- front: Your team wants faster delivery and proposes WIP = 3 for the agent. What's your response?
  back: The cost is half-done code that raises complexity and invites more overreach. Keep WIP = 1 per agent, and if you need parallelism, use isolated agents with their own worktrees and progress files.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
---
