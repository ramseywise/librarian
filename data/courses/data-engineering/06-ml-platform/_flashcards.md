---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-engineering/06-ml-platform/slides/deck.yaml
cards:
- front: What are the parts of this lecture, in order?
  back: Each part answers one silent failure in order, and the last part shows the whole chain on a second problem.
  lesson: data-engineering/06-ml-platform/readme
- front: Name four things this lecture teaches you to do.
  back: You will be able to keep a model honest offline, traceable in the registry, safe in serving and watched in production.
  lesson: data-engineering/06-ml-platform/readme
- front: What does a point-in-time join do to your score, and why take it?
  back: A point-in-time join gives a worse score that is true, which is the only score you can act on.
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What does a feature store package, and what needs testing?
  back: A feature store packages one definition, a point-in-time join and an online lookup, and its TTL rules need testing.
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What can you do without a store that still removes training-serving skew?
  back: The problem is consistency, and a shared function solves most of it before any platform is needed.
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What does experiment tracking turn a pile of notebooks into?
  back: Tracking turns a pile of notebooks into a table of runs you can query and compare.
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: What must a retrain do before it gets the alias?
  back: Newer is not better, so a retrain must beat the champion on current data before it gets the alias.
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: Why do services load an alias, and why do predictions store the version?
  back: Services load an alias, so rollback is one registry call, and predictions store the version because it never moves.
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: What are four ways a retrain gate misleads?
  back: Score both models on the same current holdout, require a gain you would defend, and know how the service picks up the alias.
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: Why default to batch serving?
  back: Default to batch, because a failed job is a rerun and consumers keep reading the last good table.
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Which input makes precomputing impossible, whatever the skew?
  back: Measure key coverage from your request logs before you build, since a Zipf curve and a flat one lead to opposite plans.
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: What does validating at the boundary and returning the version give you?
  back: Validate at the boundary and return the version, so bad input is the client's error and each answer is traceable.
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Why measure before optimising an ML service?
  back: Measure before you optimise, because features, framework and network usually cost more than the model.
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: What does each rollout stage trade, and what does that protect?
  back: Each stage risks more traffic for better evidence, so a bad model gets stopped where it harms the fewest people.
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: What are three ways serving goes wrong without an error?
  back: Serving fails quietly on reruns, on out-of-range answers and on retries, so replace the partition, decide the fallback early and make the consumer idempotent.
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Why is a p-value poor for big windows and PSI poor for small ones, and what do you do?
  back: With enough rows every shift is significant, and with few rows PSI measures noise, so report magnitude and calibrate.
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: Why does testing many features at a fixed alpha get a monitor muted?
  back: Testing many features at a fixed alpha guarantees false alarms, so correct for it or expect the monitor to be muted.
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: In the left case, why do predictions show the same p-value as distance?
  back: Input drift neither proves nor rules out damage, so only labels can tell you what a shift costs.
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: What do you check first on a drift alert, and why?
  back: Check the pipeline first, because interviewees met broken data more often than natural drift, and retraining teaches the model the bug.
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: Scheduled or triggered retraining?
  back: Triggers save fits on a sudden change and lag on a gradual one, so start scheduled and defend the cadence by experiment.
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: Which Microsoft maturity level suits a proof of concept, a business model, and full automation?
  back: A proof of concept can stay at 0, a business model should reach 2 to 3, and 4 needs strong monitoring first.
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Why can't a strong model section hide absent monitoring in the ML Test Score?
  back: The ML Test Score takes the minimum across sections, so a strong model section cannot hide absent monitoring.
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Why are code tests alone not enough for an ML system?
  back: A correct function on broken data gives a wrong model and passing tests, so code tests alone are not enough.
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Why is a dependency chain worth more than a checklist?
  back: A dependency chain makes the safe path the only path, which is worth more than a checklist someone must remember.
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: When is a stage of an ML system finished?
  back: A stage is finished when it has produced what the next stage needs, so name that handover before you start.
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: What do you state when no LLM has been measured?
  back: With no LLM measured, state a break-even, 1.43 per retried document at assumed prices, not a verdict.
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: Why does a decision model need a canary and not only a shadow?
  back: A shadow never sees its own results, so a decision model needs a canary with limits and a sized audit.
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: Why price an automation target before accepting it?
  back: 'Price an automation target before accepting it: at these invented prices, 35% automated costs less than 60%.'
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: What does each ML platform rule do to a silent failure?
  back: Each rule makes a silent failure visible or reversible, and that is the job of the platform.
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: What comes after the ML platform?
  back: 'Next is architecture and governance: from one model to an organisation of data products.'
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: What is point-in-time correctness?
  back: For each training row, use the feature value as it was knowable at that row's event time, by an as-of join on the time the value became available
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: Why does a leak make the offline metric better?
  back: The feature partly contains the label or the future. The model relies on it, and that information does not exist at serving
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What is the difference between leakage and skew?
  back: Leakage is wrong information across time. Skew is the same input producing different features in two code paths
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What are the parts of a feature store?
  back: Registry, offline store for history and point-in-time joins, online store for latest value by key, materialisation between them
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: When do you not need one?
  back: One model, batch scoring or features in the request. An as-of join and a shared function cover it
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What does TTL do in a point-in-time join?
  back: Limits how far back the join looks for a feature. A row with nothing in that window gets no value, and may be dropped
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: How do you detect skew in production?
  back: Log features at serving, join them to what training would compute for those rows, and compare values and distributions
  lesson: data-engineering/06-ml-platform/notes/01-feature-stores
