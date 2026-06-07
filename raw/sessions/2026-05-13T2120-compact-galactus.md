---
tags: [adk, context-management, eval, langgraph, resume, tmp]
date: 2026-05-13
time: 2120
duration_min: ~
project: galactus
branch: vir-138-calibrate-llm-as-judge-grader
status: in-progress
compacted: true
trigger: manual
total_tokens: 969263
skills_invoked: [resume, resume, tmp, tmp]
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-13T2120 (manual)

## Position
- **Work**: [auto-checkpoint before manual compaction — fill in manually]
- **Status**: in-progress
- **Branch**: vir-138-calibrate-llm-as-judge-grader
- **Phase**: unknown

## Metadata
- **Compacted**: yes (manual)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=1085 output=968178 cache_read=62826200 cache_write=2679392
- **Total tokens**: 969263
- **Messages**: 771
- **Skills invoked**: resume, resume, tmp, tmp
- **Session ID**: 16dfc618-8099-4951-bcc1-af098757c054

## Recent prompts
-  ok i think there is a mistake eith eval-stats golden bc its taking. along time to generate a report on a slice of data not on the compiled set file:///Users/ramsey.wise/Workspace/galactus/evals/reports/golden/20260513_154108_golden_responses_eval.html let us make a golden set py script that combine
-  btw this is just a slice and not indicative, but i think its showing us a shit ton of miscalibrated ragas scores bc we are lacking shine articles and need to also do a review of our mapping of articles we get from staging/shine and map that to the billy.dk/bkh answers for better grounding evaluatio
-  damn that's a shame.. if we had run our qa set through va-agents locally after signing into aws how we do wih src/support_agents or is it only working when we run our local rag?
- ok so our hc agents that make bedrock call should do this - but hc_rag should use its own internal rag schema.. so are we doing that with our src/ agents?
-  ok interesting can we add that to our claude/docs/plans for migration or hackaton to add to our agents and also we want to add pydantic shemas (if not already there) is that somethign we cna do quickly for saw eval runs? well do that next thanks

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
