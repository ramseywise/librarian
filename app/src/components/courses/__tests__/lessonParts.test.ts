import { describe, expect, it } from "vitest";
import { splitLesson } from "../lessonParts";

const code = ["```python", "a = 1", "b = 2", "c = a + b", "print(c)", "```"];
const note = [
  "Opening.", "",
  "## Idea", "", "Words.", "", ...code, "", "```text", "3", "```", "", "After.", "",
  "```python", "x = 1", "```", "",
  "```mermaid", "graph TD", "A-->B", "B-->C", "C-->D", "```", "",
  "## Pitfalls", "", "- One.", "",
  "## Try it", "", "1. Do it.", "", ...code, "", "---", "",
  "## Interview checklist", "", "| Prompt | Answer |", "|---|---|", "| Q | A |", "", "---", "",
  "## Next", "", "On to the next.",
].join("\n");

describe("splitLesson", () => {
  const parts = splitLesson(note);

  it("moves a code block and its output out of the lecture, leaving a link", () => {
    expect(parts.codeCount).toBe(1);
    expect(parts.lecture).toContain("[Code 1 in Labs →](#code-1)");
    expect(parts.lecture).not.toContain("c = a + b");
    expect(parts.lecture).not.toContain("```text");
    expect(parts.code).toMatch(/^## Code from this lesson\n\n### Idea\n\n<a id="code-1"><\/a>/);
    expect(parts.code).toContain("c = a + b");
    expect(parts.code).toContain("```text\n3\n```");
  });

  it("keeps short snippets, diagrams and the other sections in the lecture", () => {
    expect(parts.lecture).toContain("x = 1");
    expect(parts.lecture).toContain("```mermaid");
    expect(parts.lecture).toContain("## Pitfalls");
    expect(parts.lecture).toContain("## Next");
    expect(parts.lecture).toContain("After.");
  });

  it("sends Try it to exercises with its code, and the checklist to review", () => {
    expect(parts.exercises).toMatch(/^## Try it/);
    expect(parts.exercises).toContain("c = a + b");
    expect(parts.exercises).not.toContain("---");
    expect(parts.review).toBe("## Review questions\n\n| Prompt | Answer |\n|---|---|\n| Q | A |");
    expect(parts.lecture).not.toContain("Do it.");
    expect(parts.lecture).not.toContain("| Q | A |");
  });

  it("returns empty parts for a note with only prose", () => {
    expect(splitLesson("## A\n\nText.")).toEqual({ lecture: "## A\n\nText.", review: "", exercises: "", code: "", codeCount: 0 });
  });
});
