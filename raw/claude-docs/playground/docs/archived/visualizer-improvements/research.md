# Research: Visualizer Agent Improvements

**Date**: 2026-04-06
**Scope**: Identify improvement opportunities across the full visualizer pipeline (intake → outline → content → images → render)
**Branch**: `cord/improve-agent-visualization-7a1af2`

---

## 1. Current Architecture

The visualizer has two modes:

- **Deck mode** (`run_deck`): intake → outline → slide content → viz classification → image fetch → PPTX render
- **Image-only mode** (`run_image`): intake → concept proposals → user picks → image fetch

**Files** (8 source, 2 test):

| File                      | LOC | Responsibility                                                                    |
| ------------------------- | --- | --------------------------------------------------------------------------------- |
| `__main__.py`             | 243 | CLI entry point, orchestration for both modes                                     |
| `intake.py`               | 119 | Rich-based interactive intake (DeckIntake, ImageIntake models)                    |
| `outline.py`              | 132 | Claude generates deck outline → DeckOutline model, approval loop                  |
| `slide_writer.py`         | 91  | Claude generates per-slide content (headline, bullets, speaker note, image brief) |
| `viz_classifier.py`       | 188 | Claude fills prompt templates from viz_prompt_library.yaml → Pollinations URLs    |
| `image_fetcher.py`        | 52  | httpx GET to Pollinations, writes PNG to disk                                     |
| `renderer.py`             | 175 | python-pptx: builds .pptx from slide content + image map                          |
| `config.yaml`             | 13  | Defaults (model, audience, output dirs, image dims)                               |
| `viz_prompt_library.yaml` | 30  | 6 viz types with style strings and prompt templates                               |

**Tests**: Only 2 test files (8 tests total) covering outline parsing and VizPrompt/ImageConcept model construction. No tests for renderer, slide_writer, image_fetcher, or intake.

---

## 2. Identified Improvement Areas

### 2.1 Image Generation Quality (HIGH)

**Current state**: Pollinations.ai with a single URL-based API call per slide. No model selection, no seed control, no retry logic.

**Problems**:

- No `model` parameter in Pollinations URL — defaults to whatever their backend chooses
- No `seed` parameter — results are non-reproducible; you can't re-run and get the same deck
- Only 3 viz types produce images (architecture, concept, narrative) — limited visual variety
- Prompt templates are thin (4 variables each) — the LLM fills them but the final prompts lack the specificity that modern image models need
- No image quality validation — a failed/blank/low-quality image gets embedded as-is
- No retry or fallback when Pollinations returns errors or slow responses
- `nologo=true` is the only parameter used; Pollinations supports `enhance=true`, `model=flux`, `seed=N`

**Opportunities**:

- Add `model=flux` (or allow config override) for better image quality
- Add `seed` parameter for reproducible runs
- Add `enhance=true` to let Pollinations auto-improve prompts
- Expand viz_prompt_library.yaml with richer templates and more viz types (timeline, comparison, process-flow, infographic)
- Add negative prompt support if the API supports it
- Add image validation (check file size > threshold, retry on failure)
- Support aspect ratio presets beyond just 1280x720

### 2.2 Prompt Engineering Pipeline (HIGH)

**Current state**: Each slide gets one LLM call to fill template variables. The prompts are generic.

**Problems**:

- `_fill_template()` asks Claude to fill `{variables}` from a template, but gives it minimal context
- The slide's narrative arc, position in the deck, and relationship to adjacent slides are not considered
- No chain-of-thought or multi-turn refinement for critical slides (title slide, conclusion)
- Image briefs from slide_writer are underutilized — they're passed as context but could be the primary driver
- The concept proposal system for image-only mode generates 3 concepts but doesn't allow mixing elements from multiple concepts

**Opportunities**:

- Two-pass prompt strategy: first generate a detailed scene description, then translate to image-gen prompt
- Feed deck-level visual coherence instructions (consistent color palette, style, recurring motifs)
- Weight important slides (title, conclusion) with more detailed prompting
- Allow user to provide reference images or style guides
- Batch prompt generation so Claude sees all slides at once and can create visual continuity

### 2.3 PPTX Rendering Quality (HIGH)

**Current state**: Two layouts — full-bleed image with text overlay, or basic text slide. Hardcoded font sizes, positions, and colors.

**Problems**:

