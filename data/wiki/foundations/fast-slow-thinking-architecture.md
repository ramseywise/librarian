---
title: Fast-Slow Thinking Architecture
tags: [foundations, voice, pattern]
summary: "Three ways to give a real-time agent deep reasoning without blocking it — fast fillers then slow answers, a fast interaction model advised by a background reasoner (the 2026 mainstream), or one model that thinks while speaking — plus the text-vs-latent channel between them and the rule that the fast side never claims 'done' before the slow side confirms."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--05-RL--post-training-for-agents.md
---

# Fast-Slow Thinking Architecture

Users want millisecond responses; hard questions need seconds. Voice, computer use and
robotics all face this ([[Real-Time Multimodal Agents]]). Three solutions coexist:

| | Fast side | Slow side | Failure |
|---|---|---|---|
| **1. Fast fillers, slow answers** | Says "let me think" or a quick answer within ~500 ms | Answers fully after 5–10 s | Two uncoordinated minds: the slow answer repeats or contradicts the fast one |
| **2. Fast interacts, slow advises** | Owns the conversation | Runs in the background, sees the conversation, sends advice through a channel | The fast model can misread advice, cannot see the slow model's intermediate reasoning, and cannot think while speaking |
| **3. Unified** | One model thinks *while* speaking | — | Must be both the best reasoner and a real-time speaker, both moving targets, so it needs repeated retraining |

Solutions 1 and 2 use two independent models and can sit on top of a cascade; only
solution 3 internalises reasoning.

## Why solution 2 is the mainstream

The reason is pragmatic. Frontier reasoners change every few months; interaction skill
needs specialised data. Keep the strongest reasoner intact in the background, train only a
light foreground model, and the "brain" can always be swapped for the newest one. Good
practice from the published designs: hand the background model the **entire conversation
context**, not an isolated query; stream its results back to be woven in when the moment
fits; resolve fast/slow contradictions in favour of the slow model *before* speaking. The
text channel is typically a rolling state line like [[Agent Status Bar]].

## Thinking while speaking (solution 3)

One unified design combines two mechanisms:

- **Modality-grounded reasoning distillation** fixes *textual surrogate reasoning*: audio
  models whose reasoning data came from text models reason about transcripts ("the lyrics
  mention sadness") rather than sound ("minor key, falling pitch"), which is why longer
  chains of thought made them worse. The fix samples several traces, keeps only those that
  cite concrete acoustic features, runs SFT on them, then RL to stop the model skipping the
  thinking, and iterates.
- **Mind-paced speaking**: a formulation side streams reasoning segments and an
  articulation side turns each segment plus the reply so far into speech; first syllable
  around 350 ms. Speaking first costs almost nothing in accuracy (92.8% vs. 93.9% for
  thinking first on a spoken-math benchmark, against 70.6% with no thinking), because the
  start of a chain of thought mostly restates the problem.

A related training-side result: RL can learn **when not to think**, cutting response length
roughly in half without accuracy loss, which pairs with prompt distillation into a
fast/slow system ([[Post-Training for Agents]]).

## Text channel vs. latent channel

Text is easy to debug but narrow. A **latent bridge** freezes both models and trains only a
small projection (tens of millions of parameters) from the slow model's hidden state into a
few latent tokens in the fast model's input, the way vision tokens are inserted. On Atari
it beat the text channel by 26–82% in some games for about 5 ms per step. **The limit**:
fast/slow pays off only when the bottleneck is "cannot think of it", not "cannot react in
time", and the gain tracks how much better the slow model is (r ≈ 0.9).

## Talking while acting

The same split applies to [[Computer Use Visual Grounding|computer use]]: a fast voice model
talks to the user while a slow vision-language agent operates the browser, sharing a
plain-text status line ("filling the form, still need your date of birth"). Voice responses
became about 15× faster. The rule that makes it safe: **the fast model must never say
"done" until the status confirms it.**

## See Also
- [[Real-Time Multimodal Agents]] — instance-of (the shared division of labour)
- [[Agent Status Bar]] — prerequisite-for (the text channel between fast and slow)
- [[Voice Agent Paradigms]] — extends (adding reasoning to any voice paradigm)
- [[Harness Orchestration]] — instance-of (fast/slow as a two-agent pattern)
- [[Computer Use Visual Grounding]] — extends (talking while acting)
