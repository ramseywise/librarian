---
title: Real-Time Multimodal Agents
tags: [foundations, voice, concept]
summary: "Voice dialogue, computer use and robot control are the three settings where continuous input and a strict output time budget make multimodality hard — and all three are moving the same way, from serial pipelines toward end-to-end models and a fast/slow division of labour, with irreversible actions needing a gate."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--real-time-multimodal-agents.md
  - data/raw/repos/learn-ai-engineering/generative-ai--07-agentic-applications--README.md
  - data/raw/papers/2026-11-06-fang-2024-llama-omni.md
  - data/raw/papers/2026-11-06-huang-2023-audiogpt.md
  - data/raw/papers/2026-11-06-nachmani-2023-translatotron-3.md
  - data/raw/papers/2026-11-08-shu-2023-llasm.md
---

# Real-Time Multimodal Agents

Static image and document understanding is ordinary agent work, and image or video
*generation* is just a tool call. The hard cases are the ones where input arrives
continuously and output has a time budget: **voice**, **GUI operation** and **robot
control**. Each extends the loop in [[Agent Fundamentals]] under a latency constraint.

## The common thread

| | Serial bottleneck | End-to-end move | Fast/slow split | Still open |
|---|---|---|---|---|
| Voice | VAD → ASR → LLM → TTS | Omni models, then full-duplex | Interaction model + background reasoner | Debuggability of end-to-end models |
| Computer use | Screenshot → think → click | — | Voice model + slow GUI agent | Per-step latency, continuous video |
| Robotics | Plan → act | Vision-language-action models | Planner + VLA with action chunking | Cross-task generalisation, data |

- **Voice** — [[Voice Agent Paradigms]] (cascaded, omnimodal, full-duplex) and
  [[Semantic Turn Detection]], the streaming-perception fix for VAD's silence guess.
- **Thinking under a latency budget** — [[Fast-Slow Thinking Architecture]].
- **Computer use** — [[Computer Use Visual Grounding]].
- **Robotics** — [[Action Chunking]] and VLA action representations.

## Speech synthesis: imperfection on purpose

Perfectly fluent TTS sounds machine-made, because human pauses and fillers signal thinking
and uncertainty. The proposal is to **let the LLM decide prosody** by emitting control
tokens (a thinking pause with a filler, a searching cue, emotion, speed, a sigh or a small
laugh). Only the LLM knows whether it is mid-hard-problem or whether the user is impatient.
TTS becomes a generator that takes text plus control tokens. Two ways to build it: a
proprietary TTS with native control tokens (flexible, needs a dedicated team), or voice
cloning with a **reference library** — two dozen short clips covering emotion × speed ×
style, chosen by the control tokens so timbre stays consistent. Against no control tokens
(robotic) and a single reference clip (monotone), the multi-clip library came close to a
human agent.

## Observing an end-to-end voice model

Log the input audio, the event tokens and any inner-monologue or text stream, and replay
through a self-cascade (the same model transcribing first) to localise an error to
perception or to reasoning.

## Irreversible actions need a gate

Every fast/slow design lets the fast path act before the slow path checks — speak then
correct, click then look, step then look. Whatever is irreversible has to be gated
outside the model ([[Execution Boundaries and Guardrails]]).

## Speech systems from four papers

Numbers are the authors' own (self-reported); setups differ.

