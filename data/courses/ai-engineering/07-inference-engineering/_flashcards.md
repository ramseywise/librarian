---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- ai-engineering/07-inference-engineering/slides/deck.yaml
cards:
- front: What are the four parts of this lecture, in order?
  back: We measure first, then look inside one machine, then share a fleet, and last spend the compute that decode leaves idle.
  lesson: ai-engineering/07-inference-engineering/readme
- front: Name four things this lecture teaches you to do with a model that is slow or costly.
  back: You will be able to measure a serving system, name its limit and pick the change that answers it.
  lesson: ai-engineering/07-inference-engineering/readme
- front: What bounds prefill and decode, and which latency does each set?
  back: Prefill is compute-bound and sets TTFT; decode is memory-bandwidth-bound and sets TPOT.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: How do you turn $2/hour and 100 tokens/s into a cost, and 7B weights into a bandwidth figure?
  back: A 7B FP16 model at 100 tokens/s reads 700 GB/s, so memory bandwidth limits it long before arithmetic does.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: What is goodput, and how does it differ from throughput?
  back: Goodput is the request rate that meets every latency SLO, so optimize it rather than raw throughput.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: Which utilization metrics should you track for prefill and for decode?
  back: Track MFU for prefill, MBU for decode, and SM activity, because GPU util cannot see either bottleneck.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: What should you measure before you tune an inference service?
  back: Before tuning, define the SLO, split TTFT from TPOT, and price each request.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: How do you locate a kernel on the roofline, and what does its position imply?
  back: Left of the roofline ridge only fewer bytes help; decode at batch 1 sits two orders of magnitude left of it.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: What does performance work do on the memory ladder, and what tier is Grace memory?
  back: Performance work moves data up the ladder fewer times, and Grace memory is an overflow tier, not HBM.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: Which platform misconfigurations slow inference without raising an error?
  back: Check the NCCL log and NUMA binding on every deployment, because each of these faults just runs slowly.
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: What are the four kernel regimes, and what fixes each?
  back: A kernel is underutilized, latency-bound, memory-bound or compute-bound, and fixing one usually reveals the next.
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: What does a CUDA graph improve, and what does it leave unchanged?
  back: CUDA graphs make no kernel faster; they remove the launch gaps, so engines capture one per batch-size bucket.
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: What does torch.compile need from your model to pay off, and how do you enforce it in CI?
  back: Expect torch.compile to pay when small kernels and Python dominate, and much less when one big GEMM does.
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: In what order should you work on a performance problem, and how do you keep the gain?
  back: Profile the host before the device, and gate merges on a sustained 5% regression so the gain survives upgrades.
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: Why is round-robin a poor default for routing LLM requests?
  back: Route on load and cache affinity, not round-robin, because requests and replicas are not interchangeable.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Which parallelism strategy buys what, and in what order do you compose them?
  back: Compose TP inside one NVLink domain, add PP only for capacity, add EP for MoE, then replicate with DP.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Which signals should drive LLM autoscaling, and why is warm capacity needed?
  back: Autoscale on queue depth, KV use or TTFT, and keep warm capacity because cold starts outlast most spikes.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: How does continuous batching differ from static batching, and what makes it possible?
  back: Continuous batching swaps sequences in at every decode step, and paged KV memory is what makes that safe.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: How do you compute KV cache bytes per token, and which head count do you use?
  back: KV bytes per token use KV heads, and free memory divided by that figure usually caps decode batch size.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: How does separating prefill and decode pools raise goodput per GPU in the DistServe example?
  back: Try chunked prefill first; disaggregate only when long prompts and strict TTFT and TPOT SLOs coincide at scale.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: What does prefix-cache hit rate depend on, and what breaks it in agent sessions?
  back: Lay prompts out stable-first and route on prefix affinity, since the cached prefix must match exactly from token one.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Why does speculative decoding preserve the target model's output distribution, and what speedup should you plan on?
  back: Speculative decoding is lossless by construction; plan on about 2× and measure acceptance per traffic type.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: What did compile, INT8, INT4 and speculation each add on Llama-7B, and why did gains shrink?
  back: Gains multiply but shrink because each step attacks a smaller remaining bottleneck, and order matters.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: How does absmax quantization work, and what problem do the serious methods all address?
  back: Serious quantization methods work around outliers, and every format change needs an eval run, not just perplexity.
  lesson: ai-engineering/07-inference-engineering/notes/08c-quantization-and-low-precision
