---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/01-prompt-engineering/slides/deck.yaml
cards:
- front: Why can nothing later in a prompt change how earlier text was read?
  back: Attention flows one way, so a model reasons further only by writing tokens, which is why chain-of-thought works.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What happened when the word-count instruction moved in front of the paragraph, and what test does it suggest?
  back: When a task changes how content must be read, put the instruction first and restructure rather than insisting.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: Besides left-to-right attention, what four properties of LLMs explain most prompting rules?
  back: Tokenization, no backtracking, truth bias and the chat transcript explain why reordering beats asking harder.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What does a chat request become before the model sees it, and why must user content stay out of the system role?
  back: The API renders messages into one transcript, so roles shape behaviour but only reserved tokens separate speakers.
  lesson: ai-engineering/01-prompt-engineering/notes/01-how-models-read-prompts
- front: What four criteria must every prompt meet, and which one is never automatic?
  back: Chat fine-tuning gives you criteria one, three and four almost free, but carrying the right information never comes free.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
- front: What is the Valley of Meh, and how does the sandwich structure respond to it?
  back: Content in the early middle of a prompt is used least, so state the task early and refocus on it at the end.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: In Li's Tau-Bench ablation, which change to an agent's system prompt hurt most, and which barely mattered?
  back: Write agent prompts as numbered procedures with exception branches, and ablate one component at a time before rewriting.
  lesson: ai-engineering/01-prompt-engineering/notes/02b-document-types-formatting-and-templates
- front: According to Min et al., what do few-shot examples actually teach, and what are their three drawbacks?
  back: Few-shot examples mostly teach format and label space, so add them only when zero-shot fails in a way you can name.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: How much did chain-of-thought improve PaLM 540B on GSM8K, and how do you keep the reasoning away from the user?
  back: Chain-of-thought spends output tokens on reasoning, and a parseable block lets the app show only the answer.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: How do Tree of Thoughts and CoT compare on Game of 24, and what does ToT need that CoT does not?
  back: Tree of Thoughts recovers from dead ends through generate, evaluate and backtrack, at the cost of a code controller.
  lesson: ai-engineering/01-prompt-engineering/notes/03b-chain-of-thought-and-reasoning
- front: What does ReAct add to chain-of-thought, what are the ALFWorld results, and how does it fail?
  back: ReAct alternates reasoning with actions so answers rest on retrieved facts, and a single bad search can derail it.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
- front: When does Reflexion work, what result did it achieve on HumanEval, and when does it become dangerous?
  back: Reflexion retries with written feedback, so it needs reversible actions and an evaluator stronger than the actor.
  lesson: ai-engineering/01-prompt-engineering/notes/03-core-techniques
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
- front: What are the main paths for offline prompt evaluation, and how do you source samples?
  back: Start offline with cheap exact checks, escalate to judges only where needed, and watch acceptance online as a guardrail.
  lesson: ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts
- front: What makes a good LLM judge rubric, and why does the rubric go before the content?
  back: Ask judges a specific, ordinal, multi-aspect question, and calibrate their scores against several human annotators.
  lesson: ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts
- front: What does the prompt modification case study show about F1, template adherence and methodology?
  back: Prompt wording can move F1 by 26 points and trade against format adherence, so change one thing and re-score.
  lesson: ai-engineering/01-prompt-engineering/notes/09-evaluating-prompts
- front: What does the prompt optimization loop look like, and what automated tools can propose changes?
  back: Version the template with its model and score, and keep a new version only when it beats the old on the eval.
  lesson: ai-engineering/01-prompt-engineering/notes/08-prompt-optimization
- front: How should a model rank instructions from different sources, and which defenses are strongest?
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
  lesson: ai-engineering/01-prompt-engineering/notes/08-prompt-optimization
- front: Which pillars and readings come after prompt engineering?
  back: Prompting sets what the model is asked; the next pillar decides what else sits in the window with it.
  lesson: ai-engineering/01-prompt-engineering/notes/02-prompt-anatomy
---
