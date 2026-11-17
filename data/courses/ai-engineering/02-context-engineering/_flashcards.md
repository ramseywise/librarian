---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/02-context-engineering/slides/deck.yaml
cards:
- front: What are the four parts of this lecture, in order?
  back: The lecture runs from why the window fills, through what to select, shrink, keep and split, to how to diagnose a wrong answer.
  lesson: ai-engineering/02-context-engineering/readme
- front: Name four things this lecture teaches you to do with a context window.
  back: You will be able to assemble a window, shrink it, keep what lasts and diagnose a wrong answer by looking in the window first.
  lesson: ai-engineering/02-context-engineering/readme
- front: Why does a larger context window not solve the attention problem?
  back: Added tokens do not expand the attention budget. They split the same budget across more claimants.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: Why can a model pass a needle test at 1M tokens and still fail on shorter inputs?
  back: A model's advertised window says nothing about the length at which your task starts to fail.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: Name the four observed shapes of context rot.
  back: Context rot is a gradual decline from well below the limit, so filler is a cost and not free insurance.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: What does context engineering decide on each call?
  back: Context engineering decides, per call, what occupies each slot of the window and at what size.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: What goes wrong at each extreme of system prompt altitude?
  back: When a prompt collects a fourth conditional, the fix is usually a tool or a code-level control and not a fifth rule.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: If the agent keeps doing X, where does the fix usually belong?
  back: '"The agent keeps doing X" is usually a job for a hook, not for a stronger sentence in the prompt.'
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: Why does content order in the window matter for prompt caching?
  back: Cache economics and attention placement point the same way, so stable content goes first and the query goes last.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: What did adding a timestamp to a high-volume system prompt do, and what is the fix?
  back: Any per-request value placed early in the prompt invalidates the cached prefix on every call.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: What does an agent status bar buy, and when does it backfire?
  back: In-context learning behaves like retrieval more than reasoning, so give the model the count instead of making it count.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: Which two budgeting rules matter more than the percentage split?
  back: Reserve the output first and cap everything that grows, then treat any percentage split as a guess to measure.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: Why can summarizing an old tool result be more expensive than it looks?
  back: In agent workloads cache reads dominate cost, so a context edit that forces a re-prefill can cost more than it saves.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: How do you decide whether a section of a prompt has earned its tokens?
  back: Remove anything whose deletion does not move an eval score, and judge each layer by quality per prompt token.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: What single design question decides between pre-loading content and fetching it with a tool?
  back: Pre-load only what is needed on 80% or more of turns, and leave the long tail to tools.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: When does per-user permissioning rule out loading everything into context?
  back: These options combine, as a cached prefix plus retrieval or tools for the long tail, and permissions force retrieval.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: Why split retrieval into a wide first stage and a reranker?
  back: Recall and precision are separate jobs, with a fast wide first stage followed by a reranker that picks what reaches the window.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: What does contextual retrieval do at index time, and what does it buy?
  back: Contextual retrieval adds meaning to chunks at index time, while contextual compression removes text at query time.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: Why does the contextual-retrieval prompt put the whole document before the chunk?
  back: Putting the whole document first in each call turns the cache into the cheap way to give every chunk its context.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: Why are recent turns kept verbatim, and why are phase boundaries the better trigger?
  back: Compact at a phase boundary and keep recent turns verbatim, because the agent's working state lives in those turns.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: Which compression strategy finished the OpenAI co-founders task cheapest, and what did its prompt contain?
  back: Compression is understanding, so the compressor needs the task and the known state in its prompt.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: How do you stop compaction from dropping constraints, and why is a deterministic check needed?
  back: Pin constraints outside the summary and verify with a deterministic check, because compactors misreport what they kept.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: Rank what must survive compaction, and say why tool output comes last.
  back: 40k tokens of test output compress to "17 passed, 2 failed", while a one-sentence rationale cannot compress at all.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: Why must a memory system update and delete, rather than only append?
  back: Append-only memory is slow-motion context poisoning, so new facts must update or delete the old ones.
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: Which memory format suits critical low-volume facts, and which suits high-volume low-stakes ones?
  back: Use rich cards for critical, low-volume facts and simple notes for high-volume, low-stakes ones.
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: What does "the writer caps every reader" mean for extraction-based memory?
  back: Extraction loses information for good, so with a strong model keep the source and make it searchable.
  lesson: ai-engineering/02-context-engineering/notes/06b-memory-architectures
