"""What of a lesson may reach the voice, ported from the frontend's `speechText.ts`.

`drill_prompt` follows `drillPromptSpeech` rule for rule: a drill gives up its Prompt section or
nothing, and only when its whole shape is understood. Anything else refuses the mode for that
drill. The Solution, the Hints and even the Tests give a drill away, so what follows the Prompt
comes back separately, as `withheld`, for the model to critique against and never to read out.

`visible_text` follows `lessonSections`: a lesson with its collapsed blocks, spoiler sections and
answer keys taken out, for interview mode, which has no reason to see them.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

FRONTMATTER_RE = re.compile(r"\A﻿?---[ \t]*\r?\n.*?\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([^\s`]*)")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
TABLE_RULE_RE = re.compile(r"^ {0,3}\|?[ \t]*:?-{1,}:?[ \t]*(\|[ \t]*:?-{1,}:?[ \t]*)*\|?[ \t]*$")
SPOILER_LABEL_RE = re.compile(
    r"^(?:(?:reference|model|worked|sample|full|suggested)\s+)?"
    r"(?:solutions?|answers?|answer\s+key|hints?)(?:\s*\d+)?(?:\s*[:.—–-].*)?$",
    re.I,
)
SPOILER_LINE_RE = re.compile(
    r"^\s*(?:>\s*)?(?:\*\*|__)?(?:solutions?|answers?(?:\s+key)?|hints?)(?:\s*\d+)?"
    r"\s*(?:\*\*|__)?\s*:",
    re.I,
)
ANSWER_KEY_RE = re.compile(
    r"^\s*(?:\*\*|__)(?:answers?(?:\s+key)?(?:\s+\S+)?|rationale(?:\s+notes)?):?(?:\*\*|__)", re.I
)
DETAILS_OPEN_RE = re.compile(r"<details(?:\s|>)", re.I)
DETAILS_CLOSE_RE = re.compile(r"</details>", re.I)
COLLAPSED_RE = re.compile(r"<details(?:\s|>)|<summary(?:\s|>)", re.I)
MARKED_RE = re.compile(r"<details(?:\s|>)|<summary(?:\s|>)|<[^>]*(?:solution|answer)[^>]*>", re.I)
SUMMARY_RE = re.compile(r"<summary(?:\s[^>]*)?>(.*?)</summary>", re.I | re.S)
HINT_RE = re.compile(r"^hints?\b", re.I)
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+•]|(\d+)[.)])\s+(?:\[[ xX]\]\s+)?(.*)$")
RULE_RE = re.compile(r"^ {0,3}([-*_])[ \t]*(?:\1[ \t]*){2,}$")
LINK_DEF_RE = re.compile(r"^ {0,3}\[[^\]]+\]:\s+\S+")
INDENTED_RE = re.compile(r"^(?: {4}|\t)")
URL_RE = re.compile(r"\b(?:https?://|www\.)[^\s<>)\]]+", re.I)


@dataclass(frozen=True)
class DrillPrompt:
    """`text` is safe to say aloud. `reason` says why not, when `text` is empty."""

    text: str = ""
    withheld: str = ""
    reason: str = ""

    @property
    def ok(self) -> bool:
        return bool(self.text)


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _finish_sentence(line: str) -> str:
    return line if re.search(r"[.!?:;,][\"')\]]*$", line) else f"{line}."


def _speak_code(code: str) -> str:
    """A code span is spoken when it reads as words; `x[i]->y` is announced, not spelled."""
    symbols = len(re.sub(r"[\w\s.,()'\"-]", "", code))
    if symbols > 2 or symbols / max(len(code), 1) > 0.2:
        return "a code snippet"
    return code.replace("_", " ")


def _alt(match: re.Match[str]) -> str:
    alt = match.group(1).strip()
    return f"Image: {alt}." if alt else ""


def _link_label(match: re.Match[str]) -> str:
    label = match.group(1)
    return "a link" if re.match(r"(?:https?://|www\.)", label, re.I) else label


def _clean_prose(text: str) -> str:
    text = re.sub(r"\\\((.+?)\\\)", "a formula", text)
    text = re.sub(r"(^|[^\\$\w])\$(?=[^\s$])([^$\n]*?[^\s\\$])\$(?![\d$])", r"\1a formula", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", _alt, text)
    text = re.sub(r"!\[([^\]]*)\]\[[^\]]*\]", _alt, text)
    text = re.sub(r"<img\b[^>]*>", "", text, flags=re.I)
    text = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", _link_label, text)
    text = re.sub(r"\[([^\]]+)\]\[[^\]]*\]", r"\1", text)
    text = re.sub(r"<(?:https?://|mailto:)[^>]+>", "a link", text, flags=re.I)
    text = URL_RE.sub("a link", text)
    text = re.sub(r"<[^>\n]+>", "", text)
    text = re.sub(r"(\*\*|__)(?=\S)(.+?)\1", r"\2", text)
    text = re.sub(r"(^|[^\w*])\*(?=[^\s*])([^*\n]+?)\*(?![\w*])", r"\1\2", text)
    text = re.sub(r"(^|[^\w_])_(?=[^\s_])([^_\n]+?)_(?![\w_])", r"\1\2", text)
    text = re.sub(r"~~(.+?)~~", r"\1", text)
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|~$])", r"\1", text)
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    text = re.sub(r"\s*(?:→|->|=>)\s*", " to ", text)
    text = re.sub(r"[*#|~`]", " ", text)
    return html.unescape(text.replace("&lt;", "less than").replace("&gt;", "greater than"))


def clean_inline(line: str) -> str:
    parts = re.split(r"(`[^`\n]+`)", line)
    spoken = "".join(
        _speak_code(p[1:-1])
        if len(p) > 2 and p.startswith("`") and p.endswith("`")
        else _clean_prose(p)
        for p in parts
    )
    return re.sub(r"[ \t]{2,}", " ", spoken).strip()


def _drop_details(lines: list[str]) -> list[str]:
    """Remove every `<details>` block outside a fence. An unclosed block takes the rest of the
    text with it: what follows may well be its body."""
    out: list[str] = []
    fence: str | None = None
    i = 0
    while i < len(lines):
        line = lines[i]
        opened = FENCE_OPEN_RE.match(line)
        if fence is not None:
            if opened and opened[1].startswith(fence) and not opened[2]:
                fence = None
            out.append(line)
        elif opened:
            fence = opened[1]
            out.append(line)
        elif (m := DETAILS_OPEN_RE.search(line)) is None:
            out.append(line)
        else:
            if line[: m.start()].strip():
                out.append(line[: m.start()])
            depth = 0
            j = i
            rest = line[m.start() :]
            while True:
                depth += len(DETAILS_OPEN_RE.findall(rest)) - len(DETAILS_CLOSE_RE.findall(rest))
                if depth <= 0:
                    break
                j += 1
                if j >= len(lines):
                    return out
                rest = lines[j]
            after = rest[rest.lower().rfind("</details>") + len("</details>") :]
            if after.strip():
                out.append(after)
            i = j
        i += 1
    return out


def _is_list_context(lines: list[str], at: int) -> bool:
    for line in reversed(lines[:at]):
        if line.strip():
            return bool(
                re.match(r"^\s*(?:[-*+•]|\d+[.)])\s", line) or re.match(r"^(?: {2,}|\t)", line)
            )
    return False


def to_speech(markdown: str) -> str:
    """Markdown to text for speech: blocks announced or dropped, inline markup stripped."""
    source = FRONTMATTER_RE.sub("", markdown, count=1)
    source = re.sub(r"\r\n?", "\n", source)
    source = re.sub(r"<!--.*?(?:-->|\Z)", "", source, flags=re.S)
    source = re.sub(r"<(script|style)\b.*?(?:</\1>|\Z)", "", source, flags=re.S | re.I)
    lines = _drop_details(source.split("\n"))
    paragraphs: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            paragraphs.append(" ".join(current))
            current.clear()

    def block(text: str) -> None:
        flush()
        paragraphs.append(text)

    i = -1
    while (i := i + 1) < len(lines):
        line = lines[i]
        if not line.strip():
            flush()
            continue
        if fence := FENCE_OPEN_RE.match(line):
            i += 1
            while i < len(lines):
                close = FENCE_OPEN_RE.match(lines[i])
                if close and close[1].startswith(fence[1]) and not close[2]:
                    break
                i += 1
            language = fence[2].strip("{}")
            if re.fullmatch(r"math|latex", language, re.I):
                block("Equation omitted.")
            else:
                block(f"{language + ' code' if language else 'Code'} block omitted.")
            continue
        if re.match(r"^ {0,3}(\$\$|\\\[)", line):
            stripped = line.strip()
            closer = "$$" if stripped.startswith("$$") else "\\]"
            if closer not in stripped[2:]:
                i += 1
                while i < len(lines) and closer not in lines[i]:
                    i += 1
            block("Equation omitted.")
            continue
        following = lines[i + 1] if i + 1 < len(lines) else ""
        if "|" in line and TABLE_RULE_RE.match(following) and "-" in following:
            rows = 0
            i += 2
            while i < len(lines) and "|" in lines[i]:
                rows += 1
                i += 1
            i -= 1
            block(f"Table omitted, {rows} {'row' if rows == 1 else 'rows'}.")
            continue
        if INDENTED_RE.match(line) and not current and not _is_list_context(lines, i):
            while i + 1 < len(lines) and (
                INDENTED_RE.match(lines[i + 1])
                or (
                    not lines[i + 1].strip()
                    and i + 2 < len(lines)
                    and INDENTED_RE.match(lines[i + 2])
                )
            ):
                i += 1
            block("Code block omitted.")
            continue
        if RULE_RE.match(line):
            flush()
            continue
        if LINK_DEF_RE.match(line):
            continue
        if heading := HEADING_RE.match(line):
            if text := clean_inline(heading[2]):
                block(_finish_sentence(text))
            continue
        if item := LIST_ITEM_RE.match(line):
            flush()
            if text := clean_inline(item[2]):
                current.append(_finish_sentence(f"{item[1]}. {text}" if item[1] else text))
            continue
        if prose := clean_inline(re.sub(r"^\s*(?:>\s*)+", "", line)):
            current.append(prose)
    flush()
    out = (re.sub(r"\s{2,}", " ", re.sub(r"\s+([.,;:!?])", r"\1", p)).strip() for p in paragraphs)
    return "\n\n".join(p for p in out if re.search(r"\w", p))


def _mask_fences(lines: list[str]) -> list[str]:
    """A drill's lines with code fences blanked: nothing in an example can look like structure."""
    masked: list[str] = []
    fence: str | None = None
    for line in lines:
        opened = FENCE_OPEN_RE.match(line)
        if fence is not None:
            if opened and opened[1].startswith(fence) and not opened[2]:
                fence = None
            masked.append("")
        elif opened:
            fence = opened[1]
            masked.append("")
        else:
            masked.append(line)
    return masked


