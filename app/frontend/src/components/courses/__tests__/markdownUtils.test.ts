import { describe, expect, it } from "vitest";
import { assetUrl, resolveRelative, slugify, splitSolution } from "../markdownUtils";

describe("resolveRelative", () => {
  it("resolves against the lesson's directory", () => {
    expect(resolveRelative("c/m/lesson", "other.md")).toBe("c/m/other.md");
    expect(resolveRelative("c/m/d/lesson", "../x/y.png")).toBe("c/m/x/y.png");
    expect(resolveRelative("c/m/lesson", "./a/./b.png")).toBe("c/m/a/b.png");
  });
  it("decodes escapes and tolerates malformed ones", () => {
    expect(resolveRelative("c/m/lesson", "my%20file.png")).toBe("c/m/my file.png");
    expect(resolveRelative("c/m/lesson", "bad%zz.png")).toBe("c/m/bad%zz.png");
  });
});

describe("assetUrl", () => {
  it("maps only lesson-relative paths", () => {
    expect(assetUrl("c/m/l", "img/a.png")).toBe("/api/courses/files/c/m/img/a.png");
    expect(assetUrl("c/m/l", "https://x.org/a.png")).toBe("https://x.org/a.png");
    expect(assetUrl("c/m/l", "/static/a.png")).toBe("/static/a.png");
    expect(assetUrl("c/m/l", "data:image/png;base64,AA")).toBe("data:image/png;base64,AA");
  });
  it("drops protocol-relative (off-site) URLs", () => {
    expect(assetUrl("c/m/l", "//evil.example/x.png")).toBe("");
  });
});

describe("slugify", () => {
  it("builds GitHub-style anchors", () => {
    expect(slugify("Hello, World!")).toBe("hello-world");
    expect(slugify("Step 2: run it")).toBe("step-2-run-it");
    expect(slugify("  Multiple   spaces  ")).toBe("multiple-spaces");
  });
});

describe("splitSolution", () => {
  it("splits the first <details> block, with or without attributes", () => {
    expect(splitSolution("Q\n<details><summary>Hint</summary>\nA\n</details>\nZ")).toEqual(["Q\n", "\nA\n", "\nZ"]);
    expect(splitSolution("Q\n<details open>\n<summary>S</summary>A</details>")).toEqual(["Q\n", "A", ""]);
  });

  it("ignores <details> shown inside a code fence", () => {
    const body = "```html\n<details>example</details>\n```\n\n<details>real</details>";
    const out = splitSolution(body);
    expect(out?.[1]).toBe("real");
    expect(out?.[0]).toContain("example");
    expect(splitSolution("~~~\n<details>x</details>\n~~~\n")).toBeNull();
  });
});
