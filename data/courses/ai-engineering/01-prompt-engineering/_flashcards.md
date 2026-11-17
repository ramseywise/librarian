---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/01-prompt-engineering/slides/deck.yaml
cards:
- front: What four ways does the assistant fail, in the order this lecture takes them?
  back: The assistant first misreads the request, then guesses at the answer, then cannot act on it, and finally breaks under real traffic.
  lesson: ai-engineering/01-prompt-engineering/readme
- front: Name four things this lecture teaches you to do with a prompt.
  back: You will be able to write the prompt, pick the technique, shape the output and prove each change with an eval.
  lesson: ai-engineering/01-prompt-engineering/readme
- front: Why can nothing later in a prompt change how earlier text was read?
  back: Attention flows one way, so a model reasons further only by writing tokens, which is why chain-of-thought works.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What happened when the word-count instruction moved in front of the paragraph, and what test does it suggest?
  back: Moving the instruction before the paragraph took the count from 348 to 173; if an expert could not finish in one read, restructure.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Besides left-to-right attention, what four properties of LLMs explain most prompting rules?
  back: Tokenization, no backtracking, truth bias and the chat transcript explain why reordering beats asking harder.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What does a chat request become before the model sees it, and why must user content stay out of the system role?
  back: The API renders messages into one transcript, so roles shape behaviour but only reserved tokens separate speakers.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Which three mistakes follow from how the model reads, and what is the fix for each?
  back: Do character work in code, ground and verify rather than telling the model not to hallucinate, and keep user text out of the system role.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What four criteria must every prompt meet, and which one is never automatic?
  back: A prompt must resemble training data, carry all relevant information, lead to a solution and have a stopping point; only carrying the right information never comes free.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: What is the Valley of Meh, and how does the sandwich structure respond to it?
  back: Content in the early middle of a prompt is used least, so state the task early and refocus on it at the end.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: In Li's Tau-Bench ablation, which change to an agent's system prompt hurt most, and which barely mattered?
  back: Flattening procedure to an unordered list cut success by over 30% while tone barely mattered, so write numbered procedures and ablate one component at a time.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: According to Min et al., what do few-shot examples actually teach?
  back: Few-shot examples mostly teach format and label space, so add them only when zero-shot fails in a way you can name.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: What does ReAct add to chain-of-thought, what are the ALFWorld results, and how does it fail?
  back: ReAct alternates reasoning with actions so answers rest on retrieved facts (71% vs 45% on ALFWorld), and a single bad search can derail it.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: When does Reflexion work, what result did it achieve on HumanEval, and when does it become dangerous?
  back: Reflexion retries with written feedback (91% vs 80% on HumanEval), so it needs reversible actions and an evaluator stronger than the actor.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: How much did chain-of-thought improve PaLM 540B on GSM8K, and how do you keep the reasoning away from the user?
  back: Chain-of-thought lifted PaLM 540B on GSM8K from 17.9% to 56.9%; a parseable block lets the app show only the answer.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: How do Tree of Thoughts and CoT compare on Game of 24, and what does ToT need that CoT does not?
  back: Tree of Thoughts recovers from dead ends through generate, evaluate and backtrack (4% to 74% on Game of 24), at the cost of a code controller.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: Given a task's failure, which prompting technique do you reach for, and what does it cost?
  back: Name how the output fails, then choose the cheapest technique that buys what is missing.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: What does a stronger output guarantee fix, and what must you still validate?
  back: Stronger output guarantees fix the shape and never the truth, so validate the values too.
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Who executes a tool call, and what does the tool-calling loop look like?
  back: The model only proposes tool calls; your application executes them and appends the result as a message.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: What makes a good tool definition, and what happens if you include arguments the app already knows?
  back: Tool names, descriptions and enums steer the model's choice, so write them with the care you give a prompt.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: What is the tradeoff between generality and strength, and why does splitting a prompt into steps help?
  back: A chain gives each step one job and a checkable output, so a failure has an address and a retry point.
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: How do workflows and agents differ on control flow, and which question comes first for any task?
  back: Prefer a workflow when steps are known, since an agent trades predictability for handling open-ended tasks.
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: What prompting habits should you drop with reasoning models, and how do you control their cost?
  back: With reasoning models, state the goal and tune effort upward only while eval scores keep improving.
  lesson: ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models
