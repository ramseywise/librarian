---
title: DERA Dialog-Enabled Resolving Agents
tags: [prompting, agents, multi-agent, concept]
summary: "DERA has two GPT-4 prompts, a Researcher that points out problems and a Decider with final authority, converse over a draft and write accepted fixes to a shared scratchpad; on clinical summaries and care plans physicians preferred the result, while multiple-choice and open-ended medical QA showed little or no gain (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-nair-2023-dera.md
---

# DERA Dialog-Enabled Resolving Agents

DERA is a refinement loop built from two role-scoped prompts to the same model. The **Decider** drafts an output, answers the Researcher and has final authority; it never has to defer. The **Researcher** reviews the information and flags what looks crucial or wrong, and is not treated as the source of truth. For each point the Decider accepts or rejects, accepted corrections go to a shared **scratchpad**, and a last prompt rewrites the output from the draft plus the scratchpad instead of regenerating each turn. For question answering the Decider starts from the spread of votes produced by self-consistency, the Researcher only points to parts of the question, and the run ends in a five-sample vote. The authors contrast it with chain-of-thought, which does the researcher and decider roles jointly, and with chaining, which splits the task into sub-tasks where DERA refines the whole output iteratively.

## Reported results

All self-reported; all agents are GPT-4.

- **Summaries and care plans.** In a study with 50 telehealth encounters and 4 physicians, physicians preferred the DERA-corrected summary and care plan to the first GPT-4 output, and rated the DERA versions as capturing all clinical information or all necessary steps more often. Harmful content in summaries fell from 2% to 0%, which the authors caution against generalising. In 63% of summarization encounters the physicians accepted every suggestion on the scratchpad.
- **Synthetic corruption.** With GPT-4 summaries as ground truth and corruption at 3, 5 and 7 out of 10 (500 encounters), the GPT-judged F1 of the DERA output is stated to rise above the corrupted starting point only at corruption 7/10; the extraction gives no direction at 5/10 and 3/10.
- **Multiple-choice MedQA** (4-option test, single run): DERA barely beat zero-shot GPT-4, and both beat the PaLM and prior GPT-4 numbers cited.
- **Open-ended MedQA** (1,273 test questions, single run): exact match 0.703 for GPT-4 against 0.698 for DERA, so DERA matched one-shot GPT-4; BERTScore was slightly lower for DERA and the similarity score showed its largest gain. Only 542 of the 1,273 answers were identical between DERA and the one-shot run.

## Limits

- QA shows little or no gain over the self-consistency baseline; the authors attribute this to QA needing a single granular answer.
- QA ran once because of cost, with no significance tests. GPT-4 grades itself on several metrics, which the authors flag; the corrupted inputs are synthetic and were produced by GPT-4. The human studies cover 50 encounters, 4 physicians and one telehealth population.
- Possible MedQA contamination, unpersisted GPT-4 snapshots, and unreleased NEJM and telehealth data.
- The extraction notes that role ablations (one agent versus two, no scratchpad, number of turns) are not reported, so the Researcher's effect cannot be told apart from the benefit of a second revision pass.

## See Also
- [[Self-Refine]] — alternative-to (single-agent refinement loop)
- [[Reflexion]] — related
- [[REFINER Critic Feedback on Reasoning Steps]] — related
- [[Multi-Agent Role Specialization]] — related
- [[Prompt Chaining]] — alternative-to
