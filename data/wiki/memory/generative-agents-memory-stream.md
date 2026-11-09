---
title: Generative Agents Memory Stream
tags: [memory, pattern]
summary: "Generative agents keep a natural-language memory stream, retrieve from it by recency, importance and relevance, and add reflection and planning; in a 25-agent sandbox, raters ranked the full architecture above its ablations, with a single short run and a high token cost."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-park-2023-generative-agents.md
  - data/raw/papers/2026-11-08-park-2022-social-simulacra.md
---

# Generative Agents Memory Stream

Park et al. (UIST 2023) ask how an LLM agent architecture can give believable individual and emergent social behaviour over long horizons. The memory stream is a store of records, each holding a plain-language description plus two timestamps, one for when it was created and one for when it was last accessed. It holds observations, reflections and plans. Retrieval ranks records by adding up recency, importance and relevance scores, each with an alpha weight that the study did not vary, and the top records go to gpt3.5-turbo, which also writes reflections, daily plans, reactions and dialogue. A reflection is a higher-level, more abstract thought the agent generates, stores as a memory and includes in later retrieval.

## Results

All figures are self-reported and come from one simulation: 25 agents in a Phaser-based sandbox called Smallville for two game days.

- Believability was ranked by 100 Prolific raters across five conditions at the end of the simulation. The full architecture ranked first, then the variant without reflection, then observations only; crowdworker-written responses ranked below three of the architectures, and the fully ablated condition (no memory, planning or reflection) was last. Overall rank differences are significant; all pairwise Dunn differences are below p=0.001 except crowdworker versus fully ablated. The effect size of full over fully ablated is given as a TrueSkill-based figure. The crowdworker baseline (one worker per agent, role-playing after a replay) is not maximal human performance.
- Without user intervention, awareness of one agent's candidacy rose from a single agent to 8 of the 25, and awareness of a party rose from a single agent to 13. Just five of the twelve agents invited came to the party; among the seven who stayed away, three named scheduling conflicts and four said they were keen but never planned to attend.
- With the trigger threshold set to 150, agents reflected about two to three times per day.
- For 25 agents over two game days, the authors describe the expense only loosely, as several days of runtime and thousands of dollars of credits, with no exact number.

## Social Simulacra, the stateless precursor

Park et al. (UIST 2022) use GPT-3 prompt chains for a different job: populating a draft community design so a designer can see problems before launch. The SimReddit tool expands about 10 seed personas into 1,000, then generates posts and replies with base davinci. In a test on 50 unseen subreddits, participants misjudged the generated conversation as real in 41% of pairs (self-reported; chance is 50%); dropping the community description lowered that to 21%, and dropping personas to about 33-34% (the text and Table 1 differ). In a study of 16 designers, all found unexpected insights and all but one revised their design. These prompts are single-turn persona prompts with no memory, planning or tools.

## Limits

- One short run (two game days), one simulation, no repeated runs. Ablations were given the full architecture's accrued memories rather than re-simulated; the authors say this likely underestimates the differences.
- Typical errors included retrieval misses, memories with invented detail, and stiff formal speech that traces to instruction tuning; as agents learned more places, they also picked unusual locations.
- Robustness to prompt hacking, memory hacking and hallucination is untested. Built on gpt3.5-turbo; temperature and decoding are not stated.
- Social Simulacra: it does not predict outcomes (the authors say single-point prediction is impossible), the test checks only real-versus-generated plausibility on first-five-response threads, there is no post-launch outcome measure, and it is text-only, English-only and Reddit-only. Base davinci lacks knowledge after mid-2020.

## See Also
- [[Agent Memory Types]] — prerequisite-for
- [[Memory Decay Weighting]] — related (recency scoring in retrieval)
- [[Reflexion]] — related (stored self-reflections)
- [[MemoryBank Long-Term Memory]] — related (another store-retrieve-update memory design)
- [[Simulated User Evaluation]] — related
