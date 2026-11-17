---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/04-loop-engineering/slides/deck.yaml
cards:
- front: What are the four parts of this lecture, in order?
  back: The lecture runs from the scorekeeper, through memory and triggers and the autonomy ladder, to the exits that stop a loop.
  lesson: ai-engineering/04-loop-engineering/readme
- front: Name four things this lecture teaches you to do with a loop.
  back: You will be able to score a pass, keep a long run going from files, hand off one rung at a time and stop a loop with layered exits.
  lesson: ai-engineering/04-loop-engineering/readme
- front: Which step in try-test-fix-save makes progress a ratchet, and what does a bad pass then cost?
  back: The save step makes progress a ratchet, so a bad pass costs one rollback and not the whole run.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: What two things must exist before a loop runs, and what is going green once?
  back: A loop needs a goal and a scorekeeper before anything runs, and it should complete one green pass before growing.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: What two conditions justify building a loop, and what should you use otherwise?
  back: Build a loop only when the work repeats enough to pay for many passes and a scorekeeper can reliably validate the result.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: How many lines of the canonical loop skeleton belong to the model, and what must the last line do?
  back: The model supplies two lines of a loop, and everything else is yours to design, so a prompt cannot fix a missing line.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: Which loop pattern fits an atomic task, ordered steps, unfamiliar territory and high stakes?
  back: Choose a loop pattern from the task's shape, adding tool use first, then reflection, then planning and multi-agent once evals exist.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: What separated the harmful and helpful uses of a small decision model in the JEvAgentHarness results?
  back: A cheap decision component in the loop is safe only once you have measured where it is wrong.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: What five traits does a scorekeeper need, and why is hard to fake the critical one?
  back: Build the verifier before you scale the generator, since a generator that cannot check itself only makes plausible work faster.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: Who may write the evaluator in a loop, and why?
  back: An agent that can edit its own evaluator does not have a verifier, because it has a negotiation.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: What does a checker read, what does it run itself, and what happens if it cannot return clean?
  back: A checker works from the diff with no maker history, runs the scorekeeper itself, and must be allowed to return clean.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: Name the six loop building blocks and the failure each one fixes.
  back: Add a building block when you see the failure it fixes, and not before.
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: Walk through the steps of one full pass of a loop.
  back: Each pass reads memory, tries one change somewhere disposable, is scored by the scorekeeper, and is saved or rolled back.
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: What five fields does loop memory need, and which one prevents repeated failures?
  back: The field called what was tried earns its place, because without it a fresh pass reruns the attempt that failed an hour ago.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What do the four exit codes in the Ralph loop distinguish, and why does it matter?
  back: A Ralph loop restarts a fresh agent on every pass, and its exit codes keep success apart from cap, clock and stall.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What is the difference between the initializer and worker sessions, and why do loops prefer reset over compaction?
  back: Loops lean toward reset over compaction, since state is already on disk and the window can simply be cleared.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What question decides between run-until-done and a timer?
  back: If the work has an end, run it until done, and if it is ongoing watching, put it on a timer.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: What four cost controls does an unattended trigger need before it goes on?
  back: A trigger needs per-run and per-day caps, a no-op path that exits before the model, and alerts on spend, and events beat polling.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: What does each of the four rungs of the autonomy ladder hand off?
  back: The rungs hand off tool approval, the stop condition, the trigger to a clock, and finally the trigger and session.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: What is the agency-reliability frontier, and what can push it outward?
  back: Climbing a rung trades reliability for agency, and streaming, structured output and human controls push that curve outward.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: What six controls does a human need while a loop runs, and what do they all require?
  back: A loop that cannot be edited or forked mid-run pushes humans toward approving whatever is in front of them.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: What four roles does a human move through as an agent gains autonomy?
  back: As autonomy rises the human moves from executor to reviewer, collaborator and governor, and each role needs a different interface.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: What does an evolve loop edit, what does it leave fixed, and why must no change count as success?
  back: An evolve loop rewrites contract, state, triggers and procedure while the model stays fixed, and no change is a valid outcome.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: Why does a trajectory verifier return structured results and not a scalar?
  back: Verification output should be structured by dimension, because a single 0.57 average points at no particular fix.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: In what order should a lesson move from documents to code or weights?
  back: Choose the smallest lesson target that is easiest to verify and roll back, moving it toward code only as it proves out.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: How did a Darwin Gödel Machine agent game a hidden checker, and what does that imply?
  back: Hiding the checker is not enough, because an evolving agent can game its inputs, so those belong outside the write scope too.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: What steps does a self-modification go through, and where does the release decision live?
  back: A self-edit goes through branch, patch, checks, replay and canary, with a gate outside the model deciding the release.
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: What did autoresearch's write boundary, fixed budget and metric produce over two days?
  back: With an objective metric and a protected evaluator, a loop with an under-3% hit rate still found 20 real improvements in 700 tries.
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: What did Chen et al. find about learning and forgetting across drift scenarios?
  back: Self-evolving agents tend to forget in proportion to what they learn, so replay old tasks as well as measuring the new gain.
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: Name the six loop traps from their symptoms.
  back: Diagnose a loop by its symptom, since a green score with wrong output means cheating and change without gain means thrashing.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What are Osmani's four silent costs of loops?
  back: Osmani's silent costs land on the engineer, so build a loop intending to stay the engineer and not just the person who presses go.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What five independent exits should a loop have, and which one counts as success?
  back: Only the scorekeeper's confirmation counts as success, and the two ratchet rules are that score only rises and breaks get fixed first.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What three boundaries guard a self-modifying loop?
  back: The safety boundary is the write boundary extended to the release gate, so validators and audit logs stay out of the agent's reach.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What sections does a loop contract need?
  back: A one-page loop contract fixes goal, commands, boundary, trigger, stops, ratchet and human gates before the first pass.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: How does each of ADK, the Vercel AI SDK and LangGraph express an early exit and a hard cap?
  back: Frameworks mostly differ in names, so look for where each puts the goal, the scorekeeper and the stop rules.
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: How does an ADK LoopAgent stop early, and what is max_iterations for?
  back: In ADK's LoopAgent a sub-agent must set escalate to stop early, and max_iterations is only the backstop.
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: Give one rule of thumb each for scorekeepers, ratchets, autonomy and stopping.
  back: Goal and scorekeeper come first, the score only rises, and a cap is an escalation and never a success.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: Which pillar composes loops into graphs, and which treats the scorekeeper as an eval artifact?
  back: Loops compose into graphs in the next pillar, and the scorekeeper grows into a full eval discipline in the Eval pillar in generative-ai.
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: What is a loop, in one sentence?
  back: A goal plus a scorekeeper, repeated, with a way to stop.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: How is a loop different from a chain?
  back: A chain runs a fixed sequence whatever the intermediate results. In a loop, feedback changes the next step, so the agent can discover B failed and revise before reaching C.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: Why write the scorekeeper first?
  back: Generation is nearly free inside a loop, so verification becomes the constraint. The check makes "done" explicit and gives later decisions something to measure against.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: When would you refuse to build a loop?
  back: When the work doesn't repeat often enough to pay for many passes, or no scorekeeper can validate it. Anthropic's advice is to use a workflow first.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: Where is the line between harness and loop?
  back: The moment the agent's next run starts without you typing a prompt. The harness covers one run, and the loop decides what starts the next and when to stop.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: What are the two axes in this pillar?
  back: Capability is what the loop automates, in LangChain's four levels from work to improvement. Autonomy is what the operator handed off, from turn-based to proactive.
  lesson: ai-engineering/04-loop-engineering/notes/01-what-a-loop-is
