---
generated_by: src/librarian/slides/flashcards.py
decks:
- generative-ai/06-observability/slides/deck.yaml
cards:
- front: What changed on 11, 14 and 17 October?
  back: Three different failures overlap in one fortnight, and each is visible to a different tool, which is why no single chart will do.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: What does the tree show that a log line can't?
  back: Tracing turns one successful-looking request into a story of three failed retries, with the time and money each one cost.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: Which level does a score attach to?
  back: Session, trace, observation and score are enough to model an agent; one trace per turn and one child per call is the whole rule.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: Why must the reset sit in finally?
  back: When a framework schedules tools itself, implicit context can be lost, so hold the root in a ContextVar you own and reset it in finally.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: Why not block on language_consistency?
  back: A cheap heuristic can run on every turn, yet measure its precision per segment first, because Dutch turns can trip a check that English turns never do.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: What should a run be named after?
  back: Run every version over the same fixed items and name each run after the version, so that any two can be compared item by item.
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: How many items sit behind the refusal number?
  back: The average rose 0.21 while refusals fell 2.75 points, because the four refusal items are outvoted by twenty others.
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Why does similarity rise when behaviour reverses?
  back: Two answers with opposite meanings can share almost every word, so never use embedding similarity alone on rule-bound behaviour.
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: What does a floor do that a tolerance doesn't?
  back: Floors on rule categories block a release, drops elsewhere send someone to read the items, and the average decides nothing.
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Which stage can lower recall?
  back: A fast first pass on everything with a strong verifier on its positives gets most of the value for a fraction of the cost.
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: How do the two grounding failures differ?
  back: Keep one judge per failure mode, because each score should tell you which team and which fix, and a single quality score tells you neither.
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: Which field do we distrust, and why?
  back: Ask for evidence per claim before the verdict, then compute the verdict in code, so a model's summary can't contradict its own findings.
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: Why did final precision and recall match?
  back: Both reach the same final numbers here, yet the lenient one pays the verifier to clean up 454 flags, 389 of its false alarms being Dutch turns.
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: What decides between them?
  back: Prefer the smallest tool surface that answers the questions, since three read-only tools answered this whole investigation.
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: Why group by span before fetching a trace?
  back: Summarise first and fetch one trace later, because tool output is context and a raw export spends the window fast.
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: Why refuse a tool the model can't see?
  back: Hide the tools from the model and refuse the call anyway, because a model can name a tool it read about in a trace.
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: Where does the validator run?
  back: Run the validator in CI on a recorded turn from each framework, and run the same check as a daily coverage number on production.
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: Why keep the random slice at all?
  back: Targeted samples concentrate failures nearly five times, yet keep a random slice, because it is the only one that estimates the base rate.
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: Why measure precision per segment?
  back: Promote each check on measured per-segment precision, since blocking on language_consistency would send 61 healthy turns to a person.
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: Why put traffic and system panels beside a spend chart?
  back: A spend chart says that something costs more, and only the panels beside it say whether traffic or the system caused it.
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: What does input_tokens actually count?
  back: Price cache reads, cache writes and uncached input separately, because treating them as one is out by up to 2.5 times on a single turn.
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: Which bucket explains the jump?
  back: Money recovers at v2.1 and billing errors keep climbing, so a dashboard with only cost and latency would have called this fortnight fixed.
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: What goes wrong if you add span p95s?
  back: Report p95 per route with its turn count, and never add span percentiles, since a bad route vanishes in the mean and the sum isn't the p95.
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: Why does the ratio beat the spend alert?
  back: Replay every candidate alert on past traffic, and prefer ratios such as cache hit rate, since a traffic surge doesn't trip them.
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: Why is the router the wrong first target?
  back: Protect the cache first, cap the loops, batch the judges, then test cheaper models through the release gate.
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
---
