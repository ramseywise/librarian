---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/08-eval/slides/deck.yaml
cards:
- front: In what order does this lecture move from a definition of better to a system in production?
  back: The parts follow the README's four questions, and a fifth covers what happens once the system is live.
  lesson: generative-ai/08-eval/readme
- front: Name four things this lecture teaches you to do with an eval.
  back: You will be able to say whether a one-point gain is real, which grader to trust, and what should block a release.
  lesson: generative-ai/08-eval/readme
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
- front: Why does a row carry labels and eligibility as well as a reference?
  back: A golden row carries a reference, labels for slicing, eligibility per gate, provenance and the graders that apply to it.
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: Name the five tactics a public benchmark uses against memorization.
  back: 'Five tactics: unique answers, parameterized templates, fresh tasks, canaries and a closed test set. A canary only catches a leak and prevents nothing.'
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
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
- front: Which three ways can an eval gate fail even when its statistics are right?
  back: Treat inconclusive as its own answer, keep infrastructure errors visible, and give evals a key of their own, or the gate fails for reasons the agent did not cause.
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
- front: Why can't unit tests cover an LLM feature?
  back: The same input gives different outputs, and "correct" is often a judgment, so you need many tasks and trials and report a rate with an error bar. Unit tests still cover the deterministic parts, such as prompt rendering and retry logic.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: Define task, trial, trajectory, outcome, grader and suite.
  back: A task is an input plus success criteria, and a trial is one attempt at it. The trajectory is the record of that attempt, the outcome is its end state, a grader scores one aspect, and a suite is the set of tasks run together.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: Where do you mock the model?
  back: In unit tests, never in evals, because an eval with a mocked model measures the mock.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: How do capability and regression evals differ?
  back: A capability eval asks what the system can do and sits at a low to medium pass rate. A regression eval asks whether it still does what it used to, sits near 100% and blocks a release when it drops.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: Your suite went from 41% to 38% overnight. Block the release?
  back: First ask which suite it is. On a capability suite a 3-point drop means little alone, while on a regression suite a drop that size means something broke.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: Your PM says the demo looks great, so evals can wait. What do you say?
  back: A demo is a vibe check on a handful of inputs and leaves no number to compare after the next change. Offline evals give that number before shipping, and online evals say whether it holds for real users.
  lesson: generative-ai/08-eval/notes/01-what-an-eval-is
- front: What four questions turn a vague goal into criteria?
  back: What the user needs, what must never happen, what the unit of success is, and what it costs to be wrong. The last one sets the thresholds.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: What is the two-expert test?
  back: Two domain experts should independently reach the same verdict on a task. Run it on 20 outputs with the written criteria, and treat disagreements as faults in the criteria, not the people.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: Walk through error analysis.
  back: Collect about 100 traces, note the first failure in free text, group the notes into 5 to 15 categories, and rank by frequency × cost. Repeat until new traces stop adding categories, usually after 50 to 100.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: Why note only the first failure in a trace?
  back: Later failures are often caused by the first, so counting them inflates the wrong category.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: What is criteria drift, and what do you do about it?
  back: People's idea of a pass changes as they grade, because reading outputs exposes unwritten requirements (Shankar et al., 2024). Plan for it by versioning criteria and re-labelling a sample when they change.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: A grounding score dropped and half the failures say `bad_answer`. How would you redesign the labels?
  back: Use stable labels ordered by pipeline stage with one fix each, such as `rank_miss` for retrieval and `unsupported_claim` for generation. Add `context_missing` so a fault in the eval is not blamed on the system.
  lesson: generative-ai/08-eval/notes/02-defining-correct
- front: How big should a first eval set be?
  back: Start at 5 to 20 real tasks, then 20 to 50, and 100 to 300 for about ±5 to 8 points. LLM-graded sets often stop at 50 to 200 because of cost, and 1,000 or more is for fine differences.
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: Where do good rows come from?
  back: Production failures first, then real traffic and expert-written cases, with synthetic rows generated along chosen dimensions to fill gaps. OpenAI's practice keeps a regression pool and a discovery pool of harvested failures.
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: What is row eligibility?
  back: A row can be a valid task yet unfair for one measurement. If the expected source isn't in the index, scoring it on retrieval measures the corpus, so pools narrow the rows from `all_gt` to `generation_eligible_gt`.
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: Your grounding is 0.40 overall. Is the generator bad?
  back: 'Not necessarily. Score it only on rows where retrieval found the source: in this chapter''s example that gives 0.80, so the rest is a corpus and retrieval problem.'
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: Why not just use synthetic data?
  back: Synthetic rows carry tropes and unrealistic phrasing, and a generating model finds its own phrasing easy, which gives it a head start if it is also a candidate. Use them to bootstrap and fill gaps, generated by a different model family, then replace them with real traffic.
  lesson: generative-ai/08-eval/notes/03-eval-datasets
