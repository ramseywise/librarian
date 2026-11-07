---
generated_by: src/librarian/slides/flashcards.py
decks:
- ai-engineering/07-inference-engineering/slides/deck.yaml
cards:
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
- front: How does continuous batching differ from static batching, and what makes it possible?
  back: Continuous batching swaps sequences in at every decode step, and paged KV memory is what makes that safe.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Why is round-robin a poor default for routing LLM requests?
  back: Route on load and cache affinity, not round-robin, because requests and replicas are not interchangeable.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Which parallelism strategy buys what, and in what order do you compose them?
  back: Compose TP inside one NVLink domain, add PP only for capacity, add EP for MoE, then replicate with DP.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: How do you compute KV cache bytes per token, and which head count do you use?
  back: KV bytes per token use KV heads, and free memory divided by that figure usually caps decode batch size.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: How does separating prefill and decode pools raise goodput per GPU in the DistServe example?
  back: Try chunked prefill first; disaggregate only when long prompts and strict TTFT and TPOT SLOs coincide at scale.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: What does prefix-cache hit rate depend on, and what breaks it in agent sessions?
  back: Lay prompts out stable-first and route on prefix affinity, since the cached prefix must match exactly from token one.
  lesson: ai-engineering/07-inference-engineering/notes/07-prefill-decode-kv-cache
- front: Which signals should drive LLM autoscaling, and why is warm capacity needed?
  back: Autoscale on queue depth, KV use or TTFT, and keep warm capacity because cold starts outlast most spikes.
  lesson: ai-engineering/07-inference-engineering/notes/06-serving-at-scale
- front: Why does speculative decoding preserve the target model's output distribution, and what speedup should you plan on?
  back: Speculative decoding is lossless by construction; plan on about 2× and measure acceptance per traffic type.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: How does absmax quantization work, and what problem do the serious methods all address?
  back: Serious quantization methods work around outliers, and every format change needs an eval run, not just perplexity.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
- front: What did compile, INT8, INT4 and speculation each add on Llama-7B, and why did gains shrink?
  back: Gains multiply but shrink because each step attacks a smaller remaining bottleneck, and order matters.
  lesson: ai-engineering/07-inference-engineering/notes/08-adaptive-inference
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
---
