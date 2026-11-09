---
title: Progressive Disclosure and Skill Packs at Library Scale
tags: [context, concept]
summary: He et al. (2026) turn long books into skill packs an agent harness reads on demand; a flat pack (one SKILL.md with a chunk index) usually beat raw text, a hierarchical pack and hybrid RAG, but gains depend on task, language and harness (self-reported).
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-he-2026-progressive-disclosure-all-you-need.md
  - data/raw/papers/2026-11-06-yin-2026-skills.md
  - data/raw/papers/2026-11-06-zhao-2026-generative-skill-composition-llm-agents.md
---

# Progressive Disclosure and Skill Packs at Library Scale

The paper (LOONGDOC; arXiv 2607.17598) turns the long-document tasks of a public long-context suite into an agent environment on BenchFlow and ACP. It uses three harnesses (Codex, Pi, Claude-Code) and three models (claude-haiku-4.5, gpt-5.4-mini and qwen3.6-27b).

## Approaches compared

- **Raw:** the full text on disk.
- **Flat:** one SKILL.md holding a chunk index, with the chunks under references/.
- **Hierarchical:** a skill per chunk plus a meta-router.
- **Hybrid-rag:** BM25 and BGE-M3 with RRF and a reranker (Pi only).

## Results (self-reported, mean of three seeds)

- Single book, Pi harness, gpt-5.4-mini, En.MC: flat scored 0.9126 against 0.6398 for hierarchical, 0.8851 for raw and 0.7628 for hybrid-rag. Pi with qwen on Zh.QA: flat 0.7479 against hierarchical 0.3890. Codex results tie within error. Claude-Code with haiku on En.MC: flat 0.8667 against raw 0.7448 (plus or minus 0.1166).
- Library scale, Codex with gpt-5.4-mini, En.QA, 20 books: raw 0.257, flat 0.462, hierarchical 0.267. Raw Zh.QA falls to 0.043.
- Cost: raw 68.3M tokens (about $52 as an uncached upper bound) against 32.5M ($25) for flat.
- Pi with qwen3.6-27b: hybrid-rag scored 0.5439 on En.QA and 0.5856 on Zh.QA, below raw (0.6813, 0.7563).

## Related proposal: the @skills preprint

A separate August 2026 preprint by Li Yin and colleagues (arXiv 2608.12610) argues from the same budget framing: a skill install packages content, persistence and auto-triggering together, yet only the auto-triggering has to occupy the prompt. Its stated principle is that resident context is a budget, to be spent on what must fire implicitly, with everything else delivered at the point of use. It proposes three tiers: referenced skills (zero resident tokens, called explicitly), saved skills (kept in the repository, also zero resident tokens) and installed skills (frontmatter resident, fewer than ten recommended).

The extraction describes it as design and advocacy rather than empirical work. Figures it gives, with their basis:

- 56,804 skill directories in 1,133 public repositories from a July 2026 crawl (self-reported), an upper bound because duplicates are only partly removed.
- The suggested ceiling of under 100 dependable auto-trigger slots per agent is extrapolated from other papers rather than measured, and the authors state that no controlled measurement exists. Do not cite it as a result.
- 50 to 280 tokens of resident description per skill come from one working setup (self-reported). Category shares were estimated from a sample of 100 skills, carrying roughly plus or minus 10 points (self-reported).
- The author founded the company that sells the agent and hub the paper promotes, and the protocol is implemented only there. A fetched skill is remote text that the agent obeys, and the authors depend on provenance and review instead of filtering.

## Learned Skill-Set Composition

SkillComposer, a 2026 proposal, treats skill selection as one decision covering the skills, their number and their order. A small decoder (about 3.9M trainable parameters) sits on a frozen embedder and outputs skill IDs in order, then STOP, drawn from a fixed library of 196 skills. On SkillsBench (75 of 88 tasks, two agents, three attempts, temperature 0), pass rates for the two agents were 45.3 and 44.0 against 44.0 and 41.8 for top-3 retrieval, 22.2 and 25.8 with no skills, 29.3 and 38.7 with all skills, and 51.1 and 48.4 with gold skills (self-reported). Input tokens for the first agent were 1.03M against 1.09M for top-3 retrieval and 1.27M for all skills. On a 65-task real holdout, trained on synthetic data only, set F1 was 62.9 against 60.6 for best-k TF-IDF, while oracle-k TF-IDF scored 74.2.

Limits: synthetic training data, small margins over retrieval, and the extraction notes that the weighting values are inconsistent across sections.

## Limits

- The @skills paper never tests how trigger reliability varies with the number of installed skills, nor how compliance varies with where text is injected; the extraction flags its token measurements and corpus numbers as single-setup and single-crawl.
- The En.MC books are probably memorised, K takes only the values 1, 5, 10 and 20, and only narrative books appear. Gains are specific to a task and a language, and many gaps lie within one standard error.
- Appendix C.1 contradicts the main-text pattern: on the Pi harness at library scale, hierarchical is the best pack at K=20 (0.330) and flat falls under raw on Zh.QA.

## See Also
- [[Context Retrieval Strategies]] — prerequisite-for
- [[Coding Agents as Long-Context Processors]] — related
- [[Context Window Budgeting]] — related
- [[Codified Context Three-Tier Infrastructure]] — related
- [[HeavySkill Heavy Thinking Skill File]] — related
