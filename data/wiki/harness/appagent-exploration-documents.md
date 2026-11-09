---
title: AppAgent Exploration Documents
tags: [harness, pattern]
summary: "AppAgent lets a GPT-4 agent operate smartphone apps without training by giving it a per-element document written either through its own trial-and-error exploration or by watching a human; the paper reports success rising from 2.2% to 95.6% across configurations (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-zhang-2023-appagent.md
---

# AppAgent Exploration Documents

AppAgent (a December 2023 preprint from a Tencent team) is a multimodal agent that drives Android apps with a simplified action space and a two-phase loop. It changes no model parameters and collects no per-app training set. The extraction treats it as a preprint with no stated venue.

## Mechanism

- **Observation.** Each step the agent gets a screenshot with a numeric ID overlaid on every interactive element, plus an XML file of those elements. It is therefore not a pure-screenshot design.
- **Action space.** Tap, Long_press, Swipe (element, direction, distance), Text, Back and Exit. The paper counts four basic functions in its text but lists six. Multi-touch and irregular gestures are unsupported (the authors' stated limitation).
- **Exploration phase.** In autonomous mode the agent tries actions, compares the before and after screenshots, and writes or updates a document for each element it touched; it leaves irrelevant pages such as ads. In demonstration mode a person uses the app and the agent records just the elements and actions that person touched.
- **Deployment phase.** Each step runs observe, think, act, then summarises history into the next prompt; the documents for visible elements are added to the context.

## Results (self-reported)

All rows: GPT-4, 45 tasks on 9 apps (Lightroom excluded from scoring), success means finishing within 10 steps, exploration capped at 40 steps, single run.

| Configuration | Success rate | Reward | Avg steps |
|---|---|---|---|
| Raw action space, no document | 2.2% | 0.6 | 4.0 |
| Simplified action space, no document | 48.9% | 3.5 | 6.9 |
| Autonomous exploration document | 73.3% | 5.1 | 4.4 |
| Watching-demonstration document | 84.4% | 4.7 | 5.1 |
| Manually written document | 95.6% | 5.5 | 5.5 |

The authors explain the gain from the action space by the model's difficulty producing accurate coordinates. They call the auto and demo documents comparable to the manual one, though the table shows gaps of 22.3 and 11.2 points. Reward is a hand-scored partial-credit value with no stated scale, and average steps are counted over finished tasks only.

In a Lightroom image-editing study on 5 images (rater count not stated), average rank was 2.30 for the baseline, 1.95 with demonstration documents and 1.75 with manual documents (lower is better).

## Limits

- The extraction notes the headline says 50 tasks on 10 apps, while the scored table covers 45 tasks on 9 apps.
- One model, no repeats, no variance, a team-built benchmark and no comparison with other GUI agents.
- The oracle and demonstration documents were written by the authors, so they are not independent baselines.
- No failure analysis, cost or latency figures, and no discussion of irreversible actions despite a security claim.
- Popular apps may already be familiar to GPT-4; generalisation to unseen apps is claimed but not tested.
- Table 1 and 2 extraction is jumbled; row pairing was inferred.

## See Also

- [[Computer Use Visual Grounding]] — prerequisite-for
- [[Agent S Hierarchical GUI Agent]] — related (also learns per-app knowledge by retrieval rather than training)
- [[SeeAct Grounding Strategies]] — related (contemporary grounding comparison on the web)
- [[ReAct Pattern]] — prerequisite-for