- **LLaMA-Omni** (arXiv 2409.06666, ICLR 2025): a frozen Whisper-large-v3 encoder, a 5x-downsampling adaptor, Llama-3.1-8B-Instruct, and a 2-layer, 425M non-autoregressive speech decoder trained with CTC to produce HuBERT units (1000 clusters) vocoded by a unit HiFi-GAN. Streaming flushes a chunk once at least Omega new units exist. Minimum latency is 236.18 ms (Omega=10, one L40 GPU) against a quoted 320 ms average for GPT-4o audio. Training took about 65 hours on 4 L40 GPUs with 200K samples. In Table 2 its speech-to-text instruction score of 3.99 is the highest listed, while its ASR-WER of 10.82 is worse than the cascades' 3.78 and 6.77 (self-reported).
- **AudioGPT** (arXiv 2304.12995, AAAI 2024): ChatGPT (gpt-3.5-turbo) acts as a controller over 15 tasks mapped to existing audio models through a four-step flow that moves from modality conversion to task analysis, then model assignment and a final reply. It reports no quantitative results; the proposed consistency, capability and robustness protocols are never run, and evidence is demonstrations such as a 12-round dialogue. The authors list prompt engineering, token length and dependence on the audio models as limits.
- **Translatotron 3** (arXiv 2305.17547, ICASSP 2024): unsupervised speech-to-speech translation (Spanish and English) from monolingual data, using one shared encoder with two decoders, a masked autoencoder using SpecAugment, back-translation, and embeddings aligned with MUSE. The paper claims the first fully unsupervised direct model on real speech. Table 2 BLEU on the Unpaired-Conversational set (synthesized): 18.85 against 5.58 and 24.27 against 6.13; on real speech Es to En it is about 0.75 above a 9.92 cascade.
- **LLaSM** (arXiv 2308.15930): spoken instructions go in without an ASR step. Whisper audio embeddings pass through a modal adaptor into Chinese-LLAMA2-7B. Training has two stages: first only the adaptor is trained on public ASR data, then the adaptor and the LLM are trained together on instructions voiced with TTS. Its released instruction set holds 199k conversations and 508k samples (428k English, 80k Chinese) (self-reported). Output is text only.

## Limits

- LLaMA-Omni: speech quality (UTMOS) falls at small Omega (3.23 against 3.93 offline); evaluation uses 199 synthesized-speech instructions, a GPT-4o judge and a human study of 20 prompts with 5 raters; single turn, English only, no ablations. Inconsistencies noted by the extraction: the text calls the human-evaluation figure "Figure 5" but it is Figure 4; the Qwen2-Audio plus Orca latency of 308.61 ms at Theta=1 exceeds the text's "below 300ms"; word error under streaming (9.84-10.71) is lower than the offline 10.82.
- LLaSM: Section 4 gives only example conversations, with no WER, benchmark or baseline; speech inputs are synthetic and adaptor and training details are not given.
- AudioGPT: the extraction notes the abstract and conclusion claim outperformed abilities with no body evidence.
- Translatotron 3: the cascade baseline is weak, the Unpaired-Conversational dataset is proprietary, and it is offline only. Inconsistencies noted by the extraction: the text gives 10.67 BLEU with a +0.75 gap but Table 2 gives 10.76; the conclusion's 10.51 cascade and 1.95 gap do not reconcile (the extraction computes 1.49); the text says about 30% while the table gives 36-42%; CV11 Es to En CS is 0.56, below the "0.6" in the text; supervised rows are labelled CV11 in Table 2 but CVSS in the text.

## See Also
- [[Agent Fundamentals]] — prerequisite-for (the loop these settings extend)
- [[Voice Agent Paradigms]] — extends (the voice setting)
- [[Fast-Slow Thinking Architecture]] — extends (the shared division of labour)
- [[Computer Use Visual Grounding]] — extends (the GUI setting)
- [[Action Chunking]] — extends (the robotics setting)
- [[Post-Training for Agents]] — extends (voice SFT, robot-policy RL)
- [[Realtime Voice Architecture Reference]] — extends (build-time numbers for a voice agent)
- [[Voice Agent Patterns]] — related
- [[Speech and Audio Generation and Recognition]] — related (the codec, TTS and recognition methods behind these systems)
- [[Vision-Language Model Training Families]] — prerequisite-for (how the vision-language models in these agents are built)
- [[HuBERT Masked Prediction of Hidden Units]] — related
- [[PaLM-E Embodied Multimodal Language Model]] — related