- front: Which reasoning-model failures can you not catch by reading the visible chain of thought?
  back: Judge a reasoning model by its outputs and an eval, since the visible chain of thought is neither a complete record nor a safety monitor.
  lesson: ai-engineering/01-prompt-engineering/notes/07b-reasoning-model-failure-modes
- front: What is the offline path from cheap checks to judges?
  back: Start offline with cheap exact checks, escalate to judges only where needed, and watch acceptance online as a guardrail.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: What makes a good LLM judge rubric?
  back: Ask judges a specific, ordinal, multi-aspect question, and calibrate their scores against several human annotators.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: What does the prompt modification case study show about F1, template adherence and methodology?
  back: Prompt wording can move F1 by 26 points and trade against format adherence, so change one thing and re-score.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: Which three mistakes make a prompt eval mislead you, and what is the fix for each?
  back: An eval misleads when the judge's question is vague, when a model grades itself, or when you score the rows you patched, so split the question and hold out rows.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: What is the rule for keeping a new prompt version?
  back: Version the template with its model and score, and keep a new version only when it beats the old on the eval.
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: How should you layer defenses against prompt injection?
  back: Layer defenses from prompt warnings up to quarantined architectures, and treat all model output as untrusted.
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: How do you get diversity in synthetic data generation, and what are its pitfalls?
  back: Synthetic data needs variation seeded into the prompt, and skewed seeds or same-model evals give skewed results.
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: What should you do first to a production prompt you inherit?
  back: Start any inherited prompt with a small committed eval, then fix structure, side-effect gates and untrusted text.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
