# Plan: Visualizer Agent Improvements

Date: 2026-04-06
Based on: `.claude/docs/research/visualizer-improvements.md`

## Goal

The visualizer agent produces higher-quality slide decks by using optimized Pollinations parameters, a two-pass prompt engineering pipeline with deck-level visual coherence, a pluggable image provider (Pollinations default, Replicate optional), readable text-over-image rendering with a dark scrim, and robust error handling with retry and graceful degradation — all configured through the shared pydantic-settings system.

## Approach

Attack output quality from three angles simultaneously: better prompts (the biggest lever regardless of provider), better provider parameters (free improvement from Pollinations' model/seed/enhance flags), and a clean provider abstraction that lets the user swap in Replicate when they want premium quality. Consolidate config into the shared `Settings` model first since every other step depends on it. Keep the architecture change minimal — a Protocol-based provider interface, not a plugin system. The key tradeoff: per-slide prompting (safer, simpler) over batch prompting (more coherent) — compensated by passing deck-level style context to every call.

## Open Questions (resolved before planning)

- Q: Pollinations model default? A: Configurable via Settings, default `flux`
- Q: Batch vs per-slide prompting? A: Per-slide with deck-level style context passed to each call
- Q: Ship a template.pptx? A: Out of scope — fix readability in code with scrim overlay
- Q: Config migration scope? A: Full — move all visualizer config to shared Settings, delete config.yaml
- Q: Replicate dependency? A: Optional extra (`[replicate]`), lazy import, fail gracefully if not installed
- Q: Async image fetch? A: `concurrent.futures.ThreadPoolExecutor` in provider layer — no async plumbing needed

## Steps

### Step 1: Config & Models Foundation -- DONE 2026-04-06

**Files**:
- `src/agents/shared/config.py` (lines 10–21) — add visualizer fields to `Settings`
- `src/agents/visualizer/models.py` (NEW) — extract all Pydantic models here
- `src/agents/visualizer/intake.py` (lines 14–17, 20–33) — remove `_load_config()` + models, import from new locations
- `src/agents/visualizer/outline.py` (lines 29–39, 43, 114) — remove models, replace `anthropic.Anthropic()` with `create_client()`
- `src/agents/visualizer/slide_writer.py` (lines 7–9, 23–29, 40) — remove `SlideContent`, replace client
- `src/agents/visualizer/viz_classifier.py` (lines 9, 39–54, 100, 155) — remove `VizPrompt`/`ImageConcept`, replace client
- `src/agents/visualizer/__main__.py` (lines 18–21, 48–49) — remove `_load_config()`, use `settings`
- `src/agents/visualizer/config.yaml` — DELETE
- `tests/visualizer/test_outline.py` (lines 6–7, 31, 33) — update imports to models.py
- `tests/visualizer/test_viz_classifier.py` (lines 3–8) — update imports to models.py
- `tests/visualizer/test_config.py` (NEW) — verify visualizer Settings fields

**What**: Consolidate all configuration into the shared `Settings` class and extract all Pydantic models into a single `models.py` to break circular import chains. Replace every bare `anthropic.Anthropic()` call with `create_client()`. Delete `config.yaml`.

**Snippet** (the key pattern):
```python
# src/agents/shared/config.py — add to Settings class (after line 20):
# Visualizer settings
image_provider: str = "pollinations"  # "pollinations" | "replicate"
pollinations_model: str = "flux"
pollinations_seed: int | None = None  # None = random
pollinations_enhance: bool = False
replicate_api_token: str = ""
viz_output_dir: Path = Path("output")
image_width: int = 1280
image_height: int = 720
viz_audience: str = "mixed technical and product team"
viz_model: str = "claude-sonnet-4-6"

# src/agents/visualizer/models.py (NEW) — all models in one place:
from pydantic import BaseModel

class SlideOutline(BaseModel):
    number: int
    title: str
    type: str
    talking_points: list[str]
    speaker_note: str

class DeckOutline(BaseModel):
    title: str
    slides: list[SlideOutline]

# ... DeckIntake, ImageIntake, SlideContent, VizPrompt, ImageConcept ...

# Every module that had anthropic.Anthropic():
# Before:
client = anthropic.Anthropic()
# After:
from agents.shared.client import create_client
client = create_client()
```

**Test**: `uv run pytest tests/visualizer/ -v`
**Done when**: All 8 existing tests pass with models imported from `models.py`, config from `settings`, and client from `create_client()`. `config.yaml` deleted. `grep -r "_load_config" src/agents/visualizer/` returns nothing.

---

### Step 2: Image Provider System -- DONE 2026-04-06

**Files**:
- `src/agents/visualizer/providers.py` (NEW) — `ImageProvider` Protocol, `PollinationsProvider`, `ReplicateProvider`
- `src/agents/visualizer/image_fetcher.py` (lines 1–52, full rewrite) — delegate to provider, add parallel fetch
- `src/agents/visualizer/viz_classifier.py` (lines 56–58, `_build_url`) — move URL building into `PollinationsProvider`
- `src/agents/visualizer/__main__.py` (lines 40–90) — wire provider from `settings.image_provider`
- `pyproject.toml` (line 14) — add `replicate` as optional dependency
- `tests/visualizer/test_providers.py` (NEW) — mock-based provider tests
- `tests/visualizer/test_image_fetcher.py` (NEW) — fetch + parallel tests

**What**: Create a `typing.Protocol`-based image provider interface. Implement `PollinationsProvider` with `model`, `seed`, `enhance` params and `ThreadPoolExecutor`-based parallel fetching. Implement `ReplicateProvider` with lazy import. Update `image_fetcher.py` to be a thin dispatcher that picks the provider from config.

**Snippet**:
```python
# src/agents/visualizer/providers.py
from typing import Protocol

class ImageProvider(Protocol):
    def generate_image(self, prompt: str, dest: Path, width: int, height: int) -> Path: ...
    def generate_batch(self, prompts: list[tuple[str, Path]], width: int, height: int) -> dict[int, Path]: ...

class PollinationsProvider:
    def __init__(self, model: str = "flux", seed: int | None = None, enhance: bool = False) -> None:
        self.model = model
        self.seed = seed
        self.enhance = enhance

    def _build_url(self, prompt: str, width: int, height: int) -> str:
        encoded = quote(prompt)
        params = f"width={width}&height={height}&model={self.model}&nologo=true"
        if self.seed is not None:
            params += f"&seed={self.seed}"
        if self.enhance:
            params += "&enhance=true"
        return f"https://image.pollinations.ai/prompt/{encoded}?{params}"

    def generate_batch(self, prompts, width, height):
        with ThreadPoolExecutor(max_workers=4) as pool:
            # parallel fetch
            ...

class ReplicateProvider:
    def __init__(self, api_token: str, model: str = "black-forest-labs/flux-schnell") -> None:
        try:
            import replicate
        except ImportError:
            raise RuntimeError("Install replicate: uv add replicate")
        ...

# pyproject.toml
[project.optional-dependencies]
replicate = ["replicate>=1.0.0"]
```

**Test**: `uv run pytest tests/visualizer/test_providers.py tests/visualizer/test_image_fetcher.py -v`
**Done when**: `PollinationsProvider._build_url()` includes `model=flux&seed=N&enhance=true` when configured. `ReplicateProvider` raises `RuntimeError` with install instructions if `replicate` not installed. Parallel fetch generates images for 3+ slides concurrently (verified by mock call timing).

---

### Step 3: Prompt Engineering Pipeline -- DONE 2026-04-06

**Files**:
- `src/agents/visualizer/viz_prompt_library.yaml` (lines 1–30, full rewrite) — richer templates, new viz types
- `src/agents/visualizer/viz_classifier.py` (lines 16–31, system prompts) — new two-pass prompts
- `src/agents/visualizer/viz_classifier.py` (lines 61–91, `_fill_template`) — rewrite as two-pass: scene description then image prompt
- `src/agents/visualizer/viz_classifier.py` (lines 94–139, `classify_slides`) — accept and propagate `deck_style_context`
- `src/agents/visualizer/slide_writer.py` (lines 12–20, `SLIDE_SYSTEM`) — enhance to produce richer `image_brief`
- `src/agents/visualizer/__main__.py` (lines 64–68) — pass deck style context to `classify_slides`
- `tests/visualizer/test_viz_classifier.py` — add two-pass prompt tests
- `tests/visualizer/test_slide_writer.py` (NEW) — mock-based SlideContent tests

**What**: Upgrade the prompt pipeline from one-shot template filling to a two-pass strategy: (1) Claude generates a detailed scene description from slide context + deck style, (2) Claude translates that scene into an optimized image-gen prompt. Add deck-level style context (color palette, recurring motifs, visual tone) that propagates to every slide for coherence. Expand the viz prompt library with new types (timeline, comparison, process_flow) and richer, more specific templates.

**Snippet**:
```yaml
# viz_prompt_library.yaml — expanded:
architecture:
  style: "clean isometric technical diagram, blueprint aesthetic, dark navy and cyan palette, minimalist line art, no text labels"
  template: "isometric system architecture showing {components} connected by {relationships}, {infrastructure_type} infrastructure, {scale} scale, {detail_focus} as focal detail"
  scene_hint: "Focus on spatial relationships between components. Use depth and layering to show hierarchy."
  skip_image: false

timeline:
  style: "elegant horizontal timeline infographic, gradient progression, milestone markers, modern sans-serif, no body text"
  template: "timeline visualization showing {phases} progressing from {start_state} to {end_state}, {progression_metaphor}, {accent_color} highlights on key milestones"
  scene_hint: "Emphasize progression and transformation over time."
  skip_image: false

comparison:
  style: "clean split-screen or side-by-side layout, contrasting color zones, balanced composition, diagrammatic"
  template: "visual comparison between {option_a} and {option_b}, {comparison_dimension} as organizing axis, {visual_metaphor} to highlight difference"
  scene_hint: "Make the contrast immediately obvious through color, scale, or position."
  skip_image: false

process_flow:
  style: "flowing process diagram, connected nodes with directional arrows, soft gradients, modern flat design"
  template: "process flow visualization showing {steps} from {input} to {output}, {flow_style} layout, {emphasis_point} highlighted"
  scene_hint: "Guide the eye along the flow direction. Use size to show importance."
  skip_image: false
```

```python
# viz_classifier.py — two-pass _fill_template:
def _generate_scene_description(client, model, slide_context, deck_style_context):
    """Pass 1: Generate a rich scene description from slide + deck context."""
    ...

def _translate_to_image_prompt(client, model, scene_description, template, style):
    """Pass 2: Translate scene description into an optimized image-gen prompt."""
    ...

# classify_slides gains deck_style_context:
def classify_slides(slides, model, deck_style_context, img_width, img_height):
    ...
    for slide in slides:
        scene = _generate_scene_description(client, model, slide_context, deck_style_context)
        filled = _translate_to_image_prompt(client, model, scene, entry["template"], entry["style"])
        ...
```

**Test**: `uv run pytest tests/visualizer/test_viz_classifier.py tests/visualizer/test_slide_writer.py -v`
**Done when**: `classify_slides` uses two LLM calls per image slide (scene + prompt). Deck-level style context appears in the scene description prompt. New viz types (timeline, comparison, process_flow) in library produce valid prompts. `image_brief` from slide_writer is richer than current single-sentence output.

---

### Step 4: Renderer Readability

**Files**:
- `src/agents/visualizer/renderer.py` (lines 30–80, `_add_image_slide`) — add gradient scrim, adjust text layout
- `tests/visualizer/test_renderer.py` (NEW) — generate .pptx, verify slide count + scrim shape

**What**: Add a semi-transparent dark gradient overlay (scrim) behind text on image slides so content is readable regardless of background image brightness. Use python-pptx shape fill with transparency. Adjust text positioning to sit within the scrim area with proper padding.

**Snippet**:
```python
# renderer.py — _add_image_slide, after adding the background image:
from pptx.oxml.ns import qn
from lxml import etree

# Add dark gradient scrim at bottom third of slide
scrim = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    left=Inches(0),
    top=Inches(4.5),
    width=SLIDE_W,
    height=Inches(3.0),
)
# Set fill to black with 60% transparency
fill = scrim.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x00, 0x00, 0x00)
# Set transparency via XML (python-pptx doesn't expose this directly)
solid_fill = fill._fill.find(qn("a:solidFill"))
srgb = solid_fill.find(qn("a:srgbClr"))
alpha = etree.SubElement(srgb, qn("a:alpha"))
alpha.set("val", "40000")  # 40% opacity = 60% transparent
scrim.line.fill.background()  # no border

# Then add text box on top of scrim (z-order: image → scrim → text)
```

**Test**: `uv run pytest tests/visualizer/test_renderer.py -v`
**Done when**: Generated .pptx image slides have 3 shapes minimum (image, scrim rectangle, text box). Scrim shape has black fill with alpha < 100%. Text is white and positioned within the scrim area. Existing text-only slides are unaffected.

---

### Step 5: Error Handling & CLI

**Files**:
- `src/agents/shared/client.py` (lines 17–22) — add `parse_json_response()` with retry
- `src/agents/visualizer/providers.py` (from Step 2) — add retry with exponential backoff to image fetches
- `src/agents/visualizer/renderer.py` (lines 142–174, `render_deck`) — graceful degradation for missing images
- `src/agents/visualizer/__main__.py` (lines 224–243, `main`) — add `--dry-run` and `--provider` CLI args
- `src/agents/visualizer/outline.py` — use `parse_json_response()` instead of raw `json.loads()`
- `src/agents/visualizer/slide_writer.py` — use `parse_json_response()`
- `src/agents/visualizer/viz_classifier.py` — use `parse_json_response()`
- `tests/visualizer/test_error_handling.py` (NEW) — retry + degradation tests

**What**: Add a shared `parse_json_response()` utility that wraps `json.loads()` with one retry (re-prompts Claude to fix malformed JSON). Add exponential backoff retry (3 attempts, 2s/4s/8s) to image provider HTTP calls. When an image fetch fails after retries, fall back to text-only layout instead of embedding a blank. Add `--dry-run` (skips image fetch + render, prints outline + content) and `--provider` (overrides `settings.image_provider`) CLI flags.

**Snippet**:
```python
# src/agents/shared/client.py — new utility:
def parse_json_response(
    client: anthropic.Anthropic,
    response_text: str,
    model: str,
    system: str,
) -> dict:
    """Parse JSON from Claude response, retrying once on failure."""
    raw = strip_json_fences(response_text)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        log.warning("json.parse.retry", error=str(exc))
        retry_response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            messages=[
                {"role": "user", "content": response_text},
                {"role": "user", "content": f"Your previous response was not valid JSON: {exc}. Please return only valid JSON."},
            ],
        )
        raw = strip_json_fences(retry_response.content[0].text)
        return json.loads(raw)  # let it raise if still bad

# __main__.py — new CLI args:
parser.add_argument("--dry-run", action="store_true", help="Generate outline + content only, skip images and render")
parser.add_argument("--provider", choices=["pollinations", "replicate"], help="Override image provider")
```

**Test**: `uv run pytest tests/visualizer/test_error_handling.py -v`
**Done when**: Malformed JSON triggers exactly one retry. Image fetch failure after 3 retries falls back to text-only layout (no crash). `--dry-run` prints outline and slide content without making any image requests. `--provider replicate` overrides the config.

---

## Test Plan

- **Unit tests** (run after each step):
  - `tests/visualizer/test_config.py` — Settings fields for visualizer
  - `tests/visualizer/test_outline.py::test_generate_outline_parses_json` — existing, updated imports
  - `tests/visualizer/test_viz_classifier.py::test_build_url_encodes_prompt` — existing, updated for provider
  - `tests/visualizer/test_providers.py` — PollinationsProvider URL building, ReplicateProvider import guard
  - `tests/visualizer/test_image_fetcher.py` — parallel fetch, provider dispatch
  - `tests/visualizer/test_slide_writer.py` — SlideContent parsing with mock
  - `tests/visualizer/test_renderer.py` — .pptx generation, scrim verification
  - `tests/visualizer/test_error_handling.py` — JSON retry, fetch retry, graceful degradation
- **Full suite**: `uv run pytest tests/visualizer/ -v` (target: all pass, 0 failures)
- **Integration test**: `uv run pytest tests/ --tb=short -q` (baseline: 83 pass, 3 fail from pdftotext — unchanged)
- **Manual validation**: `uv run visualizer --dry-run` to verify full pipeline without image cost; then `uv run visualizer` with a test topic to inspect .pptx output quality

## Risks & Rollback

### Step 1: Config & Models Foundation
- **Risk**: Moving all models to `models.py` could break import paths in tests or create circular imports if models.py imports from modules that import models
- **Blast radius**: Local — only import paths change, no data or user-facing behavior affected
- **Rollback**: `git checkout HEAD -- src/agents/visualizer/ tests/visualizer/ src/agents/shared/config.py` then re-add config.yaml from git history: `git checkout HEAD~1 -- src/agents/visualizer/config.yaml`
- **Verify rollback**: `uv run pytest tests/visualizer/ -v` — all 8 original tests pass

### Step 2: Image Provider System
- **Risk**: `PollinationsProvider` with new URL params (model, seed, enhance) could break if Pollinations changes their API or stops supporting these params. Parallel fetch with ThreadPoolExecutor could cause rate limiting.
- **Blast radius**: User-visible — image quality/availability changes
- **Rollback**: `git revert HEAD --no-edit && uv run pytest tests/visualizer/ -v`
- **Verify rollback**: Existing `_build_url` tests pass, images fetch with original URL format

### Step 3: Prompt Engineering Pipeline
- **Risk**: Two-pass prompting doubles Claude API calls per image slide (was 1, now 2). For a 10-slide deck with 7 image slides, that's 7 extra API calls (~$0.01-0.03 additional). If the second pass degrades instead of improving prompts, image quality drops.
- **Blast radius**: User-visible — image quality changes; cost increase (small)
- **Rollback**: `git revert HEAD --no-edit` — falls back to one-pass template filling
- **Verify rollback**: `uv run pytest tests/visualizer/test_viz_classifier.py -v`

### Step 4: Renderer Readability
- **Risk**: python-pptx XML manipulation for transparency could break on future python-pptx versions. lxml dependency may need explicit addition.
- **Blast radius**: User-visible — slide rendering changes
- **Rollback**: `git revert HEAD --no-edit && uv run pytest tests/visualizer/ -v`
- **Verify rollback**: Generated .pptx renders without scrim (back to baseline)

### Step 5: Error Handling & CLI
- **Risk**: JSON retry re-prompts Claude with the failed output — if the model consistently fails, this burns tokens on a doomed retry. Retry backoff on image fetches adds latency (up to 14s per slide on 3 retries).
- **Blast radius**: Local — only affects error paths, happy path unchanged
- **Rollback**: `git revert HEAD --no-edit && uv run pytest tests/visualizer/ -v`
- **Verify rollback**: Original error behavior (crash on bad JSON, skip on fetch failure)

### Global rollback
All steps are independently revertible. If multiple steps need undoing:
```bash
git revert HEAD~N..HEAD --no-edit  # where N = number of steps to undo
uv run pytest tests/visualizer/ -v  # verify baseline restored
```

## Out of Scope

- **Midjourney integration** — subscription cost not justified; no official API
- **template.pptx creation** — design task, not code; current code-generated layouts are functional
- **Slide transitions/animations** — requires OPC XML patches, fragile, low ROI
- **Async/await rewrite** — ThreadPoolExecutor achieves parallelism without async plumbing
- **Web UI** — stays as CLI tool
- **Non-PPTX output** (PDF, HTML, Reveal.js) — different feature, different plan
- **UX workflow** (resume, preview, regenerate single slide) — separate plan after this ships
- **Batch processing / cron** for visualizer — not needed; decks are interactive/on-demand
- **Together.ai provider** — Replicate covers the paid-provider use case; Together.ai can be added later as another `ImageProvider` implementation if needed
- **Image-only mode improvements** — this plan focuses on deck mode; image-only mode benefits passively from provider + prompt changes but gets no dedicated work
