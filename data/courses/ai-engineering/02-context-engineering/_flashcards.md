---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/02-context-engineering/slides/deck.yaml
cards:
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
---
