"""Image fetching — dispatches to the configured provider with parallel execution."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import structlog

from core.config.agent_settings import settings
from tools.presenter.models import VizPrompt
from tools.presenter.providers import get_provider

log = structlog.get_logger(__name__)

MAX_WORKERS = 4


def fetch_images_for_slides(
    viz_prompts: list[VizPrompt],
    output_dir: Path,
    deck_slug: str,
) -> dict[int, Path]:
    """Fetch all non-skipped slide images in parallel. Returns {slide_number: image_path}."""
    provider = get_provider()
    width = settings.image_width
    height = settings.image_height
    results: dict[int, Path] = {}

    # Build work items for non-skipped slides
    work: list[tuple[int, str, Path]] = []
    for vp in viz_prompts:
        if vp.skip_image or not vp.filled_prompt:
            continue
        dest = output_dir / f"{deck_slug}_slide_{vp.slide_number:02d}.png"
        work.append((vp.slide_number, vp.filled_prompt, dest))

    if not work:
        return results

    log.info("image_fetcher.batch.start", count=len(work))

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(provider.generate_image, prompt, dest, width, height): slide_num
            for slide_num, prompt, dest in work
        }

        for future in as_completed(futures):
            slide_num = futures[future]
            try:
                path = future.result()
                results[slide_num] = path
            except Exception as exc:
                log.error(
                    "image_fetcher.slide.failed",
                    slide=slide_num,
                    error=str(exc),
                )

    log.info(
        "image_fetcher.batch.done",
        fetched=len(results),
        failed=len(work) - len(results),
    )
    return results


def fetch_single_image(prompt: str, output_dir: Path, filename: str) -> Path:
    """Fetch a single image using the configured provider."""
    provider = get_provider()
    dest = output_dir / filename
    return provider.generate_image(
        prompt, dest, settings.image_width, settings.image_height
    )
