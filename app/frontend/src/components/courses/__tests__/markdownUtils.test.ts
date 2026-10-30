import { createElement } from "react";
import { describe, expect, it } from "vitest";
import { assetUrl, headingId, resolveRelative } from "../markdownUtils";

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
});

describe("headingId", () => {
  it("builds GitHub-style anchors from nested children", () => {
    expect(headingId("Hello, World!")).toBe("hello-world");
    expect(headingId(["Step ", createElement("code", null, "2"), ": run it"])).toBe("step-2-run-it");
    expect(headingId("  Multiple   spaces  ")).toBe("multiple-spaces");
  });
});
