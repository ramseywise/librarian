---
imported_hash: 987408056c0d0cce
title: 07 — Inference Engineering
summary: 'Inference engineering is the discipline of making a model answer fast enough and cheaply enough to ship: how requests are batched and scheduled, where the KV cache lives, how prefill and decode are split across hardware, and what the GPU is…'
order: 7
source: learn-ai-engineering/ai-engineering/07-inference-engineering
readings:
- title: Inference engineering
  source: ai-engineering/07-inference-engineering/slides/inference-engineering.pdf
- title: Acharya 2024 star attention
  source: ai-engineering/07-inference-engineering/sources/acharya-2024-star-attention.pdf
- title: Aggarwal 2023 automix
  source: ai-engineering/07-inference-engineering/sources/aggarwal-2023-automix.pdf
- title: Aghajohari 2025 markovian thinker
  source: ai-engineering/07-inference-engineering/sources/aghajohari-2025-markovian-thinker.pdf
- title: Ainslie 2023 gqa
  source: ai-engineering/07-inference-engineering/sources/ainslie-2023-gqa.pdf
- title: Alizadeh 2023 llm flash
  source: ai-engineering/07-inference-engineering/sources/alizadeh-2023-llm-flash.pdf
- title: Aminabadi 2022 deepspeed inference
  source: ai-engineering/07-inference-engineering/sources/aminabadi-2022-deepspeed-inference.pdf
- title: Ashkboos 2024 slicegpt
  source: ai-engineering/07-inference-engineering/sources/ashkboos-2024-slicegpt.pdf
- title: Bae 2024 relaxed recursive transformers
  source: ai-engineering/07-inference-engineering/sources/bae-2024-relaxed-recursive-transformers.pdf
- title: Bao 2025 learning parallel
  source: ai-engineering/07-inference-engineering/sources/bao-2025-learning-parallel.pdf
- title: Bengio 2013 estimating or propagating gradients through
  source: ai-engineering/07-inference-engineering/sources/bengio-2013-estimating-or-propagating-gradients-through.pdf
- title: Bercovich 2026 nemotron labs 3 puzzle 75b
  source: ai-engineering/07-inference-engineering/sources/bercovich-2026-nemotron-labs-3-puzzle-75b.pdf
- title: Bie 2026 llada2 1
  source: ai-engineering/07-inference-engineering/sources/bie-2026-llada2-1.pdf
- title: Cai 2024 medusa
  source: ai-engineering/07-inference-engineering/sources/cai-2024-medusa.pdf
- title: Chang 2026 llm inference agentic workloads
  source: ai-engineering/07-inference-engineering/sources/chang-2026-llm-inference-agentic-workloads.pdf
- title: Chen 2023 frugalgpt
  source: ai-engineering/07-inference-engineering/sources/chen-2023-frugalgpt.pdf
- title: Crankshaw 2016 clipper
  source: ai-engineering/07-inference-engineering/sources/crankshaw-2016-clipper.pdf
- title: Dao 2022 flashattention
  source: ai-engineering/07-inference-engineering/sources/dao-2022-flashattention.pdf
- title: Dao 2023 flashattention 2
  source: ai-engineering/07-inference-engineering/sources/dao-2023-flashattention-2.pdf
- title: Deepseek ai 2024 deepseek v2
  source: ai-engineering/07-inference-engineering/sources/deepseek-ai-2024-deepseek-v2.pdf
- title: Dettmers 2022 llm int8
  source: ai-engineering/07-inference-engineering/sources/dettmers-2022-llm-int8.pdf
- title: Dettmers 2023 spqr
  source: ai-engineering/07-inference-engineering/sources/dettmers-2023-spqr.pdf
- title: Ding 2023 efficiency spectrum large language models
  source: ai-engineering/07-inference-engineering/sources/ding-2023-efficiency-spectrum-large-language-models.pdf
- title: Eliseev 2023 fast inference mixture experts language
  source: ai-engineering/07-inference-engineering/sources/eliseev-2023-fast-inference-mixture-experts-language.pdf
- title: Flashattention 3 2024
  source: ai-engineering/07-inference-engineering/sources/flashattention-3-2024.pdf
- title: Frantar 2023 sparsegpt
  source: ai-engineering/07-inference-engineering/sources/frantar-2023-sparsegpt.pdf
- title: Fu 2024 lazyllm
  source: ai-engineering/07-inference-engineering/sources/fu-2024-lazyllm.pdf
- title: Golden 2024 flash attention stable
  source: ai-engineering/07-inference-engineering/sources/golden-2024-flash-attention-stable.pdf
