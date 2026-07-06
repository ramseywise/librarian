---
title: Session Log
tags: [context-management, llm, project]
summary: Chronological index of all Claude Code and Codex sessions captured in raw/sessions/ — what was worked on, which project, and approximate token spend.
updated: 2026-07-06
sources:
  - raw/sessions/
---

# Session Log

Operational activity log compiled from `raw/sessions/`. Each row is one session. First-prompt summary indicates the primary intent; token counts are from session frontmatter.

---

## Codex Sessions — 2025-09

All on the `txmatch` project, `ramsey-feature-dev` branch (Shine — document-for-transaction validation and scoring system).

| Date | Session | Prompts | Topic |
|------|---------|---------|-------|
| 2025-09-14 | 4998c107 | 54 | Transaction autoassignment notebook, scoring system |
| 2025-09-14 | 8713027f | 3 | Document-for-transaction validation |
| 2025-09-14 | a2b0ddde | 30 | `_build_ground_truth_sets`, validation scoring |
| 2025-09-14 | ef78d2bb | 24 | Validation + transaction matching |
| 2025-09-15 | 76cb019f | 4 | Validation tabs, transaction match vectorised |
| 2025-09-16 | 58516737 | 21 | Validation refactor |
| 2025-09-16 | dabddaa4 | 20 | Scoring system finalisation |

---

## Claude Code Sessions — April 2026

### 2026-04-10 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 1900854e | 3 | 139k | Librarian folder restructure — `analyzer/` belongs in ingestion or eval; research how to reorganise `librarian/` |

### 2026-04-11 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| deb81c96 | 8 | 170k | Core module extraction — fix circular dep between `storage` and `librarian`; shared types in `core/` |
| 394ba556 | 24 | 310k | Refactor + rename `insights` skill → `claude-insights`; two analysis modes (JSONL + local artifacts) |
| 356746ec | 11 | 104k | Librarian chat as frontend; triage routing (Next.js vs LLM for binary 0/1 routing) |
| fe1c0bd1 | 8 | 100k | src/ package restructure: core + librarian + storage + orchestration + interfaces + eval; Fargate over Lambda |
| f5cfe1b3 | 5 | 67k | `infra/` under `src/` not `librarian/`; rag_core sub-organisation; listen-wiseer vs playground infra comparison |

### 2026-04-12 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 406fcc7f | 3 | 77k | Google ADK vs LangGraph orchestration comparison; ADK + Python LangGraph hybrid; LangFuse compatibility confirmed |
| 8d1a71b0 | 5 | 51k | RAG tradeoffs: BookKeeper Hero vs Bedrock KB vs Librarian; engineering risk matrix (integration/cost/latency/hallucination) |

### 2026-04-14 (Workspace — heavy day: 8 sessions)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 53ef9ef6 | 3 | 80k | LangGraph-ADK compatibility; rebuild as Python LangGraph copilot |
| a419a1f1 | 3 | 58k | Research ts-copilot-upgrades tradeoffs; update plan |
| dd36bdeb | 1 | 162k | Execute terraform-restructure → unblocks GitHub CI/CD |
| 4a5c5ba3 | 3 | 93k | Python copilot: ts_google_adk parity + copilot upgrades research |
| 48cd8a0e | 4 | 41k | Librarian as RAG-only service; bring to engineering standard |
| a6a9bcf4 | 8 | 125k | `.claude/docs` restructuring — research→plan chains, archive lifecycle |
| ec44fece | 5 | 21k | Ruff linter misconfigured for TS in polyglot repo; disable for ts folder |
| 3def7093 | 2 | 78k | `playground/src/clients` vs `interfaces` cleanup; LangGraph-ADK compat plan |
| 42826f2b | 1 | 65k | Priority order: infra-interfaces → orchestration-rollout → terraform → langgraph-adk-compat |

### 2026-04-15 (poc project — Help Support RAG Agent)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 578a75d8 | 3 | 120k | `.gitignore` audit |
| b269ccf1 | 4 | 50k | rag-poc vs playground/librarian comparison; LangGraph copilot best practices |
| 17811ed1 | 7 | 47k | Switch LLM to Anthropic API; RAG components reuse |
| eeebbd1e | 7 | 110k | Unit tests for `app`; code review; translation support (FR/DE/DA) |
| b669eebb | 6 | 231k | `app/agent_nodes/retriever` → `rag/`; orchestration domain reorg |
| 7c4e1442 | 4 | 6k | `Literal["q&a", "task_execution"] = None` typing fix |
| c2109cb9 | 3 | 79k | Code quality pass; changelog write; commit grouping |
| 92643c18 | 1 | 1k | Find `.env` with Anthropic API key |

