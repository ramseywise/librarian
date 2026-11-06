import { cleanup, fireEvent, render } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Markdown } from "../Markdown";

afterEach(cleanup);

const renderMd = (body: string, lessonId = "course/mod/dir/lesson") =>
  render(<Markdown body={body} lessonId={lessonId} onOpenLesson={vi.fn()} onOpenConcept={vi.fn()} />).container;

describe("Markdown raw HTML sanitising", () => {
  it("strips scripts, styles, event handlers, inline style and javascript: URLs", () => {
    const c = renderMd([
      '<script>window.pwned = 1</script>',
      '<style>body { display: none }</style>',
      '<img src="x.png" onerror="alert(1)" style="position:fixed">',
      '<a href="javascript:alert(1)">bad link</a>',
      '<div onclick="alert(1)">clicky</div>',
      '<iframe src="https://example.com"></iframe>',
    ].join("\n\n"));
    expect(c.querySelector("script")).toBeNull();
    expect(c.querySelector("style")).toBeNull();
    expect(c.querySelector("iframe")).toBeNull();
    expect(c.textContent).not.toContain("pwned");
    expect(c.textContent).not.toContain("display: none");
    const img = c.querySelector("img")!;
    expect(img.getAttribute("onerror")).toBeNull();
    expect(img.getAttribute("style")).toBeNull();
    expect(c.querySelector("[onclick]")).toBeNull();
    expect(c.querySelector('a[href^="javascript"]')).toBeNull();
  });

  it("keeps img, table, details/summary, br, sup/sub and div/span classes", () => {
    const c = renderMd([
      '<div class="note" align="center"><span class="hl">hi</span></div>',
      '<table><tr><th>a</th></tr><tr><td colspan="2">b</td></tr></table>',
      '<details><summary>More</summary>\n\nhidden **text**\n\n</details>',
      'x<sup>2</sup> H<sub>2</sub>O<br>next',
      '<img src="https://example.com/a.png" alt="ext" width="300" height="200">',
    ].join("\n\n"));
    expect(c.querySelector("div.note")).not.toBeNull();
    expect(c.querySelector("span.hl")?.textContent).toBe("hi");
    expect(c.querySelector("table td")?.textContent).toBe("b");
    expect(c.querySelector("details > summary")?.textContent).toBe("More");
    expect(c.querySelector("details strong")?.textContent).toBe("text");
    expect(c.querySelector("sup")?.textContent).toBe("2");
    expect(c.querySelector("sub")?.textContent).toBe("2");
    expect(c.querySelector("br")).not.toBeNull();
    const img = c.querySelector('img[alt="ext"]')!;
    expect(img.getAttribute("src")).toBe("https://example.com/a.png");
    expect(img.getAttribute("width")).toBe("300");
  });

  it("rewrites relative raw-HTML and markdown images to the courses file API", () => {
    const c = renderMd('<img src="../images/fig.png" alt="raw">\n\n![md](./pics/b.png)');
    expect(c.querySelector('img[alt="raw"]')?.getAttribute("src")).toBe("/api/courses/files/course/mod/images/fig.png");
    expect(c.querySelector('img[alt="md"]')?.getAttribute("src")).toBe("/api/courses/files/course/mod/dir/pics/b.png");
  });

  it("still renders KaTeX math after sanitising", () => {
    const c = renderMd("Inline $a^2 + b^2$ and\n\n$$\n\\int_0^1 x\\,dx\n$$\n");
    expect(c.querySelectorAll(".katex").length).toBeGreaterThanOrEqual(2);
    expect(c.querySelector(".katex-display")).not.toBeNull();
  });

  it("keeps markdown table wrapping and heading anchors", () => {
    const c = renderMd("## Hello, World!\n\n| a | b |\n|---|---|\n| 1 | 2 |\n");
    expect(c.querySelector("h2")?.id).toBe("hello-world");
    expect(c.querySelector(".lp-table > table")).not.toBeNull();
  });

  it("keeps raw-HTML target anchors (id or name) so in-page links resolve", () => {
    const c = renderMd('<a id="top"></a><a name="old-style"></a>\n\n[up](#top) [old](#old-style)');
    expect(c.querySelector("#user-content-top")?.tagName).toBe("A");
    expect(c.querySelector("#user-content-old-style")?.tagName).toBe("A");
    expect(c.querySelector(".lp-deadlink")).toBeNull();
  });

  it("ids headings from nested text and suffixes repeats like GitHub", () => {
    const c = renderMd("## Step `2`: run it\n\n## Notes\n\n### Notes\n\n## Notes-1\n");
    expect([...c.querySelectorAll("h2, h3")].map((h) => h.id)).toEqual([
      "step-2-run-it", "notes", "notes-1", "notes-1-1",
    ]);
  });
});

describe("Markdown figures and source links", () => {
  it("hides a figure that is not on disk instead of showing a broken image", () => {
    const c = renderMd("before\n\n![fig](assets/sources/book/fig-1.png)\n\nafter", "course/mod/lesson");
    const img = c.querySelector("img")!;
    expect(img.getAttribute("src")).toBe("/api/courses/files/course/mod/assets/sources/book/fig-1.png");
    fireEvent.error(img);
    expect(c.querySelector("img")).toBeNull();
    expect(c.textContent).toContain("before");
  });

  it("keeps a figure that loads", () => {
    const c = renderMd("![fig](assets/ok.png)", "course/mod/lesson");
    expect(c.querySelector("img")).not.toBeNull();
  });

  const renderWithSources = (body: string) =>
    render(
      <Markdown body={body} lessonId="c/m/lesson" onOpenLesson={vi.fn()} onOpenConcept={vi.fn()}
        sourceLinks={{ "sources/a%20b.pdf": "c/m/sources/a b.pdf", "../sources/x.pdf": "c/sources/x.pdf" }} />,
    ).container;

  it("rewrites a served sources link to the API route and keeps the page anchor", () => {
    const c = renderWithSources("[book](sources/a%20b.pdf#page=3) [up](../sources/x.pdf)");
    const links = [...c.querySelectorAll("a")];
    expect(links[0].getAttribute("href")).toBe("/api/courses/sources/c/m/sources/a%20b.pdf#page=3");
    expect(links[1].getAttribute("href")).toBe("/api/courses/sources/c/sources/x.pdf");
    expect(links[0].getAttribute("target")).toBe("_blank");
  });

  it("renders an unavailable sources link as plain text, not a link", () => {
    const c = renderMd("[gone](sources/missing.pdf) and [dir](sources/)");
    expect(c.querySelector("a")).toBeNull();
    expect(c.querySelectorAll(".lp-deadlink").length).toBe(2);
    expect(c.textContent).toContain("gone");
  });
});