- front: How do you stop a public benchmark from being memorized?
  back: Published tactics are unique answers (GAIA), parameterized templates (AndroidWorld, τ²-bench), tasks newer than the training cutoff (SWE-bench-Live), canary GUIDs (Terminal-Bench) and closed test sets. In your own suite, keep test rows out of training data and prompts.
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: Why version a dataset and freeze its references?
  back: A score from v3 and one from v4 are not comparable, and labels made by a grader shift when the grader changes, so record the dataset and grader versions with every result.
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: How much of a public benchmark survives review?
  back: Often little. For SWE-bench Verified, 93 developers reviewed 1,699 tasks and 500 survived, and 18% of the BrowseComp questions Deep Research never solved had a bad reference.
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: What does adversarial filtering do to a benchmark?
  back: It makes the set hard for the filter models, which then can't be ranked fairly on it. Humanity's Last Exam kept questions that stumped four frontier models, which then scored 3.3–9.4%.
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: How do you check a benchmark for shortcuts?
  back: Run the model on part of each row or with easy distractors. CommonsenseQA's BERT-Large went from 55.9% to 92.3% when the related distractors were swapped for random ones.
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: Why stratify dev and test by difficulty?
  back: A random split can leave one side easier, as ARC-AGI-1's public set was. ARC-AGI-2 matched mean human accuracy across splits to within 1 point.
  lesson: generative-ai/08-eval/notes/03b-splits-contamination-and-public-benchmarks
- front: What are the three kinds of grader, and in which order?
  back: Code, then model, then human. Code is cheap and exact, a model handles semantic qualities, and a human sample of about 5 to 10% calibrates the rest.
  lesson: generative-ai/08-eval/notes/04-graders
- front: Why not use BLEU or ROUGE for LLM answers?
  back: They compare surface wording, so valid paraphrases score low, and ROUGE recall favors length. A tokenization choice alone moved BLEU by up to 1.8 points on one WMT'17 language pair.
  lesson: generative-ai/08-eval/notes/04-graders
- front: Binary or 1 to 5 scale for a judge?
  back: Binary per dimension by default, because graders disagree most in the middle of a scale and a rate has simple statistics. Berryman & Ziegler prefer a described 1 to 5 scale, and both approaches fix a bar the judge would otherwise guess.
  lesson: generative-ai/08-eval/notes/04-graders
- front: What is a veto item?
  back: 'A must-pass gate on a quality dimension: if it fires the total is zero. Hallucination is the classic one, and HealthBench''s negative criteria of up to −10 points work in a similar spirit.'
  lesson: generative-ai/08-eval/notes/04-graders
- front: How do grader states work?
  back: Heuristic code checks can gate, calibrated judges can gate at their calibrated threshold, and experimental ones are tracked but can't block a release. Changing a threshold without calibration evidence sends a grader back to experimental.
  lesson: generative-ai/08-eval/notes/04-graders
- front: A new model has +5 relevance and −5 grounding, and the composite is flat. Ship?
  back: No, not on the composite. Report the dimensions, because this is worse for anyone who needs correct answers. A hybrid rule with a grounding floor would have caught it.
  lesson: generative-ai/08-eval/notes/04-graders
- front: Why do grader disagreements improve a rubric?
  back: Each disagreement exposes an edge case the rubric didn't settle. Resolved over time, they turn it from principles into a casebook of edge cases.
  lesson: generative-ai/08-eval/notes/04-graders
- front: Name the biases you'd test for, and the fix for each.
  back: 'Position: run both orders. Self-preference: use a different family. Leniency: binary criteria with tricky-FAIL examples. Master keys: put empty and opener-only answers in the calibration set. Verbosity was below 0.011 for all 21 judges under one 2026 rubric, so test it instead of assuming it.'
  lesson: generative-ai/08-eval/notes/05-llm-as-judge
- front: How do you judge at low cost?
  back: Run code first and skip the judge on failed rows, use a cost-capped deterministic sample, swap in a smaller model once it calibrates as well on test, and cache by output hash and judge version. Remember that one generate plus three judges quadruples the calls.
  lesson: generative-ai/08-eval/notes/05-llm-as-judge