### 2026-04-16 (poc project)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 314ac54a | 12 | 168k | Multi-query feature flag; LangSmith trace routing; English→German smoke test failure |
| 06b9a503 | 3 | 92k | Intensive code review — simplify and condense 19 files |
| efd3b13a | 5 | 89k | Demo data placement; LangGraph node simplification |
| ca037b9e | 1 | 65k | Eval cleanup and simplification |

### 2026-04-17 (Workspace + poc)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 7a25dbd0 | 11 | 134k | ADK samples scan — context engineering (.agent/.claude/.agents), native_skill_mcp vs rag_poc Strategy C |
| 9fc31735 | 2 | 14k | mypy/ruff linting errors; QA policy/gate node placement question |
| c44fa991 | 5 | 89k | Code review graph changes; runtime-agnostic orchestrator plan (LangGraph + ADK) |

### 2026-04-18 (Workspace + poc)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 29a60696 | 5 | 28k | LLM provider config: Bedrock → Ollama (PII concern drove local switch) |
| 57042538 | 4 | 89k | Eval cleanup — graders vs metrics vs harnesses vs experiments distinction |
| 0ef44b3d | 5 | 89k | Google ADK parity with adk-agent-samples; shared protocols vs skills; Makefile targets for both runtimes |

### 2026-04-19 (poc project)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 6765bd2b | 12 | 21k | Linting fixes; Makefile smoke test target added |
| 1bafe007 | 26 | 239k | src/ vs app/ naming decision; circular import fix (datastore); test import reorganisation |
| 9e66674c | 3 | 13k | Ingestion/embedding in preprocessing (not retrieval); single indexer decision; dead indexing.py deleted |

### 2026-04-20 (Workspace + poc)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 64095580 | 17 | 301k | playground/.claude vs adk-agent-pocs/.claude overlap; .agents/ research docs lifecycle; ADK vs Claude skills |
| ba67f0c4 | 3 | 13k | Sensitive data audit before merging open PR |

### 2026-04-21 (Workspace + playground + wiseer)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| dd86ca38 | 5 | 148k | Compare playground VA agents vs listen-wiseer setup; listen-wiseer restart |
| 46a3b186 | 25 | 423k | Playground sensitive data audit; infra folder consolidation |
| 9a091358 | 12 | 182k | listen-wiseer phase 3 refactor continuation |
| 826a1a97 | 62 | 2.6M | Track B Phase 3 — RDS Postgres for LangGraph checkpointer + EFS for Billy SQLite |
| ecf3e696 | 1 | 15k | Auto-generate CLAUDE.md for codebase |

### 2026-04-22 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 198e7d2c | 3 | 9k | `/insights` report analysis; create doc-to-linear-tickets skill; push to Linear |

### 2026-04-24 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 108c3f61 | 10 | 92k | Playground infra → GitHub; secrets audit; consolidate settings.json; name "librarian" chosen for wiki repo |

### 2026-04-25 (null)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-04- | — | — |

### 2026-04-26 (null)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-04- | — | — |
| 2026-04- | 319k | — |
| 2026-04- | 421k | — |
| 2026-04- | 537k | — |
| 2026-04- | 697k | ok then maybe we should just hae a command to do all of this in claude rather |

### 2026-04-27 (librarian)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-04- | 86k | let's do phase 1 |
| 2026-04- | 155k | This session is being continued from a previous conversation that ran out of c |
| 2026-04- | 220k | the uv sync is taking a while to buid - is it a lot from the toml that needs d |

