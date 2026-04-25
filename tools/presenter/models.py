"""Pydantic models for the visualizer agent — shared across all modules."""

from __future__ import annotations

from pydantic import BaseModel


# --- Intake models ---


class DeckIntake(BaseModel):
    goal: str
    audience: str
    tone: str
    codebase_summary: str | None = None
    use_template: bool = True


class ImageIntake(BaseModel):
    goal: str
    description: str
    audience: str
    tone: str


# --- Outline models ---


class SlideOutline(BaseModel):
    number: int
    title: str
    type: str
    talking_points: list[str]
    speaker_note: str


class DeckOutline(BaseModel):
    title: str
    slides: list[SlideOutline]


# --- Slide content ---


class SlideContent(BaseModel):
    slide_number: int
    slide_type: str
    headline: str
    body: list[str]
    speaker_note: str
    image_brief: str | None = None


# --- Viz / image models ---


class VizPrompt(BaseModel):
    slide_number: int
    viz_type: str
    skip_image: bool
    pollinations_url: str | None = None
    filled_prompt: str | None = None


class ImageConcept(BaseModel):
    label: str
    viz_type: str
    description: str
    rationale: str
    pollinations_url: str | None = None
    filled_prompt: str | None = None
