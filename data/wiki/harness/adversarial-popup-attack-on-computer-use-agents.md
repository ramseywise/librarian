---
title: Adversarial Pop-up Attack on Computer-Use Agents
tags: [harness, pattern]
summary: "An injected pop-up built from an attention hook, an instruction, an info banner and an ALT descriptor drew clicks from every tested vision-language agent in the paper's OSWorld and VisualWebArena setups, and prompt-only defences helped little (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2024-attacking-vision-language-computer-agents.md
---

# Adversarial Pop-up Attack on Computer-Use Agents

Computer-use agents act on screenshots or accessibility trees, so content injected into the screen can steer clicks. The paper builds an adversarial pop-up with four parts: an **attention hook** (text tuned to the agent's task, such as a button name derived from the user query), an **instruction** telling the agent where to click (default form: click at coordinates), an **info banner**, and an **ALT descriptor** that puts the pop-up into the accessibility text that set-of-mark agents read. Attack success rate (ASR) counts steps where the agent clicks the pop-up; the click is ignored in execution.

## Results

All numbers are the paper's own (self-reported). Setup: 50 easy OSWorld tasks (15-step limit) and 72 easy VisualWebArena tasks (30 steps), temperature 0, five models (GPT-4-Turbo and GPT-4o, Gemini 1.5 Pro and two versions of Claude 3.5 Sonnet), default attacker with full information.

- Average step-level ASR of 86% and a 47% drop in task success. Pop-up clicks made up 92.7% of attacked agents' actions in OSWorld and 73.1% in VisualWebArena.
- Every model had ASR above 60% in every scenario; the lowest table cell was GPT-4o on VisualWebArena with set-of-mark at 62.1.
- Replacing the user query in the hook with a speculated one gave 33.3% average ASR (GPT-4-Turbo on OSWorld, GPT-4o on VisualWebArena); the extraction marks the table row as unverified.
- A "VIRUS DETECTED" hook worked on screenshot agents (90.0 ASR) but not on set-of-mark agents (58.3 and 1.1); the authors guess text-based safety training stops the latter. A blank pop-up gave 2.4, 3.7 and 0.0.
- Emptying the ALT text cut ASR by 23.7 and 19.2 points for set-of-mark agents.
- Defences, prompt-only: an "ignore the pop-ups" system prompt gave almost no mitigation (generic prompt ASR 95.9, 93.4 and 60.3 against defaults of 93.3, 91.8 and 62.1); a more specific prompt gave a roughly 25% relative drop by the paper's count. Repeating the warning at every step (GPT-4-Turbo screenshot agent, OSWorld only) brought ASR to 5.9 but task success only to 8.0, and a small wording variant raised ASR to 10.4.
- Delaying the attack until after step 7 left ASR at 80.4% (screenshot) and 88.1% (set-of-mark), on GPT-4-Turbo in OSWorld.
- Among 50 hand-annotated successful OSWorld reasoning traces for each agent type, screenshot agents mentioned the fake "OK" button 52% of the time and set-of-mark agents mentioned the hook 62%; some successes never mention the pop-up, so a thought monitor would miss them.

## Limits

- Only closed-source models, with no optimised pop-up strings or persuasion; tasks are small, easy and, in OSWorld, chosen because they succeeded without attack.
- ASR counts clicks; real harm such as redirects is not measured.
- The default attacker has full information, and weaker attackers appear only as ablations.
- Models are from 2024; later models are untested. The defences tested were prompt-only; the authors name content filtering, detection modules and agent training as untested.
- Several tables were scrambled in extraction; the extraction advises verifying against the PDF before citing the step-wise defence figures or the rows labelled Speculated Query and Blank.

## See Also
- [[Prompt Injection]] — prerequisite-for
- [[Computer Use Visual Grounding]] — related (the screenshot and accessibility-tree observation paths attacked here)
- [[Lethal Triad]] — related
- [[Execution Boundaries and Guardrails]] — related
