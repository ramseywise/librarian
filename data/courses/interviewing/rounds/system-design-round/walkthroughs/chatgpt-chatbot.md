---
imported_hash: eee6b3800d81ae0d
title: Design an AI chatbot like ChatGPT (a conversational LLM service at scale)
summary: chatgpt-chatbot-walkthrough · chatbot · hard
order: 92
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/chatgpt-chatbot.md
---

# Design an AI chatbot like ChatGPT (a conversational LLM service at scale)

`chatgpt-chatbot-walkthrough` · chatbot · hard

## 1. clarify

**Interviewer:** What do you pin down before designing? Frame users, scope, latency, safety, and the memory requirement.

<details><summary>Reference</summary>

Don't jump in. A ChatGPT-scale system is huge, and in a ~45-minute round you must
REDUCE SCOPE to one crucial slice (e.g. the online serving path plus memory), not
the whole product. Clarify: (1) Users & product: general-purpose assistant vs a
narrow domain? public consumer scale (ChatGPT passed 800M weekly users) means spiky,
global, abusive-at-the-edges traffic. (2) Turns & context: multi-turn, so I must
manage conversation history against a fixed context window. (3) Latency: streaming
chat lives or dies on time-to-first-token (TTFT), so target low-hundreds-ms TTFT and
steady tokens-per-second (TPS). (4) Cost: per-token inference is a continuous cost,
so I need a cost-per-message budget. (5) Safety: input/output guardrails, abuse,
jailbreaks, PII. (6) Memory: do we personalize across conversations? State
assumptions and confirm before drawing. [igotanoffer, igotanoffer-openai, chip-huyen-platform]

</details>

## 2. high-level

**Interviewer:** Sketch the end-to-end serving path for one chat message. Name the cross-cutting layers.

<details><summary>Reference</summary>

Client (streaming UI) -> API gateway / auth + rate limiting -> orchestrator. The
orchestrator: loads conversation state, applies INPUT guardrails (PII masking,
jailbreak/abuse checks), retrieves relevant long-term MEMORY, assembles the prompt
(system prompt + memory + trimmed history + user turn) within the token budget,
calls the model through a MODEL GATEWAY, streams tokens back, and runs OUTPUT
guardrails on the stream. The model call itself is STATELESS: all needed context is
passed per request; the model retains nothing between requests. Cross-cutting
layers: model gateway/router (unified multi-provider access, per-app access control,
fallback + retry when a provider is down), a multi-layer cache, guardrails, and
observability/eval. Conversation history and memory live in stores outside the model.
[chip-huyen-platform, igotanoffer]

</details>

## 3. deep-dive

**Interviewer:** Conversation state: how do you keep multi-turn context coherent without blowing the context window?

<details><summary>Reference</summary>

Persist each conversation (message list + metadata) in a fast store keyed by
conversation id. On each turn, rebuild the prompt from the system prompt + as much
recent history as fits the token budget. When history outgrows the window, don't
just hard-truncate: keep the latest turns verbatim and REPLACE older turns with a
running summary (rolling summarization), so the model keeps the gist without paying
for every token. Budget tokens explicitly (reserve room for the reply). This is
context/prompt budgeting — a core LLM constraint interviewers probe. Optionally cache
the shared prefix (system prompt + stable context) so repeated prefixes are cheaper.
[igotanoffer, chip-huyen-platform]

</details>

## 4. deep-dive

**Interviewer:** Cross-conversation memory: how do you make the bot remember useful facts across sessions?

<details><summary>Reference</summary>

