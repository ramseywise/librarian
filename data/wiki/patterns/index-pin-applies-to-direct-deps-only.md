---
title: Index Pin Applies Only to Direct Dependencies
tags: [patterns, infra, pattern]
summary: "uv's [tool.uv.sources] index pin (e.g. torch → the CPU-only PyTorch index) is honoured only for packages the project lists directly; when torch arrives transitively (via sentence-transformers) the pin is silently ignored and Linux/Docker builds pull ~6 GB of CUDA wheels — so the pinned package must stay listed, even if no code imports it directly."
updated: 2026-10-30
sources:
  - data/raw/repos/listen-wiseer/CLAUDE.md
---

# Index Pin Applies Only to Direct Dependencies

Recorded as an active gotcha in listen-wiseer.

## Mechanism

The project wants the CPU-only build of torch, so `pyproject.toml` maps `torch` to the
`pytorch-cpu` index under `[tool.uv.sources]`. torch is needed only by
`sentence-transformers`, inside an optional `embeddings` extra. uv applies
`[tool.uv.sources]` entries **only to direct dependencies**. If torch is not listed in the
extra itself, it is resolved as a transitive dependency of `sentence-transformers`, and
the source pin does not apply. On macOS this changes nothing visible. On Linux and in
Docker the default index serves the CUDA build, about 6 GB of wheels.

So `torch` stays listed in the `embeddings` extra even though no project code imports it.
To anyone tidying dependencies it looks redundant; removing it reverts the pin silently.
The build still succeeds, only much larger.

## Related trade-off

Without the extra installed there is no torch at all, and the agent's memory search
falls back to unranked results. The extra is optional on purpose; the pin is what keeps
installing it affordable in containers.

## See Also
- [[Native Library Load-Order Collision]] (the same torch dependency's other trap in this repo)
- [[Listen-Wiseer Project]]