- front: Which format should you use for document boundaries, for prose, and for state a program reads?
  back: Use tags for boundaries, markdown for prose, and JSON for anything a program reads back.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: Why must structured state be validated before it re-enters the window?
  back: A malformed state block that is re-injected compounds on every turn, so validate at the boundary.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: What is the difference between cognitive prompting and cognitive tools, and what did the change buy?
  back: Cognitive tools apply context isolation to reasoning, because only each step's result returns to the main trace.
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: Why does a same-model verifier stop helping after a few rounds?
  back: Tests, parsers and calculators beat a model's verdict, so replace a model verifier with a deterministic check where possible.
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: What is real and what is oversold about protocol shells?
  back: A protocol shell's value is its four explicit sections, and markdown with the same sections works as well.
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: What does a sub-agent buy the orchestrator, and what does it cost in absolute spend?
  back: Sub-agents suit genuinely parallel, separable work, and they should be passed the decisions as well as the task.
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: How do tool definitions and tool results each spend the context budget?
  back: Tool descriptions are resident on every call, and results should return what the agent needs to decide, with structured errors.
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: Name the five context failure modes and the signature of each.
  back: Rot, poisoning, distraction, clash and injection have distinct causes and fixes, yet get misdiagnosed as each other.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: Walk through the five-step context diagnostic, and say what the last step separates.
  back: Rerunning the task with minimal context is the step that separates a context problem from a prompt or capability problem.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: Which prompt-injection defenses are guarantees, and which are only probabilistic?
  back: Every context-level defense against injection is probabilistic, and only code-level controls are guarantees.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: What four questions does a context eval ask in sequence?
  back: A context eval asks whether the fact existed, was retrieved, survived and was used, so each failure points at one stage.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: Describe the ablation experiment and the three actions its result can trigger.
  back: Removing one component while holding the rest fixed shows whether to cut it, compress it or protect it from compaction.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: What does the context maturity ladder warn about teams who jump to orchestration?
  back: Most production failures at level 4 are level-2 problems, and each rung multiplies cost and failure modes.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: In what order do you ask the design questions for a new context system?
  back: Start from the eval set and the smallest workable window, then add machinery only for something the model demonstrably lacks.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: How should you read claims about context attractors and resonance?
  back: Ask what the measurable behavior is, because the field-theory vocabulary has little testable content beyond a few small results.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
- front: Give one rule of thumb each for assembling, selecting, compressing and isolating context.
  back: 'Justify every token: keep stable content first, cap what grows, pin the rules, and measure before adding machinery.'
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: Which pillar picks up when the loop assembling context becomes stateful?
  back: Next comes the harness, which owns the loop that assembles this context on every call and keeps it reliable.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: What is the goal of context engineering?
  back: Find the smallest set of high-signal tokens that makes the desired outcome likely. A bigger window changes the ceiling, not the goal.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: Why isn't a bigger window a fix?
  back: 'Attention relates every token to every other, so pairs grow as n², and benchmarks fall well before the limit: GPT-5 (272K) is near 0% on OOLONG-Pairs by 33K while needle recall holds to 262K.'
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: Name the shapes context rot takes.
  back: The middle of the window gets neglected, distractors pull answers away, instructions decay over a long session, and needle-style recall hides all of this because it stays high.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: A vendor shows 100% passkey recall at 1M tokens. Do you buy it for long-document analysis?
  back: Not on that evidence. Qwen2.5-1M holds passkey to 1M while its LV-Eval falls from 54.5 at 16K to 43.3 at 256K, so I'd test on reasoning questions at my real length.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: Does a new architecture that reads 1M tokens end context limits?
  back: It moves where rot starts. Infini-attention solved passkey out to 1M only after fine-tuning on 5K-token passkey inputs, and zero-shot it found start or middle passkeys only 3-14% of the time.
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: Pointer or payload in the window?
  back: 'A pointer, unless the content is needed on nearly every turn: it costs a few tokens and the payload stays one tool call away.'
  lesson: ai-engineering/02-context-engineering/notes/01-why-context-is-finite
