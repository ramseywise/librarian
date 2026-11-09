---
title: Prompting Reasoning Models
tags: [prompting, llm, pattern]
summary: Reasoning models do chain-of-thought natively, so prompts shift from how to think to what to achieve — state goals and constraints, drop manual CoT (it can degrade instruction-following), escalate effort gradually against an eval, and never treat the visible thinking as a faithful audit trail.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--07-prompting-reasoning-models.md
  - data/raw/papers/2026-11-06-wu-2024-comparative-study-reasoning-patterns-openai.md
  - data/raw/papers/2026-11-06-xiang-2025-towards-system-2-reasoning-llms.md
  - data/raw/papers/2026-11-07-kargupta-2025-cognitive-foundations-reasoning-their-manifestation.md
  - data/raw/papers/2026-11-07-parmar-2025-challenges-ensuring-ai-safety-deepseek.md
  - data/raw/papers/2026-11-07-shakarian-2023-independent-evaluation-chatgpt-mathematical-word.md
  - data/raw/papers/2026-11-07-sivakumaran-2026-balancing-faithfulness-performance-reasoning-multi.md
  - data/raw/papers/2026-11-07-wang-2025-thoughts-all-over-place.md
  - data/raw/papers/2026-11-07-weinberger-2026-prompt-induced-waste-coding-agents.md
---

# Prompting Reasoning Models

Reasoning models spend **test-time compute** on hidden or summarized thinking tokens
before answering. More thinking usually means better answers on hard tasks, at more
latency and cost — controlled by an **effort or budget** setting, not by prompt wording.
The [[Chain of Thought]] scaffolding written for standard models is redundant at best:
explicit step-by-step prompting has been shown to *degrade instruction-following* in
reasoning models (*The Pitfalls of Reasoning for Instruction Following*, 2025). Model
behaviour here moves fast; treat specifics as dated.

## Do / don't

| Do | Don't |
|---|---|
| State goal, constraints and output format at a high level | Prescribe the reasoning steps |
| General nudges for more effort ("consider several approaches") | Bolt on "Let's think step by step" |
| Delimit inputs; specify the format explicitly | Leave format to chance — formatting drift is common |
| Few-shot **only** for style/format the model gets wrong | Pad with examples by default |
| Ask it to verify its work before finishing | Trust reasoning because it was long |
| Explicit quality modifiers when you want ambition | Expect "above and beyond" unasked |

With extended thinking, high-level instructions beat prescriptive ones — read the thinking,
then steer. Few-shot examples may include thinking blocks to show reasoning *style*. In
agent loops, interleaved thinking between tool calls lets the model reflect on each result.

## Escalate gradually (hybrid models)

1. Thinking off; evaluate. A manual CoT prompt is a cheap middle step.
2. If failures look like reasoning failures, enable thinking at low effort.
3. Escalate to medium, then high, **only while eval scores keep improving** ([[Evaluating Prompts]]).
4. Use examples to fix style and format, not reasoning.

Optimize accuracy first, then latency and cost.

## Where they earn their cost

Put the reasoning model in the reasoning-heavy *module*, not the whole app: planners in
orchestrator–worker agents, agentic RAG routing, judges that must reason, large codebases
and scientific work, and writing prompts for other models ([[Prompt Optimization]]).
Simple extraction, classification and rewriting rarely need one.

## Failure modes