- front: Why did Chatbot Arena move from Elo to Bradley–Terry?
  back: 'Elo depends on the order of the matches, and Bradley–Terry is a global fit that doesn''t. Its coverage is still thin: 153 comparisons per pair in January 2024.'
  lesson: generative-ai/08-eval/notes/05b-pairwise-ranking-elo-and-bradley-terry
- front: What can break a Bradley–Terry ranking from an LLM judge?
  back: Position bias and cycles. Swap the order on every pair and count a win only if it holds both ways. The model also assumes preferences are transitive, which judges and humans often violate, so check for cycles before trusting the ranking.
  lesson: generative-ai/08-eval/notes/05b-pairwise-ranking-elo-and-bradley-terry
- front: Why grade both outcome and trajectory?
  back: They fail independently. The right answer by an unsafe path passes an outcome-only eval, and a reasonable path that failed on a tool timeout isn't the agent's fault.
  lesson: generative-ai/08-eval/notes/06-evaluating-agents
- front: The agent says "I've issued your refund". How do you grade it?
  back: 'Check the end state: the refund row with the right amount, not the sentence. A judge on the text gives full marks to a refund that doesn''t exist.'
  lesson: generative-ai/08-eval/notes/06-evaluating-agents
- front: How strictly should tool calls match the expected ones?
  back: 'Only as strictly as the requirement: exact for protocols such as auth before action, in order for a required sequence, any order for independent lookups, subset or superset for allowed sets. Check arguments separately.'
  lesson: generative-ai/08-eval/notes/06-evaluating-agents
- front: Compare pass@k and pass^k, with numbers.
  back: pass@k is the chance that at least one of k trials succeeds, and pass^k that all do. At p = 0.75 and k = 3 they are 0.98 and 0.42, so use pass^k for customer-facing agents where each user gets one try.
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: How would you evaluate a router-plus-skills agent?
  back: 'Give each part a grader: a judge over the tool-call span for the router, per-skill checks (code execution for the visualization skill), and optimal ÷ actual steps for the path, then an end-to-end score. An end-to-end failure alone doesn''t say which part broke.'
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: What is convergence, and what's the catch?
  back: Optimal steps ÷ actual steps over paraphrases of a question. "Optimal" is the shortest run observed, so a suite where every run thrashes can still score near 1.0.
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: Why does agent cost grow faster than step count?
  back: Every turn re-sends the whole context, so a 5,000-token tool output is billed again each later turn. Thinking tokens and detours add to it, which makes turn count and context growth the levers, not only a cheaper model.
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: A simple baseline nearly matches your agent framework on accuracy. How do you decide?
  back: Plot accuracy against cost with simple baselines. Kapoor et al. found a warming baseline at 93.2% for $2.45 against LDB at 93.3% for $6.36, so check the gap against the error bar and log tokens so that you can re-price later.
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: Why record how each failed agent run ended?
  back: The mix of endings varies by environment, so one failure rate hides it. AgentBench sorts runs into completed, context limit exceeded, invalid format, invalid action or task limit exceeded, which covers running out of turns or repeating itself.
  lesson: generative-ai/08-eval/notes/06b-components-trials-and-cost
- front: A simulated user gives a 0.47 reward. Do you trust it?
  back: Not from one cooperative user. In GAUGE, a population of personas cut mean verifiable reward by 42%, from 0.47 to 0.27, and the judge needs to see tool calls and outcome, since a truncated transcript got 4.6/7 for satisfaction with reward 0.
  lesson: generative-ai/08-eval/notes/06c-agent-suites-and-environment-hygiene
- front: Beyond the task set, which suites does a tool-using agent need?
  back: An error-handling suite with malformed input, tool errors, timeouts and empty results, plus an adversarial suite with injection and out-of-scope requests. Neither failure shows up in tasks where every tool behaves.
  lesson: generative-ai/08-eval/notes/06c-agent-suites-and-environment-hygiene
- front: A task fails every trial across several model versions. What do you do?
  back: Check the task before the agent. On BrowseComp, 21 of the 118 questions Deep Research never solved had a bad reference answer.
  lesson: generative-ai/08-eval/notes/06c-agent-suites-and-environment-hygiene
