import { describe, expect, it } from "vitest";
import { chunkForSpeech, drillPromptSpeech, lessonSections, toSpeech } from "../speechText";

describe("toSpeech", () => {
  it.each<[string, string, string]>([
    ["frontmatter", "---\ntitle: Hidden\nsummary: x\n---\nVisible.", "Visible."],
    ["no frontmatter", "A line.\n\n---\n\nNext.", "A line.\n\nNext."],
    ["bold, italic, strike", "**Bold** and *soft* and _low_ and ~~gone~~.", "Bold and soft and low and gone."],
    ["snake_case stays", "Call snake_case_name now.", "Call snake_case_name now."],
    ["multiplication stars", "Take 2 * 3 * 4.", "Take 2 3 4."],
    ["heading", "## Big Idea", "Big Idea."],
    ["heading with hashes", "## Big Idea ##", "Big Idea."],
    ["bullets", "- one\n- two", "one.\n\ntwo."],
    ["numbered", "1. first\n2. second", "1. first.\n\n2. second."],
    ["task list", "- [x] done item", "done item."],
    ["blockquote", "> quoted line", "quoted line"],
    ["em dash as pause", "This — that", "This, that"],
    ["arrow", "a -> b", "a to b"],
    ["fence with language", "Before.\n\n```python\nprint('x')\n```\n\nAfter.", "Before.\n\npython code block omitted.\n\nAfter."],
    ["fence bare", "```\n$ rm -rf /\n```", "Code block omitted."],
    ["tilde fence", "~~~js\nlet a;\n~~~", "js code block omitted."],
    ["unclosed fence", "```ts\nconst a = 1;\nconst b = 2;", "ts code block omitted."],
    ["fence holding a heading", "```md\n## Not a heading\n```", "md code block omitted."],
    ["math fence", "```math\nx^2\n```", "Equation omitted."],
    ["indented code", "Intro.\n\n    let x = 1;\n    let y = 2;\n\nOutro.", "Intro.\n\nCode block omitted.\n\nOutro."],
    ["indent under a list is prose", "- item\n\n    continued words", "item.\n\ncontinued words"],
    ["short code span", "Use `groupBy` here.", "Use groupBy here."],
    ["symbol code span", "Use `x[i]->y{}` here.", "Use a code snippet here."],
    ["display math", "$$\n\\sum_{i} x_i\n$$", "Equation omitted."],
    ["display math one line", "$$E = mc^2$$", "Equation omitted."],
    ["bracket math", "\\[\na+b\n\\]", "Equation omitted."],
    ["inline math", "Where $x_i^2$ grows.", "Where a formula grows."],
    ["paren math", "Where \\(x^2\\) grows.", "Where a formula grows."],
    ["dollars are not math", "It costs $5 and $10.", "It costs $5 and $10."],
    ["table", "| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n\nAfter.", "Table omitted, 2 rows.\n\nAfter."],
    ["table one row", "a | b\n--- | ---\n1 | 2", "Table omitted, 1 row."],
    ["image with alt", "![a diagram of a tree](t.png)", "Image: a diagram of a tree."],
    ["image no alt", "Before ![](t.png) after", "Before after"],
    ["html image", '<img src="t.png" alt="a chart">', "Image: a chart."],
    ["link", "See [the docs](https://example.com/a).", "See the docs."],
    ["url label", "See [https://example.com](https://example.com).", "See a link."],
    ["bare url", "See https://example.com/a?b=c now.", "See a link now."],
    ["autolink", "See <https://example.com>.", "See a link."],
    ["wikilink", "See [[Some Page]] and [[Page|alias]].", "See Some Page and alias."],
    ["footnote mark", "A claim[^1].", "A claim."],
    ["html stripped", "A <b>bold</b> word.", "A bold word."],
    ["comment", "A<!-- hidden note --> word.", "A word."],
    ["entities", "x &lt; y &amp; z", "x less than y & z"],
    ["rule only", "---", ""],
    ["punctuation only", "***", ""],
    ["details named", "Top.\n\n<details>\n<summary>Worked steps</summary>\n\nInner body.\n\n</details>\n\nEnd.", "Top.\n\nCollapsed section, not read: Worked steps.\n\nEnd."],
    ["details unnamed", "<details>\nInner body.\n</details>", "Collapsed section, not read."],
    ["details nested", "<details><summary>S</summary>\n<details>\nInner.\n</details>\nOuter.\n</details>\nEnd.", "Collapsed section, not read: S.\n\nEnd."],
    ["details unclosed drops the rest", "Top.\n\n<details>\nInner.\n\nMore inner.", "Top.\n\nCollapsed section, not read."],
    ["details in a fence is code", "```html\n<details>\n```\n\nEnd.", "html code block omitted.\n\nEnd."],
  ])("%s", (_name, input, expected) => {
    expect(toSpeech(input)).toBe(expected);
  });
});