- front: Why does sorting texts by length speed up an encoder, and what does a token budget give you instead?
  back: Every text is padded to the longest in its batch, so measure padding share and sort; a token budget caps memory, not time.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Why does a short reply from a vision-language model stay slow, and which setting changes that most?
  back: The longest edge sets the tiles and so the fixed cost per page, making it your main serving control, and short replies feel it most.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: When should you merge a LoRA adapter for serving, and when should you keep it attached?
  back: Merge a single adapter into a float base, and keep adapters unmerged for many customers or on a 4-bit base.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: What makes AI-generated kernels safe to use, and what results has the verifier loop produced?
  back: Trust the verifier and not the model, and compare generated kernels against the best existing kernel.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: In what order do you walk the inference checklist?
  back: Walk measurement, host, placement, engine, kernels, then monitoring, and treat every printed gain as a hypothesis.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: How do you approach an inference problem, and when do you re-run evals?
  back: Name the bound, measure goodput against an SLO, and re-run evals whenever a change can alter outputs.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: Which pillars connect to inference engineering, and where do the labs live?
  back: This layer can shave a badly sized context or a chatty loop, but only the layers above can remove them.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: Why is prefill compute-bound and decode bandwidth-bound?
  back: Prefill processes all prompt tokens in parallel, so it does much math per byte and sets TTFT. Decode reads every weight and the KV cache to produce one token per sequence, so it waits on memory and sets TPOT.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: GPU utilization reads 95%. Can this box take more traffic?
  back: You can't tell from that number, because it is the fraction of time any kernel runs. Check MFU, MBU, SM activity and queue depth; a decode loop can read near 100% at light load.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: What does the 90% figure in "inference is up to 90% of ML cost" actually claim?
  back: 'Desislavov et al. give it as an upper bound on a deployed system''s ML cost. It is why inference is treated as its own bill: training is paid once and inference on every request.'
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: Why not report mean TTFT?
  back: One 3,000 ms outlier among fast requests gives a 390 ms mean that describes no request. For an agent making ten calls, about 65% of tasks hit at least one call beyond the single-call p90, if calls are independent.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: Hardware costs $2/hour and makes 100 output tokens/s. What does a million tokens cost?
  back: About $5.56 (Huyen's example), since it takes 10,000 s to make a million tokens. That is at full use, so serving below capacity costs more per token.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: Your choice is a part with 2× FLOPS or one with 2× memory bandwidth, for chat at low batch. Which?
  back: Bandwidth, because decode at small batch sits on the bandwidth slope of the roofline. The extra FLOPS would help prefill and TTFT only.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: Throughput and goodput disagree. Which one do you tune?
  back: Goodput, the throughput that meets the SLO. In Huyen's figure only two of ten requests clear both lines, whatever the raw token rate, even though her caption says three.
  lesson: ai-engineering/07-inference-engineering/notes/01-why-inference-is-its-own-discipline
- front: What is in a GB200 superchip, and why does the C2C link matter?
  back: One Grace CPU with 480 GB LPDDR5X and two B200s with 192 GB HBM3e each, joined by coherent NVLink-C2C at ~900 GB/s. That is roughly 14× PCIe Gen5 x16's 64 GB/s, so spilling is possible, though still far from HBM's ~8 TB/s.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: 'Coherent means uniform: true or false?'
  back: False. A GPU can touch Grace memory directly, but at about a ninth of HBM bandwidth and with far higher latency, so placement still decides speed.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: What limits occupancy on a B200 SM?
  back: 64 resident warps (2,048 threads) and 32 blocks, plus 64K registers and up to 228 KB of SMEM. Whichever runs out first sets occupancy; 12.x parts allow only 48 warps.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: How far apart are the levels of the memory ladder?
  back: Registers ~1 cycle, SMEM ~20–30, L2 ~200 and HBM hundreds to ~1,000. So an HBM load costs as much time as hundreds of arithmetic instructions, which is what occupancy, ILP and pipelining are there to cover.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: You need TP across more GPUs than a rack holds. What do you do?
  back: 'Avoid it: keep TP and EP inside the NVLink domain (up to 72 GPUs on NVL72) and use cross-rack links for pipeline stages or replicas, because those links give about 10× less bandwidth at 5–10 µs.'
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: Where is a vector add on the roofline?
  back: One FLOP per 12 bytes is 0.083 FLOP/byte, more than 100× below the 10 FLOP/byte FP32 ridge (80 TFLOPS / 8 TB/s), so it is purely bandwidth-limited.
  lesson: ai-engineering/07-inference-engineering/notes/02-the-hardware
- front: A job runs to completion, but GPU utilization dips and CPU spikes on each all-reduce. What do you check?
  back: The NCCL log for `NET/Socket` instead of `NET/IB`, then `NCCL_SOCKET_IFNAME`. RDMA falling back to TCP gives this signature and no error.
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: What did Fregly measure for Gloo against NCCL?
  back: On a 400 MB all-reduce with 2 ranks over 800 Gb/s InfiniBand, Gloo took 200 ms (2 GB/s, a CPU core near 100%) and NCCL took 4 ms (~100 GB/s, line rate).
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: MIG or MPS for several small models on one B200?
  back: 'MIG when they have separate SLOs or need isolation, since MPS has no memory isolation. MIG''s costs: changing the layout needs an idle, reset GPU, and instances can''t use NVLink peer-to-peer.'
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: Do containers slow GPU work?
  back: Under 2% in Fregly's measurement, because the driver is shared. The risk is version skew between the image's CUDA toolkit and the host driver.
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: What fails most at scale, and what does a fleet need for it?
  back: Meta's Llama 3 405B run logged 419 interruptions in 54 days, 30.1% faulty GPUs and 17.2% HBM3. So you need health checks (DCGM, XID errors), timeouts on collectives, and a way to pull a degraded GPU.
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: Your cold start takes too long. What are the options from this note?
  back: Fast NVMe and the page cache for weights, persistence mode for the 1–2 s driver init, and `cuda-checkpoint` with CRIU to restore a warmed, compiled server instead of rebuilding it.
  lesson: ai-engineering/07-inference-engineering/notes/03-the-platform
- front: A kernel is slow. Walk through the diagnosis.
  back: Nsight Systems for the timeline, then Nsight Compute on the hot kernel, built with `-lineinfo`. Sort it into underutilized, latency-bound, memory-bound (DRAM ≳ 80% of peak) or compute-bound, then fix that regime and re-measure, since fixing one exposes the next.
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: What does occupancy buy?
  back: 'More resident warps give the scheduler something to issue while others wait on memory. The maximum is 64 warps per SM on Hopper and datacenter Blackwell, reached for example by `__launch_bounds__(256, 8)`: 256 × 8 = 2,048 threads.'
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: How do you avoid bank conflicts in a 32 × 32 SMEM tile?
  back: Pad to `tile[32][33]`, which costs about 3% and shifts each row by a bank, or use an XOR swizzle as CUTLASS does, which wastes nothing.
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: Why is structure of arrays better for coalescing?
  back: Consecutive threads then touch consecutive addresses, so a warp's 32 float loads fit four 32-byte sectors in one 128-byte line. A shifted read straddles two lines and touches five.
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: Your kernel is memory-bound at peak bandwidth. What are the options?
  back: 'Raise arithmetic intensity: tiling, fusion so intermediates never reach HBM, recompute instead of store, or lower precision such as FP8 or NVFP4. FlashAttention combines the first three. Occupancy won''t help.'
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: When is a megakernel worth it?
  back: For small-batch decode latency, at the research frontier. Fregly cites 1.2–6.7× lower decode latency than vLLM or SGLang for a Mirage-style persistent kernel, so treat it as research, not a default.
  lesson: ai-engineering/07-inference-engineering/notes/04-kernels
- front: What does `torch.compile` actually do?
  back: TorchDynamo hooks bytecode into an FX graph with guards, AOTAutograd traces ahead of time, PrimTorch decomposes 2,000+ ops to ~250 primitives, and TorchInductor fuses and generates Triton kernels. Fusion and removing Python are where inference gains come from.
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: Your compiled model is no faster. Where do you look?
  back: Graph breaks first (`torch._dynamo.explain`), then recompiles from changing shapes, then whether one large GEMM dominates. Fregly's dense case may see under 10%, since Tensor Cores are already doing the work.
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: '`reduce-overhead` or `max-autotune`?'
  back: '`reduce-overhead` for small batches and stable decode shapes, through CUDA graphs. `max-autotune` when you compile once and serve long, on GEMM-heavy work. `default` has no CUDA graphs.'
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: How do you serve variable lengths with CUDA graphs?
  back: 'Bucket: pad to a few lengths within ±10–20% and capture one graph per batch-size bucket (Fregly''s example uses 1, 2, 4, 8) from a shared memory pool, largest first.'
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: Your scale-out takes minutes because of compile. What are the options?
  back: Regional compilation of one transformer block, a Mega-Cache shared across replicas, or `torch.export` with AOTInductor to ship a binary with no compile on the serving path.
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: How do you stop performance regressions reaching main?
  back: A CI job on a fixed model and hardware that fails on a slowdown of 5% or more sustained over 3 runs, with pinned versions so noise and upgrades don't look like regressions.
  lesson: ai-engineering/07-inference-engineering/notes/05-compilers-and-frameworks
- front: Why does latency buy throughput?
  back: 'In the Handbook''s arithmetic, 20 requests in 100 ms is 200 RPS and 60 in 200 ms is 300 RPS: each request waits twice as long and the fleet serves 50% more. Decode''s weight read is amortized over the batch.'
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Static, dynamic or continuous batching?
  back: Static waits to fill. Dynamic also fires on a time window, but runs until its longest member finishes. Continuous admits and retires at each decode step, and needs paged KV memory and a scheduler.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: How do you split a model too big for one GPU?
  back: 'TP inside the NVLink domain, PP only for capacity, EP for MoE, then replicate with DP: Fregly''s order is TP → PP → EP → DP. Measure before adding EP or CP.'
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: What should autoscaling track?
  back: Queue depth, KV utilization or TTFT. GPU utilization is time-active and misses KV exhaustion, and with 15–30 min deploys you also need warm headroom.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Someone proposes a cascade with 60% of traffic on a 10× smaller model. What saving do you tell them?
  back: About 2.2× (0.6 × 0.1 + 0.4 = 0.46), not the book's 5×, and less if escalated queries pay for both models. Decide after measuring how often the small model must escalate.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Copy-engine utilization spikes while compute stays flat. What is happening?
  back: The engine is probably swapping KV to host memory because it is out of KV space, and latency is about to jump. Lower the batch cap, shrink KV, or add capacity.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: What are the two ways to deal with prefill and decode interfering?
  back: Chunked prefill, which slices prefill so decodes run alongside it (SARATHI reports ~1.3–1.9× over naive scheduling) and is the first choice on one pool. Or disaggregation, which moves prefill to its own GPUs.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Walk through DistServe's numbers.
  back: Colocated, the GPU holds 3 RPS for TTFT but 1.6 RPS for TPOT, so 1.6. With 2 prefill at 5.6 and 1 decode at 10, min(11.2, 10) / 3 ≈ 3.3 RPS per GPU, about 2×.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: When would you not disaggregate?
  back: 'Short prompts with long outputs, low load or loose SLOs, KV crossing slow Ethernet, or only a handful of GPUs. Huyen''s ratios also show it depends on workload: 2:1 to 4:1 for long inputs and 1:2 to 1:1 for short.'
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: How big is the KV cache for Llama 2 13B at 4,096 tokens?
  back: 2 × 40 × 40 × 128 × 2 bytes ≈ 0.82 MB/token, so 3.36 GB in FP16 per sequence. With GQA-8 it would be 0.67 GB.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Why did PagedAttention matter?
  back: Reserved slabs left only 20–38% of KV memory holding real tokens. Paging cut waste to under 4%, lets a sequence grow by a block at a time, and lets common prefixes share physical blocks with copy-on-write.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Your agent's cache hit rate is low. What do you check?
  back: Prompt layout first, because one changed early token invalidates everything after it and vLLM matches full 16-token blocks exactly from the first token. Then whether routing sends requests to the replica holding the prefix.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Do long agent sessions change the picture?
  back: 'Yes: in one AgentSysBench session accumulated tool calls and observations reached 84.3% of the input, and the final step emitted 151 tokens after a 166,721-token input. The input side dominates that step, not decode.'
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Why is speculative decoding cheap?
  back: Verifying K tokens is one parallel pass, and decode is bandwidth-bound, so the verification FLOPs are nearly free. Fregly's "one by one" contradicts both the method and his own figure.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: What speedup do you promise?
  back: About 2× for a well-matched pair on a large target, and measure it. The sources range from 3–4× at an assumed 90% acceptance to "not significant" on a small target on a T4.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: When does speculative decoding hurt?
  back: When batches already saturate compute (high MFU), or when the draft isn't at least ~4× faster. It also needs the target's tokenizer and vocabulary.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: Speculation and quantization both speed things up. What's the difference for quality?
  back: Speculative decoding with the standard rejection-sampling rule keeps the output distribution. Quantization changes outputs, so every format change needs an eval run, and perplexity alone isn't enough.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: 'Read the PyTorch stack: 25.5 → 107.0 → 157.4 → 202.1 → 244.7 tokens/s.'
  back: 'At batch 1 on Llama-7B and an A100, compile gives 4.2× because launch overhead dominates, then each step gains less: 1.5×, 1.3×, 1.2×. The total is 9.6×, but quality wasn''t measured and it won''t hold at large batch.'
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: Is SpeCache speculative decoding?
  back: No. Despite the name and the book's figure title, it prefetches predicted KV blocks to hide the latency of offloaded cache tiers, so it is a KV-tiering technique.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: What is knowledge distillation?
  back: Training a small student against a large teacher with a blended loss, `(1 - alpha) * task_loss + alpha * KL`, where the KL term compares their temperature-scaled outputs.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: How does serving an embedding model differ from an LLM?
  back: One forward pass, with no KV cache or streaming. Throughput is set by the batch's rectangle, the longest text times the batch size.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: How do you speed up an encoder without new hardware?
  back: Sort or bucket by length. Here that cut padding from 80% to about 5% and gave about 3×. Check the padding share first.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Why have a token budget per batch?
  back: It caps memory on a rare long batch. It gave no reliable speed-up without sorting.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Would you set a batching window?
  back: Start at zero. A busy worker batches by itself. In a simulation over measured service times, waiting 50 ms added about 35 ms at the median and at least 47 ms at p99, and gave nothing back.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Is int8 or ONNX faster?
  back: It depends on hardware. Published x86 results favoured int8. On an Apple CPU, PyTorch won by about 1.8× and int8 lost 8% of the top ten.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Where does a VLM's time go?
  back: Before the first token, the vision pass and the prefill both scale with tiles. At a 2048 edge the vision pass was 54% of a 50-token reply. It runs once, and the decode uses the KV cache.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Is preprocessing the bottleneck?
  back: Measure both rates. Here one CPU thread was about ten times the GPU's rate, but on clean pages and a laptop GPU.
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: Merge the adapter, or serve it attached?
  back: 'One adapter on a float base: merge, since attached cost 1.8× here. Many adapters: an engine like S-LoRA. A 4-bit base: keep it attached.'
  lesson: ai-engineering/07-inference-engineering/notes/08b-serving-encoders-and-vision-models
- front: FP8 or FP4 on Blackwell?
  back: FP8 is the safe default, with 2× FP16's tensor-core math rate and half the bytes. The book gives FP4 an effective ~1.8× over FP8 with no model or batch size, so validate it per model.
  lesson: ai-engineering/07-inference-engineering/notes/08c-quantization-and-low-precision
- front: What are the four duties of a kernel verifier?
  back: Correctness against a reference on random inputs and shapes with edge cases, proper timing (warm-up, synchronization, repeated runs, served shapes), guarding against reward hacking, and human review before merge.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: What is reward hacking here?
  back: A kernel that caches results, skips work on test shapes or reads the reference output looks fast. KernelBench-style benchmarks have documented it; fresh inputs and held-out shapes defend against it.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: What do the R1 results show?
  back: With a verifier, about 15 minutes on an H100 gave attention kernels 1.1–2.1× faster than FlexAttention and passed 100% of KernelBench level 1 and 96% of level 2. FlexAttention is 85–90% of FlashAttention-2, so the baseline matters.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: A team wants to let a model write production kernels. What's your answer?
  back: Only in a loop with a correctness and timing verifier, with review before merge. Predibase's fine-tuned model reached only about 40% correct after about 5,000 steps, which is fine inside verified search and dangerous anywhere else.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: The checklist says leave ECC on and try an 80% TDP cap. How do you decide on the cap?
  back: Measure tokens per joule before and after on your own load. The appendix reports similar throughput for bandwidth-bound decode at lower power, but treat that as a hypothesis, and alert on thermals near ~85°C and on throttling.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
- front: Why does the checklist run in this order?
  back: Measurement comes first, or no later step can be judged, and host and placement faults can swamp anything a kernel gains. Kernels come late because most engineers will get more from the steps before them.
  lesson: ai-engineering/07-inference-engineering/notes/09-checklist-and-ai-assisted-tuning
---
