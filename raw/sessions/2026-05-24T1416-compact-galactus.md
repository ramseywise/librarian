---
tags: [adk, context-management, eval, langgraph]
date: 2026-05-24
time: 1416
duration_min: ~
project: galactus
branch: main
status: in-progress
compacted: true
trigger: manual
total_tokens: 112727
skills_invoked: []
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-24T1416 (manual)

## Position
- **Work**: [auto-checkpoint before manual compaction — fill in manually]
- **Status**: in-progress
- **Branch**: main
- **Phase**: unknown

## Metadata
- **Compacted**: yes (manual)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=3000 output=109727 cache_read=16045840 cache_write=305567
- **Total tokens**: 112727
- **Messages**: 188
- **Skills invoked**: none
- **Session ID**: 4f44c71f-d600-43a3-ba59-007fabf270e5

## Recent prompts
-  then why is there only 38 capability test in baseline/eval sets - are the latter just overlapping and 597 is adjusted? can you explain what is the difference between the edge cases, unrated or verify and confirm the regression/capability bits?
-  ok so to be clear - the capability and regression tests are increased (so here there is overlap with rating up and down bsically) is after adjusting for the url? but im still confused - verify should be no overlap but if disliked maybe it's a tp or fp.. while edge cases have no source and could be 
- so the dataset we would us for adk/lg bedrock agents is the golden 597 queries.. can you update that and the make command to test after signing into aws? should we test one to make sure it works and returns source from bedrock? and is the 148 of the regression/cpaability only? or the whole 597? and 
-  make smoke aws
/Users/ramsey.wise/Workspace/galactus/.venv/bin/python3: Error while finding module specification for 'evals.pipelines.va.eval_chat' (ModuleNotFoundError: No module named 'evals.pipelines.va')
- query: Kan det virkelig passe at fordi man laver en fejl i en faktura derfor skal lave 
message: (no response)
sources: []
scores: {'mrr': 0.0, 'p@1': 0.0, 'r@1': 0.0, 'ndcg@1': 0.0, 'p@3': 0.0, 'r@3': 0.0, 'ndcg@3': 0.0, 'p@5': 0.0, 'r@5': 0.0, 'ndcg@5': 0.0}

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
