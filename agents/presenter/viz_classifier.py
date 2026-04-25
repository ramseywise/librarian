"""Visual prompt engineering — two-pass strategy for high-quality image prompts."""

from __future__ import annotations

from pathlib import Path

import yaml

from core.client import create_client, parse_json_response
from agents.presenter.models import ImageConcept, SlideContent, VizPrompt

LIBRARY_PATH = Path(__file__).resolve().parent / "viz_prompt_library.yaml"

# --- System prompts for two-pass strategy ---

SCENE_SYSTEM = """You are a visual scene designer for presentations. Given a slide's content,
its position in the deck, and the deck's visual style guidelines, generate a detailed scene
description that will become an image generation prompt.

Output a JSON object with:
- "scene": 2-3 sentences describing the visual scene in vivid, specific detail
- "key_elements": list of 3-5 concrete visual elements that must appear
- "mood": one word for the emotional tone
- "color_palette": 2-3 specific colors that match the deck's style

Be concrete and visual. "A glowing neural network" is better than "AI technology".
Reference the deck style context to maintain visual coherence across slides."""

PROMPT_SYSTEM = """You are an expert at writing prompts for AI image generation models.
Given a scene description and a prompt template with variables, fill in the template
variables to produce the most visually striking, coherent image possible.

Return a JSON object with the variable names as keys and your filled values as strings.
Be specific and cinematic — these values are fed directly to an image generation model.
Avoid text, words, or labels in the image. Focus on visual elements only."""

CONCEPT_SYSTEM = """You are a visual creative director. Given a goal, description, audience, and tone,
propose exactly {n} distinct image concepts. Each should be visually distinct in approach.
Return a JSON array of objects, each with:
- "label": short name (3-5 words)
- "viz_type": one of architecture|concept|narrative|timeline|comparison|process_flow
- "description": one sentence of what the image depicts
- "rationale": one sentence on why this suits the goal"""


def _load_library() -> dict:
    with LIBRARY_PATH.open() as f:
        return yaml.safe_load(f)


def _generate_scene_description(
    client: object,
    model: str,
    slide_context: str,
    deck_style_context: str,
) -> dict:
    """Pass 1: Generate a rich scene description from slide + deck context."""
    user_msg = (
        f"Deck visual style:\n{deck_style_context}\n\nSlide context:\n{slide_context}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=SCENE_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    return parse_json_response(client, response.content[0].text, model, SCENE_SYSTEM)


def _translate_to_image_prompt(
    client: object,
    model: str,
    scene: dict,
    template: str,
    style: str,
    scene_hint: str,
) -> str:
    """Pass 2: Translate scene description into an optimized image-gen prompt."""
    import re

    variables = re.findall(r"\{(\w+)\}", template)
    if not variables:
        return f"{template}, {style}"

    scene_description = scene.get("scene", "")
    key_elements = ", ".join(scene.get("key_elements", []))
    mood = scene.get("mood", "")
    color_palette = ", ".join(scene.get("color_palette", []))

    user_msg = (
        f"Scene description: {scene_description}\n"
        f"Key visual elements: {key_elements}\n"
        f"Mood: {mood}\n"
        f"Color palette: {color_palette}\n"
        f"Scene hint: {scene_hint}\n\n"
        f"Template: {template}\n"
        f"Variables to fill: {variables}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=PROMPT_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    filled_vars = parse_json_response(
        client, response.content[0].text, model, PROMPT_SYSTEM
    )
    filled = template.format(**{k: filled_vars.get(k, k) for k in variables})
    return f"{filled}, {style}"


def classify_slides(
    slides: list[SlideContent],
    model: str,
    deck_style_context: str = "",
    img_width: int = 1280,
    img_height: int = 720,
) -> list[VizPrompt]:
    """Classify slides and generate image prompts using two-pass strategy."""
    client = create_client()
    library = _load_library()
    results: list[VizPrompt] = []

    for slide in slides:
        viz_type = slide.slide_type
        entry = library.get(viz_type, library["concept"])

        if entry["skip_image"] or not slide.image_brief:
            results.append(
                VizPrompt(
                    slide_number=slide.slide_number,
                    viz_type=viz_type,
                    skip_image=True,
                )
            )
            continue

        slide_context = (
            f"Slide {slide.slide_number}: {slide.headline}\n"
            f"Type: {viz_type}\n"
            f"Bullet points: {', '.join(slide.body)}\n"
            f"Image brief: {slide.image_brief}"
        )

        # Pass 1: scene description
        scene = _generate_scene_description(
            client, model, slide_context, deck_style_context
        )

        # Pass 2: translate to image prompt
        filled = _translate_to_image_prompt(
            client,
            model,
            scene,
            entry["template"],
            entry["style"],
            entry.get("scene_hint", ""),
        )

        results.append(
            VizPrompt(
                slide_number=slide.slide_number,
                viz_type=viz_type,
                skip_image=False,
                filled_prompt=filled,
            )
        )

    return results


def propose_image_concepts(
    goal: str,
    description: str,
    audience: str,
    tone: str,
    model: str,
    n: int = 3,
    img_width: int = 1280,
    img_height: int = 720,
) -> list[ImageConcept]:
    """Propose image concepts for image-only mode."""
    client = create_client()
    library = _load_library()

    system = CONCEPT_SYSTEM.format(n=n)
    user_msg = (
        f"Goal: {goal}\nDescription: {description}\nAudience: {audience}\nTone: {tone}"
    )

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )

    concepts = [
        ImageConcept(**item)
        for item in parse_json_response(client, response.content[0].text, model, system)
    ]

    # Fill prompts for each concept using two-pass
    for concept in concepts:
        entry = library.get(concept.viz_type, library["concept"])
        if entry["skip_image"]:
            continue

        scene = {
            "scene": concept.description,
            "key_elements": [concept.label],
            "mood": tone,
            "color_palette": [],
        }
        filled = _translate_to_image_prompt(
            client,
            model,
            scene,
            entry["template"],
            entry["style"],
            entry.get("scene_hint", ""),
        )
        concept.filled_prompt = filled

    return concepts