### 2026-04-29 (playground)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-04- | 52k |  can you find SEVDESK_API_TOKEN |
| 2026-04- | 139k | and what about these open issues? should we move the plans to research where u |
| 2026-04- | 223k | /compact sounds good, lets proceed we want to finish all the plans and put the |
| 2026-04- | 52k | yes please but leave the regex part 1 as the precursor to run gdor review |
| 2026-04- | 269k | This session is being continued from a previous conversation that ran out of c |
| 2026-04- | 125k |  and the global skills? any iteration needed? |
| 2026-04- | 365k | what about langgraph-prompts? |
| 2026-04- | 230k |  wait since we added pre-commit we seem to have a lot of issues for these but |
| 2026-04- | 412k | ok all three sound good.. i'm wondering also about context chunks how long are |
| 2026-04- | 275k |  i have 33 tickets that mention sevdesk - can we make these generic names plea |
| 2026-04- | 307k | not just for this session but also uncommitted changes. and i already removed |
| 2026-04- | 25k | yes that would be great thank you |
| 2026-04- | 64k |  WARN[0112] Found orphan containers ([listen-wiseer-app listen-wiseer-db-init |

### 2026-04-30 (playground)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-04- | 63k |  i just realized we have been naming everything billy - but actually this is j |
| 2026-04- | 169k |  i still see 70 files with billy mentioned that's insane and also did i remove |
| 2026-04- | 204k |  idk i still see 60 files |

### 2026-05-04 (playground)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 99k |  what scripts for eval of bedrockKB do we have available here? we dont need al |
| 2026-05- | 121k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 173k | I guess one nbk is fine |
| 2026-05- | 190k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 223k | Continue from where you left off. |
| 2026-05- | 5k |  TypeError: dtype 'str' does not support operation 'mean' |
| 2026-05- | 266k | that sounds great |
| 2026-05- | 297k | why is topic distribution so long? perhaps do something to get top topic_descr |

### 2026-05-05 (playground)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 50k |  eval notebook somehow lost the 1f. lexical and semantic similarity subplot bu |
| 2026-05- | 73k |  ratings looks good but the user feedback and notes should be histogram like t |
| 2026-05- | 132k |  no histogram and there are some rated like and dislike not a number but a str |
| 2026-05- | 211k |  ok for lexical similarity can we just do the repeated question distrbution an |
| 2026-05- | 295k |  df = pd.read_csv("evals/data/bookkeeperHero.csv") |
| 2026-05- | 431k |  i see the 1g but no code |
| 2026-05- | 441k |  i'm looking at it now and we're missing the code for source fidelity and lexi |
| 2026-05- | 508k |  did you delete the code? |
| 2026-05- | 52k |  What's working well |
| 2026-05- | 14k |  i want to get the naming convention correct here bc we have turns = task_id.. |
| 2026-05- | 40k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 63k | i've added them to a nbks/sevdesk folder here |
| 2026-05- | 80k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 105k |  ok so the parkey is creating data path but actually we whave evalse/data wher |
| 2026-05- | 114k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 135k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 17k |  fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 4)) |
| 2026-05- | 115k |  ignore the comments i'm trying to fix this figure.. but we shoud also save th |
| 2026-05- | 202k |  just please have a look at the nbk its not aligned with the 6 eda topics .. e |
| 2026-05- | 231k |  it was overwritten again somehow please update the nb |
| 2026-05- | 266k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 19k |  so i dont know if you are aware, but our analysis is basically per turn right |
| 2026-05- | 44k |  ok but the question remains - does this eda nbk output @results/eda_output/ p |

### 2026-05-06 (playground)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 9k |  how to export nbk as html in a cell |
| 2026-05- | 114k |  i think we also use sentence transformers - but my point is that in playgroun |
| 2026-05- | 212k |  is there also a flag for when the response language is not the same as the qu |
| 2026-05- | 407k | ok so what have i commited so far bc i dont see it on github.. as anything pus |
| 2026-05- | 473k |  any insights here === df (full) === |
| 2026-05- | 817k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 110k |  a few thoughts about our eval set aggregation and metrics to track from regre |
| 2026-05- | 210k |  exactly and we want to full base that contains all 5 separate datasets.. the |
| 2026-05- | 210k |  are you use you updated te nbk loks the same to me |
| 2026-05- | 319k | looks but i'm wondering if eval sets should be more like this breakdown 100 li |
| 2026-05- | 429k |  ok let's look a bit more closely now that we have our eval data set.. does it |
| 2026-05- | 515k |  ok the nbk ran through - but was anything recorded? or do i have to uncomment |
| 2026-05- | 672k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 1172k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 96k |  can we double check the sentiment distr for each of our samples used for llm |

### 2026-05-07 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 59k |  what do we think of just the base output and the 500 sample for the llm as gr |
| 2026-05- | 153k | wait a minute - did you just run the quality test through base? it was only me |
| 2026-05- | 120k |  we should have the --fix in the make lint command for ruff and also execute b |
| 2026-05- | 268k | looks great, but we are missing the all_stats.html did i delete it or was it n |
| 2026-05- | 397k | you ran it and think it lokos great? no this is what i'm seeing.. the fix need |
| 2026-05- | 118k |  if or file, this would look like make eval-stats --file? or make eval-stats f |
| 2026-05- | 249k | @evals/reports/bkh/all_stats.html , @evals/reports/bkh/base_stats.html , @eval |
| 2026-05- | 74k | exactly thank you lets make those changes, update paths and validate tests |
| 2026-05- | 176k | Let's think this through a little bit. Because we're in going in the right dir |
| 2026-05- | 244k | layer 1. satisfaction rate, resolution rate, resolution with friction rate, an |
| 2026-05- | 398k | you think so? i think resolution rate is north star with satisfaction, retriev |
| 2026-05- | 98k |  i just noticed a mistak maybe where no source liked is FN but this is problab |
| 2026-05- | 197k | are there any metrics from quality or intent graders we can add with instead o |
| 2026-05- | 93k |  can you run this skill to get insights report from claude usage - i'm trying |
| 2026-05- | 110k |  ok we have done a lot of good stuff here.. can we do a code review before we |
| 2026-05- | 87k | [Request interrupted by user] |

