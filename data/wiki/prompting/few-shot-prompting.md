---
title: Few-Shot Prompting
tags: [prompting, llm, concept]
summary: Providing worked examples before the task — the most reliable lever for steering output format, tone and structure without fine-tuning, but examples teach more than intended (distribution, order, range), so use them only for what is genuinely non-obvious.
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt--prompt-engineering.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch05-prompt-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--03-core-techniques.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--10-adversarial-prompting.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
  - data/raw/papers/2026-11-08-song-2023-pre-trained-large-language-models.md
  - data/raw/papers/2026-11-08-dong-2024-survey-context-learning.md
---

# Few-Shot Prompting

## Zero-Shot vs Few-Shot

- **Zero-shot** — instruct with no examples, relying on the model's general knowledge.
  Sufficient for well-known tasks with unambiguous output shape.
- **Few-shot (multishot)** — provide 3–5 worked examples before the actual task.

Examples are one of the most reliable ways to steer output format, tone, and structure.
Where a paragraph of instructions describing the desired format often underspecifies,
three examples of it pin it down exactly.

## Three Properties of Good Examples

| Property | Requirement | Failure if violated |
|---|---|---|
| **Relevant** | Mirror the actual use case | Model generalises from the wrong domain |
| **Diverse** | Cover edge cases; vary enough | Model latches onto an unintended pattern shared by all examples |
| **Structured** | Wrap in `<example>` tags | Model confuses examples with instructions |

The diversity requirement is the one most often missed. If every example happens to have a
short answer, the model will infer "short answers" as a rule you never stated.

## Structuring

Wrap examples in tags so the model distinguishes demonstration from instruction — see
[[XML Prompt Structuring]]:

```xml
<examples>
<example>
  <input>...</input>
  <output>...</output>
</example>
</examples>
```

## What Examples Actually Teach

In-context learning emerges with scale — small models barely benefit. Examples teach far
more than the rule you had in mind: a handful of `(title): (rating)` pairs implicitly
teach that ratings are integers 1–5, the exact line format, and the *distribution* of
ratings. That makes few-shot good for "I know it when I see it" categories and a cheap way
to pin down format.

What matters in the examples (Min et al., 2022):

- **Label space and input distribution** matter more than per-example label correctness —
  random labels still beat no examples.
- **Format** matters a lot; a consistent format with random labels still helps.
- Sampling labels from the true distribution beats a uniform spread.

## Three Drawbacks (Berryman & Ziegler)

Use few-shot only when something is genuinely non-obvious:

| Drawback | What happens | Mitigation |
|---|---|---|
| Scales badly with context | Each example must carry the real question's context; the prompt balloons and similar blocks confuse attention | Scope examples to teaching format only |
| Anchoring | The examples' range becomes the model's expectation | Match the true outcome distribution; include edge cases without overweighting them |
| Spurious patterns | Example *order* is learned instead of content | Shuffle; evaluate subsets and orders; let [[DSPy]] select and order against a metric |

Three examples land in accidentally ascending order one time in six. "Happy path first,
edge cases last" is the classic trap: the model learns the sequence, so a real question
that breaks it is predicted from position, not content. Shortening examples to dodge the
context cost can also nudge the model away from deeper reasoning.

**Bias from the prompt itself:** skewed label distributions (8 negative, 2 positive) tip
ambiguous inputs toward the majority label; strong models resist on clear inputs. Grouping
labels by position teaches a positional pattern. Synthetic examples inherit whatever skew
their seeds had ([[Diversity Seeding for Synthetic Data]]).

**Placement in agent prompts:** 2–3 boundary-covering examples in the system prompt or as
synthetic first-turn messages, kept **byte-stable** — per-request "most relevant" examples
break the prefix cache ([[SOP-Style Agent System Prompts]]).

Structure-oriented meta-prompting — an abstract solution template instead of worked
examples — avoids anchoring at lower token cost ([[Prompt Optimization]]).

## Combining with Reasoning

Few-shot composes with [[Chain of Thought]]: examples that show the *reasoning chain*, not
just the input/output pair, teach both the format and the method. This is few-shot CoT, and
on genuinely multi-step reasoning tasks it outperforms either technique alone.

The gain does not carry over to single-label classification. In Clavié et al. (2023),
zero-shot CoT (F1 81.4) beat few-shot CoT (F1 78.4) on a job-posting classification task
needing no expert knowledge — the examples anchored the model ([[Evaluating Prompts]]).
Default to zero-shot CoT, and add worked reasoning examples only when the task has real
intermediate steps and an eval shows they help.

## Reported limited gains

Huyen (AI Engineering, ch. 5) relays a 2023 Microsoft analysis in which examples added little over zero-shot for GPT-4-class models. The chapter adds that domain tasks, such as the Ibis dataframe API, may still benefit, so the study could understate that use. The chapter runs no experiment and gives no figures. A compact example format also cost fewer tokens than Input/Output blocks on a three-item labelling prompt with the GPT-4 tokenizer. For a variant that adds a wrong rationale to each example, see [[Contrastive Chain of Thought]].

## Demonstration selection for GPT-4 control (Song et al.)