- title: Gu 2025 jet nemotron
  source: ai-engineering/07-inference-engineering/sources/gu-2025-jet-nemotron.pdf
- title: Gu 2025 tensorllm
  source: ai-engineering/07-inference-engineering/sources/gu-2025-tensorllm.pdf
- title: Guo 2025 sonicmoe
  source: ai-engineering/07-inference-engineering/sources/guo-2025-sonicmoe.pdf
- title: Han 2015 deep compression
  source: ai-engineering/07-inference-engineering/sources/han-2015-deep-compression.pdf
- title: Heakl 2025 dr llm
  source: ai-engineering/07-inference-engineering/sources/heakl-2025-dr-llm.pdf
- title: Ho 2026 language models can control their
  source: ai-engineering/07-inference-engineering/sources/ho-2026-language-models-can-control-their.pdf
- title: Jin 2024 efficient multimodal large language models
  source: ai-engineering/07-inference-engineering/sources/jin-2024-efficient-multimodal-large-language-models.pdf
- title: Kim 2016 sequence level knowledge distillation
  source: ai-engineering/07-inference-engineering/sources/kim-2016-sequence-level-knowledge-distillation.pdf
- title: Kou 2024 cllms
  source: ai-engineering/07-inference-engineering/sources/kou-2024-cllms.pdf
- title: Kumar 2024 scaling laws precision
  source: ai-engineering/07-inference-engineering/sources/kumar-2024-scaling-laws-precision.pdf
- title: Labs 2025 mercury
  source: ai-engineering/07-inference-engineering/sources/labs-2025-mercury.pdf
- title: Lai 2026 minimax sparse attention
  source: ai-engineering/07-inference-engineering/sources/lai-2026-minimax-sparse-attention.pdf
- title: Lee 2024 exploring trade offs
  source: ai-engineering/07-inference-engineering/sources/lee-2024-exploring-trade-offs.pdf
- title: Li 2024 eagle 2
  source: ai-engineering/07-inference-engineering/sources/li-2024-eagle-2.pdf
- title: Liu 2023 ring attention blockwise transformers near
  source: ai-engineering/07-inference-engineering/sources/liu-2023-ring-attention-blockwise-transformers-near.pdf
- title: Liu 2024 survey text sql era llms
  source: ai-engineering/07-inference-engineering/sources/liu-2024-survey-text-sql-era-llms.pdf
- title: Liu 2025 tidar
  source: ai-engineering/07-inference-engineering/sources/liu-2025-tidar.pdf
- title: Luo 2024 addition all you need energy
  source: ai-engineering/07-inference-engineering/sources/luo-2024-addition-all-you-need-energy.pdf
- title: Ma 2024 era 1 bit llms
  source: ai-engineering/07-inference-engineering/sources/ma-2024-era-1-bit-llms.pdf
- title: Ma 2025 bitnet b1 58 2b4t technical
  source: ai-engineering/07-inference-engineering/sources/ma-2025-bitnet-b1-58-2b4t-technical.pdf
- title: Moba 2025
  source: ai-engineering/07-inference-engineering/sources/moba-2025.pdf
- title: Monea 2023 pass
  source: ai-engineering/07-inference-engineering/sources/monea-2023-pass.pdf
- title: Nguyen tri 2025 attention all you need kv
  source: ai-engineering/07-inference-engineering/sources/nguyen-tri-2025-attention-all-you-need-kv.pdf
- title: Ning 2023 skeleton thought
  source: ai-engineering/07-inference-engineering/sources/ning-2023-skeleton-thought.pdf
- title: Nvidia 2026 nemotron 3 super
  source: ai-engineering/07-inference-engineering/sources/nvidia-2026-nemotron-3-super.pdf
- title: O brien 2023 contrastive decoding improves reasoning large
  source: ai-engineering/07-inference-engineering/sources/o-brien-2023-contrastive-decoding-improves-reasoning-large.pdf
- title: Ong 2024 routellm
  source: ai-engineering/07-inference-engineering/sources/ong-2024-routellm.pdf
- title: Park 2024 comprehensive survey compression algorithms language
  source: ai-engineering/07-inference-engineering/sources/park-2024-comprehensive-survey-compression-algorithms-language.pdf
- title: Peng 2023 fp8 lm
  source: ai-engineering/07-inference-engineering/sources/peng-2023-fp8-lm.pdf
- title: Peng 2023 rwkv
  source: ai-engineering/07-inference-engineering/sources/peng-2023-rwkv.pdf