- front: What do you shape first, where do guarantees live, and how do you prove a change?
  back: Shape the document first, then keep guarantees in code and prove every change with an eval.
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: What does prompting leave to the next pillar?
  back: Prompting sets what the model is asked; the next pillar decides what else sits in the window with it.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: What is a prompt, mechanically?
  back: The opening of a document. The model continues it with the most plausible next tokens, and chat, tools and agents are all application code building text before the call and parsing it after.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Why does chain-of-thought work, mechanically?
  back: Compute per token is fixed and insights only flow upward through the layers, so a thought written out as tokens is the only way the model can reuse it. Reasoning before the answer conditions the answer on it.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Why can't telling the model "don't hallucinate" fix hallucination?
  back: 'To the model a hallucination is the same as any other completion: it is always guessing, and the guess has the right shape. Ask for checkable output and ground it with retrieved context.'
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What did RLHF add that SFT alone could not?
  back: Honesty signal. Labelers writing ideal answers can't see what the model knows, while ranking its own completions rewards content consistent with its knowledge. GPT-4 went from about 30% to about 60% on TruthfulQA after RLHF.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Why does a system message carry more weight than a user message, if both go into one sequence?
  back: It sits first, and models are post-trained to rank it higher. There is no separate channel.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: You swap one open-weight model for another and quality drops with no errors. What do you check first?
  back: The chat template. A wrong template or an extra newline fails silently, so print the final serialized prompt and compare it with the model card.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Raw completion or chat API, when would you pick each?
  back: Chat by default for steerability and clear turns. Use completion when you need output control, or a range of voice RLHF narrows, and accept that you own the template.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What are the four criteria every prompt has to meet?
  back: Resemble training data, carry all relevant and only relevant information, lead to a solution, and have a natural stopping point. Chat models give you 1, 3 and 4 largely through fine-tuning, and 2 is never automatic.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: How would you decide what to fetch for a prompt?
  back: Ask about latency, preparability and comparability for each source, sort by proximity and stability, gather more than fits, then score it. All context is optional, and you quantify how optional.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: Should you default to embedding retrieval?
  back: 'No. Lexical search is cheap and debuggable, and Copilot uses plain Jaccard over open files. Neural retrieval earns its place by matching ideas: synonyms, typos, other languages.'
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: General or task-specific summary?
  back: Specific keeps what the task needs but must be redone if the question changes. General can be shared across questions, apps and models, but may drop the offhand detail you needed.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: What is the Valley of Meh, and what is the evidence?
  back: Early-middle content gets used less than the start or the second half. Liu et al. moved the answer document through 10 to 30 documents and accuracy was U-shaped in every model, with mid-position accuracy below closed-book for GPT-3.5-Turbo.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: What is the sandwich technique?
  back: An introduction that frames the task, the long context, then a refocus restating the question near the end, followed by a transition into the answer. It covers both models that do better with the task first and those that do better with it last.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: Your support agent skips "verify identity" about a third of the time. The prompt lists all the rules. What do you try?
  back: Rewrite it as an SOP with ordered stages. Flattening a procedure to a list cost over 30% success in Li's ablation, while tone changes hardly mattered. Ablate before rewriting.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: Zero-shot or few-shot first?
  back: Zero-shot, then add examples only when it fails in a way you can name. Few-shot still earns its place for non-obvious format, or a domain the model rarely saw, like Huyen's Ibis example.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: Do labels in few-shot examples have to be correct?
  back: 'Less than you''d think. Min et al. found random labels still beat no examples, since label space, input distribution and format matter more. Don''t take that as licence, though: correct labels aren''t what''s being tested there.'
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: When does Reflexion fail?
  back: With a weak evaluator or irreversible actions. On MBPP Python, its self-written tests passed wrong solutions, so it stopped early and scored below no reflection.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: How big are chain-of-thought's gains?
  back: 'Large on math: Wei et al. took GSM8K from 17.9% to 56.9% with PaLM 540B. Near zero on commonsense: 74.8% to 75.7% in Sprague''s runs, and small models scored below standard prompting.'
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: Why does "Let's think step by step" use two calls?
  back: The first generates the reasoning, and the second appends an extraction prompt such as "Therefore, the answer (arabic numerals) is" to get a parseable answer.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: Why did Tree of Thoughts reach 74% on Game of 24 when 100 CoT samples got only 9%?
  back: Most CoT failures come at the first step. Evaluating and backtracking fixes that, while sampling more chains doesn't. It needs a controller loop in code, so it is orchestration more than a prompt.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: You have invoice math failing under CoT. CoT, self-consistency or PAL?
  back: PAL, in a sandbox. On GSM8K-Hard, plan plus Python reached 68.0% against 47.8% for CoT with Llama 3.1 70B, and code is exact where voting only reduces noise.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: Stop sequence or stream-and-cancel?
  back: Prefer a stop, since it wastes nothing server-side. A stop is a fixed string though, so endings like a matching brace or a dedent need streaming and cancelling. Combine them for the common cases.
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Rank the ways to get structured output, and how far should you climb?
  back: Ask, show, fence, prefill, constrain, tool schema. Climb only as far as you need, and note some newer models reject a prefilled assistant turn. None guarantees truth.
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Can JSON output hurt accuracy, even when it parses?
  back: 'Yes. Tam et al. saw LLaMA 3 8B lose 38.15 points on Last Letter with only 0.148% parse failures. It can also help: Gemini 1.5 Flash rose from 41.6% to 60.3% on DDXPlus. The tests were on small 2024 models and simple schemas.'
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: What do logprobs give you, and how would you use them for quality?
  back: 'The log probability of each token and its alternatives, at no extra compute. Average rather than sum, gate on the score, and don''t interrupt users on low confidence: the book''s "don''t be like Clippy".'
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Your moderation model blocks too many emails. There's no budget to retrain. What do you do?
  back: 'Calibrate: 50% isn''t your threshold. Shift the logprob per label by a constant (the book adds 0.3 to "Yes" before comparing with "No"), found by experiment or cross-entropy on labeled data.'
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Prompting, soft prompting, LoRA or full fine-tune?
  back: LoRA for formats and priors, with hundreds to thousands of examples and days of work. Full fine-tuning for new facts, with tens of thousands and weeks to months. Soft prompting is fastest, but Lester et al. only matched full tuning at T5-XXL (11B).
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Does Phoenix & Taylor's Fig 1-13 show fine-tuning beating prompting after a few thousand examples?
  back: No. Both curves are fine-tuned RoBERTa, one with a prompt and one with a classifier head. Scao & Rush's result is that the prompt's advantage is worth hundreds of labelled points and runs out with more data.
  lesson: ai-engineering/01-prompt-engineering/notes/04-controlling-output
