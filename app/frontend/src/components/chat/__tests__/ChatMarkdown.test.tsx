import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ChatMarkdown } from "../ChatMarkdown";

afterEach(cleanup);

describe("ChatMarkdown", () => {
  it("renders markdown and replaces [page:id] markers with chips", () => {
    const onOpenPage = vi.fn();
    const { container } = render(
      <ChatMarkdown
        content={"**RRF** is parameter-free [page:rag-retrieval] and [page:ghost-page]."}
        ungrounded={["ghost-page"]}
        onOpenPage={onOpenPage}
      />
    );
    expect(container.querySelector("strong")?.textContent).toBe("RRF");
    expect(container.querySelector("p")?.textContent).not.toContain("[page:");

    fireEvent.click(screen.getByRole("button", { name: "Open page rag-retrieval" }));
    expect(onOpenPage).toHaveBeenCalledWith("rag-retrieval");

    const warn = screen.getByRole("button", { name: /ghost-page \(cited but not read\)/ });
    expect(warn).toHaveAttribute("data-ungrounded", "true");
  });

  it("leaves markers inside inline code and fences alone", () => {
    const { container } = render(
      <ChatMarkdown
        content={"Use `[page:inline-id]` like this:\n\n```\n[page:fenced-id]\n```\n\nsee [page:real]"}
        onOpenPage={() => {}}
      />
    );
    expect(container.querySelector("code")?.textContent).toBe("[page:inline-id]");
    expect(container.querySelector("pre")?.textContent).toContain("[page:fenced-id]");
    expect(screen.getAllByRole("button").map((b) => b.textContent)).toEqual(["real"]);
  });

  it("renders inert chips without onOpenPage", () => {
    const { container } = render(<ChatMarkdown content="see [page:foo]" />);
    expect(screen.queryByRole("button")).toBeNull();
    expect(container.querySelector("p")?.textContent).toBe("see foo");
  });

  it("opens external links in a new tab and escapes raw HTML", () => {
    const { container } = render(
      <ChatMarkdown content={"[docs](https://example.com) <b>raw</b>"} />
    );
    const a = container.querySelector("a")!;
    expect(a).toHaveAttribute("target", "_blank");
    expect(a).toHaveAttribute("rel", "noreferrer");
    expect(container.querySelector("b")).toBeNull();
  });

  it("renders an unclosed fence (mid-stream) as a code block", () => {
    const { container } = render(<ChatMarkdown content={"Here:\n\n```python\nprint(1"} />);
    expect(container.querySelector("pre code")?.textContent).toContain("print(1");
  });
});
