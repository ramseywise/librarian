---
tags: [adk, chat, context-management, eval, langgraph, tmp]
date: 2026-05-24
time: 2142
duration_min: ~
project: galactus
branch: main
status: in-progress
compacted: true
trigger: manual
total_tokens: 1503958
skills_invoked: [chat, tmp, tmp, tmp, tmp, tmp, tmp, tmp]
skill_candidates: 0
friction_count: 0
work_type: ~
output_type: ~
key_output: ~
---

# Session checkpoint — 2026-05-24T2142 (manual)

## Position
- **Work**: [auto-checkpoint before manual compaction — fill in manually]
- **Status**: in-progress
- **Branch**: main
- **Phase**: unknown

## Metadata
- **Compacted**: yes (manual)
- **Key tools**: [fill in]
- **Files touched**: [fill in]
- **Token hotspots**: input=5944 output=1498014 cache_read=164967377 cache_write=3084574
- **Total tokens**: 1503958
- **Messages**: 1814
- **Skills invoked**: chat, tmp, tmp, tmp, tmp, tmp, tmp, tmp
- **Session ID**: 4f44c71f-d600-43a3-ba59-007fabf270e5

## Recent prompts
-  why is this last reranker taking so long? been almost 30 min
-  BEST_CHUNKER   = 'html_aware_512'  (embedded chunker — swap RETRIEVAL_CHUNKER to compare others)
BEST_RETRIEVAL = 'rrf_k20'  MRR=0.3289
BEST_RERANKER  = 'mmarco-multi'  MRR=0.3457 so suprised html is better than parnet child and this is basically bedrock hierarchical equiv right? rrf makes sense al
- but also this still is pretty awful - how does bkh and va compare? metrics? is this already adjusted for kb map?
- wait we didnt test hierichal/parentdocchunker ok we want that html aware is not enough can we please add this to the rag nbk and colbertbut like please don t rerun what we already have just add to the end to compare our best so far - and also it would be interesting to see if some of these perform b
-  running it now.. in the rag system though can we rename parent doc chunker to hiearchal please and also i think the html aware is gettnig biased by the dataset issue but lets see what the results say

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