- front: An agent passes a task it shouldn't be able to. What do you check?
  back: Whether the answer was in reach. Claude 3.7 Sonnet found a capture-the-flag answer in plaintext after searching the machine, so keep references, grader code and hidden tests away from the agent's tools and read surprising passes.
  lesson: generative-ai/08-eval/notes/06c-agent-suites-and-environment-hygiene
- front: How do you split a RAG eval?
  back: Retrieval (Recall@k, hit rate), ranking (MRR, nDCG), context precision, generation (faithfulness, completeness, relevance) and citations, each with its own required inputs.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: Recall@k or hit rate?
  back: Hit rate when one good source is enough, recall when the answer needs several. Set k to what reaches the prompt in either case.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: How does claim-based faithfulness work?
  back: Extract atomic claims, verify each against the passages as supported, contradicted or not found, and score supported ÷ total. Report contradicted separately, because it is worse than an omission.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: Which citation checks need no LLM?
  back: Cited ID in the retrieved set, quote found (fuzzy) in the cited passage, every strict-tier claim cited, and markers that parse. Only citation precision and recall need a judge.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: Grounding dropped to 0.5 across every row overnight. First suspicion?
  back: The grader's inputs, not the model. The case study's custom grader returned a flat 0.5 and `context_missing` when given URLs in place of text.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: Why isn't high faithfulness enough?
  back: It measures the generator against whatever was retrieved, so a stale document gives a faithful wrong answer. Correctness against a reference measures the system.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: RAGAS or ARES?
  back: RAGAS for quick iteration, reference-free, after calibrating. ARES needs setup per domain and about 150 labels, and in its paper it beat RAGAS by 59 points on context relevance, so it pays off at volume.
  lesson: generative-ai/08-eval/notes/07-evaluating-rag-and-grounding
- front: What must a retrieval span record?
  back: The query after rewriting, the returned IDs and text, scores and rank. Without text, a grounding grader has nothing to verify.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: What goes on the root span?
  back: User or session ID, final output, outcome label, total cost, and the versions of prompt, model, tool set, index and config.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: Why use the OpenTelemetry GenAI conventions?
  back: Standard span and attribute names such as `invoke_agent` and `gen_ai.usage.input_tokens` let you switch backends without re-instrumenting.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: Where do you redact PII?
  back: At span export, so raw PII never reaches the backend, with role-based access on raw traces. Eval rows derived from traces should inherit the same retention limit.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: What do MTTD, MTTR and CFR tell you?
  back: Time to detect, time to resolve, and the share of deploys that need a fix or rollback. A high CFR says the offline eval pipeline is missing bad changes.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: Your bill doubled overnight and traffic is flat. Where do you look?
  back: Cache hit rate first, since a prompt change that breaks the cacheable prefix can double cost, then input-token share by source for context bloat, then cost per success by version.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: What features would you require of a tracing tool?
  back: Evals over stored traces, scores attached to spans, datasets built from traces, and side-by-side experiment comparison. Those four turn a trace viewer into part of the eval loop.
  lesson: generative-ai/08-eval/notes/08-tracing-and-observability