- front: What five parts does every loop need?
  back: A testable goal, a tool set, context management, termination logic and error handling. Missing any one, it hangs, thrashes or quietly ships garbage.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: How many lines of the loop are the model's?
  back: 'Two: reasoning about state and choosing an action. Everything else is yours, including executing, updating state, compacting, scoring, rollback and escalation.'
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: Why several independent exits?
  back: So one failing doesn't leave the run going. Success, iteration cap, budget cap, stall detector and human escalation fire on different signals, and only success counts as success.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: ReAct, Plan-then-Act or Plan-and-Revise?
  back: ReAct adapts and can wander on long tasks. Plan-then-Act is predictable and brittle when a step invalidates a later one. Plan-and-Revise is the usual production compromise.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: Loop, workflow or graph for a new task?
  back: Start with a workflow if steps are known in advance, a loop if steps depend on what the last one found, and a graph if several loops or agents must hand off. Move right only when the task forces it.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: You could delegate decisions in the loop to a small, cheap model. What's the catch?
  back: The threshold. In JevAgentHarness a call cost 28% of an LLM call's time and 2.6% of its price in one recorded episode, but delegating tool choices with no fitted threshold cut success by 19 points.
  lesson: ai-engineering/04-loop-engineering/notes/02-loop-shapes
- front: What traits must a scorekeeper have?
  back: Objective, automatic, fast and clear, per KodeKloud, plus hard to fake. A loop that can lower the bar will take the easiest path to green.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: How do you stop a loop gaming its tests?
  back: Held-out checks, a tamper-proof location for scoring logic, auditable artifacts and watching the score trend. Permissions are rules, and prompt instructions are only suggestions.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: Deterministic checks or a model grader?
  back: Deterministic first, with model judgment only above that floor for what no check can express. If the end state can only be described as "looks right", you have no scorekeeper yet.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: Why separate maker and checker?
  back: The maker trusts its own output and misses its own mistakes. The checker is a fresh agent without the maker's history, and it must be allowed to return "clean" or it will invent findings.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: Verification adds latency and cost. When is it worth it?
  back: LangChain's answer is when quality matters more than speed. In a loop the generator runs cheaply and repeatedly, so an unchecked one just produces plausible-looking work faster.
  lesson: ai-engineering/04-loop-engineering/notes/03-the-scorekeeper
