import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { ChatPanel } from "../../ChatPanel";
import type { ChatMessage } from "../../../hooks/useChatStream";
import { RELEASE_EVENT } from "../../../utils/api";
import { GroundingLine } from "../GroundingLine";
import { CHANGED_LABEL, MISSING_LABEL, UNSUPPORTED_LABEL } from "../groundingLabels";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
// jsdom has no layout, so no scrollIntoView.
beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn();
});

const grounding = { cited: ["a", "b", "c"], pagesRead: ["a", "b", "c"], ungrounded: [] };

describe("GroundingLine", () => {
  it("lists a changed and a deleted page under their own labels, with a count", () => {
    const onOpenPage = vi.fn();
    render(
      <GroundingLine
        grounding={grounding}
        stale={{ b: { status: "changed", now: "b-renamed" }, c: { status: "missing" } }}
        onOpenPage={onOpenPage}
      />
    );
    const changed = screen.getByTestId("grounding-changed");
    expect(changed).toHaveTextContent(`${CHANGED_LABEL} (1):`);
    const chip = within(changed).getByRole("button", { name: `Open page b (${CHANGED_LABEL})` });
    expect(chip).toHaveAttribute("data-stale", "changed");
    // A renamed page opens under the id it has now.
    fireEvent.click(chip);
    expect(onOpenPage).toHaveBeenCalledWith("b-renamed");

    const missing = screen.getByTestId("grounding-missing");
    expect(missing).toHaveTextContent(`${MISSING_LABEL} (1):`);
    // A deleted page cannot be opened: its chip is text, not a button.
    expect(within(missing).queryByRole("button")).toBeNull();
    expect(within(missing).getByText("c")).toHaveAttribute("data-stale", "missing");

    // Only the unchanged page is still a plain source.
    expect(screen.getAllByRole("button", { name: /^Open page/ })).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Open page a" })).not.toHaveAttribute("data-stale");
  });

  it("lists a read page whose claim was not found under the third label", () => {
    expect(UNSUPPORTED_LABEL).toBe("read, support not found");
    render(
      <GroundingLine
        grounding={{ ...grounding, unsupported: ["b", "c"] }}
        stale={{ c: { status: "changed" } }}
        onOpenPage={vi.fn()}
      />
    );
    const row = screen.getByTestId("grounding-unsupported");
    expect(row).toHaveTextContent(`${UNSUPPORTED_LABEL} (1):`);
    expect(
      within(row).getByRole("button", { name: `Open page b (${UNSUPPORTED_LABEL})` })
    ).toHaveAttribute("data-unsupported", "true");
    // A page that has changed since is listed once, as changed.
    expect(within(screen.getByTestId("grounding-changed")).getByText("c")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Open page a" })).not.toHaveAttribute(
      "data-unsupported"
    );
  });

  it("shows no stale rows when nothing changed", () => {
    render(<GroundingLine grounding={grounding} />);
    expect(screen.queryByTestId("grounding-unsupported")).toBeNull();
    expect(screen.queryByTestId("grounding-changed")).toBeNull();
    expect(screen.queryByTestId("grounding-missing")).toBeNull();
  });
});

describe("ChatPanel stale citations", () => {
  const message: ChatMessage = {
    id: "a1",
    role: "assistant",
    content: "Chunk by headings [page:chunking].",
    streaming: false,
    grounding: {
      cited: ["chunking"],
      pagesRead: ["chunking"],
      ungrounded: [],
      sources: [{ id: "chunking", hash: "h1" }],
    },
  };
  const panel = (
    <ChatPanel
      messages={[message]}
      streaming={false}
      onSend={() => {}}
      onClearHighlights={() => {}}
      onOpenPage={() => {}}
    />
  );
  const answer = (status: string) =>
    new Response(JSON.stringify({ citations: [{ id: "chunking", status }] }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });

  it("asks the API about the stored hashes and marks a changed page's chips", async () => {
    const fetchMock = vi.fn(async () => answer("changed"));
    vi.stubGlobal("fetch", fetchMock);
    render(panel);

    await screen.findByTestId("grounding-changed");
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/chat/citations/check");
    expect(JSON.parse(init.body as string)).toEqual({
      citations: [{ id: "chunking", hash: "h1" }],
    });
    // The inline chip and the grounding-line chip both say so.
    expect(
      screen.getAllByRole("button", { name: `Open page chunking (${CHANGED_LABEL})` })
    ).toHaveLength(2);
  });

  it("rechecks when the content release changes", async () => {
    let status = "current";
    const fetchMock = vi.fn(async () => answer(status));
    vi.stubGlobal("fetch", fetchMock);
    render(panel);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    expect(screen.queryByTestId("grounding-missing")).toBeNull();

    status = "missing";
    window.dispatchEvent(new CustomEvent(RELEASE_EVENT, { detail: "r2" }));
    expect(await screen.findByTestId("grounding-missing")).toHaveTextContent(MISSING_LABEL);
  });

  it("leaves the chips alone when the check fails", async () => {
    const fetchMock = vi.fn(async () => new Response("nope", { status: 500 }));
    vi.stubGlobal("fetch", fetchMock);
    render(panel);
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expect(screen.getAllByRole("button", { name: "Open page chunking" })).toHaveLength(2);
  });
});