def _source_lines(body: str) -> list[str]:
    return re.sub(r"\r\n?", "\n", FRONTMATTER_RE.sub("", body, count=1)).split("\n")


def drill_prompt(body: str) -> DrillPrompt:
    """Exactly one Prompt heading, closed by a later heading, with a Solution recognised after it
    and no solution-like content inside it. Anything else is a refusal with its reason."""
    lines = _source_lines(body)
    masked = _mask_fences(lines)
    headings = [
        (at, clean_inline(m[2]).removesuffix(":").strip())
        for at, line in enumerate(masked)
        if (m := HEADING_RE.match(line))
    ]
    prompts = [h for h in headings if h[1].lower() == "prompt"]
    if not prompts:
        return DrillPrompt(reason="it has no Prompt section")
    if len(prompts) > 1:
        return DrillPrompt(reason="it has more than one Prompt section")
    start = prompts[0][0]
    end = next((at for at, _ in headings if at > start), None)
    if end is None:
        return DrillPrompt(reason="nothing marks where its Prompt section ends")
    if COLLAPSED_RE.search("\n".join(masked[:start])):
        return DrillPrompt(reason="it has a collapsed block before the Prompt")
    section = masked[start + 1 : end]
    if MARKED_RE.search("\n".join(section)):
        return DrillPrompt(reason="its Prompt section contains a collapsed or marked block")
    if any(SPOILER_LINE_RE.match(line) for line in section):
        return DrillPrompt(reason="its Prompt section appears to contain an answer")

    def names_solution(text: str) -> bool:
        return bool(SPOILER_LABEL_RE.match(text)) and not HINT_RE.match(text)

    rest = "\n".join(masked[end:])
    named = any(at > start and names_solution(text) for at, text in headings)
    summaries = (_strip_tags(m).strip() for m in SUMMARY_RE.findall(rest))
    if not named and not any(names_solution(s) for s in summaries):
        return DrillPrompt(reason="its Solution is not marked in a way this app recognises")
    text = to_speech("\n".join(lines[start + 1 : end]))
    if not text:
        return DrillPrompt(reason="its Prompt section has nothing to read")
    return DrillPrompt(text=text, withheld="\n".join(lines[end:]).strip())


def visible_text(body: str) -> str:
    """A lesson's prose without its collapsed blocks, spoiler sections or answer keys."""
    lines = _drop_details(_source_lines(body))
    kept: list[str] = []
    fence: str | None = None
    skipping = False
    for line in lines:
        opened = FENCE_OPEN_RE.match(line)
        if fence is not None:
            if opened and opened[1].startswith(fence) and not opened[2]:
                fence = None
        elif opened:
            fence = opened[1]
        elif heading := HEADING_RE.match(line):
            skipping = bool(SPOILER_LABEL_RE.match(clean_inline(heading[2]).removesuffix(":")))
        elif ANSWER_KEY_RE.match(line) or SPOILER_LINE_RE.match(line):
            skipping = True
        if not skipping:
            kept.append(line)
    return to_speech("\n".join(kept))