- front: What are the six building blocks?
  back: Automations, worktrees, skills, connectors and plugins, sub-agents, and memory. Goal and scorekeeper are the foundation beneath them.
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: Why do worktrees matter to a loop?
  back: 'They make experiments disposable and concurrent: an isolated copy sharing one history, where a failed try costs one `remove` and parallel agents don''t clash.'
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: Why a skill rather than one large prompt?
  back: Consistency, since the same steps run every pass, and clarity, since the base prompt stays small and know-how loads only on a matching task.
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: What privilege do you give a connector?
  back: The least that does the job. Read-only for triage, limited change scoped to specific repos, and avoid full access, or put a human approval in front of it and audit it.
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: A main loop's context keeps flooding. What do you change?
  back: 'Push heavy scanning to a sub-agent that returns "3 call sites: …" instead of the files. Keep its scope bounded, its permissions minimal and its return format distilled.'
  lesson: ai-engineering/04-loop-engineering/notes/04-building-blocks
- front: What three walls does a long-running loop hit?
  back: 'Context rot, context anxiety and session end. All three have one fix: progress lives in files, not in the context window.'
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What's in a good loop memory?
  back: 'Three tiers of now, recent and archive, and five fields: goal, last score, what was tried, what is next and what''s waiting for a human. It stays small, because a few precise notes beat a transcript.'
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What is a Ralph loop, and what does it lack?
  back: A bash loop that re-runs the agent with fresh context, with state on the filesystem. The bare form lacks a stop condition, a budget and a scorekeeper.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: Compaction or reset for a loop?
  back: Reset, usually. Ralph and initializer/worker already keep state on disk, and compaction risks summary-of-a-summary drift. Reset loses only what wasn't written down.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What do the initializer and worker each do?
  back: The initializer runs once and turns the task into files. The worker runs each session, picks one unfinished item, implements and tests it, commits, updates the log and exits cleanly.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What is context drift, and why is it dangerous?
  back: Notes that no longer match the code, schema or goal. The loop then acts on a stale picture with full confidence, so update notes when those change.
  lesson: ai-engineering/04-loop-engineering/notes/05-long-running-loops
- front: What changes at capability level 3?
  back: The agent stops being invoked by hand and becomes a component that schedules, webhooks and messages start. The trigger is a separate design decision from the loop inside it.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: Run-until-done or timer?
  back: Run-until-done for a concrete goal, stopped by a finish signal or a cap. A timer for monitoring, where each run is short and has to be cheap when there's nothing to do.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: Your scheduled agent mostly finds nothing. What do you do?
  back: Prefer events if the source can notify you. Otherwise add a deterministic pre-check, such as fetching updates since the last run, and wake the agent only if there's work.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: Which ceilings go on an unattended trigger?
  back: A per-run cap, a per-day cap on the trigger, a no-op path that exits in seconds, and alerts on spend. A trigger multiplies whatever one run costs.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: '`/loop` or `/schedule`?'
  back: '`/loop` runs in your session with your permissions. `/schedule` is a cloud routine with no session open, so it needs a verifier you already trust.'
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: Is this just cron?
  back: Mostly, as Messer says. What's new is that the thing on the cron is nondeterministic, which is why the scorekeeper and stop rules carry the weight.
  lesson: ai-engineering/04-loop-engineering/notes/06-triggers-and-schedules