- front: Does the model execute tools?
  back: No. It proposes a call as tokens, your code executes it and appends the result, and the loop stops when a reply has no tool calls.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: How do tool definitions reach the model on OpenAI, per the book's reconstruction?
  back: As TypeScript-style declarations in a `namespace functions` block appended to the system message. They count against your budget, and a call is just more tokens.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: Why TypeScript rather than raw JSON Schema there?
  back: Richer types, natural doc comments, and named arguments, which put each argument's name right before its value and cut mis-assignment.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: How would you force structured output with tools?
  back: Define a tool whose parameters are your schema and set `tool_choice` to that tool. The call is the output, and no tool needs to exist.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: Should the system prompt or the code enforce confirmation before a booking?
  back: Code. A prompt instruction will eventually be skipped, so let the model request freely and intercept side effects with approval that shows the exact arguments.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: Your agent has 40 tools and often picks the wrong one. What do you try first?
  back: Expose only the tools relevant to the conversation's state, merge overlapping ones, sharpen when-to-use descriptions and add a routing rule. Every extra tool is a distractor.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: What's a good tool error?
  back: One phrased in the tool's own terms, such as "`date` must be YYYY-MM-DD", so the model can retry correctly. A raw stack trace doesn't help it.
  lesson: ai-engineering/01-prompt-engineering/notes/05-tools-and-function-calling
- front: Why split one prompt into several?
  back: 'Strength over generality: one job, short context, a checkable output, and a failure that traces to one step. GoDaddy''s split of a 1,500+ token prompt performed better and cost fewer tokens.'
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: What's the default topology, and why?
  back: A DAG. Each task gets what it needs directly and dependencies stay simple, where a pipeline loses what isn't passed along and a cycle must carry failure context and an attempt cap.
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: Where should retry logic live?
  back: Inside a task when possible. A cycle across tasks forces every task to handle retried items.
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: How do you get an LLM to extract structured data reliably?
  back: A forced tool call whose parameters are the schema, with strict outputs. If it still fails, check whether the source is hard for a human too and split a big schema across calls.
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: Workflow or agent?
  back: 'Workflow when steps are known: control flow in code, with high predictability and cost control. Agent for open-ended tasks. Most production systems are hybrids, with a workflow routing to agents.'
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: What are Anthropic's five workflow patterns?
  back: Prompt chaining, routing, parallelization (sectioning or voting), orchestrator-workers, and evaluator-optimizer.
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: Output quality on a task is short. In what order do you try fixes?
  back: 'Tighten the prompt, force a planning pass with `tool_choice: "none"`, then task-level Reflexion, and then sub-agents, which are heavier and costlier. Add a human for irreversible actions.'
  lesson: ai-engineering/01-prompt-engineering/notes/06-chaining-and-workflows
- front: What changes in prompting for a reasoning model?
  back: 'From how to think to what to achieve: high-level goals, constraints and format, with effort set by a parameter. Few-shot is only for style or format it gets wrong.'
  lesson: ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models
- front: Does explicit CoT help a reasoning-capable model?
  back: Often not. Li et al. saw it lower constraint accuracy for 13 of 14 models on IFEval and all on ComplexBench. Reasoning helped formatting and exact wording but dropped simple constraints.
  lesson: ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models
- front: What does "NoThinking" show?
  back: Ma et al. prefilled the thinking block in an open-weight model and used 2.0 to 5.1 times fewer tokens. It trailed at pass@1 but matched at large k, so with a verifier, try several thinking-off samples first. It couldn't be tested on closed models.
  lesson: ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models