| Issue | Mitigation |
|---|---|
| Overthinking easy tasks, underthinking hard ones | Be specific; route only hard subtasks; tune effort |
| Mixed languages, repetition, format drift | Unambiguous instructions, explicit format, post-validation |
| Instruction-following degrades with explicit CoT | Drop manual CoT; curated examples; self-reflection |
| **Unfaithful reasoning** — visible CoT need not reflect what drove the answer (*Reasoning Models Don't Always Say What They Think*, 2025) | Don't use thinking text as an audit trail or sole safety monitor; evaluate outputs |
| Weaker tool calling in some open models | Test parallel and multi-step tool use explicitly |
| Sampling parameters fixed or rejected | Control with effort ([[Sampling Parameters]]) |

## Prompting deep-research agents

Runs are slow and expensive, so get the prompt right first time: give a plan and be
specific about scope, period and trusted sources; **answer its clarifying questions
thoroughly** (the cheapest steering point); supply precise keywords (they become search
queries); use clear task verbs (*compare*, *recommend*, *report*); specify the report
format; upload documents you already have; and verify the sources — citation errors,
domain bias, date sensitivity and paywalls are known weaknesses. Use deep research only
for multi-source, time-sensitive synthesis.

## What doesn't change

Still document completion; not psychic (smarter models don't fill missing context); easily
distracted, and more so when reasoning over everything; the rendered prompt must be
decipherable by a human; it must be led — on goals now rather than steps. Public
benchmark scores saturate and leak into training data, so they don't predict your task:
build your own eval.

## Paper evidence

Each item gives its setup; figures are (self-reported) by the paper unless noted.

- **Guidance prompts (cognitive-foundations study).** A prompt steering the reasoning approach changed accuracy by an average of +2.0% across 14 models, up to +66.7%. Capable models gain; DeepScaleR-1.5B averages -52.6% and Hermes-3-8B -17.5%. Design problems are excluded after 0% accuracy. In 192,709 traces, successful runs scope the problem first, where a common failure rushes to forward chaining (0.748).
- **R1 safety position paper.** It asserts that few-shot prompting degrades R1 and recommends zero-shot or structured prompts, and that R1 is unsuitable for agentic use. It reports no numbers, so these are asserted and unmeasured. See [[Few-Shot Prompting]] for the general guidance on examples.
- **o1 patterns.** Overall scores on four filtered benchmarks (HotpotQA 274 items, Collie 226, USACO bronze 139, AIME 90): the agent workflow got 24.70 and GPT-4o 18.44, against o1-preview at 34.32 and o1-mini at 35.77. o1-mini beats o1-preview on AIME (62 vs 44) and Collie (53.53 vs 34.07) and loses on USACO (12.23 vs 44.60). Best-of-N, step-wise best-of-N and Self-Refine hurt on Collie. Six reasoning patterns were counted by hand on 20 to 30 samples per benchmark.
- **Underthinking.** A persistence prompt barely changes R1's thought switching (13.8 to 12.0 switch tokens), while a decoding penalty on switch tokens (alpha=3 for 600 positions, tuned on QwQ) gives 74.8 accuracy with 5.7 switch tokens; it needs logit access. Over 70% of incorrect responses hold an unfinished correct thought, and the judge agrees with labels about 82% of the time. GPQA moves 57.6 to 59.1.
- **Faithfulness training.** REMuL rewards a model when listener models, reading 25/50/75% prefixes of its chain of thought, reach its answer. On Qwen3-14B and Phi-4-reasoning-plus (1250 BBH pairs, out-of-domain tests) it gives +2.5% faithfulness with +1.8% and +1.5% accuracy. Faithfulness-only training costs accuracy; sycophancy rises 38.6 to 41.8.
- **Meta-CoT position paper.** A MATH-test prompting study over five strategies and eight models found regret under 0.5% for baseline and CoT; the highest value, 25.67%, was Llama 3.1 70B with Think and Verify. Prompt overhead was 23, 35, 1,895, 4,659 and 2,111 tokens across strategies. It cites one search tree costing up to 20M tokens, about $100.
- **ChatGPT on word problems (2023).** On DRAW-1K, 84% failure when asked for no work against 20% when work is shown, with 51% fully correct versus 59% reported for a specialised system.

- **Prompt-induced waste in coding agents.** A preregistered benchmark of prompt components on coding agents is summarised on [[Prompt-Induced Waste in Coding Agents]]; the instruction-length and token-cost findings sit there.

## Limits

- The o1-pattern study filters its datasets to items other LLMs fail, runs once, mixes models, and the extraction notes weak relevance to prompting. Its text says step-wise best-of-N is under 12% on Collie while Table 1 lists 19.55 for N=4, and the text is inconsistent on which patterns are most common.
- The cognitive-foundations extraction has internal inconsistencies: Qwen3-7B versus R1-Distill-Qwen-7B for the +66.7 figure, 170K versus 192K traces, 78.8 versus 79.5 on one story figure, Olmo presence 48.4% versus 0.491, a -72.0 versus -56.0 for DeepScaleR, and 8% versus 16% for self-awareness.
- The Meta-CoT pipeline is proposed and not run; its regret metric is phrase matching.
- The word-problem study confounds prompt and show-work, uses different access tiers, and runs once.
- The faithfulness study is 14B only, with small gains, no seeds and keyword-detected hints.

## See Also
- [[Chain of Thought]] — supersedes (for reasoning-model endpoints, manual CoT is replaced by effort settings)
- [[Sampling Parameters]] — extends
- [[Evaluating Prompts]] — prerequisite-for
- [[Prompts as Document Completion]] — extends
- [[REST Multi-Problem Stress Testing]] — related (reasoning models under several questions in one prompt)
- [[Embers of Autoregression]] — related (o1-preview tested for next-word-prediction effects)
- [[Knowledge Index and Information Gain]] — related (step-level scores for distilled and RL-trained reasoners)
- [[Reflection in Pre-Training]] — related (reflection appears in base models before post-training)
- [[Overthinking and Concise Reasoning]] — related (token savings from shorter reasoning)
- [[Inverse Scaling in Test-Time Compute]] — related (tasks where more budget lowers accuracy)
- [[LLM Reasoning Surveys and the Can-LLMs-Reason Debate]] — related
- [[MAKER Million-Step Decomposition]] — related (small non-reasoning models for single steps)
- [[MVoT Multimodal Visualization of Thought]] — related
- [[Prompt-Induced Waste in Coding Agents]] — instance-of (coding-agent prompt waste benchmark)