- title: Peng 2026 efficient pre training token superposition
  source: ai-engineering/07-inference-engineering/sources/peng-2026-efficient-pre-training-token-superposition.pdf
- title: Peng 2026 long context pre training lighthouse
  source: ai-engineering/07-inference-engineering/sources/peng-2026-long-context-pre-training-lighthouse.pdf
- title: Pope 2022 efficiently scaling transformer inference
  source: ai-engineering/07-inference-engineering/sources/pope-2022-efficiently-scaling-transformer-inference.pdf
- title: Powerinfer 2023
  source: ai-engineering/07-inference-engineering/sources/powerinfer-2023.pdf
- title: Qin 2025 seer
  source: ai-engineering/07-inference-engineering/sources/qin-2025-seer.pdf
- title: Ramapuram 2024 theory analysis best practices sigmoid
  source: ai-engineering/07-inference-engineering/sources/ramapuram-2024-theory-analysis-best-practices-sigmoid.pdf
- title: Raposo 2024 mixture depths
  source: ai-engineering/07-inference-engineering/sources/raposo-2024-mixture-depths.pdf
- title: Rostam 2024 achieving peak performance large language
  source: ai-engineering/07-inference-engineering/sources/rostam-2024-achieving-peak-performance-large-language.pdf
- title: Saad falcon 2025 intelligence per watt
  source: ai-engineering/07-inference-engineering/sources/saad-falcon-2025-intelligence-per-watt.pdf
- title: Sadhukhan 2024 magicdec
  source: ai-engineering/07-inference-engineering/sources/sadhukhan-2024-magicdec.pdf
- title: Shazeer 2019 fast transformer decoding
  source: ai-engineering/07-inference-engineering/sources/shazeer-2019-fast-transformer-decoding.pdf
- title: Sheng 2023 flexgen
  source: ai-engineering/07-inference-engineering/sources/sheng-2023-flexgen.pdf
- title: Sheng 2023 s lora
  source: ai-engineering/07-inference-engineering/sources/sheng-2023-s-lora.pdf
- title: Sun 2023 simple effective pruning approach large
  source: ai-engineering/07-inference-engineering/sources/sun-2023-simple-effective-pruning-approach-large.pdf
- title: Sun 2024 you only cache once
  source: ai-engineering/07-inference-engineering/sources/sun-2024-you-only-cache-once.pdf
- title: Tang 2024 bi mamba
  source: ai-engineering/07-inference-engineering/sources/tang-2024-bi-mamba.pdf
- title: Tschand 2026 jaxbench
  source: ai-engineering/07-inference-engineering/sources/tschand-2026-jaxbench.pdf
- title: Wang 2025 harnessing reasoning economy
  source: ai-engineering/07-inference-engineering/sources/wang-2025-harnessing-reasoning-economy.pdf
- title: Wang 2026 flashmemory deepseek v4
  source: ai-engineering/07-inference-engineering/sources/wang-2026-flashmemory-deepseek-v4.pdf
- title: Wei 2026 hysparse2
  source: ai-engineering/07-inference-engineering/sources/wei-2026-hysparse2.pdf
- title: Wijmans 2024 cut your losses large vocabulary
  source: ai-engineering/07-inference-engineering/sources/wijmans-2024-cut-your-losses-large-vocabulary.pdf
- title: Wortsman 2023 stable low precision training large
  source: ai-engineering/07-inference-engineering/sources/wortsman-2023-stable-low-precision-training-large.pdf
- title: Wu 2024 layer condensed kv cache efficient
  source: ai-engineering/07-inference-engineering/sources/wu-2024-layer-condensed-kv-cache-efficient.pdf
- title: Wu 2025 llamarl
  source: ai-engineering/07-inference-engineering/sources/wu-2025-llamarl.pdf
- title: Xiao 2023 efficient streaming language models attention
  source: ai-engineering/07-inference-engineering/sources/xiao-2023-efficient-streaming-language-models-attention.pdf
- title: Xu 2024 survey resource efficient llm multimodal
  source: ai-engineering/07-inference-engineering/sources/xu-2024-survey-resource-efficient-llm-multimodal.pdf
- title: Xu 2024 think
  source: ai-engineering/07-inference-engineering/sources/xu-2024-think.pdf
- title: Yang 2024 1 58 bit flux
  source: ai-engineering/07-inference-engineering/sources/yang-2024-1-58-bit-flux.pdf
- title: Yuan 2025 efficientllm
  source: ai-engineering/07-inference-engineering/sources/yuan-2025-efficientllm.pdf