- front: What goes in the stable prefix and what stays out?
  back: System prompt, tools and stable memory go in, in a fixed order. Time, per-user quota, retrieved documents and history stay out, because any change there invalidates everything after it.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: Your agent's bill doubled overnight and TTFT went from 0.5 s to 3-5 s, with no model change. First check?
  back: Diff the assembled prompt between two calls and look for a value that changes in the prefix, such as a `Current time` line, then read the cache-hit numbers.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: What does "altitude" mean for a system prompt?
  back: 'The level between brittle rules and vague guidance: specific enough to steer behaviour, general enough to carry heuristics, with 2-5 examples for the hard cases.'
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: What does a status bar buy, and how do you keep it accurate?
  back: In Li and Shi (11 models, about 24k evals), weak models gained 40-54 points and strong models kept accuracy while cutting reasoning tokens 80-90%. Maintain it in code from observations, and monitor it, since errors above about 10% are worse than no bar.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: Why would sub-agents be byte-aligned with their parent?
  back: So their side queries reuse the parent's cached prefix. Same prompt, tools, model config and message prefix means a cache hit instead of a fresh prefill.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: 'Flatten messages to `USER: ... ASSISTANT: ...` text to save effort?'
  back: No. The main damage is leaving the trained format, which leads to ignored tool results, repeated actions and text where a call was needed. Use the API's structured roles.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: How much cheaper is a cached read?
  back: About one-tenth of fresh prefill at Anthropic, DeepSeek and OpenAI's GPT-5 family, as a rough figure that ignores any cache-write premium. Anthropic needs explicit `cache_control` breakpoints.
  lesson: ai-engineering/02-context-engineering/notes/02-context-anatomy
- front: What do you allocate first in a context budget, and why?
  back: 'The output reserve: `max_tokens` plus any thinking budget. A window filled with input leaves the model no room to answer.'
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: How do you decide whether a component deserves its tokens?
  back: Ablate it and measure quality per 1k tokens. The information-theoretic version is its added information about the right answer given everything else, `I(Y*; c | C_rest)`.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: Does prompt caching change your budget?
  back: It changes the cost side only. A cached 20k prefix is cheap and fast but still takes attention, so I keep separate cost and quality budgets.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: Your agent's edits to old tool results made it more expensive. Why?
  back: An edit changes the text, so everything after it is prefilled again, and Fu et al. put KV-cache reads at 82.4% of API cost. Batch edits at stable boundaries.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: Summarize tool output or drop it on a rolling basis?
  back: Where you control serving, Fu et al.'s rolling-drop beats threshold summarization by +1.7 points at 27.7% lower cost. On a hosted API you can't edit the KV cache, so you only get the lesson about edit timing.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: Is a 20/30/30/15/5 split correct?
  back: It's a heuristic from the upstream reference. The two rules that matter are reserving output first and capping every growing component.
  lesson: ai-engineering/02-context-engineering/notes/03-budgeting-the-window
