import { fireEvent, render, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { GlossaryTerm as Term } from "../../../types";
import { Markdown } from "../Markdown";

const term = (id: string, label: string, aliases: string[] = []): Term => ({
  id, label, aliases, def: `${label} defined.`, page: null, mentions: 1,
});
const TERMS = [term("rag", "RAG", ["retrieval-augmented generation"]), term("bm25", "BM25"), term("rerank", "reranking", ["re-rank"])];

function show(body: string, terms?: Term[]) {
  const { container } = render(
    <Markdown body={body} lessonId="c/m/l" onOpenLesson={() => undefined} onOpenConcept={() => undefined} terms={terms ?? TERMS} />,
  );
  return { container, marks: () => [...container.querySelectorAll(".gloss-term")] };
}
const words = (marks: Element[]) => marks.map((m) => m.firstChild?.textContent);

describe("glossary terms in rendered markdown", () => {
  it("marks only the first mention in a section, per term", () => {
    const { marks } = show("RAG uses BM25.\n\nRAG again, and BM25 again.");
    expect(words(marks())).toEqual(["RAG", "BM25"]);
  });

  it("starts over at each heading", () => {
    const { marks } = show("RAG one.\n\n## Next\n\nRAG two. RAG three.\n\n### Deeper\n\nRAG four.");
    expect(words(marks())).toEqual(["RAG", "RAG", "RAG"]);
  });

  it("never marks a heading, and the heading doesn't use up the section's mark", () => {
    const { container, marks } = show("## What RAG is\n\nRAG retrieves.");
    expect(container.querySelector("h2 .gloss-term")).toBeNull();
    expect(container.querySelector("h2")?.id).toBe("what-rag-is");
    expect(words(marks())).toEqual(["RAG"]);
  });

  it("leaves code blocks, inline code and math alone", () => {
    const { container, marks } = show("`RAG` inline.\n\n```\nRAG in a block\n```\n\n$RAG$\n\nProse RAG.");
    expect(container.querySelector("pre .gloss-term, code .gloss-term, .katex .gloss-term")).toBeNull();
    expect(words(marks())).toEqual(["RAG"]);
  });

  it("never nests in a link", () => {
    const { container, marks } = show("[RAG docs](https://example.com) and [[x]] then RAG.");
    expect(container.querySelector("a .gloss-term")).toBeNull();
    expect(words(marks())).toEqual(["RAG"]);
  });

  it("matches like the backend: acronyms exact, the rest any case, whole words only", () => {
    expect(words(show("rag cloth and fragrant ragged.").marks())).toEqual([]);
    expect(words(show("Reranking helps.").marks())).toEqual(["Reranking"]);
    expect(words(show("We re-rank here.").marks())).toEqual(["re-rank"]);
  });

  it("an alias counts as the term", () => {
    const { marks } = show("Retrieval-augmented generation, or RAG.");
    expect(words(marks())).toEqual(["Retrieval-augmented generation"]);
  });

  it("marks across inline formatting and keeps the sentence", () => {
    const { container, marks } = show("Plain **bold RAG** tail.");
    expect(words(marks())).toEqual(["RAG"]);
    expect(container.querySelector("strong .gloss-term")).not.toBeNull();
  });

  it("raw HTML can't forge a term", () => {
    const { marks, container } = show('<gloss-term data-def="<img src=x>">forged</gloss-term>\n\nNothing here.', []);
    expect(marks()).toEqual([]);
    expect(container.querySelector("img")).toBeNull();
    const second = show('<gloss-term data-def="evil">forged</gloss-term>');
    expect(words(second.marks())).toEqual([]);
  });

  it("no terms, no marks", () => {
    const { container } = render(
      <Markdown body="RAG here." lessonId="c/m/l" onOpenLesson={() => undefined} onOpenConcept={() => undefined} />,
    );
    expect(container.querySelector(".gloss-term")).toBeNull();
  });
});

describe("definition popover", () => {
  it("opens on hover, closes on leave", async () => {
    const { marks } = show("RAG here.");
    const [mark] = marks();
    const pop = within(mark as HTMLElement).getByRole("tooltip", { hidden: true });
    expect(pop).toHaveAttribute("hidden");
    fireEvent.mouseEnter(mark);
    expect(pop).not.toHaveAttribute("hidden");
    expect(pop).toHaveTextContent("RAG defined.");
    fireEvent.mouseLeave(mark);
    expect(pop).not.toHaveAttribute("hidden"); // Time to cross the gap onto the definition.
    await waitFor(() => expect(pop).toHaveAttribute("hidden"));
  });

  it("is reachable by keyboard and described to a screen reader", async () => {
    const user = userEvent.setup();
    const { marks } = show("RAG here.");
    await user.tab();
    const [mark] = marks();
    expect(document.activeElement).toBe(mark);
    const pop = within(mark as HTMLElement).getByRole("tooltip");
    expect(mark).toHaveAttribute("aria-describedby", pop.id);
    await user.tab();
    expect(pop).toHaveAttribute("hidden");
  });

  it("Escape closes it and is claimed, so the chat panel stays open", () => {
    const { marks } = show("RAG here.");
    const [mark] = marks();
    fireEvent.focus(mark);
    const notPrevented = fireEvent.keyDown(document.body, { key: "Escape" });
    expect(notPrevented).toBe(false);
    expect(within(mark as HTMLElement).getByRole("tooltip", { hidden: true })).toHaveAttribute("hidden");
    expect(fireEvent.keyDown(document.body, { key: "Escape" })).toBe(true);
  });

  it("closes on scroll", () => {
    const { marks } = show("RAG here.");
    const [mark] = marks();
    fireEvent.mouseEnter(mark);
    fireEvent.scroll(window);
    expect(within(mark as HTMLElement).getByRole("tooltip", { hidden: true })).toHaveAttribute("hidden");
  });
});
