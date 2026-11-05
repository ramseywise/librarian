---
generated_by: tools/slides/flashcards.py
decks:
- data-engineering/06-ml-platform/slides/deck.yaml
cards:
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
- front: Where next
  back: 'Next is architecture and governance: from one model to an organisation of data products.'
  lesson: data-engineering/06-ml-platform/notes/06-ml-system-framing-to-monitoring
---
