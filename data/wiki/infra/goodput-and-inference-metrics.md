---
title: Goodput and Inference Metrics
tags: [infra, reference]
summary: "Reference for the serving metrics the inference sources use (TTFT, TPOT, throughput, goodput, MFU, MBU): two different goodput definitions, worked examples, and the advice to report percentiles."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch09-inference-optimization.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch01-introduction-ai-system-overview.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch17-scaling-disaggregated-prefill-decode-inf.md
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch08-addressing-constraints.md
  - data/raw/papers/2026-11-08-xiao-foundations-llms-ch05-inference.md
  - data/raw/papers/2026-11-07-llm-engineers-handbook-ch10-inference-pipeline-deployment.md
---

# Goodput and Inference Metrics

## Definitions

- TTFT (time to first token) is how quickly the first token appears after a query and corresponds to prefill. TPOT (time per output token) is the pace of each later token.
- Throughput is output tokens per second across all users. Huyen advises counting input and output throughput separately and comparing servers by cost per request.
- MFU is observed throughput relative to the theoretical peak at peak FLOP/s. MBU is the share of achievable memory bandwidth used. Huyen advises not using nvidia-smi GPU utilisation as an efficiency metric.

## Two goodput definitions

- Serving goodput (Huyen, and the DistServe usage in chapter 17): requests per second that meet the latency SLO. Worked example: 100 requests per minute completed, 30 meeting TTFT of 200 ms or less and TPOT of 100 ms or less, gives a goodput of 30 per minute.
- Cluster goodput (chapter 1): useful work per unit time as a fraction of peak, with no SLO. Worked examples: 8 GPUs handling 100,000 tokens in 10 s when the peak is 12,000 tokens/s gives 83.3%; a training job reaching 300 of an ideal 1,000 samples/s gives 30%. The chapter reports (from a Meta analysis, no model or date) a cluster that looked fully utilised losing 70-75% of its compute to overheads.

The two should not be mixed in one comparison; the extraction notes chapter 1's definition is for training clusters and not SLO-based.

## Worked numbers

- Ten TTFT samples, nine near 100 ms and one at 3,000 ms, average 390 ms; this is Huyen's reason to report p50, p90, p95 and p99 and to plot TTFT against input length.
- 7B parameters at FP16 and 100 tokens/s moves 700 GB/s; measured against the 2 TB/s of an A100-80GB, that is 70% MBU.
- At $2 per hour and 100 output tokens/s, cost is about $5.556 per million output tokens, assuming full utilisation.
- A TPOT near 120 ms suffices for streamed reading (claim). Chapter 17 quotes MLPerf v5.0 p99 SLOs: Llama 2 70B about 450 ms TTFT and 40 ms TPOT; Llama 3.1 405B about 6 s and 175 ms (reported).
- Training MFU figures quoted from the PaLM paper: PaLM 540B 46.2%, Gopher 280B 32.5%, Megatron-Turing NLG 530B 30.2%, GPT-3 175B 21.3% (reported).
- LinkedIn is quoted as saying throughput can often double or triple if TTFT and TPOT are sacrificed. Output tokens cost about 2-4x input tokens across providers; Anyscale is quoted as finding one output token costs the latency of about 100 input tokens.

## Degradation testing metrics (Pattern 27)

The chapter measures time to first token (TTFT), end-to-end request latency (EERL, including queueing, network and KV-cache creation, at P50/P95/P99), output tokens per second (TPS) and requests per second (RPS), and says to find the degradation point rather than just the failure point, with scalability, stress and load tests. Example benchmark: gpt-4o-mini via the OpenAI API, 100 users x 25 requests, max 150 tokens, temperature 0.7, a single short prompt: a mean TTFT of 3.556 s with throughput of 1914.5 tokens/s overall, 2499 requests succeeded and 1 failed in 190.57 s (self-reported, the authors' own benchmark tool). An unnamed setup under similar load averaged 52 s TTFT with mostly failed requests (self-reported). Levers named for lowering TTFT: a shorter prompt, a cached prefix, a smaller max context window, and retrieved text placed late in the prompt.

## Xiao and Zhu's metric list

Xiao and Zhu define time to first token (TTFT) as the time from sending a request to the first generated token, and call the time for each later token inter-token latency. They list latency, throughput, utilisation, energy and cost alongside these and advise reporting quality and efficiency metrics together.

## Latency and throughput arithmetic in the LLM Engineer's Handbook

The handbook's illustrative arithmetic (unbatched, sequential): 100 ms per request gives 10 requests per second and 10 ms gives 100. With batching, 20 requests in 100 ms is 200 requests per second and 60 in 200 ms is 300, so doubling latency raises throughput by half. It also cites a 2016 Google study, via Think with Google, that 53% of mobile visits were abandoned when a site took over three seconds to load.

## Limits

- Prices, batch-API discounts (50% cheaper, hours of turnaround), MFU benchmarks and hardware specs date from the books' writing (2024-2025).
- The extraction lost the MBU equations and figures, and most chapter-1 figures are uncited or quoted from vendors; the chapter text conflicts on H800 memory.
Limits of this section:
- One run per setup, a single prompt, no variance. The chapter calls Pattern 27 by a different name in its summary.
- The handbook's latency-throughput figures are worked examples, not measurements, and its abandonment figure is a cited mobile-site result, not a model-serving one.


## See Also
- [[Disaggregated Prefill-Decode Serving]] — related
- [[LLM Inference Economics]] — prerequisite-for
- [[LLM System Bottleneck Table]] — related
- [[AI Application Planning: Usefulness Threshold and Milestones]] — related (TTFT and TPOT as part of a usefulness threshold)