- front: Pre-load or fetch just in time?
  back: Pre-load only what's needed on about ≥80% of turns. Otherwise a path costing about 10 tokens beats a 5,000-token file.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: RAG or long context for a document set?
  back: 'Depends on the query: on LOFT with 128k in the prompt, Gemini 1.5 Pro matched specialized retrievers on text retrieval (.77 vs .76) and RAG (.53 vs .52) but not SQL-like reasoning (.38 vs .65).'
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: How do you combine them?
  back: 'Route. Full context and top-5 RAG gave identical answers on 63% of LongBench queries, so Self-Route lets RAG answer first and escalate on "unanswerable": 48.89 against 48.67 for GPT-4o on 61% of the tokens.'
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: What does latency look like at long context?
  back: LOFT saw roughly 4 s, 12 s and 100 s at 32k, 128k and 1M. A long-context design has to be acceptable at that latency before accuracy matters.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: When does retrieval structurally fail?
  back: On aggregation and rule induction, where the answer isn't in any chunk. Distill those at index time, for example the count of 90 black cats or the nurse rule.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: Why add context to chunks before embedding?
  back: Anthropic reports top-20 retrieval failures down 49% with contextual embeddings and contextual BM25, and 67% with a reranker, at about $1 per million document tokens with prompt caching. A chunk alone often lacks the identifier that makes it findable.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: Two retrieved documents contradict each other. What do you do?
  back: Surface the conflict rather than silently picking one. To stop it recurring, tag chunks with a version and effective and expiry dates and filter at query time, since a superseded policy left in the index gets retrieved alongside its replacement.
  lesson: ai-engineering/02-context-engineering/notes/04-retrieval
- front: What should survive compaction word for word?
  back: Constraints, identifiers, numbers, error strings and open decisions. A summary can paraphrase reasoning, not these.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: How safe is `/compact` for safety rules?
  back: 'Not safe alone: Zerhoudi measured 53% kept after one round and 10% after five on Sonnet 4.6. Wang et al.''s constraint registry, appended verbatim after the summary, reached 90-95%.'
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: When do you trigger compaction?
  back: Near ~80% occupancy or at a phase boundary, and the boundary is usually the better moment because state is clean there.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: Why might per-turn trimming cost more than no trimming at all?
  back: 'Each edit rewrites the prefix so the cache misses: 1.85× the full-context baseline for last-12-responses on 100 BrowseComp-Plus tasks. A 48K summarization threshold was about 7% cheaper than full context but lost 5 accuracy points.'
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: You have a 1M-token codebase task. Summarize or use recursion?
  back: 'If the answer depends on dense access throughout, try an RLM: GPT-5 scored 58.0 as one against 0.1 F1 alone or with summarize-on-overflow on OOLONG-Pairs, and 91.3% against 70.5% on BrowseComp-Plus. The costs are latency and a long tail of expensive runs.'
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: How do you test a compressor?
  back: 'Plant known facts, compress, and check deterministically. TypeCompact shows why: a reported recall of 1.00 hid a mean drop of 57%.'
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: When does crash recovery stop being optional?
  back: Past roughly thirty minutes of agent runtime, as a rule of thumb, because the probability of some interruption over a long run approaches one.
  lesson: ai-engineering/02-context-engineering/notes/05-compression-compaction
- front: Episodic or semantic memory?
  back: Episodic records what happened, semantic records what's true, and the useful step distils the first into the second, such as three commit-format corrections into one rule.
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: How would you handle "I moved to Shanghai" when "lives in Beijing" is stored?
  back: Run a write-time decision between ADD, UPDATE, DELETE and NOOP, then UPDATE. Append-only leaves two contradictory facts for retrieval to choose between.
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: How do you structure user facts for reliability?
  back: 'When questions aggregate, use typed state: User as Code regenerates typed Python from a fact log and reached about 99% on aggregation against 6-43% for retrieval-based memory, because a count becomes one expression.'
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: What's the highest-leverage part of an index-plus-detail memory?
  back: The one-line hook, because it decides whether the detail file ever gets opened.
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: How do short-term and long-term memory differ?
  back: The trajectory is an append-only log that is never rewritten, while long-term memory is an archive that gets rewritten, merged and pruned. Working memory is the filtered subset of both that is in the window right now.
  lesson: ai-engineering/02-context-engineering/notes/06-memory
