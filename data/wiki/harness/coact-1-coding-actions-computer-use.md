---
title: CoAct-1 Coding Actions for Computer Use
tags: [harness, pattern]
summary: A computer-use multi-agent system whose Orchestrator delegates each subtask to a GUI Operator or a Programmer that writes Python and Bash, so code becomes an action beside clicks.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-song-2025-coact-1.md
---

# CoAct-1 Coding Actions for Computer Use

CoAct-1 (Song et al., USC and Salesforce AI Research, ICLR 2026 per the PDF header) argues that GUI-only computer-use agents are brittle and slow. An Orchestrator sends each subtask to a GUI Operator or to a Programmer. The authors attribute the gain to the wider action space, not to a new topology. Numbers are the authors' own.

## Mechanism

- **Roles and setup:** The system is built on AG2, with o3 as Orchestrator, o4-mini as Programmer, OpenAI computer-use-preview as GUI Operator and o4-mini as summariser. Each role has a cap: 20 rounds for the Programmer, 25 steps for the GUI Operator and 15 rounds for the Orchestrator.
- **Isolated memory:** executors do not share histories, and an executor's working memory is cleared once it reports back. A summariser condenses its history into a short summary, returned with the final screenshot.
- **Independent check:** the paper says the GUI Operator hallucinates often when self-checking, so the Orchestrator verifies on its own.

## Reported numbers (self-reported)

Setup: OSWorld (369 tasks) and WindowsAgentArena (154) scored by each benchmark's rule-based evaluators. The paper reports no run count, seeds, variance or cost.

- OSWorld 60.76% at 150 steps and 59.93% at 100, against Agent S2.5 w/ o3 55.98% and GTA-1 w/ o3 53.07% at 100 steps. With a 15-step budget it gets 39.81%, which is under the 42.37% of Jedi-7B w/ o3.
- WindowsAgentArena: the step budget matters, with 52.5% at a 100-step budget, then 43.5% at 50 and only 21.4% at 15, against 29.8% for Agent S2.
- Role ablation, with the CUA 4o GUI Operator in each row: o4-mini plus o4-mini 43.43, o3 plus o3 58.72, o3 plus o4-mini 60.76.
- Modality ablation: Programmer only 35.73%, GUI Operator only 50.68%, both 60.76%.

## Limits

- The ablations compare action modalities, not topologies, so they do not show the Orchestrator and executor split helps. Isolated memory and the summariser are never ablated.
- Each of the last two role rows is one run, and they differ by only 2 points.
- Average steps are steps per success, so Programmer-only (1.14) is not comparable, since it solves only easy tasks.
- Only OpenAI models; no cost or latency figure; summariser fidelity unmeasured.
- Authors list four failure types: intent inference, ambiguous queries, reflection errors (only the final state returns, hiding intermediate GUI mistakes) and hallucination. The prompt-based mitigation is not measured.
- Model names and the leaderboard position have dated.

## See Also
- [[Tool Design as Harness Surface]] — related (code as an action)
- [[Harness Orchestration]] — related
- [[Verification Loops]] — related (independent re-check of executor claims)
- [[OS-Copilot FRIDAY Tool Repository]] — related
