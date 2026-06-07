---
tags: [adk, chat, context-management, eval, langgraph, tmp]
date: 2026-05-24
time: 1824
duration_min: ~
project: galactus
branch: main
status: in-progress
compacted: true
trigger: auto
total_tokens: 911019
skills_invoked: [chat, tmp, tmp, tmp, tmp, tmp, tmp, tmp]
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-24T1824 (auto)

## Position
- **Work**: [auto-checkpoint before auto compaction — fill in manually]
- **Status**: in-progress
- **Branch**: main
- **Phase**: unknown

## Metadata
- **Compacted**: yes (auto)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=4300 output=906719 cache_read=107049824 cache_write=1899999
- **Total tokens**: 911019
- **Messages**: 1174
- **Skills invoked**: chat, tmp, tmp, tmp, tmp, tmp, tmp, tmp
- **Session ID**: 4f44c71f-d600-43a3-ba59-007fabf270e5

## Recent prompts
-  data/datasets/support-agents/eval_sets/proper_eval_51.jsonl --endpoint http://localhost:8011/chat \
                --agent hc_adk_proper --output data/datasets/support-agents/ablation/hc_adk_proper.json --concurrency 3 --resume
Resuming — 51 already done, 0 remaining === this should run all 500 no
-  why are there two different make commands for lg both should have mq but with a feature flag.. and yes lets add f1_correctness or f1@k to retrieval metrics thanks
- can we just make them all up - these are from hc_right? and like we are loading the bedrock or hc_rag tool calll option and multiquery, can we just run first the noraml every thing up get test the entire 597 queries or should we do everything wth parallel multiquery like va-agents? yeah lets do it t
- why yis rag_v2 not the same as copusv1?
- but the ablation isnt going to run adk and lg at same time right bc of the api call issue

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
