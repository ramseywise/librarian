---
tags: [adk, context-management, eval, langgraph]
date: 2026-05-11
time: 1120
duration_min: ~
project: galactus
branch: main
status: in-progress
compacted: true
trigger: manual
total_tokens: 85893
skills_invoked: []
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-11T1120 (manual)

## Position
- **Work**: [auto-checkpoint before manual compaction — fill in manually]
- **Status**: in-progress
- **Branch**: main
- **Phase**: unknown

## Metadata
- **Compacted**: yes (manual)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=146 output=85747 cache_read=7216493 cache_write=298301
- **Total tokens**: 85893
- **Messages**: 84
- **Skills invoked**: none
- **Session ID**: 66c91c41-4eb3-4265-9a15-ea0a5c86f537

## Recent prompts
- btw are any of these other metrics useful for us that we might want to add later? or should we add now? i think the rag pipeline agents and chatbots could be interesting down the road but how costly is that or should we customize something similar for these?
- ok lets add hallucination, answer relevance and faithfulness to our grounding category - and should we make this more explicit to have apples to apples scenario? all of the ragas stuff we will bring into play with hc_rag so still important (see evals/grader/ragas), but do we use ragas, deepeval or c
-  ok that sounds good ..  let's do that, but for this nbk what aare we testing and how many llms
-  ok va-compare is really llm-callibrate - and it should be 2 llm calls (1 for combined custom graders, 1 to deepeval combined graders) - is that what you are seeing? we can drop epa for now its fine, leave out epa, friction and intent for now
- yes but we want 1 llm for our 3 custom and 1 lm for deepeval 3 metrics to callibrate, understood?

## Gotchas
[Fill in after resuming — non-obvious traps found before compaction]

## Friction signals
- [ ] [Fill in]

## Context to restore
[Critical: fill this in before compacting — what a cold agent needs to resume]
- No custom note provided

## Open questions

## Skill candidates

## Session insights

## Next session prompt
[Fill in: where we are, first action, key gotchas]
