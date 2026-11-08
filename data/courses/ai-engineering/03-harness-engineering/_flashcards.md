---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/03-harness-engineering/slides/deck.yaml
cards:
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
  back: A harness grows by encoding each real failure as a check, so the same failure cannot happen again.
  lesson: ai-engineering/03-harness-engineering/notes/01-what-a-harness-is
- front: 'An agent is confidently wrong rather than stuck: which subsystem has the gap?'
  back: Agents are rarely stuck and often confidently wrong, which points at a gap in the feedback subsystem.
  lesson: ai-engineering/03-harness-engineering/notes/02-harness-anatomy
- front: In what order do you build up a harness?
  back: Build capability first, then the constraints that make it survive scale, and productize last.
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
- front: What decides whether a constraint belongs in AGENTS.md, a permission gate or a hook?
  back: An instruction is a request and a hook is a rule, so anything that must hold every time belongs in a hook or a permission.
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
- front: How do WIP = 1 and script-owned feature states stop overreach and under-finishing?
  back: With one active feature and a script that flips the state, an agent cannot overreach or mark its own work as passing.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
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
- front: What happens to each question a fresh session cannot answer?
  back: Every question a fresh session cannot answer gets guessed, and every new session guesses again.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
- front: What goes in AGENTS.md, and where do the hard constraints go?
  back: The entry file should route to topic docs and keep hard constraints at its edges, so dead rules can be audited and deleted.
  lesson: ai-engineering/03-harness-engineering/notes/09-repo-as-system-of-record
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
- front: What do you do when an agent fails?
  back: When an agent fails, change the system around it, and then make sure that failure cannot happen again.
  lesson: ai-engineering/03-harness-engineering/notes/08-maturity-and-failure-modes
- front: Which pillar covers the loops a harness runs?
  back: Loop engineering runs the harness again, against a goal, until a scorekeeper says stop.
  lesson: ai-engineering/03-harness-engineering/notes/10-scope-and-done
---
