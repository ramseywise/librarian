---
generated_by: src/librarian/slides/flashcards.py
decks:
- ai-engineering/04-loop-engineering/slides/deck.yaml
cards:
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
- front: What steps does a self-modification go through, and where does the release decision live?
  back: A self-edit goes through branch, patch, checks, replay and canary, with a gate outside the model deciding the release.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: What did autoresearch's write boundary, fixed budget and metric produce over two days?
  back: With an objective metric and a protected evaluator, a loop with an under-3% hit rate still found 20 real improvements in 700 tries.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: What did Chen et al. find about learning and forgetting across drift scenarios?
  back: Self-evolving agents tend to forget in proportion to what they learn, so replay old tasks as well as measuring the new gain.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
- front: How did a Darwin Gödel Machine agent game a hidden checker, and what does that imply?
  back: Hiding the checker is not enough, because an evolving agent can game its inputs, so those belong outside the write scope too.
  lesson: ai-engineering/04-loop-engineering/notes/08-self-improving-loops
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
---
