import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { ChatPanel } from "../ChatPanel";
import type { ChatMessage } from "../../hooks/useChatStream";

afterEach(cleanup);
// jsdom has no layout, so no scrollIntoView.
beforeAll(() => {
  Element.prototype.scrollIntoView = vi.fn();
});

const base = { onSend: () => {}, onClearHighlights: () => {} };
const reply = (extra: Partial<ChatMessage>): ChatMessage => ({
  id: "a1",
  role: "assistant",
  content: "",
  streaming: false,
  ...extra,
});

describe("ChatPanel", () => {
  it("hides stop and clear until the host wires them", () => {
    render(<ChatPanel {...base} messages={[]} streaming />);
    expect(screen.queryByRole("button", { name: "Stop generating" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Clear conversation" })).toBeNull();
    expect(screen.getByRole("log")).toHaveAttribute("aria-live", "polite");
    expect(screen.getByLabelText("Ask the wiki agent")).toBeInTheDocument();
  });

  it("swaps send for stop while streaming and calls onStop", () => {
    const onStop = vi.fn();
    render(<ChatPanel {...base} messages={[reply({ streaming: true })]} streaming onStop={onStop} />);
    expect(screen.queryByRole("button", { name: "Send" })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Stop generating" }));
    expect(onStop).toHaveBeenCalled();
  });

  it("clear is disabled when empty and clears otherwise", () => {
    const onClear = vi.fn();
    const { rerender } = render(<ChatPanel {...base} messages={[]} streaming={false} onClear={onClear} />);
    expect(screen.getByRole("button", { name: "Clear conversation" })).toBeDisabled();
    rerender(<ChatPanel {...base} messages={[reply({ content: "x" })]} streaming={false} onClear={onClear} />);
    fireEvent.click(screen.getByRole("button", { name: "Clear conversation" }));
    expect(onClear).toHaveBeenCalled();
  });

  it("shows the stopped note with the partial text, and grounding ids as chips", () => {
    const onOpenPage = vi.fn();
    render(
      <ChatPanel
        {...base}
        streaming={false}
        onOpenPage={onOpenPage}
        messages={[
          reply({ id: "a1", content: "partial **bold**", error: true, stopped: true, note: "stopped" }),
          reply({
            id: "a2",
            content: "answer [page:x]",
            grounding: { cited: ["x", "y"], pagesRead: ["x"], ungrounded: ["y"] },
          }),
        ]}
      />
    );
    expect(screen.getByText("stopped")).toBeInTheDocument();
    expect(screen.getByText("bold").tagName).toBe("STRONG");
    expect(screen.getAllByRole("button", { name: "Open page x" })).toHaveLength(2);
    fireEvent.click(screen.getByRole("button", { name: /Open page y/ }));
    expect(onOpenPage).toHaveBeenCalledWith("y");
  });

  it("keeps user messages as plain text", () => {
    render(
      <ChatPanel
        {...base}
        streaming={false}
        messages={[{ id: "u1", role: "user", content: "**not bold** [page:z]", streaming: false }]}
      />
    );
    expect(screen.getByText("**not bold** [page:z]")).toBeInTheDocument();
  });
});