Song et al. (2023 technical report) prompt GPT-4 as an HVAC controller in the BEAR simulator, with historical (H), representative (R) and expert (E) demonstrations written as H/R/E plus a count. Setup: one target scenario (OfficeMedium/CoolDry), 240 steps, five seeds, reward compared with a PPO controller (1.21); all numbers self-reported.

- With no demonstrations GPT-4 scores 1.01; two expert demonstrations alone score lower than none; eight randomly sampled demonstrations are far worse than selected ones.
- Using only its own four historical demonstrations gave the best GPT result, above PPO. Counting only historical demonstrations, two score 1.15, four score 1.23 and eight score 1.21.
- Manual feedback comments on demonstrations raised reward from 0.99 to 1.16, while self-generated comments dropped it to 0.59. Writing real numbers in the prompt as rounded integers raised it from 1.07 to 1.16.
- Adding instructions to a task description lowered reward from 1.12 to 1.07. Under noise added to the outside temperature, GPT-4 moved from 1.16 to 1.15 and PPO fell from 1.21 to 1.07.

Limits: a single target scenario; the "fewer samples" claim is not measured, since the expert demonstrations come from PPO trained for 100M steps; many differences are within one standard deviation; no significance test; GPT-4 version and decoding settings not stated.

## Survey evidence on in-context learning (Dong et al., EMNLP 2024)

A survey of in-context learning (ICL) defines it as a paradigm where language models learn a task from a few demonstration examples with no parameter update. It treats ICL as a subclass of prompt tuning where demonstrations are part of the prompt. Scoring functions come in three forms: Direct, P(y|C,x); PPL, the perplexity of the whole sequence with the candidate label; and Channel, the probability of the input given the label.

The authors ran a small experiment of their own: 8 demonstrations per prompt and perplexity-based inference, run on four models (the older GPT-2 and GPT-J, plus Qwen2-7B-Instruct and Llama3-8B-Instruct) over five classification sets (SST2, SST5, CommonsenseQA, AG News, SNLI) with 1000 test items for each.

- Demonstration selection depends on the model: mdl won on GPT-2, while top-k nearest-neighbour selection won on the other three (self-reported; 8 demonstrations, 1000 test items per dataset).
- Latency with 8 in-context examples: PPL scoring runs about 2.61x the cost of Direct scoring and Channel about 2.90x, averaged over the four models (self-reported).
- Over 5 random seeds, each drawing 8 examples from 5k training items, Channel scoring varied most from one demonstration set to the next and PPL varied least (self-reported).

Findings the survey reports from other work: adding demonstrations does not always help and can hurt in many-shot long-context use; warmup gains plateau as training data grows; whether the input-label mapping matters is disputed (Min et al. saw little effect; later work found correct mappings matter a lot); results are sensitive to order across models, and k demonstrations can be arranged in k! ways; current ICL methods do badly at planning and at reasoning about actions and change.

Its practice list: optionally warm up with instruction tuning before inference; start from nearest-neighbour selection (kNN, KATE) and try supervised retrievers (EPR) to beat it; check selection on the target model; put the most similar example last or sort from simple to complex; choose Direct scoring when efficiency matters, PPL when stability and coverage do, and Channel when classes are imbalanced.

Limits of this section:

- The survey's authors admit omissions, and many of the papers it covers used older models; theory work mostly addresses simple tasks and small models.
- The authors' own experiment is small (8 demonstrations, four models of at most 8B, five classification datasets) and excludes agent, planning and tool-use settings. The caption of Table 5 says the test set has 10k items, while Appendix B gives 1000 items for some datasets, an internal conflict.
- Distilling demonstrations to fix efficiency needs parameter access, which closed models do not give.

## See Also
- [[Prompt Engineering]] — related (part of)
- [[XML Prompt Structuring]] — prerequisite-for
- [[Chain of Thought]] — related (composes with)
- [[DSPy]] — extends (automated example selection and ordering)
- [[Prompting Technique Selection]] — extends
- [[Evaluating Prompts]] — contradicts (zero-shot CoT beat few-shot CoT)
- [[LongICLBench and Many-Shot ICL Scaling]] — extends
- [[Mixtures of In-Context Learners]] — extends
- [[Implicit Weight-Patch Theory of In-Context Learning]] — related
- [[Rephrase and Respond]] — related (combined with few-shot in the paper's tests)
- [[Medprompt]] — instance-of (kNN-selected few-shot examples)
- [[Contrastive Chain of Thought]] — extends
- [[Chain-of-Thought Prompting]] — extends
- [[Symbol Tuning]] — extends
- [[Flipped-Label In-Context Learning]] — extends
- [[Prompt Order Sensitivity and Entropy Probing]] — extends (order of the same examples)
- [[LM-BFF and PET Prompt-Based Fine-Tuning]] — related
- [[LLM-R Learned In-Context Example Retriever]] — extends (learned example selection)
- [[LLM Prompting for Mobile UI Screens]] — instance-of
- [[Analogical Prompting]] — extends
- [[Context-Faithful Prompting]] — related
- [[RAG+ Application-Aware Retrieval]] — related
- [[HiAR-ICL Thought Cards]] — extends
