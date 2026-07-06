# .claude/docs

Reference documentation for listen-wiseer. Plans are implementation-ready specs; research docs are decision support. Archive holds completed phases — useful for context, not active work.

---

## research/

Decision support docs. Start here before planning new work.

### music-agent/

| Doc | What it covers |
|---|---|
| [exploration-architecture.md](research/music-agent/exploration-architecture.md) | **Phase 7 design doc.** Spotify MCP server extraction, graph + intent refactor, exploration UX, implementation sequence |
| [recommender-design.md](research/music-agent/recommender-design.md) | Phase 2 recommender assessment: corpus characteristics, audio feature gaps, ENOA differentiator, Spotify API capabilities, RAG/websearch strategy |
| [peer-repos.md](research/music-agent/peer-repos.md) | Peer repo survey: spotify-ai-analytics, spotify-langgraph-agent, WikiSpotify-MCP — what they do better and what we should adopt |
| [spotify-repos.md](research/music-agent/spotify-repos.md) | Six Spotify repos studied for improvement ideas: ETL patterns, playlist tools, discovery flows |

### evaluation/

| Doc | What it covers |
|---|---|
| [eval-harness.md](research/evaluation/eval-harness.md) | Phase 5c eval harness research: LangFuse tracing, golden dataset design, intent/tool metrics |

---

## plans/

Active and upcoming implementation plans.

| Plan | Status | What it covers |
|---|---|---|
| [phase7a-exploration-tools.md](plans/phase7a-exploration-tools.md) | ✓ DONE | 6 new fetch functions, 7 new agent tools, MCP parity, 22 tests |
| [phase7b-intent-refactor-ux.md](plans/phase7b-intent-refactor-ux.md) | PLANNED | Add `explore_my_taste` + `discover` to classifier; wire suggestions → Chainlit chips |
| [phase7c-memory-genre-polish.md](plans/phase7c-memory-genre-polish.md) | PLANNED | Genre lineage tool, taste drift analysis, swap InMemoryStore → Postgres |

---

## archive/

Completed phase plans (phases 1–6) and superseded research. Read-only reference.
