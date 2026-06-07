---
tags: [adk, context-management, eval, langgraph]
date: 2026-05-13
time: 2128
duration_min: ~
project: galactus
branch: vir-138-calibrate-llm-as-judge-grader
status: in-progress
compacted: true
trigger: manual
total_tokens: 81918
skills_invoked: []
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-13T2128 (manual)

## Position
- **Work**: [auto-checkpoint before manual compaction — fill in manually]
- **Status**: in-progress
- **Branch**: vir-138-calibrate-llm-as-judge-grader
- **Phase**: unknown

## Metadata
- **Compacted**: yes (manual)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=144 output=81774 cache_read=7480254 cache_write=445219
- **Total tokens**: 81918
- **Messages**: 108
- **Skills invoked**: none
- **Session ID**: de9aa2f3-292e-446b-a773-e90b926c05fc

## Recent prompts
-  ok looks good.. dont we want to also show the repo structure for core and evals just at a high level in the tree digram?
-  i had to not save but shit we i also want us to fix clarity one data sources their vaule and limitations thanks 
## Data Sources
### Raw Articles (billy/Intercom)
### Intercom Conversational Data (shine migration, benchmark, v1 bedrockKB)
### BookKeeper Hero (Baseline, V1 bedrockKB)

### Golden Eva
-  can we update data sources like this ces

### Raw Articles (Billy / Intercom)

Help center articles fetched from Intercom (Billy corpus). Source of truth for the knowledge base — ingested by `core/articles/billy/`, vectorised into `data/datastores/knowledge.duckdb` for local testing vs Bedrock Know
- ok but for limitation of intercom articles and conversational data is that there is a transition for v1 billy to v2 shine and no human in the loop to validate or comfirm sources for grounding.. and also for using intercom historical data where references are billy not shine. also intercom coversatio
-  also it tells about core in the readme but nothing about evals (we can add to agent pocs later after ablation test but for sure we are very proud of our eval pipeline as much as our data ingestion and agentic pipelines

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
