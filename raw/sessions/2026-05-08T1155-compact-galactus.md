---
tags: [adk, context-management, eval, langgraph]
date: 2026-05-08
time: 1155
duration_min: ~
project: galactus
branch: vir-158-create-evaluation-pipeline-run-first-eval-test
status: in-progress
compacted: true
trigger: manual
total_tokens: 110850
skills_invoked: []
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-08T1155 (manual)

## Position
- **Work**: [auto-checkpoint before manual compaction — fill in manually]
- **Status**: in-progress
- **Branch**: vir-158-create-evaluation-pipeline-run-first-eval-test
- **Phase**: unknown

## Metadata
- **Compacted**: yes (manual)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=129 output=110721 cache_read=4839627 cache_write=234622
- **Total tokens**: 110850
- **Messages**: 77
- **Skills invoked**: none
- **Session ID**: 2b8066d6-798b-45dd-80eb-c73367f43b16

## Recent prompts
-  something doesnt look right in the nbk for Calibration metrics (liked = positive class):
TP	FN	TN	FP	precision	recall	F1	liked_avg	disliked_avg	delta	aligned
grader											
answer_relevancy	0	17	33	0	nan%	0%	nan%	0.00	0.00	+0.00	✗
completeness	0	17	33	0	nan%	0%	nan%	0.00	0.00	+0.00	✗
grounding	0
-  grounding: score=0.0  reasoning=Grader error: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'This model models/gemini-2.0-flash is no longer availab
is my .env wrong? # GEMINI_MODEL=gemini-2.5-flash-lite
GEMINI_MODEL=gemini-2.0-flash-lite
-  also lets please make md clear in nbk when llm is called before costs are incurred unknowingly please
-  NameError: name '_DEFAULT_MODEL' is not defined
-  my nbk results are still not finding reasoning bc of the model name something isnt right grounding: score=0.0  reasoning=Grader error: 404 NOT_FOUND. {'error': {'code': 404, 'message': 'This model models/gemini-2.0-flash-lite is no longer av

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