- No `template.pptx` file exists — config references it but it's missing, so every deck uses python-pptx defaults (plain white)
- `_add_image_slide()` puts text at a fixed position (y=5.2") with white text — unreadable on light images
- No semi-transparent overlay/scrim behind text (the comment says "semi-transparent overlay strip" but it's just a plain textbox)
- `_add_text_slide()` falls back to placeholder[0]/placeholder[1] which may not exist in custom templates
- No title slide image support
- No slide transitions or animations
- Font choices are hardcoded (system default) — no branding support
- No progress indicator/slide numbering in the deck
- Layout is the same for every image slide regardless of content type

**Opportunities**:

- Create a proper default template.pptx with branded master slides
- Add a dark scrim/gradient overlay behind text on image slides for readability
- Multiple layout strategies per viz type (architecture → labeled diagram layout, narrative → full-bleed cinematic, concept → split image/text)
- Support slide numbering and section dividers
- Add transition support (python-pptx has limited transition support but OPC-level XML patches work)
- Support both 16:9 and 4:3 aspect ratios

### 2.4 Config & Architecture (MEDIUM)

**Current state**: Config is a standalone YAML file loaded ad-hoc. No integration with shared `Settings` from `config.py`.

**Problems**:

- Visualizer has its own `config.yaml` + `_load_config()` in both `__main__.py` and `intake.py` — duplicated
- Not integrated with `src/agents/shared/config.py` (`pydantic-settings`) — can't override via `.env`
- Anthropic client is instantiated raw (`anthropic.Anthropic()`) in every module instead of using `shared.client.create_client()`
- Output paths are relative to `AGENT_DIR` (the source directory) — output lands inside `src/`
- No shared Anthropic client or model config — each file reads its own
- `image_fetcher.py` uses a type comment `list[VizPrompt]` to avoid circular imports — messy

**Opportunities**:

- Migrate config to `shared/config.py` pydantic-settings model (consistent with research agent)
- Single `create_client()` usage across all modules
- Output path configurable via `.env` (default to project-level `output/` not inside `src/`)
- Extract Pydantic models to a `models.py` to break circular import chains

### 2.5 Error Handling & Resilience (MEDIUM)

**Current state**: Minimal error handling. JSON parse failures crash the process. Image fetch failures are logged but lost.

**Problems**:

- `json.loads()` on Claude output has no fallback — malformed JSON crashes the run
- No retry logic on Claude API calls (transient failures, rate limits)
- Image fetch timeout is 60s but no retry — a slow Pollinations response = missing slide image
- No graceful degradation — if 1 of 10 images fails, the deck still renders but with a blank slide and no warning to user
- No cost tracking or token usage reporting

**Opportunities**:

- Add JSON parse retry with re-prompting (ask Claude to fix its output)
- Add httpx retry with backoff for image fetches
- Graceful degradation: render text-only layout for slides where image fetch fails, notify user
- Track and report token usage per deck generation
- Add `--dry-run` flag that generates outline + content but skips image fetch and rendering

### 2.6 Test Coverage (MEDIUM)

**Current state**: 8 tests covering outline parsing and model construction. No integration-style tests.

**Problems**:

- 0 tests for `renderer.py` — the most brittle module (python-pptx layout logic)
- 0 tests for `slide_writer.py` — Claude JSON parsing
- 0 tests for `image_fetcher.py` — HTTP fetch logic
- 0 tests for `intake.py` — interactive prompts (harder to test, but model construction testable)
- No test for the end-to-end deck workflow with mocked Claude responses

**Opportunities**:

- Add renderer tests (generate a .pptx, assert slide count, check for images)
- Add slide_writer tests (mock Claude, verify SlideContent parsing)
- Add image_fetcher tests (mock httpx, verify file writing and error handling)
- Add an end-to-end test that runs the full pipeline with all Claude calls mocked

### 2.7 UX & Workflow (LOW-MEDIUM)

**Current state**: Rich-based interactive CLI. Linear workflow, no resume/undo.

**Problems**:

- No way to save/resume a partially-completed deck
- Image-only mode revision loop appends `_v2` suffix — no proper versioning
- No preview of images before final render (user sees the deck after it's done)
- No way to regenerate a single slide's image without re-running the whole pipeline
- Codebase summary is top-level `ls` + README — shallow

**Opportunities**:

- Save intermediate state (outline, content, image map) to YAML/JSON so runs can be resumed
- Add `--preview` flag that opens each image for approval before rendering
- Add `--regenerate-slide N` to re-fetch a single image
- Better codebase analysis (tree structure, key file content, not just top-level ls)

---

## 3. Priority Ranking

| Priority | Area                        | Impact                                  | Effort      |
| -------- | --------------------------- | --------------------------------------- | ----------- |
| 1        | Prompt engineering pipeline | High — directly improves output quality | Medium      |
| 2        | Image generation quality    | High — Pollinations params + retry      | Low-Medium  |
| 3        | PPTX rendering quality      | High — the final user-facing output     | Medium-High |
| 4        | Config & architecture       | Medium — consistency, maintainability   | Low         |
| 5        | Error handling & resilience | Medium — production reliability         | Low-Medium  |
| 6        | Test coverage               | Medium — safety net for all changes     | Medium      |
| 7        | UX & workflow               | Low-Medium — nice-to-have               | Medium      |

---

## 4. Key Technical Decisions Needed

1. **Pollinations model selection**: Should we default to `flux` or make it configurable? Flux produces significantly better results but may have different latency characteristics.

2. **Batch vs per-slide prompting**: Generating all image prompts in one Claude call would improve visual coherence across the deck but increases token usage and failure blast radius.

3. **Template strategy**: Ship a default template.pptx in the repo, or generate layouts purely in code? A template gives better visual control but is harder to version/diff.

4. **Config migration scope**: Migrate everything to shared `Settings` now, or just add the missing fields incrementally?

5. **Async image fetching**: Images are currently fetched sequentially. For a 10-slide deck, that's ~10 sequential HTTP calls at up to 60s each. `httpx.AsyncClient` or `concurrent.futures` could parallelize this.

---

## 5. Out of Scope

- Switching away from Pollinations.ai (constraint: no API key required)
- Adding video or animation support to slides
- Building a web UI — this stays as a CLI tool
- Supporting non-PPTX output formats (PDF, HTML, Reveal.js)