- front: What is the difference between a run and a registered model version?
  back: A run records one training execution. A version is a named, numbered pointer to a run that someone decided matters
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: What must you log so that a run can be reproduced?
  back: Code version, data version, parameters, metrics, the model artifact and its environment
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: Stage or alias?
  back: Alias. Stages are one fixed lifecycle, deprecated since MLflow 2.9. Aliases are as many movable pointers as you need
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: Does moving `@champion` change production?
  back: Only if something resolves it again. The registry labels; a pipeline or a restart deploys
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: Run ID or alias in the service?
  back: Run ID pins exactly and promotion is a redeploy. Alias makes promotion a registry action, but you must log which version was resolved
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: What is passive retraining?
  back: Retrain on a schedule, compare against production on a newer holdout, and promote only on a win
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: Why keep the versions that lost?
  back: Rollback, audit, and a record of what was tried
  lesson: data-engineering/06-ml-platform/notes/02-experiment-tracking-and-model-registry
- front: How do you choose batch, stream or online?
  back: By when the consumer needs the answer. Batch unless someone is waiting, stream if a system can wait seconds, online if a person or synchronous call waits
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Why is batch the default?
  back: No service to keep up, failures are reruns, consumers read the last good table
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: What makes batch scoring safe to rerun?
  back: A deterministic output location replaced whole, with the version on each row
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: When does precomputing fail?
  back: When traffic is spread across many keys, or the inputs include session data not known in advance
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Where does online latency go?
  back: Usually feature fetches, network and framework; rarely the model. Measure
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: What is shadow deployment, and when can't you use it?
  back: Both models see requests, only the champion answers. It breaks down when predictions affect future data, since the shadow never sees the results of its own decisions
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Why hash for a canary?
  back: So a user stays on one side and the comparison stays clean
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: Why return the model version?
  back: To join predictions to the model that made them, for monitoring and for incidents
  lesson: data-engineering/06-ml-platform/notes/03-batch-and-online-serving
- front: What is the difference between concept and data drift?
  back: Data drift moves $p(X)$. Concept drift moves $p(y \mid X)$. Only the second needs labels to see, and only changes affecting the decision need action
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: Why does a drift monitor fire on healthy data?
  back: Many tests at a fixed α guarantee false alarms, and large samples make trivial shifts significant
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: How do you reduce false alarms?
  back: Bonferroni or similar, restrict to important features, report magnitude, and calibrate thresholds on historical windows
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: What can univariate tests not see?
  back: A change in how features relate. A domain classifier can
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: What did *Failing Loudly* find?
  back: On images, aggregated univariate tests did as well as multivariate, testing the existing classifier's softmax outputs was best, and half the simulated shift types were identified as harmless
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: Can you detect concept drift without labels?
  back: Generally not when inputs stay put. It needs performance feedback, or labels on a sample
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: What do you do on a drift alert?
  back: Check for a pipeline fault, then measure cost with labels if possible, then retrain, gate and roll out
  lesson: data-engineering/06-ml-platform/notes/04-drift
- front: What are the Microsoft MLOps levels?
  back: 0 no MLOps, 1 DevOps without MLOps, 2 automated training, 3 automated deployment, 4 full automated operations
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: What level should a model aim for?
  back: Depends on the stakes. Business-critical usually 2 to 3. Level 4 needs strong monitoring and many models or fast drift
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: What is the difference between CT and CI/CD?
  back: CT retrains when data or a schedule says so. CI/CD ships new pipeline code when code changes. Different triggers
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: What is the ML Test Score?
  back: 28 tests in four sections, half a point manual, one automated, and the final score is the minimum across sections
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Why the minimum?
  back: So a weak section cannot hide behind a strong one
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: What should you test beyond code?
  back: Data validity, model sanity such as overfitting a batch, and behaviour such as invariance and direction
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Why inject callbacks?
  back: So tests can run the handler with no cloud, and see what it would have written
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Why does the overfit test matter?
  back: A model that cannot memorise a tiny batch has a wiring bug, and tuning won't help
  lesson: data-engineering/06-ml-platform/notes/05-mlops-maturity-and-best-practices
- front: Walk me through designing an ML system
  back: Decision and prices, then what's correct, then data and labels, baseline, per-sub-task model choice, offline gate, shadow and canary, monitoring, correction loop. Say what each hands to the next
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: How do you choose between rules, ML and an LLM?
  back: Per sub-task. Start from a measured baseline, ask what the better route must beat and at what price, and keep checks that don't trust the model
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: What does "correct" mean for extraction?
  back: Field, document or match, and decision. Each can pass while the next fails. The normalisation rule is part of the metric
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: A model improves offline. Why might the system get worse?
  back: Downstream models were calibrated on the old signal, thresholds were fixed for the old scores, and slices can fall while the average rises
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: Why can't you just shadow a router?
  back: It sees outcomes only where the champion produced them. It never sees what happens after its own choices, so it needs a canary with limits and an audit
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: How do you monitor when labels take months?
  back: Operations and inputs for breakage, predictions for calibration when labels come, and a random audit that brings labels forward
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: Is a falling correction rate good?
  back: Unknown. It can be a better model, a worse one or a tired clerk. Read an audit and seeded problems
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: Why not train on what reviewers corrected?
  back: The model chose what they saw. In a simulation it stopped paying almost anything, and error on paid looked excellent
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: What's your fallback?
  back: The baseline, kept working and sized for the load, with a rollback someone has rehearsed
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
- front: What's a straight answer when asked about an LLM you haven't tested?
  back: Say it's untested, give the break-even price, and state the measurement that would decide it
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
---
