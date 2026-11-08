---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/08-eval/slides/deck.yaml
cards:
- front: Name the five steps of the core eval flow in order.
  back: An eval runs tasks through k trials, captures what happened, grades each dimension and aggregates with an error bar.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: What is the difference between a trajectory and an outcome?
  back: A trajectory is the full record of messages and tool calls; an outcome is the end state, such as the refund row.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: Which behaviour belongs in a unit test and which in an eval, and why?
  back: Unit-test deterministic behaviour; measure the non-deterministic as a rate over many tasks, and never assert an exact LLM string.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: What should a drop mean on each of the two suites?
  back: A drop on a regression suite blocks the release; on a capability suite it shows room to climb.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: What is the two-expert test, and what do you fix when it fails?
  back: If two experts would not reach the same verdict on an output, fix the criteria rather than the grader.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: Why read traces before building a grader?
  back: Do not build a grader for a failure mode you have not seen; reading traces produces the ranked list of what to measure.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: What failure does a suite of only positive cases hide?
  back: Without negative cases, a change that calls tools more often looks like better recall while precision quietly breaks.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: Name the five tactics a public benchmark uses against memorization.
  back: 'Five tactics: unique answers, parameterized templates, fresh tasks, canaries and a closed test set. A canary only catches a leak and prevents nothing.'
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: Why does a row carry labels and eligibility as well as a reference?
  back: A golden row carries a reference, labels for slicing, eligibility per gate, provenance and the graders that apply to it.
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: In what order do you stack the grader kinds?
  back: 'Graders are layers rather than alternatives: run code first and stop early, so judge budget goes where judgment is needed.'
  lesson: generative-ai/08-eval/notes/04-graders
- front: Why does a grader declare what it requires?
  back: A grader declares what it requires and skips with context_missing when it is absent, instead of guessing a verdict.
  lesson: generative-ai/08-eval/notes/04-graders
- front: How can a composite score stay flat while users get a worse system?
  back: Prefer binary pass or fail per dimension with vetoes for never-events, because a weighted average can trade grounding for relevance.
  lesson: generative-ai/08-eval/notes/04-graders
- front: What goes in a judge prompt besides the criterion, and why does the reason come before the label?
  back: Give a judge one criterion, defined labels, delimited inputs and a CANNOT_GRADE escape, and ask for the reason before the label.
  lesson: generative-ai/08-eval/notes/05-llm-as-judge
- front: Once biases are controlled, how well do strong judges agree with humans?
  back: Once biases are controlled, strong judges agree with humans about as often as humans agree with each other, over 80%.
  lesson: generative-ai/08-eval/notes/05-llm-as-judge
- front: Why does Elo give different ratings for the same votes, and what do you publish instead?
  back: Use Elo for a live leaderboard and a Bradley–Terry fit with bootstrap intervals for any ranking you publish or gate on.
  lesson: generative-ai/08-eval/notes/05b-pairwise-ranking-elo-and-bradley-terry
- front: What are the three grader states, and which ones may block a release?
  back: Heuristics and calibrated judges can gate; an experimental judge only tracks, and a threshold change without fresh evidence moves a judge back to experimental.
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
- front: Why is high test-retest reliability not evidence that a judge is valid?
  back: Lead with kappa rather than raw agreement, because a judge can be perfectly repeatable and still be reliably biased.
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
- front: Which cell of the cross do you read first, and why does agreement with code not move a grader out of experimental?
  back: Cross code checks with the judge to find what to fix, then read the false passes first. Agreement with code never replaces human labels.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: Why does 9/9 on test support no strong claim?
  back: Each change must win on dev. The test's 9/9 has a Wilson interval of 0.70 to 1.00, and its perfect score is a property of this setup.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: What does a cue test measure, and what does passing it prove?
  back: Use a critique to find what to change, and change the input to see whether the verdict follows, because it can leave out what moved the verdict.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: Which two cells does an outcome-only eval get wrong?
  back: Score outcome and trajectory separately, because an outcome-only eval passes a wasteful path and blames the agent for a timeout.
  lesson: generative-ai/08-eval/notes/06-evaluating-agents
