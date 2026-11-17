---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- generative-ai/06-observability/slides/deck.yaml
cards:
- front: Name the six uses of a trace that this lecture covers, in order.
  back: One data model of trace, span and score, and of dataset and run, serves all six uses, and each use sees a different part of the fortnight.
  lesson: generative-ai/06-observability/readme
- front: Name four things this lecture teaches you to do with an agent's traces.
  back: You will be able to say what an agent did, whether a release made it better, and what it cost, from the traces alone.
  lesson: generative-ai/06-observability/readme
- front: What changed on 11, 14 and 17 October?
  back: Three different failures overlap in one fortnight, and each is visible to a different tool, which is why no single chart will do.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: Which level does a score attach to?
  back: Session, trace, observation and score are enough to model an agent; one trace per turn and one child per call is the whole rule.
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: What does the tree show that a log line can't?
  back: Tracing turns one successful-looking request into a story of three failed retries, with the time and money each one cost.
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
- front: Name three ways an MCP server over traces goes wrong, and the fix for each.
  back: A trace server fails through its keys, the size of its output and its loops, so scope the key, summarise by default and cap the iterations.
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
- front: Name three ways a trace contract and its checks fail, and the fix for each.
  back: A contract decays unless it is validated, and a check misleads unless its precision is read per segment, so test both and keep a random slice.
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
- front: What is the difference between a trace and an observation?
  back: A trace is one request end to end, and observations are the spans, generations and tool calls nested in it. The root observation supplies the trace's input and output
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: Why not rely on logs?
  back: 'Logs record events, while a trace records causation and nesting: which search fed which answer, at what token cost. Agents are non-deterministic, so you can''t reproduce a turn to debug it later'
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: How do you trace tools in a framework that runs its own event loop?
  back: Hold the root in a `ContextVar`, open children from that object with `start_observation`, and reset in `finally`. Then test that children share the trace id and parent
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: How are cached tokens reported to Langfuse?
  back: As separate exclusive usage keys. The API's `input_tokens` excludes cache reads and writes, so the total is the sum of all three
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: Would you put one tracing wrapper over all frameworks?
  back: No. Native instrumentation has more depth. Standardise the metadata keys, and accept the cost of joining at analysis time
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: What should you check about a heuristic score before alerting on it?
  back: Precision and recall on labelled traces, per segment, because a check that is fine in one language can be mostly false alarms in another
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: How do you stop personal data reaching the trace store?
  back: A client-side `mask` function, plus `capture_input=False` on sensitive functions, so the data never leaves the process
  lesson: generative-ai/06-observability/notes/01-tracing-with-langfuse
- front: What does a dataset run add over a script that prints scores?
  back: The link from item to trace to score, so two runs line up item by item and you can click from a low score to the turn that earned it
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Average score went up by 0.1 on 20 items. Ship it?
  back: Not on that evidence. It's within judge noise. Look at categories, and treat rule categories as pass or fail
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Why can't embedding similarity catch a bad refusal?
  back: A refusal and a compliance share topic and most words, so they embed close together. Similarity measures overlap, not what the answer commits to
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: How do you handle a judge's reply that was refused or truncated?
  back: Check `stop_reason`, record no score, and count the unscored items. Otherwise the failure mode of the judge turns into data
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Code judges or managed evaluators?
  back: Code judges for pre-release tests, because they are versioned and run on your schedule. Managed for sampling live traffic, where editing a rubric in the UI is fine
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Why turn off a framework's automatic tool execution?
  back: Tools called inside the SDK don't get their own spans, so the trajectory can't be scored. A manual loop lets you trace each one
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: What can a golden set not tell you?
  back: How production is behaving. It only covers known questions, so you still need production monitoring and human review alongside it
  lesson: generative-ai/06-observability/notes/02-scoring-datasets-experiments
- front: Why several judges and not one?
  back: Each failure has a different fix. A wrong answer from irrelevant documents is a retrieval bug, and from relevant documents a generation bug. One score can't separate them
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: What does gating verification on positives cost?
  back: It lowers cost, but recall can only fall at the second stage. Sample the negatives to measure what is lost
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: Why make the judge list evidence first?
  back: Models often write a right list and a wrong flag. Recompute the verdict from the list
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: How do you decide between a lenient and a strict judge?
  back: Run both over the same turns, and compare precision, recall and cost per segment. A lenient judge's false alarms often concentrate in one language or route
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: What breaks a trend line of judge scores?
  back: A change to the judge, and schema drift in the export. Keep the judge version on the score and report parse coverage
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: How do you run this cheaply on Claude?
  back: A small model on every turn, a stronger one only on flagged turns, a cached system prompt, and the Batches API at 50% off since nobody is waiting
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: Why not record a refused judge reply as a zero?
  back: It would turn the judge's failure into a false finding about the product. Count unjudged turns separately
  lesson: generative-ai/06-observability/notes/03-judge-pipelines-over-trace-exports
