import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import { AnswerRating } from "../AnswerRating";
import { ReportButton } from "../ReportButton";
import { MyFeedback } from "../../account/MyFeedback";
import { FeedbackSummaryView } from "../../account/FeedbackSummary";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const mockFetch = (fn: (url: string, init?: RequestInit) => Promise<Response>) => {
  const m = vi.fn(fn);
  vi.stubGlobal("fetch", m);
  return m;
};
const posts = (m: ReturnType<typeof mockFetch>) =>
  m.mock.calls.filter(([, i]) => i?.method === "POST").map(([u, i]) => [u, JSON.parse(String(i?.body))]);

describe("AnswerRating", () => {
  it("posts the rating and toggles aria-pressed", async () => {
    const m = mockFetch(async () => json({ id: "f1" }, 201));
    render(<AnswerRating answerId="abc" />);
    const up = screen.getByRole("button", { name: "Good answer" });
    expect(up).toHaveAttribute("aria-pressed", "false");
    await userEvent.click(up);
    await waitFor(() => expect(up).toHaveAttribute("aria-pressed", "true"));
    expect(posts(m)).toEqual([["/api/feedback", { kind: "answer", target: "abc", rating: 1 }]]);
    expect(screen.getByRole("status")).toHaveTextContent("Thanks");
    await userEvent.click(screen.getByRole("button", { name: "Bad answer" }));
    await waitFor(() => expect(screen.getByRole("button", { name: "Bad answer" })).toHaveAttribute("aria-pressed", "true"));
    expect(up).toHaveAttribute("aria-pressed", "false");
    expect(posts(m)[1][1]).toMatchObject({ rating: -1 });
  });

  it("sends a note with the down-rating", async () => {
    const m = mockFetch(async () => json({ id: "f1" }, 201));
    render(<AnswerRating answerId="abc" />);
    await userEvent.click(screen.getByRole("button", { name: "Bad answer" }));
    await userEvent.type(await screen.findByLabelText("Note on this answer"), "wrong page");
    await userEvent.click(screen.getByRole("button", { name: "Send note" }));
    await waitFor(() => expect(posts(m)).toHaveLength(2));
    expect(posts(m)[1][1]).toEqual({ kind: "answer", target: "abc", rating: -1, body: "wrong page" });
  });

  it("shows an error inline and stays unpressed", async () => {
    mockFetch(async () => json({ detail: "nope" }, 400));
    render(<AnswerRating answerId="abc" />);
    await userEvent.click(screen.getByRole("button", { name: "Good answer" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("nope");
    expect(screen.getByRole("button", { name: "Good answer" })).toHaveAttribute("aria-pressed", "false");
  });
});

describe("ReportButton", () => {
  it.each([
    ["page", "rag/rrf"],
    ["lesson", "ai/rag/l1"],
  ] as const)("posts kind and target for a %s", async (kind, target) => {
    const m = mockFetch(async () => json({ id: "f2" }, 201));
    render(<ReportButton kind={kind} target={target} />);
    await userEvent.click(screen.getByRole("button", { name: new RegExp(`this ${kind}`) }));
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    await userEvent.type(screen.getByRole("textbox"), "typo");
    expect(screen.getByText("4/2000")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByRole("status")).toHaveTextContent("Thanks");
    expect(posts(m)).toEqual([["/api/feedback", { kind, target, body: "typo" }]]);
  });
});

describe("MyFeedback", () => {
  it("deletes a row via DELETE and removes it", async () => {
    const m = mockFetch(async (_u, init) =>
      init?.method === "DELETE"
        ? new Response(null, { status: 204 })
        : json([{ id: "f1", ts: "2026-11-01T10:00:00Z", kind: "page", target: "rag/rrf", rating: null, body: "fix this" }]),
    );
    render(<MyFeedback />);
    expect(await screen.findByText("fix this")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /Delete my page feedback/ }));
    await waitFor(() => expect(screen.queryByText("fix this")).toBeNull());
    expect(m.mock.calls.some(([u, i]) => u === "/api/feedback/f1" && i?.method === "DELETE")).toBe(true);
  });
});

describe("FeedbackSummaryView", () => {
  it("renders lists, notes, and none yet for missing ones", async () => {
    mockFetch(async () =>
      json({
        answers_down: [{ target: "ans1", count: 3, notes: ["bad cite"], extra: 1 }],
        lesson_miss_rates: [{ target: "ai/l1", count: 10, misses: 4, miss_rate: 0.4 }],
        page_reads: [{ target: "rag/rrf", read: 5, cited: 2, ungrounded: 1 }],
      }),
    );
    render(<FeedbackSummaryView />);
    expect(await screen.findByText("ans1")).toBeInTheDocument();
    expect(screen.getByText("bad cite")).toBeInTheDocument();
    expect(screen.getByText("40%")).toBeInTheDocument();
    expect(screen.getByRole("group", { name: "Pages reported" })).toHaveTextContent("none yet");
    expect(screen.getByRole("group", { name: "Unanswered queries" })).toHaveTextContent("none yet");
  });
});
