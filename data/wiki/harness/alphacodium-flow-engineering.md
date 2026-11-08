---
title: AlphaCodium Flow Engineering
tags: [harness, pattern]
summary: A multi-stage code-generation flow for competitive programming that iterates on public tests, then on model-written tests guarded by test anchors; raised GPT-4 pass@5 on CodeContests validation from 19% to 44%.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-ridnik-2024-code-generation-alphacodium.md
---

# AlphaCodium Flow Engineering

AlphaCodium (Ridnik et al., CodiumAI, January 2024) replaces a single prompt with a test-based iterative flow on CodeContests. Its design observation is that producing additional useful tests is a simpler job than producing a correct solution.

## The flow

Stages: reflect on the problem, reason about public tests, propose 2 or 3 solutions and rank them, generate 6 to 8 extra tests aimed at cases the public tests miss, write initial code (retrying until tests pass or a try limit is hit, then keeping whichever code came closest on output), then iterate against the public tests, then iterate on the model-written tests. Public tests can be trusted as correct yet cover little, so iterating on only those leaves blind spots.

**Test anchors** guard against wrong model-written tests. Passing public tests become anchors. Model-written tests are tried easiest first; a passing one joins the anchors, and a failing one is treated as a sign the code is wrong, with the fix required to pass every anchor so far. **Double validation** asks the model to regenerate its own tests and correct wrong outputs, which the authors say works better than a yes-or-no check (no number is given). Other practices, qualitative only: YAML structured output, bullet-point reasoning, small sub-functions, and ranking several solutions rather than choosing early.

## Results (self-reported)

- GPT-4, CodeContests validation (107 problems), pass@5: 19% with a single direct prompt, 44% with the flow. On the test set (165 problems): 12% to 29%. DeepSeek-33B: validation 7 to 20, test 12 to 24. GPT-3.5: validation 15 to 25, test 8 to 17.
- Against CodeChain with GPT-3.5, pass@5: 25% against 17% on validation, 17% against 14% on test.
- Against AlphaCode, whose figures are taken from its paper: GPT-4 validation 44% against 17% or 24% (two sampling budgets), test 29% against 16% or 28%.
- Budget: about 15 to 20 LLM calls per solution and about 100 for pass@5, against an assumed one million calls for AlphaCode's largest setting.

## Limits

- CodeContests only; generality is a belief, not shown. pass@5 only, with no variance and no dollar cost; a 107-problem set makes each point about 1%.
- No component ablation: the only comparison is a direct prompt against the full flow, so the gain from the anchors or the extra tests is not isolated.
- AlphaCode and CodeChain numbers come from their papers; the AlphaCode call count is an assumption; the test-set margin over AlphaCode's larger budget is 29% against 28%. The authors ran the direct-prompt baseline themselves.
- Models are 2024 versions; contamination of CodeContests is not discussed; the authors work for a commercial vendor.

## See Also

- [[Verification Loops]] — prerequisite-for
- [[Three-Layer Termination Check]] — related
- [[TestGen-LLM Filter Cascade]] — related