- front: Do Shojaee et al.'s Hanoi results show reasoning collapses at scale?
  back: Be careful. Scoring required every move, and 2^N-1 moves overrun output limits, and Lawsen found unsolvable River Crossing cases. The overthinking result on easy tasks is the part that survives.
  lesson: ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models
- front: How do you add reasoning to a hybrid model in production?
  back: Thinking off first, optionally manual CoT, then low, medium and high effort while eval scores keep rising. Use it for the reasoning-heavy module only, such as planning or synthesis.
  lesson: ai-engineering/01-prompt-engineering/notes/07-prompting-reasoning-models
- front: Can you trust the visible chain of thought as a monitor?
  back: Not on its own, since it catches only what the chain states and chains are not always faithful. OpenAI's GPT-4o monitor flagged 0.17% of 102,443 o1-preview chains as deceptive.
  lesson: ai-engineering/01-prompt-engineering/notes/07b-reasoning-model-failure-modes
- front: You can only build one eval. Which?
  back: End-to-end, then unit tests on the critical path. Composition has no unit-level substitute.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: Offline or online?
  back: Offline first, because it needs no users. Online is the only fully valid data, but live traffic is scarce, so whittle candidates offline first.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: Where can eval samples come from, and what's the trap in each?
  back: Existing records (ubiquity against similarity), telemetry (doesn't exist before launch, and outcomes are biased by your own suggestions), and synthetic (tropes, plus bias toward the generating model).
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: What is SOMA?
  back: 'A judge rubric: Specific questions, an Ordinal scale with described levels, and Multi-Aspect scoring such as Copilot''s relevance, truth and completeness.'
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: What can you claim from "81% correct" from an LLM judge?
  back: Little alone. Scores are relative, so "B is judged correct more often than A" is the valid claim.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: Which online metric would you start with for a coding assistant?
  back: User acceptance. For Copilot it correlated with self-reported productivity gains more strongly than fancier impact measures. Set guardrails like latency and errors before the test starts.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: What did Clavié et al. show?
  back: With `gpt-3.5-turbo`, F1 rose from 65.6 to 91.7 by wording alone, zero-shot CoT beat few-shot, and a strict template raised adherence to 98% while cutting F1 from 89.3 to 86.3. Change one thing, re-score.
  lesson: ai-engineering/01-prompt-engineering/notes/08-evaluating-prompts
- front: How does APE work?
  back: An LLM generates candidate instructions from demonstrations, each is scored on a target model, and the best are kept and resampled. It found a trigger scoring 82.0 on MultiArith against 78.7 for "Let's think step by step".
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: What's the lasting lesson of OPRO's "Take a deep breath"?
  back: 'Not the phrase, which is model-specific: 80.2% against 71.8% on GSM8K with PaLM 2-L, with a different winner per scorer. Search against a metric beats intuition once you have one.'
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: What are the two meanings of meta-prompting?
  back: Structure-oriented templates for a class of problems (Zhang et al.), and using a model to write or critique prompts. Generated prompts are a first draft that must still win on your eval.
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: How does GEPA differ from keeping the best prompt?
  back: An LLM reads full traces to diagnose failures, and it keeps a Pareto front of candidates best on at least one example. The front gained 12.44 points where mutating the current best gained 6.05.
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: When is DSPy worth it?
  back: With a multi-step pipeline, a scorable metric, and dozens to hundreds of labeled examples. Skip it for one-off prompts or tasks you can't score automatically.
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: Prompts in git or a catalog?
  back: Same-repo git is simple, but moves all consumers together. A catalog versions each prompt on its own and can tell owners when a new version lands, which pays off when apps share prompts.
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: Your team wants a stronger model because quality is short. What do you check first?
  back: 'The cheaper layers: instruction clarity, context, ordering, examples, CoT, splitting. A stronger model costs money and latency, which is why early Copilot chose the small, fast Codex.'
  lesson: ai-engineering/01-prompt-engineering/notes/09-prompt-optimization
- front: Why is prompt injection compared to SQL injection, and how does it differ?
  back: Instructions and data share one channel in both, but LLMs have no equivalent of a parameterized query.
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: Are role markers a real boundary?
  back: Only for roles and only through the chat API, where reserved tokens can't be typed. Inside a turn it's still one channel, and self-serialized templates depend on how you call the tokenizer.
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: 'Direct or indirect injection: which matters more?'
  back: 'Indirect, for applications: the attacker needn''t be your user, and the harm scales with what the model can do, from a bad summary to exfiltration by an agent with email tools.'
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: What's the strongest design-level defense?
  back: Separating a privileged model from a quarantined one that reads untrusted content and can't call tools (the dual-LLM pattern, CaMeL-style tracking). It costs more engineering.
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: What does the instruction hierarchy do?
  back: Fine-tunes the model to rank system over user over model output over tool output. Wallace et al. report up to 63% more robustness, and you benefit by keeping retrieved text in `tool` messages.
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: Your model refuses "how do I kill a process?" What now?
  back: 'Over-refusal: track the false refusal rate next to the violation rate, and scope generic safety wording to your domain. Code Llama''s refusal went away when the broad system prompt was removed.'
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: Can you extract training data with no known context?
  back: Yes. Carlini started GPT-2 XL from empty prompts and got 604 verbatim strings from 1,800 top candidates, and Nasr et al.'s repeat-forever attack made ChatGPT diverge into memorized text.
  lesson: ai-engineering/01-prompt-engineering/notes/10-adversarial-prompting
- front: How do you get diverse synthetic data?
  back: Seed the prompt with sampled values per dimension, as TinyStories did with a ~1,500-word vocabulary and story features. Temperature alone gives near-duplicates.
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: What made phi-1 notable, and what's the caveat?
  back: 1.3B parameters reached 50.6% pass@1 on HumanEval with textbook-quality data. But synthetic text was only about 1B of 7B tokens, the rest filtered web code, and fine-tuning used about 180M tokens of synthetic exercises.
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: How can you train a retriever with almost no labels?
  back: 'Promptagator: 8 labeled examples and an unlabeled corpus, where an LLM writes a query per document, and you train on the pairs. About 50k synthetic pairs matched a comparable amount of human labels.'
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: What are the two biggest levers for code generation?
  back: Context (relevant files, types, tests) and verification (compile, lint, run tests, feed failures back).
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: What is FIM and how do you request it?
  back: 'Fill-in-the-middle: prefix and suffix given, middle generated. Code models use dedicated tokens or a `suffix` parameter, while chat text only approximates it.'
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: How does a model read an image?
  back: Likely as patch vectors of the same size as text-token embeddings, with positional information, in the same transformer, so include only relevant images and introduce each in the text. Vendors don't publish specifics.
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: What would you change about plain chat for editing a long document?
  back: Separate the object from the conversation, edit by diff rather than regeneration, support several named objects, and feed the user's direct edits into the next prompt.
  lesson: ai-engineering/01-prompt-engineering/notes/11-applications
- front: What's the lesson of the extraction prompt?
  back: Define the output format and the empty case. Without `["NA"]`, the model makes up an answer.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
- front: Where does the instruction go in a summarize prompt?
  back: Content first, instruction last, so "Explain the above in one sentence:" also cues the answer. Change the audience or form in that line.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
- front: Why do made-up labels fail?
  back: The model's prior wins, so `nutral` comes back `Neutral`. Define unusual labels explicitly and show them in examples.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
- front: How do you stop a closed-domain rewrite from adding facts?
  back: You can't fully do so with the word "exclusively". Add a second call that verifies each claim against the facts, which is a two-step chain.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
- front: A colleague pastes a GPT-3.5-era decompose-the-steps prompt into a reasoning model. What do you say?
  back: Keep the shape, but drop the step scaffolding and state the goal. Strong current models rarely need it, and it can hurt.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
- front: Why are these prompts still worth keeping if they're dated?
  back: The shape of each transfers even though the wording is from the GPT-3.5 and GPT-4 era. Each entry teaches one move, such as format, empty case or cue.
  lesson: ai-engineering/01-prompt-engineering/notes/prompt-library
---