- front: Version B got 80% and A got 72% on 50 tasks. Ship?
  back: Not on that. At n = 50 and p = 0.80 the 95% interval is 69% to 91%, so the two are not distinguishable. Compare them paired and collect more tasks.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: How many tasks to detect a 5-point change?
  back: About 400 to 800, against 50 to 100 for 15 points and 2,500 or more for 2. Each 3× smaller difference needs about 10× the samples, by OpenAI's rule of thumb as Huyen quotes it.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Why compare on the same tasks?
  back: Most tasks pass or fail on both versions, so the differences are mostly zero and their SE is much smaller than either rate's. In this chapter's made-up 200-task example the SE falls from 0.042 unpaired to 0.022 paired.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: What is McNemar's test telling you?
  back: Only discordant tasks carry information. At 14 wins and 6 losses the exact p is 0.115, suggestive at best, at 15–5 it's 0.041, and at 11–9 it's 0.824.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: You ran 100 tasks five times. What's your n?
  back: '100, not 500, because repeats of a task are correlated. Average within a task or cluster by it. Miller reports a clustered SE of 1.34 against a naive 0.44 on DROP, over 3× larger, for the same reason: rows that share a document aren''t independent.'
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Overall score rose 1 point, and non-English fell 17. What do you do?
  back: Hold the release and read those transcripts. An average can rise while a slice collapses, and with enough mix change it can even reverse (Simpson's paradox). Check the slice's n too.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Version B's pass rate rose, but it errored on 8% of tasks. What's the first check?
  back: The denominator. If those tasks were dropped, B is being scored on an easier 92%. Put them back in the reported rate, and list them.
  lesson: generative-ai/08-eval/notes/09-reading-results
- front: Absolute floor or regression gate?
  back: Both, for different failures. A floor catches never-events such as schema validity under 99% or any citation hallucination. A paired baseline comparison catches drift that stays above any floor.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: Why not block if the candidate's score is lower?
  back: Because Δ < 0 blocks on noise half the time. Gate on the CI instead, as in "block if the upper bound of Δ is below −3".
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: Why split into run and assert phases?
  back: The run is slow, costly and non-deterministic, while asserting is free and deterministic. You can change a threshold or add a slice without re-running, and a crash in assert doesn't lose a $30 run.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: 8% of tasks hit rate limits during a run. Block the PR?
  back: No verdict either way. Retry, report the errors as their own count, and rerun, since the score can't be read while the failures are about the provider. Don't count them as task failures or drop them.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: What runs on a PR, and what nightly?
  back: Fast code graders and regression sets on PRs that touch relevant paths, and larger suites with judges nightly, which alert without blocking. The gate ladder then limits later gates to rows that earlier gates found fair.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: When is the baseline updated?
  back: Deliberately, after a release, storing results with dataset and grader versions. A baseline that moves on its own hides slow decline.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: Who owns what?
  back: An infra owner runs the runner, CI and cost, a criteria owner signs off pass/fail definitions and calibration, and every engineer adds a row when fixing a bug. Production metrics cross teams, so give each a RACI row.
  lesson: generative-ai/08-eval/notes/10-evals-in-ci
- front: Describe the eval maturity ladder.
  back: 0 manual review, 1 deterministic gates, 2 separated evaluator, 3 eval sets from real failures plus tracing, 4 production sampling with drift alerts. Most systems sit at 0, and production needs 3 or above.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: How does an online grader differ from an offline one?
  back: It has no reference for live traffic, so it must be reference-free or judged, and it's run on a sample to control cost. The grader code should be the same one CI uses.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: What do you sample from production?
  back: All negative feedback, plus escalations, high cost, long conversations and a random slice, with more for 48 hours after a change. Only the random slice is used to estimate rates.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: Scores fell 4 points this week. Your steps?
  back: Check data validity, schema changes and outliers first, then provider model version, then compare input mix against the baseline. Only a confirmed shift justifies re-tuning.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: Shadow, canary or A/B?
  back: Shadow gets real inputs but shows you no user reaction, canary exposes 1 to 5% of traffic to catch failures, and A/B measures outcomes with guardrails. They go in that order.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: Should you optimize thumbs-up rate?
  back: No. Feedback is sparse and skewed, and optimizing 👍 rewards flattery. Use it as one signal alongside graded samples and outcomes such as resolution.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: Your A/B test won on plan length, and session cost rose. Which one counts?
  back: Session cost. Plan length is the mechanism and cost is the target, since shorter plans can cause more edit loops.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: How should review change after a model or prompt change?
  back: Raise it to elevated or full review for the first 48 hours. Keep the random sample separate when you report rates, because rule-based samples are skewed toward failures.
  lesson: generative-ai/08-eval/notes/11-production-and-the-maturity-ladder
- front: The score dropped this morning. What's your order?
  back: Infrastructure, then versions, then 10 to 20 failed traces with their grades, then slices, and only then the agent.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: How do you handle a saturated eval?
  back: Graduate its tasks into a regression suite and add harder ones. Public benchmarks do the same, as with GLUE to SuperGLUE and MMLU to MMLU-Pro, or o3 (Medium) at 53.0% on ARC-AGI-1 and 3.0% on ARC-AGI-2.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: Give examples of Goodhart in agent evals.
  back: Answers padded for a verbosity-biased judge, a code agent editing tests rather than code, 👍 optimized into flattery, and escalation rate cut until it won't escalate when it should.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: How can test-set scores leak?
  back: Every reported score leaks some information. ARC Prize disclosed about 10,000 scores against the same 100 private tasks from 2020 to 2024, enough for teams to fit the private set.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: How do you detect contamination?
  back: Scores well above similar unseen tasks, verbatim completions of task text, and drops on paraphrases. N-gram overlap and perplexity are the two heuristics, with different costs.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: Provider silently updates the model. What protects you?
  back: Pin versions and re-run on each model change. Chen et al. found GPT-3.5 and GPT-4 scores changed significantly on many benchmarks from March to June 2023.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: Offline scores improve each release, but resolution is flat. What's going on?
  back: The eval has stopped measuring what users care about, through a generic metric, wrong unit, wrong denominator, or a set that no longer resembles traffic. Check whether offline wins predict online wins.
  lesson: generative-ai/08-eval/notes/12-failure-modes
- front: Why separate routing and domain evals in a multi-agent system?
  back: They're two failure surfaces. Routing asks if the root picked the right sub-agent, and domain assumes correct routing and asks if the sub-agent used the right tools and produced the right output.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: Why eight gates, not one score?
  back: Each gate answers one question on its own row pool, so a retrieval change can't hide behind a generation gain. Any claim names its gate, pool and n.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: Low agreement between your grounding grader and two others. Which do you trust?
  back: 'None yet. In this study the comparison passed URL strings: the custom grader''s guard returned 0.5, and the others judged URLs. Check inputs, and then investigate before switching.'
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: Your grader has high recall and another high precision against user sentiment. How do you use them?
  back: The highest-recall one for the gate, to catch what users dislike, and the highest-precision one for building golden traces, where false positives pollute labels.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: A judge's liked and disliked means differ by under 0.05. Next step?
  back: Iterate on the prompt (the study's `score_delta` rule). Custom answer_relevancy went from Δ −0.080 at v2 to +0.214 at v3 on the same sample.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: When is a composite grader worth it?
  back: When its F1 against sentiment beats the best single signal, which it must do to justify 3× the cost.
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: What's the main limit of a 50-task, liked-versus-disliked calibration?
  back: 'At n = 25 per group, a Δ of 0.03 is noise, and sentiment is a proxy label with its own biases. Results also don''t transfer: strong separation on help-centre traffic fell near zero on routing-agent staging traffic.'
  lesson: generative-ai/08-eval/notes/13-case-study-support-agent
- front: Your judge passes a row your code check failed. What does that tell you?
  back: Possibly a false pass on a provable fault, so read it first, and a person decides which of them to fix.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: Why not stop early during calibration?
  back: It removes the rows that test whether the judge catches provable faults, so stop early only in production.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: Can you estimate TPR and TNR from the disagreement queue?
  back: No, its rows were selected on disagreeing. Use a random sample, or a stratified one with known odds of selection.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: Check and judge agree on every failure. Is that good news?
  back: Only if they're independent. If they share a signal, it shows they share a signal.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: How do you use a judge's critiques?
  back: Tag them on disagreements and a sample of agreements, fix the largest class of error, and keep a change only if it wins on dev.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: Does a plausible critique tell you why the judge decided?
  back: Not on its own. In Turpin et al. and much of Marioriyad et al., outputs shifted with cues the explanations didn't mention, so run cue and edit tests.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: What does passing a cue test prove?
  back: Little by itself. It's necessary and not sufficient for faithfulness, and it covers only the cues you tried.
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: A paper's mitigation made judges cue-invariant. Ship it?
  back: 'Check what it costs first: Tapwal et al.''s locked notes tied on 82 to 94% of near-equivalent pairs, which a release gate can''t copy as it stands.'
  lesson: generative-ai/08-eval/notes/14-calibrating-judges-with-checks-and-critiques
- front: What makes an LLM judge calibrated?
  back: 'You have measured how often it agrees with humans on your data: 100 to 200 labels split into train, dev and test, with TPR, TNR and κ reported once on test and compared with human–human agreement.'
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
- front: TPR or TNR for a release gate?
  back: TNR, because it measures how many bad outputs get caught. A golden-label builder wants high precision on PASS instead, and if one judge doesn't win both, use two.
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
- front: Why lead with κ over raw agreement?
  back: Ties and base rates inflate agreement. Norman et al. note that "85% agreement" on MT-Bench corresponds to κ of about 0.48.
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
- front: A rubric question was never asked. What does the scorer return?
  back: Not enough evidence, not a low score, with the abstention rate reported per vertical. A zero there measures the agent's coverage and blames the candidate, and error on scored rows can't see an agent that stops asking, so coverage needs its own floor.
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
- front: Two judges from different vendors disagree on a candidate. Add a third?
  back: Not to settle close pairs. In GAUGE's τ²-bench test the four-judge average picked the wrong winner 31% of the time on close pairs, the same as the best single judge, because the judges were correlated. Report "no detectable difference", or abstain when the gap is inside the noise.
  lesson: generative-ai/08-eval/notes/15-calibration-against-human-labels
---
