---
imported_hash: 6f40a1937947420b
title: Your LLM app gets 1M queries/day. How do you optimize cost (without wrecking quality)?
summary: cost-optimization-1m-walkthrough · scaling · medium
order: 95
kind: reading
section: System design round / Walkthroughs
source: sisyphus/interviewing/rounds/system-design-round/walkthroughs/cost-optimization-1m.md
---

# Your LLM app gets 1M queries/day. How do you optimize cost (without wrecking quality)?

`cost-optimization-1m-walkthrough` · scaling · medium

## 1. clarify

**Interviewer:** What do you clarify and measure first before optimizing anything?

<details><summary>Reference</summary>

Don't optimize blind. First MEASURE: what's the cost breakdown per query — input
tokens vs output tokens, which model, and which query types dominate spend? Route
everything through a MODEL GATEWAY so you can attribute token usage and cost per
request, per model, and per feature; that's the control point for the whole exercise.
Clarify constraints: (1) latency SLOs (can some traffic be async/batch?), (2) quality
bar per query type (which queries truly need the premium model), (3) traffic shape
(how much is repeated or near-duplicate?), (4) data/privacy limits on caching and
self-hosting. Ignoring cost/latency is a classic interview miss, so show you'd
quantify before cutting. State assumptions and confirm. [chip-huyen-platform, igotanoffer]

</details>

## 2. high-level

**Interviewer:** Name the main cost levers, in rough order of bang-for-buck.

<details><summary>Reference</summary>

Bend the cost curve rather than just buying GPUs. The big levers: (1) CACHING —
especially the shared system-prompt prefix, plus exact and semantic caches. (2) MODEL
TIERING / ROUTING — send easy queries to a cheap small model, reserve the premium
model for hard ones. (3) TOKEN REDUCTION — compress prompts, trim context, cap output
length. (4) BATCHING — move latency-tolerant traffic to discounted async batch. (5)
SERVING EFFICIENCY — if self-hosting, continuous batching + high GPU utilization; API
vs self-host trade-off. All measured and enforced through the gateway. Order them by
effort vs savings for THIS workload, using the measurements from step one.
[chip-huyen-platform, igotanoffer, openai-batch, vllm]

</details>

## 3. deep-dive

**Interviewer:** Caching: what kinds, and how big is the win at 1M queries/day?

<details><summary>Reference</summary>

Three layers. (1) PROMPT/PREFIX cache: a large shared system prompt is re-sent on every
call — Chip Huyen's math: a 1k-token system prompt over 1M calls/day is ~1 BILLION
repeated input tokens/day that a prompt cache eliminates. Hosted prompt caching kicks in
automatically for long-enough prefixes and cuts input cost up to ~90% and latency up to
~80% (Anthropic similar, with cache reads ~10% of base input). This alone is often the
single biggest win. (2) EXACT cache: store answers for identical requests (FAQ-style
repeats) and serve them for free. (3) SEMANTIC cache: match near-duplicate queries by
embedding similarity — but flag its risk: a wrong similarity match returns a wrong
answer, so it needs careful thresholds and is more dubious than exact caching.
[chip-huyen-platform, openai-prompt-cache, anthropic-prompt-cache]

</details>

## 4. deep-dive

**Interviewer:** Model tiering / routing: how do you serve most traffic on cheaper models without hurting quality?

<details><summary>Reference</summary>

Most queries are easy and don't need the flagship model. Put a ROUTER in front: a cheap
classifier (or heuristic) estimates query difficulty and routes simple queries to a
small/cheap model and only hard ones to the premium model. Since a huge share of
traffic is typically easy, this shifts the cost mix dramatically. Calibrate the router
against your quality bar per query type, and monitor quality on the cheap tier so you
catch regressions. The gateway makes routing, fallback, and per-model cost tracking a
single control point. [chip-huyen-platform, igotanoffer]

</details>

## 5. deep-dive

**Interviewer:** Token reduction & batching: how else do you cut spend per request?

<details><summary>Reference</summary>

Cost is per token, so cut tokens. Compress prompts (drop boilerplate, summarize history
instead of resending it), retrieve/rerank so you send only the few most relevant chunks
rather than stuffing context, and CAP OUTPUT length — output tokens are often the
pricier side. For latency-TOLERANT work (offline enrichment, bulk classification,
overnight jobs), move it to the async BATCH API for a ~50% discount on input and output
tokens. Combine with request de-duplication so identical in-flight requests share one
call. [igotanoffer, chip-huyen-platform, openai-batch]

</details>

## 6. tradeoffs

**Interviewer:** Self-host vs hosted API: when does owning the serving stack pay off?

<details><summary>Reference</summary>

Hosted APIs are cheap to start and you pay per token; SELF-HOSTING trades ops complexity
for control and, at high steady volume, lower unit cost — IF you keep GPUs busy. The key
is SERVING EFFICIENCY: continuous batching + PagedAttention (vLLM) can give up to ~24x
throughput over naive serving by cutting KV-cache memory waste to under 4% and raising
GPU utilization, which is what makes cost-per-token competitive. Add quantization to fit
bigger models on cheaper GPUs. The trade-off: self-hosting only wins with high, steady
utilization and the team to run it; bursty or low volume favors the API (and its batch/
caching discounts). [vllm, chip-huyen-platform]

</details>

## 7. tradeoffs

**Interviewer:** What are the risks of aggressive cost-cutting, and how do you keep quality safe?

<details><summary>Reference</summary>

Every lever has a downside — name them AND the guardrail. (1) Semantic cache false
matches return wrong answers: tune thresholds, exclude high-stakes queries, monitor
cache-hit correctness. (2) Cheap-model routing degrades hard queries: monitor quality by
tier and route conservatively; keep a fallback to the premium model. (3) Over-
compression drops needed context and hurts answers: A/B test prompt changes. (4) Output
caps truncate legitimately long answers: cap per query type. (5) Stale caches serve
outdated info: set TTLs and invalidation. Track cost-per-query AND quality/latency
together so you never trade away quality invisibly. Close by prioritizing: usually
prompt caching + routing first (biggest, safest wins), then token trimming and batching.
[chip-huyen-platform, igotanoffer]

</details>

## Sources

- [Chip Huyen — Building a Generative AI Platform](https://huyenchip.com/2024/07/25/genai-platform.html)
- [OpenAI API — Prompt caching guide](https://developers.openai.com/api/docs/guides/prompt-caching)
- [Anthropic — Prompt caching with Claude](https://claude.com/blog/prompt-caching)
- [OpenAI API — Batch API guide](https://developers.openai.com/api/docs/guides/batch)
- [vLLM — Easy, Fast, and Cheap LLM Serving with PagedAttention](https://vllm.ai/blog/2023-06-20-vllm)
- [IGotAnOffer — Generative AI System Design Interview](https://igotanoffer.com/en/advice/generative-ai-system-design-interview)
