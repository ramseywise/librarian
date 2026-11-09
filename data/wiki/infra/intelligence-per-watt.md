---
title: Intelligence per Watt
tags: [infra, concept]
summary: "Intelligence per Watt (IPW) divides mean task accuracy by mean power and Intelligence per Joule adds latency; Saad-Falcon et al. use both to compare local and cloud inference, reporting a 5.3x per-watt gain from 2023 to 2025 and a per-watt and per-joule picture that disagrees (self-reported, with several internal inconsistencies)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-saad-falcon-2025-intelligence-per-watt.md
---

# Intelligence per Watt

Saad-Falcon et al. (Stanford and Together AI, preprint v7) propose two efficiency metrics: IPW = E[accuracy] / E[power] and IPJ = E[accuracy] / E[power x latency], with binary accuracy and a ratio of means. Power is measured at 50 ms sampling on the accelerator only, with each query run 10 times. The authors' harness is public.

## Claims (self-reported)

- Per-watt gain: best local model (at most 20B active parameters) on the best accelerator per year improved 5.3x from 2023 to 2025 (Mixtral-8x7B with a Quadro RTX 6000, then Llama-3.1-8B with an RTX 6000 Ada, then GPT-OSS-120B with an Apple M4 Max), attributed 3.1x to the model and 1.7x to hardware. Per joule the gain is 18.0x (3.1x model, 5.9x hardware), so the split reverses. Single-turn chat and reasoning mix, batch size 1.
- Local against cloud on identical models, batch size 1, vLLM, 3-5 runs: B200 leads M4 Max by 1.4x in IPW and by 1.6 to 2.3x in IPJ (Qwen3-32B: 2.75e-3 against 1.97e-3 per watt), and SambaNova SN40L leads M4 Max by 1.78x in IPW and 6.5 to 7.4x in IPJ. The explanation, memory bandwidth, is asserted and not isolated.
- Batching on B200 (batch 1 against 64, Qwen3-8B, 14B and GPT-OSS-120B): 11-20x per-joule gain; Qwen3-8B energy per query 6,449 J to 548 J while GPU power rose only from 255 W to 883 W. This is a single ablation. The 1.4x gap above is therefore at the cloud's worst case.
- Hybrid routing in a 24-hour simulation covering 80.2M queries (local Qwen3 and GPT-OSS on M4 Max, cloud Qwen3-235B on H200): oracle routing saves 80.4% energy, 77.3% compute and 73.8% cost; an 80%-accurate router saves 64.3% / 61.8% / 59.0%. The paper says the effect is mostly model size, not hardware.
- Coverage: best-of-local routing across 20+ local models answers 88.7% of 1M single-turn queries; the best single model, GPT-OSS-120B, 71.4%. The authors call best-of-local over best-of-cloud a selection effect.
- Quantization: Moving from FP16 to FP4 cut energy 3 to 3.5x at a cost near 2.5 accuracy points per step (Qwen3-14B on SuperGPQA scored 54.5%, 52.0% and 49.0% at FP16, FP8 and FP4, with 3.23x less energy). Serving framework moved IPW 3-12% without changing rankings (four models, one device).
- An iPhone 16 Pro chip showed roughly 7 times the IPW of workstation GPUs while running 9 to 26 times slower, which is why IPJ is reported.
- Multi-turn check (GAIA 165 queries, TerminalBench v2 80 queries): cloud 2.4-3.0x better IPJ while M4 Max is 3.7-3.8x better IPW; the authors call 245 queries a sanity check.

## Limits

- Power is accelerator only (NVML, `powermetrics`), software telemetry with 10-15% error by the authors' admission; host, DRAM, cooling and network are excluded, so this is not wall power. Inputs capped at 32,000 characters; no long-context prefill or KV pressure; single runtime for the main results.
- The Qwen3-235B judge scores chat as win-or-tie, which is lenient; no goodput or SLO analysis.
- Internal inconsistencies in the extraction: 3.0x (Fig 3 caption) against 3.1x model gain and "18.0x over 16 months" against two years, with a different hardware set from Table 2; the abstract's "at least 1.4x" against "1.5x" in Fig 1; best-of-local SuperGPQA of 83.6% in text and 77.0% in a caption; B200 Qwen3-8B IPJ 8.71 (Table 14) against 8.92 (Table 15); batching quoted as 11-20x, 12-20x and 11.2-19.7x; M4 Max power 240 W (Table 17) against a 480 W PSU rating (Table 7); GPT-5 at 77.9% in text against 78.9% in a table row; the abstract's coverage rise from 23.2% to 71.3% is defined differently from the 88.7% figure.
- Models and hardware are as of October 2025; frontier references are old.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (the serving levers these metrics score)
- [[Cheap-First Gating and Model Cascades]] — related (the routing arm of the savings estimate)
- [[Local-Only Deployment]] — related