describe("chunkForSpeech", () => {
  it("keeps every piece under the limit and loses no words", () => {
    const sentence = "This sentence is about twelve words long and it keeps on going. ";
    const text = `${sentence.repeat(20)}\n\n${sentence.repeat(3)}`;
    const chunks = chunkForSpeech(text, 180);
    expect(chunks.length).toBeGreaterThan(5);
    expect(Math.max(...chunks.map((c) => c.length))).toBeLessThanOrEqual(180);
    expect(chunks.join(" ").split(/\s+/)).toEqual(text.trim().split(/\s+/));
  });

  it("breaks a sentence with no stops at commas and then at spaces", () => {
    const commas = Array(30).fill("a short clause here").join(", ");
    expect(Math.max(...chunkForSpeech(commas, 100).map((c) => c.length))).toBeLessThanOrEqual(100);
    const words = Array(60).fill("word").join(" ");
    const chunks = chunkForSpeech(words, 50);
    expect(Math.max(...chunks.map((c) => c.length))).toBeLessThanOrEqual(50);
    expect(chunks.join(" ")).toBe(words);
  });

  it("returns nothing for nothing", () => {
    expect(chunkForSpeech("")).toEqual([]);
  });
});

describe("lessonSections", () => {
  it("makes one section per h1-h3 and keeps deeper headings inside", () => {
    const sections = lessonSections("Opening.\n\n## One\n\nFirst.\n\n#### Deep\n\nInner.\n\n### Two\n\nSecond.", "The Title");
    expect(sections.map((s) => s.heading)).toEqual(["The Title", "One", "Two"]);
    expect(sections[1].text).toContain("Deep");
  });

  it("does not take a heading from a code fence or from a collapsed block", () => {
    const sections = lessonSections("## One\n\n```md\n## Fake\n```\n\n<details>\n\n## Inner\n\nSecret words.\n\n</details>", "T");
    expect(sections.map((s) => s.heading)).toEqual(["One"]);
    expect(sections[0].text).not.toContain("Secret");
  });

  it.each(["Solution", "Solutions", "Answer", "Answer key", "Hints", "Hint 2", "Reference solution", "Solution: a walk-through"])(
    "announces and skips a section headed %s",
    (heading) => {
      const [, section] = lessonSections(`## Task\n\nDo it.\n\n## ${heading}\n\nThe secret words.`, "T");
      expect(section.text).toMatch(/Not read\.$/);
      expect(section.text).not.toContain("secret");
    }
  );

  it("drops an answer key and its rationale until the next heading", () => {
    const sections = lessonSections("### Q1\n\nWhich?\n\n**Answers 1-5** B C A D A\n\n**Rationale notes**\n\nBecause.\n\n### Q2\n\nAnd?", "T");
    const spoken = sections.map((s) => s.text).join(" ");
    expect(spoken).toContain("Which?");
    expect(spoken).toContain("And?");
    expect(spoken).not.toMatch(/B C A D|Because/);
  });
});

// The two shapes real drills come in, with invented text. Everything after the Prompt is a spoiler.
const SECRET = /secret|sealed|unlock|assert|tumbler/i;
const WITH_HEADINGS = `---
track: python
---
# Lock picker

## Prompt

Build a counter that **tracks** keys in a \`Counter\`.

- Keep it short.
- See [the guide](https://example.com/guide).

## Starter

\`\`\`python
def tumbler(): ...
\`\`\`

## Tests

\`\`\`python
assert tumbler() == 1
\`\`\`

## Hints

<details>
<summary>Hint 1</summary>

The secret is a loop.

</details>

## Solution

<details>
<summary>Solution: reference approach</summary>

The sealed approach is to unlock it.

</details>

## Notes

Further secret reading.
`;
const SUMMARY_ONLY = `## Prompt

Review this config and list what is wrong.

## Tests

Should flag the unlocked tumbler and the secret bucket.

<details>
<summary>Solution</summary>

The sealed answer.

</details>

## Notes

More secret notes.
`;