- front: At p = 0.75 and k = 3, what are pass@k and pass^k, and which suits a support agent?
  back: 'Report pass^k for customer-facing agents: a 75% agent passes 98% with three retries, but all three times only 42% of the time.'
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: What did a simple retry baseline show about the HumanEval leaderboard agents?
  back: Plot accuracy against cost with simple baselines, because similar accuracy can differ by almost two orders of magnitude in cost.
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: What do you check first when a task fails every trial across several model versions?
  back: Reset state for every trial, keep trials isolated, and check the task before the agent when it fails every time.
  lesson: generative-ai/08-eval/notes/06c-agent-suites-and-environment-hygiene
- front: What does an answer that is faithful but wrong tell you?
  back: Split a RAG eval by stage, so that a retrieval miss does not get counted as a bad answer and sent to the wrong team.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: What is the most common grounding eval bug, and how do you guard against it?
  back: Pass the grader passage text, not pointers, because a grader handed URLs scores near zero or grades from its own knowledge.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: What does a trace record at each span kind, and why must retrieval spans hold the text?
  back: Record model, tool, retrieval and root spans, with retrieval text included, so a trace says where a run went wrong.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: About how many paired tasks does it take to detect a 5-point difference?
  back: A 5-point difference needs 400–800 paired tasks; a 50-task golden set is a smoke detector, not an instrument.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Under McNemar, which tasks count?
  back: Run both versions on identical tasks and analyse per-task differences, since only the tasks that flip carry evidence.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: What did the +1 overall hide in the worked example?
  back: An overall gain of one point can ship a change that breaks one group of users, so slice before concluding and show n per slice.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Where did the headline gain live in the Yang et al. strata?
  back: Report difficulty strata, because a rising average can sit on top of a flat hard tail.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Where do errors and refusals go in the denominator?
  back: Count errors and refusals as failures or as their own rate, and never let them leave the denominator.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: What artefact sits between the two phases?
  back: A results.jsonl file sits between run and assert, so you can change a threshold or add a slice in seconds without re-running a $30 suite.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: Why does blocking when the delta is below zero fail as a gate?
  back: Block when the upper bound of the difference is below −3, since a rule of blocking on any drop fires on noise half the time.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: Which rung does production need, and which gives the highest return per effort?
  back: Production needs at least level 3, failure evals with tracing, and deterministic gates give the highest return on the way there.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: What is each layer's job in two-layer online review?
  back: Judges alone drift unnoticed and humans alone do not cover real traffic, so sample by rule and have humans calibrate the judge.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: Name two biases in user feedback, and how a broken form can mislead you.
  back: Test the feedback form and look at the rating distribution, because user signals carry the same biases as judges plus broken UI.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: What is the debug order when an eval score drops?
  back: Skipping straight to the agent fixes something that was not broken, so check infrastructure, versions, grades and slices first.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: Name two defences of an eval against being gamed.
  back: Defend an eval with several dimensions, held-out tests, reading the biggest gains and refreshing tasks from production.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: What does an inverted separation tell you about an off-the-shelf judge?
  back: An inverted judge scores disliked answers above liked ones, so validate judges against users and recalibrate per domain.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: What must every gate's artefact name, and why not one blended score?
  back: 'Do not collapse corpus, retrieval, agent, generation and calibration into one score: each gate answers one question over a named pool.'
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: Give one rule of thumb for each stage, from criteria through production.
  back: Define correct first, check graders against humans, grade state and path, read intervals and slices, gate on baselines, then keep sampling.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: What does the pillar's lab build, and which note shows the method on a real system?
  back: The eval-suite-ci lab builds a paired regression gate; note 13 shows the method on a real support system.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
---