- front: What are the four rungs, and what does each hand off?
  back: Turn-based hands off tool approval, goal-based the stop condition, time-based the trigger to a clock, and proactive the trigger and the session. They're cumulative.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: Which rung is pivotal, and why?
  back: Rung 2, the first unattended loop. Every rung above inherits its verifier, so a weak one there is a weak one where nobody watches it fail.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: Why is time-based the right resting place for most loops?
  back: It is session-scoped and inherits your permissions, so it needs no credential grant of its own. That makes it cheaper and safer than proactive.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: How do rungs and capability levels differ?
  back: Levels ask what the loop automates and rungs ask what the human handed off. A hill-climbing loop at level 4 can run at rung 1, and that's the recommended start for the evolve loop.
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: Beyond approve or deny, what does a human need during a run?
  back: '*Learning LangChain*''s six controls: interrupt, authorize, resume, restart, edit state and fork, all of which need a checkpointer and a thread ID.'
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: Autonomy costs reliability. How do you get more of both?
  back: 'Push the curve outward: streaming intermediate output, structured output, human-in-the-loop controls, a policy for mid-run input, and a verifier, which buys reliability without taking autonomy away.'
  lesson: ai-engineering/04-loop-engineering/notes/07-autonomy-ladder
- front: What does an evolve loop rewrite?
  back: 'Files, not weights: contract, state, trigger logic and SOP steps, every 5–10 runs of the fast loop.'
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: What is the anti-busywork rule?
  back: Make `no change needed` a successful outcome, because agents default to doing something and those invented edits degrade a working loop.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: Why verify before learning?
  back: Learning from a run nobody verified can teach the wrong lesson. Verify outcome and process by code, and quality by rubric, and return a structured result.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: Where does a lesson go?
  back: 'The smallest medium that holds it: a doc for a sourced exception, a Skill for a procedure, code for a hard constraint, weights last.'
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: How does an agent safely modify itself?
  back: 'As a release: branch from stable, patch a candidate, run checks, replay failures, run regressions, then canary. It never overwrites stable.'
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: A skill passes validation and task scores don't move. Why?
  back: It may never be loaded or followed. Measure activation and adherence, then use a two-way model swap to find the bottleneck.
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: How do you know an evolve loop's gain is real?
  back: Compare against plain retries at a matched budget on unseen tasks, as Wang et al. did with five attempts per task, and replay old tasks to catch forgetting.
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: Why does `autoresearch` work with a hit rate under 3%?
  back: Attempts are cheap and unattended, the metric is objective and the evaluator is outside the agent's write scope, so 700 tries yielded 20 real improvements.
  lesson: ai-engineering/04-loop-engineering/notes/08b-releasing-self-edits
- front: What are Masood's three structural failures?
  back: Context rot, termination failure and weak verification, fixed by pruning inside the loop, layered exits with no-progress detection, and deterministic checks first.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What are Osmani's four silent costs?
  back: Verification debt, comprehension rot, cognitive surrender and token blowout. They don't show up in traces and grow the longer a loop runs.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What are the two ratchet rules?
  back: The score only goes up, so a lower score is undone automatically, and fix breaks before adding more. A worktree per try and a commit per green pass make both cheap.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: How many ways should a loop stop?
  back: 'Several independent ones: success, iteration cap, budget cap, stall detector and human escalation. Only one of them is a success.'
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: What can a self-modifying loop never edit?
  back: The validators, test cases, release thresholds, audit logs and stable backups that approve its own updates. It may edit prompts, Skills, knowledge and tools.
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: Green scores but nobody understands the code. Is that a problem?
  back: 'Yes, comprehension debt: the score isn''t understanding, and a fast loop requires fast reading. Osmani''s point is to stay the engineer rather than the person who presses go.'
  lesson: ai-engineering/04-loop-engineering/notes/09-failure-modes-and-guardrails
- front: How does ADK's `LoopAgent` stop?
  back: At `max_iterations`, or when a sub-agent sets `tool_context.actions.escalate`, typically via an `exit_loop` tool. It doesn't decide on its own, so you have to implement termination.
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: How do state and memory move between passes in the ADK refinement shape?
  back: '`output_key` writes each agent''s reply to session state, and `{draft}` and `{critique}` read it back into the next instruction. That''s the whole memory between passes.'
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: What's the Vercel AI SDK equivalent of a cap and a trace?
  back: '`stopWhen: stepCountIs(n)` for the cap and `result.steps` for the trace. `WorkflowAgent` with `''use step''` adds durability by replaying completed steps.'
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: What is a loop in LangGraph?
  back: 'An explicit cycle: a node, a conditional edge that loops back or routes to `END`, `recursion_limit` as the hard cap, and a checkpointer for durability.'
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: You must pick a framework for a refinement loop. How do you compare them?
  back: Look at where each puts the goal, scorekeeper and stop rules. ADK has the critic and refiner shape built in as a documented pattern, Vercel leaves the check to you inside a tool or step, and LangGraph makes the cycle explicit with middleware for rubrics.
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
- front: Why name a sandbox by run ID?
  back: You get one sandbox per run, reused across calls, so retried steps reattach to it.
  lesson: ai-engineering/04-loop-engineering/notes/10-framework-bindings
---