describe("drillPromptSpeech", () => {
  it.each([
    ["Solution heading and collapsed block", WITH_HEADINGS],
    ["collapsed Solution with no heading", SUMMARY_ONLY],
    ["CRLF line ends", WITH_HEADINGS.replace(/\n/g, "\r\n")],
    ["lowercase headings", WITH_HEADINGS.replace("## Prompt", "## prompt").replace("## Solution", "## solution")],
    ["h3 headings", WITH_HEADINGS.replace("## Prompt", "### Prompt").replace("## Solution", "### Solution")],
    ["heading with colon", WITH_HEADINGS.replace("## Prompt", "## Prompt:")],
    ["bold heading", WITH_HEADINGS.replace("## Prompt", "## **Prompt**")],
    ["Answer in place of Solution", WITH_HEADINGS.replace("## Solution", "## Answer").replace("Solution: reference", "Answer: reference")],
    ["open details", SUMMARY_ONLY.replace("<details>", "<details open>")],
    ["attributes and markup in summary", SUMMARY_ONLY.replace("<summary>Solution</summary>", '<summary class="x"><b>Solution</b></summary>')],
    ["answer key summary", SUMMARY_ONLY.replace("<summary>Solution</summary>", "<summary>Answer key</summary>")],
  ])("reads only the prompt: %s", (_name, body) => {
    const result = drillPromptSpeech(body);
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.text).not.toMatch(SECRET);
    expect(result.text).toMatch(/^(Build a counter|Review this config)/);
  });

  it("cleans the prompt it reads", () => {
    const result = drillPromptSpeech(WITH_HEADINGS);
    expect(result).toEqual({
      ok: true,
      text: "Build a counter that tracks keys in a Counter.\n\nKeep it short.\n\nSee the guide.",
    });
  });

  it("does not take a Prompt heading from inside a code fence", () => {
    const body = "## Starter\n\n```md\n## Prompt\n\nsecret\n```\n\n## Solution\n\nsealed";
    expect(drillPromptSpeech(body).ok).toBe(false);
  });

  it.each<[string, string, RegExp]>([
    ["no Prompt heading", "## Task\n\nDo it.\n\n## Solution\n\nsecret", /no Prompt section/],
    ["two Prompt headings", "## Prompt\n\nA.\n\n## Prompt\n\nsecret\n\n## Solution\n\nsealed", /more than one/],
    ["Prompt runs to the end", "## Solution\n\nsecret\n\n## Prompt\n\nDo it.", /ends/],
    ["no marked Solution", "## Prompt\n\nDo it.\n\n## Notes\n\nsecret", /not marked/],
    ["unrecognised Solution name", "## Prompt\n\nDo it.\n\n## Walkthrough\n\nsecret", /not marked/],
    ["only hints marked", "## Prompt\n\nDo it.\n\n## Hints\n\n<details><summary>Hint 1</summary>secret</details>", /not marked/],
    ["Solution collapsed inside the Prompt", "## Prompt\n\nDo it.\n\n<details>\n<summary>Solution</summary>\nsecret\n</details>\n\n## Notes\n\nx", /collapsed/],
    ["unnamed collapse inside the Prompt", "## Prompt\n\nDo it.\n\n<details>\nsecret\n</details>\n\n## Solution\n\nx", /collapsed/],
    ["custom element in the Prompt", "## Prompt\n\nDo it.\n\n<div class=\"solution\">secret</div>\n\n## Solution\n\nx", /marked block/],
    ["collapse before the Prompt", "<details>\nsecret\n</details>\n\n## Prompt\n\nDo it.\n\n## Solution\n\nx", /before the Prompt/],
    ["answer line in the Prompt", "## Prompt\n\nDo it.\n\n**Answer:** secret\n\n## Solution\n\nx", /contain an answer/],
    ["solution line in the Prompt", "## Prompt\n\nDo it.\n\nSolution: secret\n\n## Notes\n\nx", /contain an answer/],
    ["empty Prompt", "## Prompt\n\n## Solution\n\nsecret", /nothing to read/],
  ])("reads nothing and says why: %s", (_name, body, reason) => {
    const result = drillPromptSpeech(body);
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.reason).toMatch(reason);
  });

  it("allows the ordinary words solution and answer in a prompt", () => {
    const body = "## Prompt\n\nCompare your solution to the answer the tests expect.\n\n## Solution\n\nsecret";
    expect(drillPromptSpeech(body)).toEqual({ ok: true, text: "Compare your solution to the answer the tests expect." });
  });
});
