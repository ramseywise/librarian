import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetCourseCachesForTests } from "../../../hooks/useCourses";
import type { LabChatContext } from "../../../hooks/useChatStream";
import { LabsView } from "../LabsView";
import { LabWorkspace } from "../LabWorkspace";
import type { LabDetail, LabsList } from "../types";

const ID = "data-science/01-classical-ml/practice/importance_noise.py";
const note = { id: "data-science/01-classical-ml/notes/importance", title: "Feature Importance", section: "", kind: "reading", summary: "S" };
const outline = {
  id: ID, title: "Importance noise", course: "data-science", module: "01-classical-ml",
  path: "practice/importance_noise.py", purpose: "Permutation importance against noise.", pattern: "evaluation",
  language: "python", runsOffline: true, hasRun: true, hasCheck: true,
};
const list: LabsList = {
  canRun: true,
  labs: [
    { ...outline, notes: [note] },
    { ...outline, id: "gen-ai/01-rag/practice/widget.ts", title: "Widget", course: "gen-ai", module: "01-rag", language: "typescript", hasRun: false, hasCheck: false, notes: [] },
  ],
};
const detail = (canRun: boolean): LabDetail => ({
  ...outline, licence: "course", verifiedBy: "uv run importance_noise.py",
  run: "uv run importance_noise.py", check: "uv run importance_noise.py",
  files: [{ path: "importance_noise.py", text: "print('hi')\n" }], notes: [note], canRun,
});

const enc = new TextEncoder();
const sse = (events: object[]) =>
  new Response(
    new ReadableStream<Uint8Array>({
      start(c) {
        events.forEach((e) => c.enqueue(enc.encode(`data: ${JSON.stringify(e)}\n\n`)));
        c.close();
      },
    }),
    { status: 200 },
  );

beforeEach(() => {
  resetCourseCachesForTests();
  localStorage.clear();
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("LabsView", () => {
  it("groups labs by course and module, filters by course and opens labs and notes", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(list), { status: 200 })));
    const onOpenLab = vi.fn();
    const onOpenLesson = vi.fn();
    render(<LabsView onOpenLab={onOpenLab} onOpenLesson={onOpenLesson} onOpenDrills={vi.fn()} />);

    expect(await screen.findByRole("heading", { name: "data-science · Classical ml" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "gen-ai · Rag" })).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Importance noise" }));
    expect(onOpenLab).toHaveBeenCalledWith(ID);
    await userEvent.click(screen.getByRole("button", { name: "▤ Feature Importance" }));
    expect(onOpenLesson).toHaveBeenCalledWith(note.id);

    await userEvent.click(screen.getByRole("button", { name: "gen-ai" }));
    expect(screen.queryByRole("button", { name: "Importance noise" })).toBeNull();
    expect(screen.getByRole("button", { name: "Widget" })).toBeInTheDocument();
  });

  it("says runs are local only when the server cannot run them", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify({ ...list, canRun: false }), { status: 200 })));
    render(<LabsView onOpenLab={vi.fn()} onOpenLesson={vi.fn()} onOpenDrills={vi.fn()} />);
    expect(await screen.findByText(/Running one is local only/)).toBeInTheDocument();
  });
});

describe("LabWorkspace", () => {
  const renderLab = (onChatContext = vi.fn(), onAsk = vi.fn()) =>
    render(<LabWorkspace labId={ID} onOpenLesson={vi.fn()} onBack={vi.fn()} onAsk={onAsk} onChatContext={onChatContext} />);

  it("runs the lab, streams output and figures, and tells the chat what ran", async () => {
    const fetchMock = vi.fn(async (url: string) =>
      url.startsWith("/api/courses/labs/")
        ? new Response(JSON.stringify(detail(true)), { status: 200 })
        : sse([
            { type: "start", command: "uv run importance_noise.py" },
            { type: "output", stream: "stdout", text: "AUC 0.91\n" },
            { type: "output", stream: "stderr", text: "warn\n" },
            { type: "image", path: "sources/images/fig.png", mime: "image/png", data: "cG5n" },
            { type: "done", exit: 0, seconds: 2, timedOut: false, truncated: false },
          ]),
    );
    vi.stubGlobal("fetch", fetchMock);
    let getContext: (() => LabChatContext) | null = null;
    const onAsk = vi.fn();
    renderLab(vi.fn((g) => { getContext = g; }), onAsk);

    await userEvent.click(await screen.findByRole("button", { name: "▶ Run" }));
    expect(await screen.findByText("Ran in 2s")).toBeInTheDocument();
    expect(screen.getByText("AUC 0.91")).toBeInTheDocument();
    expect(screen.getByText("warn")).toHaveClass("lab-stderr");
    expect(screen.getByRole("img")).toHaveAttribute("src", "data:image/png;base64,cG5n");

    const post = (fetchMock.mock.calls as unknown as [string, RequestInit][]).find(([, i]) => i?.method === "POST");
    expect(post?.[0]).toBe("/api/courses/lab-runs");
    expect(JSON.parse(String(post?.[1].body))).toEqual({ lab: ID, mode: "run", files: {} });

    expect(getContext).not.toBeNull();
    expect(getContext!()).toEqual({ id: ID, files: {}, output: "AUC 0.91\nwarn\n", exit: 0 });
    await userEvent.click(screen.getByRole("button", { name: "Review my run ↗" }));
    expect(onAsk).toHaveBeenCalledWith(expect.stringMatching(/^Review my run/));
  });

  it("offers the drafted edits from storage and a per-file reset", async () => {
    localStorage.setItem(`librarian.lab.${ID}`, JSON.stringify({ "importance_noise.py": "print('mine')\n" }));
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(detail(true)), { status: 200 })));
    renderLab();
    expect(await screen.findByText(/1 file edited/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Reset importance_noise.py" }));
    await waitFor(() => expect(screen.queryByText(/1 file edited/)).toBeNull());
    expect(localStorage.getItem(`librarian.lab.${ID}`)).toBeNull();
  });

  it("shows the command to run by hand when the server cannot run labs", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(detail(false)), { status: 200 })));
    renderLab();
    expect(await screen.findByText(/Running labs is local only/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "▶ Run" })).toBeNull();
    expect(screen.getByRole("button", { name: "Explain this lab ↗" })).toBeInTheDocument();
  });
});