- front: Does a good memory system need a vector database?
  back: Not always. ChatGPT's memory, as analysed here, has four layers with about 33 facts and about 15 summaries and no vector DB, and Peng found a coding agent searching raw history hit 99% at under half full context's cost, on one conversation and one run.
  lesson: ai-engineering/02-context-engineering/notes/06b-memory-architectures
- front: Do you evaluate a memory system on overall answer accuracy only?
  back: No. Evaluate at three levels, including hit rate. In Peng's test Opus 5.5 reading Zep's GPT-4o-mini graph scored 45% against GPT-4o-mini's 43%, so a stronger reader can't recover what a weak writer never stored.
  lesson: ai-engineering/02-context-engineering/notes/06b-memory-architectures
- front: Extract facts at write time, or keep raw chunks?
  back: 'Keep raw chunks and invest in retrieval: in Yuan et al.''s grid (ten LoCoMo conversations, GPT-5-mini) the retriever moved accuracy by 20 points and the write strategy by 3–8.'
  lesson: ai-engineering/02-context-engineering/notes/06b-memory-architectures
- front: How does MEM1 keep memory constant?
  back: It overwrites one internal state each turn instead of appending. On 16-question multi-hop QA, MEM1-7B answered 3.5× more questions than Qwen2.5-14B at 3.7× less peak memory, with most of the gain from RL.
  lesson: ai-engineering/02-context-engineering/notes/06b-memory-architectures
- front: When does a fixed-size compressed memory fail?
  back: 'On exact recall: Artificial Hippocampus Networks scored 26.8% on NIAH at 128K (Qwen2.5-7B), the same as dropping the old tokens, against 98.6% for full attention.'
  lesson: ai-engineering/02-context-engineering/notes/06b-memory-architectures
- front: Why does structure help a model at all?
  back: It gives separation, addressability and consistency, so less attention goes to working out what each part is. Yang et al.'s symbolic circuit makes this plausible but doesn't prove it.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: JSON, XML tags or markdown?
  back: Tags for boundaries, markdown for prose, JSON for anything a program reads back.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: If the provider enforces a schema at decode time, do you still validate?
  back: Yes. Enforcement stops parse failures, but `jsonschema.validate` still catches constraints the provider's subset doesn't support, such as patterns and cross-field rules.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: A model returns invalid JSON one time in ten. What's your design?
  back: A small retry loop that appends the validation error and caps attempts, then fails loudly to the harness. In the worked example three attempts took the prompt from 292 to 600 characters, so retries also cost context.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: How should agent state be stored in the window?
  back: As a single block that's overwritten on each update, not an appended log, so there is only one current `next_step` for the model to follow.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: When do you use triples rather than prose?
  back: When the facts are relationships that the task will traverse or check, and a table or graph gives the model and your code one consistent, addressable form.
  lesson: ai-engineering/02-context-engineering/notes/07-structured-context
- front: What's a cognitive tool?
  back: 'A reasoning step packaged like a function: a named prompt with inputs and outputs that the model or your code can call, and which adds no external capability.'
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: What's the evidence for them?
  back: 'Ebouky et al.: GPT-4.1 on AIME 2024 went from 32.0 to 53.0 with tools, against 42.0 for cognitive prompting and 44.6 for o1-preview.'
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: Do they help every model equally?
  back: No. Qwen2.5-32B went from 17.2 to 32.1 and Llama3.3-70B from 13.1 to 29.8, but Qwen2.5-7B only from 12.5 to 14.6 and Llama3.1-8B from 5.8 to 8.8.
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: Should a tool call or a fixed order drive the reasoning?
  back: Let the model choose when the problem varies, since that freedom accounts for the +11 over forced cognitive prompting. Use a program with a fixed order when the workflow is known.
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: Your self-correction loop stops at a self-score of 0.8 and quality is flat. Why?
  back: The verifier shares the writer's blind spots. In a simple model with `blind=0.9`, accuracy stays near 0.526 at any bound, so replace the self-score with a deterministic check.
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: How many correction rounds do you allow?
  back: 2-3. In the worked model with a perfect check, 3 rounds reach 0.938 from 0.5, and further rounds add little while each one adds to the window.
  lesson: ai-engineering/02-context-engineering/notes/08-cognitive-tools
