---
title: Prompts as Document Completion
tags: [prompting, llm, concept]
summary: An LLM is a document-completion engine, so a prompt is the opening of a document whose most plausible continuation is the answer — five properties (tokens, autoregression, left-to-right attention, truth bias, chat-as-transcript) explain nearly every prompting rule.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--01-how-models-read-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--prompt-library.md
---

# Prompts as Document Completion

The mechanism page under [[Prompt Engineering]]. The thesis (Berryman & Ziegler,
*Prompt Engineering for LLMs*): **the model is a mimic, not an oracle.** Don't ask "how
would a reasonable person reply?" — ask "if a random training document began with exactly
this text, how would it continue?" Chat, tool calls and agents are all the application
constructing text before the call and parsing text after it; there is no separate
"answering" or "tool-using" mechanism inside the model.

A base model given `What is a good dish for chicken?` may well continue with
`What is a good dish for beef?` — a list of questions is a plausible document.

**Know the training mix.** Completions follow the genres the model saw most. A model
pretrained on A and fine-tuned on B should be prompted as if trained on B (early code
models were general models fine-tuned on code, so you prompt them with code). Because
memorization is treated as a defect, a model that "solves" a famous problem may still
fail a novel variant of it.

Why this became a discipline: GPT-3 showed that a handful of examples *in the prompt*
reproduces almost any task with no weight update — task behaviour became something you
elicit by changing the input.

## The Five Properties

| # | Property | Consequence | Rule |
|---|---|---|---|
| 1 | **Tokens, not characters** (~4 chars/token) | Letter counting, reversal, ROT13 are hard; `ghost` is 1 token, `gohst` 3; SHOUTING, emoji and random IDs cost more tokens | Do sub-token work in code; measure with a real tokenizer |
| 2 | **Autoregressive** — one pass per token, no lookahead, no takebacks | Fixed compute per token; early errors compound; repetition traps | Buy compute with more tokens ([[Chain of Thought]]); put error detection in the surrounding system |
| 3 | **Left-to-right attention** | Later text can't change how earlier text was read | State the task *before* content when it changes how content must be read |
| 4 | **Truth bias** | Hallucination is the same behaviour as fluency; a false premise is run with, not questioned | Ask for checkable output; ground and quote; never feed it nonsense |
| 5 | **Chat = completion of a transcript** | Roles are document structure, not a security boundary (except reserved role tokens) | Never paste untrusted text into `system` ([[Prompt Injection]]) |

### Autoregression details

- **No internal monologue.** In the book's "minibrain per position" model, insights flow
  up the layers and left-to-right only. The single channel back down is an emitted token,
  so **writing a thought out is the only way the model can reuse it** — chain-of-thought
  is a mechanism, not a style.
- **Rarely self-corrects**, because published documents rarely contain visible
  corrections.
- **Repetition traps**: continuing a pattern is the likeliest next token, so lists
  degenerate into loops. Mitigate with stop sequences, penalties or higher temperature
  ([[Sampling Parameters]], [[Stop Sequences and Completion Anatomy]]).
- **Reading is ~10x cheaper than writing**: prompt tokens process in parallel, completion
  tokens one pass each. Favour long inputs and short outputs.

### Order matters — the word-count example

Asked to count words in a 173-word paragraph *after* reading it, a chat model answered 348;
asked *first*, it answered 173 — it wasn't counting while reading because it didn't know
that was the job. The counterweight for long inputs is the introduction-plus-refocus
"sandwich" in [[Long-Context Prompting]].

**One-pass heuristic:** could a domain expert with all the facts complete this prompt in a
single read, without notes or backtracking? If not, restructure (reorder, decompose, or move
computation into code) rather than asking more forcefully.

### Truth bias, used deliberately

"Don't make things up" has limited effect: the model doesn't distinguish knowing from
guessing. Mitigations: ask for *checkable* specifics (names, quotes, sources,
calculations), ground in retrieved text, license "I don't know" explicitly (and show it in
an example — a `?` answer for an unknown entity), and verify in a second step. A prompt
saying "using *exclusively* the information above" still produced invented facts (a BMI,
"signs of malnutrition") in a medical-note rewrite; a generate-then-check step caught them
([[Prompt Chaining]]). Conversely, exploit the bias: assert a hypothetical as fact rather
than asking the model to pretend.

Priors also override made-up labels: ask for the label `nutral` and the model writes
`Neutral`. Define unusual labels explicitly and show them in examples.

## Chat Models Are Completion Models Wearing a Transcript

Alignment targets *helpful, honest, harmless* via the RLHF recipe (SFT → reward model →
PPO constrained near the SFT policy; see [[RLHF Pipeline]]). Honesty needs the RL stage:
labellers writing ideal answers can't see what the model knows, so SFT alone teaches it to
fabricate or to hedge everything. Cost: the **alignment tax** on some tasks.

**ChatML** makes turn-taking explicit with reserved tokens (`<|im_start|>role … <|im_end|>`).
Typed literally by a user, those strings tokenize as ordinary pieces, so users are locked
into the `user` role — unless you paste their content into `system`. Other templates
differ: Mistral's `[INST]` markers are *ordinary strings* a user can type. Calling an
open-weight model as raw completion means reproducing its chat template yourself
(`apply_chat_template`).

What chat costs vs. raw completion: the alignment tax, **output control** (preamble and
disclaimers — a completion prompt ending in a code fence with a fence stop returns only
code), and **range** (RLHF narrows voice, bad for realistic synthetic data —
[[Diversity Seeding for Synthetic Data]]).

**Two scripts.** The user's conversation and the transcript you send are different
documents: yours can hold synthetic turns, retrieved context and tool results the user
never sees. Synthetic `assistant` turns are treated as things the model said.

## The Four Levels of Prompt Engineering

| Level | Application does |
|---|---|
| 1. Thin wrapper | Passes user text through with light formatting |
| 2. Augmented input | Adds retrieved context; rebuilds and trims history each turn ([[Context Engineering]]) |
| 3. Tool use | Model requests actions, app executes ([[Tool Definitions as Prompts]]) |
| 4. Agency | Model decides how to reach a goal — still fails often unless tightly scoped |

## See Also
- [[Prompt Engineering]] — prerequisite-for
- [[Four Prompt Criteria]] — prerequisite-for
- [[Chain of Thought]] — prerequisite-for (CoT works because tokens are the only feedback channel)
- [[Long-Context Prompting]] — prerequisite-for
- [[Prompt Injection]] — prerequisite-for (roles are structure, not a boundary)
- [[RLHF Pipeline]] — extends
- [[Why Context Is Finite]] — extends
- [[Prompt Assembly as Snippet Packing]] — prerequisite-for