### 2026-05-08 (Workspace)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 98k |  right but @playground is wired to test clara tickets i guess only va-support- |
| 2026-05- | 210k | quick question bc i just want to test the 3 va models against the sevdesk data |
| 2026-05- | 110k |  something doesnt look right in the nbk for Calibration metrics (liked = posit |
| 2026-05- | 260k |  can you give me how to store under@data/baseline/golden_traces for the 12 and |
| 2026-05- | 429k |  NameError: name '_DEFAULT_MODEL' is not defined |
| 2026-05- | 99k | ok while that is running we should add data/baseline to gitignore and change t |
| 2026-05- | 367k | ok yeah cool it makes sense that routing fails here - leave it for now we will |
| 2026-05- | 91k |  yes please update the nbk so that it will run now thanks |
| 2026-05- | 428k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 614k | very nice.. should we make the old data set into regression/capability set for |
| 2026-05- | 217k | yes please collapse into one, but i think in nb 04_quality grader we compared |
| 2026-05- | 315k | sorry but we already ran eval_runner_quality what we're missing are the stats |

### 2026-05-09 (Workspace)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 771k | Check if the calibration eval (background task b6fo15w0q) has completed by rea |
| 2026-05- | 1079k | ok before we run the same 50 eval quality - can we instead include the single |
| 2026-05- | 93k |  question - what is the best way to handle data/report issues - if we push the |
| 2026-05- | 82k | ok lets move it to specs then and can we create specs/evals folder where all t |
| 2026-05- | 220k |  Okay. Yeah. Great. Glad we're on the same page here. So what I've done is I'v |
| 2026-05- | 305k | Oh, I think I know it got cut off. Um, Yeah. For the single agents, we don't n |
| 2026-05- | 149k |  Yep. That pretty much touches on everything we discussed, but one thing that' |
| 2026-05- | 322k | perfect lets write that plan and continue implementation thanks |
| 2026-05- | 60k | yes lets do that and does this apply also to langgraph or is independent to ad |
| 2026-05- | 200k |  ok i did a pretty heavy refactoring of @galactus/data which i think makes sen |
| 2026-05- | 163k | also the adk/langgraph agents calling bedrock should be similar in coverage - |
| 2026-05- | 348k | no lg is also broke |
| 2026-05- | 414k | oh intersting that hc_rag mrr is better than va_staging.. actually it looks li |
| 2026-05- | 581k | oh no something fucked up for hc_lg and hc_rag |
| 2026-05- | 739k |  ok we want next to these experiments also the comparison for va-agents with s |

### 2026-05-10 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 875k |  wait what? bkh should definitely not look higher.. why do we not have 44 task |
| 2026-05- | 1029k | this is what i see bkh missing data  , deepeval data misssing - eval_suite mda |
| 2026-05- | 633k |  ok heres the deal - i have renamed datasets to datasets_old.. what files need |
| 2026-05- | 1072k | ok this looks better but should the pipeline folder reflect the breakdown you |
| 2026-05- | 1603k | can we update readme please bc this is important step alos what are our repo r |

### 2026-05-11 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 85k | btw are any of these other metrics useful for us that we might want to add lat |
| 2026-05- | 97k |  also do we have the reranker in the ablation study? so is it just hyde is the |
| 2026-05- | 240k |  ok but did we dod the deepeval on bkh? if so we could just run that in the nb |
| 2026-05- | 397k | ok awesome.. i have also some metrics from @nbks/sevdesk - is there anhything |
| 2026-05- | 536k |  making the call now and to be clear, make va-calibrate-full  will calibrate t |
| 2026-05- | 124k |  what other topics would be interesting from our multiagent lg version - every |

### 2026-05-12 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 324k |  great can we finish va-migration? |
| 2026-05- | 129k |  is part of this plan or va-migration include adding safeguards, confidence ga |
| 2026-05- | 133k |  for the recent addition of grounding to our support-agents.. we also have ver |
| 2026-05- | 159k |  ok then lets do sprints 1-4 and we should touch kb urls - but we may have to |
| 2026-05- | 294k | y ty - and yes i am particularly interested in business analyst regarding invo |
| 2026-05- | 502k |  awesome before we move to sprint 2, can you please review these documents tha |

### 2026-05-13 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 171k |  ok i am thinking - lets make a new nbk.. golden_traces.. lets load the data w |
| 2026-05- | 116k |  # 17. Final Showdown — Custom v4 vs DeepEval vs RAGAS (second 50-query set) |
| 2026-05- | 291k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 384k | i said to do batches just bc its sooooo slow |
| 2026-05- | 99k |  edge_paths = { |
| 2026-05- | 468k | ok so now i can call the next fifty va-call-golden INPUT=data/datasets/va_stag |
| 2026-05- | 135k |  Grounding summary (192 graded items): |
| 2026-05- | 522k | ok lets review this a bit.. is the golden running both bkh and va responses/so |
| 2026-05- | 710k |  alright what do we think of the output for i think our golden traces nbk? its |
| 2026-05- | 871k |  btw are we getting the call latency and error reported anywhere? |
| 2026-05- | 969k |  ok i think there is a mistake eith eval-stats golden bc its taking. along tim |
| 2026-05- | 81k |  ok looks good.. dont we want to also show the repo structure for core and eva |
| 2026-05- | 166k | what happened to our eval metrics in file:///Users/ramsey.wise/Workspace/galac |
| 2026-05- | 188k |  ok i reran the nbk but not sure if all paths were updated? some still say 192 |

### 2026-05-14 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 113k |  so our golden traces have a problem with url match between old and new versio |
| 2026-05- | 99k | Love that. Can you also add this information to a read me somewhere maybe arou |
| 2026-05- | 261k |  ok looks like everything works but is it retrieving from 500? not the va-stag |
| 2026-05- | 351k | wait but pycall is also bedrock which doesnt work now bc of aws creds.. so we |
| 2026-05- | 440k | ok raw json givs 5 sources but only title url   "suggestions": [], |
| 2026-05- | 561k |  but is the retrival 500 the same as our 600 count? we should have task id and |
| 2026-05- | 128k |  {"status":"ok","backend":"langgraph"}%   but backend should be hc_rag |

### 2026-05-15 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 194k | looks good but now we are missing the va-hit-count as well as the billy url if |
| 2026-05- | 373k | ok but the ub_url_coverage has only 1395 rows.. are there some. missing maybe |
| 2026-05- | 503k |  index error.. ok i like where we're going with this from bkh to liked we can |
| 2026-05- | 137k |  I just added @worksapce/chat-agent that has a pretty sophisticated eval and o |
| 2026-05- | 589k | look where we start eda (i added markdown separator) the first cell is bkh hit |
| 2026-05- | 205k |  no lets add it to the plan and start implementing - although there might be s |
| 2026-05- | 665k |  Golden responses: 597 rows |
| 2026-05- | 298k | This session is being continued from a previous conversation that ran out of c |

### 2026-05-16 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 823k |  ok but that's where we're wrong.. first of all expected_url is this mapped to |
| 2026-05- | 989k |  did you add that at the end i just reran and dont see it |
| 2026-05- | 1123k | ok very cool.. yes i agree with your insights will check it out, but this is s |

### 2026-05-18 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 142k |  in this report.. we show top 10 disliked topics.. but lets also show top 10 l |
| 2026-05- | 97k |  for the eval methods tab do we need to update any of the stats or quality gra |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |

### 2026-05-19 (.claude)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |

### 2026-05-20 (.claude)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |
| 2026-05- | 0k | — |

### 2026-05-21 (.claude)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 0k | — |

### 2026-05-24 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 112k |  then why is there only 38 capability test in baseline/eval sets - are the lat |
| 2026-05- | 261k | question is hc_adk and hc_lg currently wired to the hc_rag or to bedrock? has |
| 2026-05- | 42k |  now that we have the golden 597 we can do the ablation study - what is left t |
| 2026-05- | 400k | ok lets please fix all of these monitoring and metric issues and i will rerun |
| 2026-05- | 124k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 618k | also it looks like adk is running but there are no logs so i have no idea wher |
| 2026-05- | 253k |  help.shine.co should be the corpus_articles (formerly billy help).. we should |
| 2026-05- | 700k |  interesting and how does this compare to va-agents? bc i think the adjusted m |
| 2026-05- | 911k |  data/datasets/support-agents/eval_sets/proper_eval_51.jsonl --endpoint http:/ |
| 2026-05- | 154k | make crawl-billypedia |
| 2026-05- | 82k |  these reports enrichment folder is getting out of control can we refactor and |
| 2026-05- | 1239k |  well actually can we create a nbk like the onese we did at sevdesk for findin |
| 2026-05- | 212k |  how does this metadata compare to bedrock config for DATA_SOURCE_IDS = { |
| 2026-05- | 1503k |  why is this last reranker taking so long? been almost 30 min |
| 2026-05- | 70k |  ok and what about the mq? do we include that for the ablation as well? |
| 2026-05- | 156k |  but i want to see this table by source |

### 2026-05-25 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 298k | oh intersting ok so looks like we were escalating cases that we prob could hav |
| 2026-05- | 648k | ok interesting our router to source typd didnt work.. but if we had thinking t |
| 2026-05- | 792k | Okay. So I do make s a eighty k bedrock up and then run this. Is that right? |
| 2026-05- | 893k | This session is being continued from a previous conversation that ran out of c |

### 2026-05-26 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 176k |  if we were to vibe code this agentic framework with eval and data ingestion a |

### 2026-05-28 (null)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| a0a707d3 | 77k | — |

### 2026-05-29 (null)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 68493546 | 67k | — |

### 2026-05-30 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-05- | 79k |  hmm so these are used by both ingestion and preprocessing? or more eval? like |
| 2026-05- | 134k |  nice is there anything from plans we can archive or remove? also research - i |
| 2026-05- | 204k | This session is being continued from a previous conversation that ran out of c |
| 2026-05- | 122k |  now that we have refactored core - our data folder is a hot mess.. is there a |

### 2026-06-01 (Workspace)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-06- | 177k |  can ytou give a summary of all the changes i just pulled particularly from he |
| 2026-06- | 137k |  instead of matching our intercom conversations by our rated bkh n=597 qa samp |

### 2026-06-02 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-06- | 369k |  did we update it? it looks the same gold df and for the sentence transformer |
| 2026-06- | 362k | ok and is there anything here on latency and evaluation of this invocation flo |
| 2026-06- | 749k |  ok so if i look at the gold_df by match_type=bkh_liked, there is no intercom |
| 2026-06- | 722k |  in the doc can you explain this a bit better Tier 1 (hallucinated IDs), Tier |
| 2026-06- | 1254k | ok thanks and to be clear and the qa pairs from gold overlapping with any of t |
| 2026-06- | 1191k | what do you think about this bc in galactus we use ragas and thats as good or |
| 2026-06- | 184k |  i think its even less after deduplication within queries, 195 but yes can you |
| 2026-06- | 1296k | This session is being continued from a previous conversation that ran out of c |
| 2026-06- | 242k |  I UNCOMMENT GENAI USE TO TRUE BUT IT SAYS GOOGLE API key not set |
| 2026-06- | 83k |  is there also overlap with @tooling/evals - for example the multiagent vs sup |

### 2026-06-03 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-06- | 97k |  if this eval calibration is done can you mark it as such, also the pii pipeli |
| 2026-06- | 1465k | Base directory for this skill: /Users/ramsey.wise/.claude/skills/execute-tasks |
| 2026-06- | 142k |  yo what's going on with this make file, please reduce it's crazy - all the ab |
| 2026-06- | 158k | actually i delete evals graders shared and also data is root of galactus not i |
| 2026-06- | 79k | oh thats not good.. we need to centralize our support agent schemas and config |
| 2026-06- | 154k | oh ok bur actually.. the loop is research -> plan -> plan review (dor gate) -> |
| 2026-06- | 223k | Start or continue a research phase. Delegates to the `research-review` protoco |
| 2026-06- | 377k | well the agent creator folder is used for the claud agents to execute i guess? |
| 2026-06- | 539k | can we also run a hook to do a lint after run-code-review? |

### 2026-06-04 (galactus)

| Session | ~Tokens | Topic |
|---------|---------|-------|
| 2026-06- | 107k |  make test 3 skipped, 22 deselected, 9 errors in 3.36s |
| 2026-06- | 84k |  how would you compare @chat-agent/src/agentic_rag to @galactus/src/support_ag |
| 2026-06- | 92k |  is this src folder linted already? |
| 2026-06- | 83k | ok cool is that something we need to refactor, is it fine where it sits in the |
| 2026-06- | 125k | sorry my skills strucutre looks different |

## Notes

- `poc` project = Help Support RAG Agent (early RAG POC, pre-librarian-wiki era)
- `wiseer` / `listen-wiseer` = Spotify recommendation agent
- `playground` = Billy VA agent + infra
- `txmatch` = Shine transaction matching (Codex, 2025)
- Token counts omitted where not available in frontmatter (many sessions lacked full stats in migrated skeleton notes)

## 2026-04 Early Sessions (ingested 2026-07-05 / 2026-07-06)

Sessions from 2026-04-10 to 2026-04-27. Key knowledge extracted:

| Date | Session | Topic | Wiki page |
|---|---|---|---|
| 2026-04-10 | 1900854e | Module restructure: `infra/`/`ingestion/`/`orchestration/` layout | [[Librarian Project]] |
| 2026-04-11 | deb81c96 | Core module extraction — break circular dep between `storage` + `librarian` | [[Librarian Project]] |
| 2026-04-11 | fe1c0bd1 | src/ package layout finalized; Fargate over Lambda | [[Librarian Project]] |
| 2026-04-11 | f5cfe1b3 | `infra/` under `src/`; `rag_core/` under `librarian/` | [[Librarian Project]] |
| 2026-04-12 | 406fcc7f | ADK + Python LangGraph hybrid; LangFuse compatible with both | [[ADK vs LangGraph Comparison]] |
| 2026-04-12 | 8d1a71b0 | Bedrock vs LangGraph engineering risk matrix (4 axes) | [[Bedrock KB vs LangGraph Decision]] |
| 2026-04-14 | 48cd8a0e | Librarian scope locked: RAG-only, not copilot | [[Librarian Project]] |
| 2026-04-14 | a6a9bcf4 | `.claude/docs` lifecycle: research→plan chains, archive model | [[Claude Workflow System]] |
| 2026-04-14 | 3def7093 | `clients/` vs `interfaces/` boundary clarified | [[Librarian Project]] |
| 2026-04-14 | ec44fece | Polyglot ruff config (TS folders need explicit exclude) | [[Session Insights]] |
| 2026-04-15 | b269ccf1 | rag_poc vs librarian: evolution path to production copilot | [[Librarian Project]] |
| 2026-04-17 | c44fa991 | Runtime-agnostic orchestrator plan (LangGraph + ADK factory pattern) | [[Session Insights]] |
| 2026-04-17 | 7a25dbd0 | ADK samples context engineering scan vs rag_poc; Strategy C → B upgrade path | [[ADK Context Engineering]] |
| 2026-04-18 | 57042538 | Graders vs metrics vs harnesses distinction; eval dir structure | [[VA Eval Harness]] |
| 2026-04-19 | 9e66674c | Ingestion/embedding in preprocessing (not retrieval); one-indexer rule | [[RAG Retrieval Strategies]] |
| 2026-04-19 | 1bafe007 | src/ vs app/ naming; circular import `datastore`↔`factory` fix | [[Session Insights]] |
| 2026-04-20 | 64095580 | Multi-repo .claude/ organization; .agents/ research docs lifecycle | [[Multi-Repo Claude Organization]] |
| 2026-04-24 | 108c3f61 | MCP server security — sandbox isolation, secrets, read-only invariant | [[MCP Server Security Patterns]] |
| 2026-04-26 | — | Session enrichment, output type taxonomy, wiki taxonomy design | [[Session Knowledge Capture Patterns]] |
| 2026-04-27 | — | Wiki decisions in domain dirs; raw sources as references | [[Karpathy LLM Wiki Pattern]] |

Remaining sessions (linting ops, git ops, compact checkpoints): manifest-only, no wiki pages.

## 2026-05–06 Batch (ingested 2026-07-06)

Sessions from 2026-04-27 to 2026-06-04. Mostly compact stubs and migrated JSONL sessions with quantitative metadata only; no wiki pages generated.

| Period | Project | Count | Theme |
|---|---|---|---|
| 2026-04-27 | librarian | 2 | Lint + UI graph view iterations |
| 2026-04-29–30 | playground | 15 | RAG migration Track 2, sevdesk → generic renaming |
| 2026-05-04–06 | playground | 14 | Eval EDA notebooks, eval set aggregation |
| 2026-05-06–07 | galactus | 16 | Initial galactus setup: Makefile, pre-commit, project rename from intercom-data |
| 2026-05-08–10 | galactus + Workspace | 20 | Calibration eval (VIR-138): LLM judge baselines, dataset splits |
| 2026-05-11–12 | galactus | 10 | Ablation study (VIR-179): 14 configs, VA migration sprint |
| 2026-05-13–16 | galactus | 22 | Golden dataset: 597 queries built from BKH liked + Intercom; grader calibration |
| 2026-05-18 | galactus + .claude | 6 | Eval report (top liked/disliked topics); skill dev (auto-compacted empty sessions) |
| 2026-05-19–21 | .claude | 21 | Skill iteration sessions (all auto-compact stubs, 0 tokens) |
| 2026-05-24–26 | galactus | 17 | Corpus data types (help.shine.co, billypedia, pricing); ablation continuation |
| 2026-05-28–29 | null | 2 | Galactus codebase refactor: ingestion/preprocessing separation (migrated JSONL) |
| 2026-05-30 | galactus | 4 | Core refactor; data folder reorganization |
| 2026-06-01–04 | galactus + Workspace | 12 | GT dataset verification (VIR-212); accounting_agent inception |

## 2026-06–07 Individual Chat Sessions (ingested 2026-07-06)

| Date | Session | Project | Topic |
|---|---|---|---|
| 2026-06-04 | 57331686 | librarian | Google Drive scraping for ingest pipeline |
| 2026-06-05 | e8f4eeed | galactus | README update for ingestion path change |
| 2026-06-05 | 824e04f8 | galactus | Eval data confirmation |
| 2026-06-05 | 54fbb1fb | galactus | "Ralph" reference — escalation language considerations |
| 2026-06-05 | f38c3543 | galactus | Ingestion path location debate |
| 2026-06-07 | eeeb2744 | galactus | Legacy file cleanup |
| 2026-06-07 | 3e89eb49 | galactus | Experiment runner design |
| 2026-06-07 | a758a3bb | galactus | 500-test suite simplification |
| 2026-06-07 | 83bb4b48 | galactus | Capability docs location → `src/` as specs |
| 2026-06-07 | e9506f1e | galactus | Ruff formatter scope |
| 2026-06-08 | 09914670 | galactus | Calibrated LLM-as-judge: answer_relevancy + completeness + grounding + RAGAS |
| 2026-06-08 | 7aa3db68 | galactus | Linear tickets for copilot capabilities |
| 2026-06-08 | fe31aacc | galactus | Eval schema update |
| 2026-06-08 | b52a3ff9 | galactus | CodeQualityAgent (Akira) scope |
| 2026-06-08 | 4c189a8c | galactus | FileNotFoundError debug |
| 2026-06-08 | 52d344b8 | galactus | Schema clarity check |
| 2026-06-08 | fdc67863 | galactus | Notebook CSV path fix |
| 2026-06-08 | be975ee5 | galactus | EUR token budget tracking |
| 2026-06-09 | 0c6ec8a1 | galactus | IndexError debug |
| 2026-06-09 | 660918fb | galactus | ModuleNotFoundError (rag module) |
| 2026-06-09 | bf836c46 | galactus | Metric/exploration selection for eval |
| 2026-06-10 | 9ddbb706 | galactus | Fable model integration check |
| 2026-06-11 | 8caa7044 | galactus | Eval quality bug fix |
| 2026-06-19 | 8877c883 | galactus | execute-tasks skill invocation |
| 2026-06-19 | 094b14b7 | galactus | accounting_agent inception; LangGraph parity with va-agents |
| 2026-06-19 | 11d354a7 | galactus | SANYI applied to eval pipeline |
| 2026-06-19 | 6a1505ca | galactus | Task completion check |
| 2026-06-19 | b4f26fe7 | galactus | Notebook run verification |
| 2026-06-19 | 5bae9447 | galactus | SANYI vs Akira code review system design |
| 2026-06-19 | 130222d2 | galactus | MD report evaluation |
| 2026-06-22 | 93b4309e | galactus | Corpus data push (700 files); accounting_agent smoke test |
| 2026-06-22 | 84c3ba53 | va-agents | Thinking budget for VA/HCA agents |
| 2026-06-22 | f3d8c629 | galactus | Cursor bot in GitHub repo |
| 2026-06-23 | 2a6c99c4 | galactus | Heuristic JSON file loading |
| 2026-06-23 | bf544d36 | galactus | Escalation response language (should be English) |
| 2026-06-24 | b0642ba1 | galactus | HTML linting suppression |
| 2026-06-24 | 7e180bf0 | galactus | Lint toggle for HTML pages |
| 2026-06-24 | b9dc2827 | galactus | Core preprocessing grounding comment thread |
| 2026-06-24 | 4034555a | galactus | Eligibility grounding preprocessing |
| 2026-06-24 | 76bda47b | galactus | `make eval-all` error fix |
| 2026-06-24 | 6210d985 | galactus | Log visibility issue |
| 2026-06-24 | a7cab4b9 | galactus | VA eval framework assessment vs baseline docs |
| 2026-06-24 | de544217 | galactus | Playground vs galactus comparison |
| 2026-06-24 | 51b184ce | va-agents | Post-pull change review |
| 2026-06-24 | 890685a5 | galactus | Onboarding doc gap analysis |
| 2026-06-24 | 0c67abca | galactus | Escalation section documentation |
| 2026-06-24 | b91ebc5f | galactus | Eval count check |
| 2026-06-24 | 419dc79c | galactus | Pre-push review |
| 2026-06-24 | b92e12ec | galactus | Graph clarity improvement |
| 2026-06-24 | c46b867f | galactus | 15sec latency spike investigation |
| 2026-06-25 | 4ad49b99 | galactus | Dataset size decision (240 QA) |
| 2026-06-25 | b6ed6cf9 | galactus | Page update |
| 2026-06-25 | 6be85145 | galactus | Tab update in report |
| 2026-06-25 | 8cc7f4f3 | galactus | Document-to-eval-framework alignment check |
| 2026-06-25 | 0310489c | galactus | Old dataset cleanup |
| 2026-06-25 | c28a2b11 | galactus | Rebase from old branch |
| 2026-06-25 | cb15d378 | galactus | Dataset query_word_count removal |
| 2026-06-25 | a9522055 | galactus | Source baseline removal from overview |
| 2026-06-25 | e6f88df0 | galactus | HCA y_true plot fix |
| 2026-06-26 | 71d75bb4 | galactus | Overview section cleanup |
| 2026-07-05 | 4914f277 | Workspace | galactus vs awesome-copilot vs sevdesk-platform-ai-catalog comparison |
| 2026-07-05 | c7597adf | librarian | Librarian repo scraping question → this ingest session |
| 2026-07-05 | 0ee40dd4 | librarian | `make lint` debugging |

## See Also

- [[Librarian Project]]
- [[Librarian KB — Build Plan]]
- [[Claude Workflow System]]
- [[Session Insights]]
- [[Session Knowledge Capture Patterns]]