Two distinct mechanisms, mirroring how ChatGPT does it. (1) EXPLICIT saved memories:
facts the user asks to remember (name, preferences), stored as durable structured
records and injected into the system prompt. (2) INFERRED memory from chat history:
a BACKGROUND process reads across many past conversations and synthesizes salient,
reusable facts (OpenAI calls this "dreaming") into a per-user memory store (vector
store for semantic recall + structured profile). At query time, retrieve the
memories relevant to the current turn (RAG over the user's own memory) and add them
to context. Memory must UPDATE and FORGET: revise "going to Singapore in July" to
"went to Singapore" once the date passes, and don't retain everything. Give users
control: turn memory off, view/delete individual memories, temporary chats that
bypass memory. Note the extraction/synthesis is real compute you must budget.
[openai-memory-help, openai-memory-dreaming, openai-memory-controls]

</details>

## 5. deep-dive

**Interviewer:** Serving & latency: how do you hit a low TTFT and protect the model providers under spiky load?

<details><summary>Reference</summary>

Stream tokens as they generate so the user sees output almost immediately — TTFT is
the metric that governs perceived speed; TPS governs the felt "typing" rate. In
front of the model, protect providers with rate limits, queues + backpressure,
timeouts, retries with idempotency keys, and circuit breakers so a provider hiccup
doesn't cascade. The model gateway centralizes routing and provider FALLBACK: if the
primary model/endpoint is unavailable, retry or route to an alternate. Scale
inference on GPU pools with continuous batching to keep utilization high. Warm
capacity for spikes and shed/queue gracefully when saturated. [chip-huyen-platform, igotanoffer]

</details>

## 6. deep-dive

**Interviewer:** Safety: what guardrails do you run, and where?

<details><summary>Reference</summary>

Guardrails on BOTH sides. INPUT: mask PII (e.g. replace a phone number with a
placeholder), detect jailbreak/prompt-injection and disallowed requests before the
model call. OUTPUT: scan the streamed response for toxic/unsafe content, malformed
output, and sensitive-data leakage, and be ready to stop/replace the stream. Any
action with side effects (tools that write data) must sit behind human approval —
you don't let an unreliable model execute irreversible actions on its own. Log
everything for audit and abuse investigation. [chip-huyen-platform, igotanoffer]

</details>

## 7. tradeoffs

**Interviewer:** How do you keep cost per message down at tens of millions of users without hurting quality?

<details><summary>Reference</summary>

Bend the cost curve rather than just buying GPUs. Caching: cache the shared
system-prompt prefix (cached input tokens are heavily discounted), an exact cache for
identical requests, and a semantic cache for near-duplicates — but flag that semantic
caching is risky, since a wrong similarity match returns a wrong answer. Model
tiering / routing: an intent classifier sends easy turns to a small cheap model and
only hard turns to the premium model. Compress prompts and summarize history to cut
input tokens; cap output length. Track cost-per-message and TTFT/TPS per model and
per prompt version through the gateway. [chip-huyen-platform, igotanoffer]

</details>

## 8. tradeoffs

**Interviewer:** What breaks at scale, how do you detect it, and how does the system degrade gracefully?

<details><summary>Reference</summary>

Name failure modes AND detection. (1) Provider outage / rate-limit: detect via error
rate + latency, degrade by gateway fallback to an alternate model. (2) Latency
blowup under spikes: monitor TTFT/TPS, queue depth, GPU utilization; degrade to a
smaller model, shorter context, or graceful queueing. (3) Context overflow / lost
coherence in long chats: monitor truncation rate; degrade via summarization. (4)
Unsafe or hallucinated output: output guardrails + an eval/feedback loop (thumbs
up/down) with metrics segmented by model and prompt version. (5) Memory errors —
stale or wrong personal facts: version and expire memories, and expose user controls.
(6) Cost blowup: monitor cost-per-message and cache hit rate, throttle or downshift
models. Close with the biggest risks and what you'd measure and improve first.
[chip-huyen-platform, igotanoffer, openai-memory-controls]

</details>

## Sources

- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
- [IGotAnOffer — OpenAI System Design Interviews](https://igotanoffer.com/en/advice/openai-system-design-interview)
- [Chip Huyen — Building a Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html)
- [OpenAI Help Center — How does 'Reference saved memories' work?](https://help.openai.com/en/articles/11146739-how-does-reference-saved-memories-work)
- [OpenAI — Dreaming: Better memory for a more helpful ChatGPT](https://openai.com/index/chatgpt-memory-dreaming/)
- [OpenAI — Memory and new controls for ChatGPT](https://openai.com/index/memory-and-new-controls-for-chatgpt/)
