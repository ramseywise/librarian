---
title: Reflexion
tags: [prompting, llm, concept]
summary: Verbal reinforcement learning — an actor attempts, an evaluator scores, a self-reflection step turns the score into natural-language feedback kept in memory for the retry; it works only when you get a do-over and an objective evaluator, and reinforces confident mistakes with a weak one.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--06-chaining-and-workflows.md
  - data/raw/papers/2026-11-06-lakshmanan-hapke-genai-design-patterns-ch06-improving-reliability.md
  - data/raw/papers/2026-11-06-yao-2026-parammem.md
  - data/raw/papers/2026-11-07-shinn-2023-reflexion.md
  - data/raw/papers/2026-11-08-building-applications-with-ai-agents-ch07-learning-agentic-systems.md
---

# Reflexion

Shinn et al. (2023). Three components:

| Component | Role |
|---|---|
| **Actor** | Produces actions/text (CoT or ReAct) |
| **Evaluator** | Scores the trajectory — exact match, heuristics, unit tests, or an LLM judge |
| **Self-reflection** | Converts the score into natural-language feedback stored in memory for the next attempt |

Loop: attempt → evaluate → reflect → retry with the reflection in context. HumanEval
pass@1 reached 91% vs. GPT-4's 80% at the time.

Reflexion (Shinn, Cassano, Berman and colleagues, 2023 preprint) asks whether a language agent can improve through repeated attempts, with no change to its weights, by turning task feedback into written self-reflections held in an episodic memory. The authors' hypothesis is that such a reflection acts as a semantic gradient that improves the agent over successive trials. The paper frames the policy as the agent's memory encoding paired with the LLM parameters.

## Mechanism and results in the 2023 paper

Three LLM roles loop over trials:

1. **Actor** generates a trajectory.
2. **Evaluator** scores it using exact match, a heuristic, an LLM classifier, or unit tests the model wrote itself.
3. **Self-Reflection** writes a short verbal lesson that is added to a size-limited memory and handed to the Actor for the next trial.

Memory is a sliding window of 1 to 3 reflections. The Actor is ReAct or chain-of-thought depending on the task. The paper also introduces LeetcodeHardGym: 40 hard Leetcode questions in 19 languages.

## Results (self-reported)

- HumanEval Python with GPT-4 and self-generated unit tests: 91% pass@1 against 80% for GPT-4 alone.
- ALFWorld, ReAct actor with heuristic self-evaluation over 12 trials: 130 of 134 tasks solved. The ReAct-only agent plateaued with a 22% hallucination rate.
- HotPotQA, 100 questions, chain-of-thought with ground-truth context, retrying until 3 consecutive failures: +14% absolute. Self-reflection beat an episodic-memory-only ablation (most recent trajectory only) by 8% absolute.
- HumanEval Rust, hardest 50, GPT-4: 68.0 against 60.0 baseline; omitting test generation gave 52% and omitting self-reflection 60%, equal to the baseline. MBPP Rust 75.4 against 70.9.
- MBPP Python was worse than GPT-4 alone (77.1 against 80.1). The paper attributes this to false-positive self-generated tests: 16.3% on MBPP Python against 1.4% on HumanEval Python.
- LeetcodeHardGym Python pass@1 15.0 against 7.5 for GPT-4.
- No gain for starchat-beta on HumanEval Python (0.26 both, average over 8 trials); the authors describe self-correction as emergent in stronger models.

## Reflexion in a practitioner chapter

The seventh chapter of the book Building Applications with AI Agents, on learning in agentic systems, presents Reflexion as a nonparametric method to try before fine-tuning, alongside saved exemplars and ExpeL-style insight lists. In its code, the reflection prompt receives just the three latest reflections, which keeps context bounded. It says Reflexion helps from code debugging to multistep reasoning, but gives no numbers and cites no experiment for that.

## When it works

- **Only when you get a do-over** — useless for irreversible actions.
- **Ideally with an objective evaluator** (tests, compilers, checkers). With a weak
  evaluator it reinforces confident mistakes — the failure [[Verification Loops]]
  addresses by keeping the evaluator separate from the generator.
- Memory is a sliding window, so long retry histories get truncated.

## At the workflow level

Inside a [[Prompt Chaining]] workflow, task-level Reflexion means: check the output with a
validator, tests or a judge; on failure, re-prompt with the requirements, the failed
attempt and the critique. It is much more expensive than tightening the prompt — try that
first. It is the *evaluator–optimizer* pattern in Anthropic's taxonomy
(Agentic Workflow Patterns). For code, compile/lint/test-and-feed-back is the second
biggest lever after context ([[Code Generation Prompting]]).

## One retry in practice (Lakshmanan and Hapke)

The reliability chapter describes the generate, critique, regenerate loop and notes that exactly one retry is common because it avoids defining what good enough means. In their single run, a weighted rubric scored the real Pydantic logo and a generated sushi-restaurant logo at 0.9 each (self-reported), which the authors say makes it hard to separate good enough from great, which is why they used one fixed round of critique with a different model as critic to limit self-bias. They warn reflection adds calls and tail latency when API availability is poor (a 2025 statement), and, in the authors' view, that code generation, with a compiler or sandbox as the evaluator, justifies multiple stages.

## ParamMem

Yao et al. (2026) find that the diversity of an agent's reflections correlates with task success (average Pearson r 0.76 across datasets, but 0.22 on MBPP) and train a small LoRA module on synthetic data to generate reflections from patterns learned across samples instead of retrieving them. On HumanEval with Llama-3.1-8B it scored 82.93 against 76.22 for Reflexion (self-reported). Limits: no variance reported, small test sets, a token cost 10 to 24 times higher, and on MATH Retroformer scored better than the ParamMem variant.

## Limits

- Depends on the LLM's own evaluation or heuristics, with no guarantee of success; it can get stuck in local minima, and WebShop showed no improvement after 4 trials.
- Memory is only a sliding window; vector or SQL memory is left to future work.
- Self-written unit tests are unreliable for functions that are non-deterministic, impure, hardware-dependent or concurrent.
- The models are 2023 API versions of GPT-3, 3.5 and 4, and most results come with no seeds, variance or compute cost.
- The chapter's Reflexion claim has no experiment or citation behind it; it is a claim, not a result.
- Generated code runs without validation, so the authors advise isolated environments.

## See Also
- [[Verification Loops]] — extends
- [[Prompting Technique Selection]] — instance-of
- [[Loop Detection and the Two-Retry Rule]] — extends (bounding the retry budget)
- [[MetaCrit Adaptive Critique]] — related (a critique pipeline whose paper found unconditional critique lowered accuracy)
- [[RISE Recursive Introspection]] — related (trains multi-turn self-correction into the weights instead of prompting for it)
- [[Self-Consistency]] — alternative-to (at equal token cost, sampling more beat reflection in a small-model study)
- [[Learned Skill and Action Libraries]] — related
- [[DECKARD LLM-Hypothesized World Model]] — related (learning from experience)
- [[Self-Refine]] — alternative-to (feedback without episode memory)
- [[ExpeL Experiential Learning]] — extends
- [[ReST Meets ReAct Agent Self-Improvement]] — related
- [[ReAct Synergizing Reasoning and Acting]] — related
- [[DERA Dialog-Enabled Resolving Agents]] — related
- [[Buffer of Thoughts]] — related (reusable templates across tasks)
- [[Chain-of-Thought Prompting]] — prerequisite-for
- [[SkillRL Hierarchical Skill Bank]] — alternative-to (distilled skills trained into a policy, with Reflexion as a baseline)