- front: What's a protocol shell?
  back: A structured prompt in pseudo-code with a name, intent, inputs, ordered process and declared output. The model doesn't execute it, and no parser exists.
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: Is Pareto-lang a real language?
  back: It's a shared vocabulary of operations such as filtering and compression, read by the model as text, so its value is consistency and not special syntax.
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: Shell or markdown?
  back: Results should be about the same with the same four sections. Pick the shell for a reusable, shareable procedure among non-coders, and a prompt template with variables if the users code.
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: How does "protocol" here differ from MCP?
  back: A shell is a prompt pattern read by a model, while MCP is a wire protocol carrying context between programs (10).
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: Name a test for a good step.
  back: If it needs "and", split it, because one action per step keeps the model from doing only half of it.
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: A colleague wants to adopt the full catalogue of about 50 shells. What's your advice?
  back: Adopt the four-part form and only the shells that match repeating workflows, and treat the `/attractor.*` and `/resonance.*` shells as the speculative material covered in 99.
  lesson: ai-engineering/02-context-engineering/notes/09-protocols
- front: When do you use sub-agents?
  back: 'When the tasks are independent and the window is the constraint, after compression has been tried, since isolation has the highest cost: 240k real tokens for 6k visible in this chapter''s example.'
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: What does the orchestrator hold?
  back: The plan and summaries, about 2k rather than 100k, and that is the benefit of isolation.
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: How long should an agent's description be?
  back: Long enough to route on. A ~45-token description that says when to use it beats a ~9-token label, and the cost is small compared with a wrong delegation.
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: Why does MCP help at scale?
  back: 'It turns an M×N integration problem into M+N: 12 integrations become 7 in this chapter''s example.'
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: Your team wants to auto-generate an MCP server from your REST API. What do you say?
  back: 'No: granular endpoints mean several tool choices per action, and at 95% each five choices succeed only about 77% of the time, at around 8× the tokens in the book''s estimate.'
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: An agent's output is passed to the next agent and a schema field is renamed. What should happen?
  back: The pipeline should fail at the boundary rather than continue on empty input, as in Rothman's `facts` versus `summary` case. Pass outputs by reference and validate them in code.
  lesson: ai-engineering/02-context-engineering/notes/10-tools-and-multi-agent
- front: Name the five failure modes in one line each.
  back: 'Rot: quality declines as the window fills. Poisoning: a false fact gets reused. Distraction: irrelevant material outcompetes evidence. Clash: two sources disagree. Injection: data acts as an instruction.'
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: An agent misbehaves at turn 40. What's your first move?
  back: Print the window that was actually sent. Most context bugs are visible there, and many turn out to be assembly bugs.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: How do you tell a context problem from a prompt problem?
  back: 'The minimal-context test: if the same task works with minimal context, it''s a context problem, and if it still fails, it''s a prompt or capability problem.'
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: An injection filter passes all your tests. Are you safe?
  back: 'No, a regex can be beaten by paraphrase. Treat instructions as code-level controls: fail closed, check both ends and restrict what tools can do.'
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: Retrieval returns 40 documents to be safe. Good idea?
  back: Usually not, because distractors compete for attention. Rerank down to what's needed, around 3 in this chapter's example, and measure.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: A user says "use pnpm" at turn 12, and "we use npm" from turn 3 is still in the window. What's the fix?
  back: That's a clash, and nothing marks turn 3 as superseded. Remove or date the stale statement, and state a precedence rule rather than relying on recency.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: The same task works in one message but fails over several turns, with the window nearly empty. What's going on?
  back: 'Probably not rot: in Laban et al.''s simulations, GPT-4o and GPT-4o-mini degraded at two turns, and the authors suspect models build on their early guesses. Their advice is to restate the requirements in a fresh session.'
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: Context poisoning or memory poisoning?
  back: Context poisoning is a hallucination, stale fact or wrong retrieval in the window being treated as truth. Written to long-term memory it becomes durable and is re-injected every future session, so one hallucination turns into a permanent false belief.
  lesson: ai-engineering/02-context-engineering/notes/11-failure-modes