- title: Yuan 2025 native sparse attention
  source: ai-engineering/07-inference-engineering/sources/yuan-2025-native-sparse-attention.pdf
- title: Zadouri 2026 flashattention 4
  source: ai-engineering/07-inference-engineering/sources/zadouri-2026-flashattention-4.pdf
- title: Zhang 2025 beyond gpt 5
  source: ai-engineering/07-inference-engineering/sources/zhang-2025-beyond-gpt-5.pdf
- title: Zhang 2025 survey parallel text generation
  source: ai-engineering/07-inference-engineering/sources/zhang-2025-survey-parallel-text-generation.pdf
- title: Zhang 2026 toktier
  source: ai-engineering/07-inference-engineering/sources/zhang-2026-toktier.pdf
- title: Zhao 2024 galore
  source: ai-engineering/07-inference-engineering/sources/zhao-2024-galore.pdf
- title: Zhao 2026 heterogeneous computing
  source: ai-engineering/07-inference-engineering/sources/zhao-2026-heterogeneous-computing.pdf
- title: Zhen 2025 taming titans
  source: ai-engineering/07-inference-engineering/sources/zhen-2025-taming-titans.pdf
- title: Zhu 2023 survey model compression large language
  source: ai-engineering/07-inference-engineering/sources/zhu-2023-survey-model-compression-large-language.pdf
- title: Zhu 2024 scalable matmul free language modeling
  source: ai-engineering/07-inference-engineering/sources/zhu-2024-scalable-matmul-free-language-modeling.pdf
- title: Appendix ai systems performance checklist 175 items
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/appendix-ai-systems-performance-checklist-175-items.pdf
- title: Ch01 introduction ai system overview
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch01-introduction-ai-system-overview.pdf
- title: Ch02 ai system hardware overview
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch02-ai-system-hardware-overview.pdf
- title: Ch03 os docker kubernetes tuning gpu based
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch03-os-docker-kubernetes-tuning-gpu-based.pdf
- title: Ch04 tuning distributed networking communication
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch04-tuning-distributed-networking-communication.pdf
- title: Ch05 gpu based storage i o optimizations
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch05-gpu-based-storage-i-o-optimizations.pdf
- title: Ch06 gpu architecture cuda programming maximizing occupancy
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch06-gpu-architecture-cuda-programming-maximizing-occupancy.pdf
- title: Ch07 profiling tuning gpu memory access patterns
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch07-profiling-tuning-gpu-memory-access-patterns.pdf
- title: Ch08 occupancy tuning warp efficiency instruction level
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch08-occupancy-tuning-warp-efficiency-instruction-level.pdf
- title: Ch09 increasing cuda kernel efficiency arithmetic intensity
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch09-increasing-cuda-kernel-efficiency-arithmetic-intensity.pdf
- title: Ch10 intra kernel pipelining warp specialization cooperative
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch10-intra-kernel-pipelining-warp-specialization-cooperative.pdf
- title: Ch11 inter kernel pipelining synchronization cuda stream
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch11-inter-kernel-pipelining-synchronization-cuda-stream.pdf
- title: Ch12 dynamic scheduling cuda graphs device initiated
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch12-dynamic-scheduling-cuda-graphs-device-initiated.pdf
- title: Ch13 profiling tuning scaling pytorch
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch13-profiling-tuning-scaling-pytorch.pdf
- title: Ch14 pytorch compiler openai triton xla backends
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch14-pytorch-compiler-openai-triton-xla-backends.pdf
- title: Ch15 multinode inference parallelism decoding routing optimizations
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch15-multinode-inference-parallelism-decoding-routing-optimizations.pdf
- title: Ch16 profiling debugging tuning inference scale
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch16-profiling-debugging-tuning-inference-scale.pdf
- title: Ch17 scaling disaggregated prefill decode inference
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch17-scaling-disaggregated-prefill-decode-inference.pdf
- title: Ch18 advanced prefill decode kv cache tuning
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch18-advanced-prefill-decode-kv-cache-tuning.pdf
- title: Ch19 dynamic adaptive inference engine optimizations
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch19-dynamic-adaptive-inference-engine-optimizations.pdf
- title: Ch20 ai assisted performance optimizations scaling toward
  source: ai-engineering/07-inference-engineering/sources/ai-systems-performance-engineering/ch20-ai-assisted-performance-optimizations-scaling-toward.pdf
- title: Ch09 inference optimization
  source: ai-engineering/07-inference-engineering/sources/huyen-ai-engineering/ch09-inference-optimization.pdf
---