- front: Why put traces behind MCP?
  back: So the assistant can follow a line of investigation itself, with each answer shaping the next query, without someone copying data between a UI and a chat
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: What's the main design constraint on a trace tool?
  back: Tool output is context. Return summaries by default, filter on the server, cap results, and keep long text behind a switch
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: Why is reading traces a security issue, even with no write tools?
  back: Traces contain customer text, which is untrusted input to the model. And it can expose personal data, so mask it at instrumentation time
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: How would you restrict a server that has 95 tools?
  back: A project-scoped key, a client-side allowlist by tool name, and approval for anything destructive
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: Does `read_only_hint` enforce anything?
  back: No. It's the server's own claim, useful for your own servers and for UI, but not a permission
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: How should a tool report a bad argument?
  back: As an error message the model can read, saying what to do next. In the 2.x SDK that's `ToolError`
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: How do you test an MCP server without a client app?
  back: The SDK's in-memory `Client` connects to the server object, so you can list tools and call them in a unit test
  lesson: generative-ai/06-observability/notes/04-langfuse-mcp-server
- front: What must every agent log, regardless of framework?
  back: Run and session ids, agent, model, prompt version, git commit, latency, input, output and cache tokens, and the outcome. Those make a trace queryable and a run reproducible
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: How do you stop the schema drifting?
  back: A validator in CI on a recorded turn from each framework, and a daily coverage number on production
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: Why two layers of evaluation?
  back: Human labels find failure patterns and calibrate, and judges give coverage. A judge alone drifts, and people alone don't scale
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: When may a grounding check start blocking answers?
  back: After it has run log-only and people have labelled a sample, and when its precision is acceptable in every segment. A multilingual agent makes this strict
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: What's a good sampling strategy for review?
  back: Rules on errors, long turns and bad feedback to concentrate on failures, plus a small random slice to find what the rules can't see
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: What does a managed knowledge base cost you in observability?
  back: Chunk ids, passage text and per-chunk scores. Without them you can't compute faithfulness, so comparisons have to use shared fields such as URL hit rate
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: What does the AgentOps taxonomy add?
  back: A checklist of span types beyond LLM calls, so that plans, reasoning and tools get their own metadata. It's from a preprint and hasn't been validated in real case studies
  lesson: generative-ai/06-observability/notes/05-support-agent-observability
- front: How do you compute the cost of a Claude call with caching?
  back: Input, cache read, cache write and output are separate buckets with separate prices. `input_tokens` is only what comes after the last breakpoint, and the prompt size is the sum of the three input fields
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: Why report p95 by route and not mean latency?
  back: The tail is the experience of real customers, and a slow route gets lost in an overall mean. On low traffic, p99 is noise, so use a longer window
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: Can you add step p95s to get a turn's p95?
  back: No. Slow steps rarely coincide. Use each step's share of total time to attribute, and its own percentile to describe it
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: What's the best single cost metric?
  back: Cost per resolved ticket, paired with a quality signal, because cost per turn ignores whether anyone was helped, and the ratio alone can be gamed by giving up
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: How would you catch a silent prompt-cache regression?
  back: A standing alert on cache hit rate for prefixes you expect to be cached. It's a ratio, so traffic doesn't move it, and usage fields are the only ground truth
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: How do you set an alert threshold?
  back: Replay it over history, count how often it fires, read those days, and name an owner and a first check
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: What can a cost and latency dashboard not tell you?
  back: Whether the answers are right. Put judge scores on the same rows, or a bill that recovers looks like a fix when quality is still falling
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
- front: The bill is too high. What do you do first?
  back: Break it down by bucket, route and model, then price each lever on recorded tokens. Protect the cache, cap loops, batch what can wait, and test cheaper models through the regression gate
  lesson: generative-ai/06-observability/notes/06-cost-and-latency-dashboards
---