- front: How do context evals differ from prompt evals?
  back: Prompt evals ask if the instructions work. Context evals ask if the right material reached the window and whether the model used it, so they need separate metrics.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: What are the three levels of a context eval?
  back: Component (retriever recall@k, compactor retention), integration (retrieved chunks survive budgeting, memory writes are read back) and system (task success, groundedness, tokens per task).
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: 'Compression ratio 13.7× against 6.1×: which compactor do you ship?'
  back: Ask for retention first. In this chapter's toy, the 13.7× one kept 2 of 5 facts and the 6.1× one kept all 5, so I'd ship the second.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: What's ablation?
  back: Removing one component at a time and measuring the change, so that each part of the window has to justify its tokens.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: Quality falls as sessions get longer. How do you test it?
  back: Sweep occupancy at 10, 25, 50 and 75% with the evidence at different positions, which separates a length effect from a position effect.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: Which cost metric do you report?
  back: Tokens per successful task, because a per-call number makes cheap failed runs look good.
  lesson: ai-engineering/02-context-engineering/notes/12-evaluating-context
- front: What's the rule for moving up the maturity ladder?
  back: Climb only when the level below fails measurably, because each level adds tokens and failure modes.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: How would you generate a 40-section report?
  back: Outline, evidence per section, and a capped running summary. With this chapter's assumed sizes, section 40 is 2.8k tokens that way against about 79.8k with full prior text.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: What's reconstructive memory, in practical terms?
  back: Retrieval over atomised fragments plus model-written synthesis, rather than replaying transcripts. It's sound, but synthesis can confabulate connections, so keep source pointers.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: What's the first question when designing a context system?
  back: What success looks like and how you'll measure it, so the eval set comes first. Then the smallest window that could work, and only then what the model lacks.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: A stakeholder asks for a research agent with memory, graph and four agents. How do you respond?
  back: Start with the lowest level that could work, build the baseline eval, then add each lever only for a measured gap.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: When have you left context engineering behind?
  back: When the loop that assembles context becomes stateful and conditional, you're in the harness layer.
  lesson: ai-engineering/02-context-engineering/notes/13-putting-it-together
- front: Is the semantic field a real mechanism?
  back: It's a metaphor for context behaviour, useful as vocabulary but not as an engineering method.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
- front: Does a CHSH value above 2 show quantum semantics?
  back: No. Agostino's S of 1.2-2.8 (several runs at 2.3-2.4) breaks the classical bound only if no-signalling holds, and direct influence alone reaches 4.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
- front: What did Yang et al. show?
  back: A three-stage circuit of abstraction, induction and retrieval heads in Llama-3.1 70B at 95% on small tasks such as ABA and ABB. It supports structure as a mechanism on those tasks, no further.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
- front: What's a practical takeaway from Wang's paraphrasing result?
  back: Iterated rewriting can fall into a 2-cycle between clusters, so don't assume that repeated summarization converges on the meaning.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
- front: What do you keep from the track?
  back: That early framing is sticky, salience comes from structure and repetition, and ambiguity gets resolved by context. All three translate into window design choices.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
- front: A colleague proposes a "resonance score" as an eval metric. How do you respond?
  back: Ask for its definition in measurable terms, and whether it predicts task success better than existing metrics, otherwise I'd stick with fact retention and task success.
  lesson: ai-engineering/02-context-engineering/notes/99-speculative-field-track
---
