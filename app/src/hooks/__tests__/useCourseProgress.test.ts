import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { fromServer, loadProgress, PROGRESS_KEY, resetProgressStoreForTests, useCourseProgress } from "../useCourseProgress";

let posts: { lesson: string; state: string }[];
let server: Record<string, { state: "opened" | "done"; updatedAt: string }>;

beforeEach(() => {
  localStorage.clear();
  resetProgressStoreForTests();
  posts = [];
  server = {};
  vi.stubGlobal(
    "fetch",
    vi.fn(async (url: string, init?: RequestInit) => {
      if (init?.method === "POST") {
        posts.push(JSON.parse(String(init.body)));
        return new Response(JSON.stringify({ logged: true }), { status: 200 });
      }
      expect(url).toBe("/api/courses/progress");
      return new Response(JSON.stringify({ lessons: server }), { status: 200 });
    }),
  );
});
afterEach(() => vi.unstubAllGlobals());

describe("useCourseProgress", () => {
  it("loads the user's progress from the server", async () => {
    server = {
      "c/m/l1": { state: "done", updatedAt: "2026-11-01T10:00:00" },
      "c/m/l2": { state: "opened", updatedAt: "2026-11-02T10:00:00" },
      "d/m/x": { state: "opened", updatedAt: "2026-11-01T09:00:00" },
    };
    const { result } = renderHook(() => useCourseProgress());
    await waitFor(() => expect(result.current.done.has("c/m/l1")).toBe(true));
    expect(result.current.last).toEqual({ c: "c/m/l2", d: "d/m/x" });
  });

  it("shares one store across hook instances and writes through", async () => {
    const a = renderHook(() => useCourseProgress());
    const b = renderHook(() => useCourseProgress());
    await act(() => loadProgress());
    act(() => a.result.current.markDone("c/m/l1"));
    expect(b.result.current.done.has("c/m/l1")).toBe(true);
    act(() => b.result.current.markVisited("c", "c/m/l1"));
    act(() => b.result.current.markVisited("c", "c/m/l1")); // unchanged: no second write
    expect(a.result.current.last).toEqual({ c: "c/m/l1" });
    act(() => a.result.current.markDone("c/m/l1")); // done stays done
    await waitFor(() =>
      expect(posts).toEqual([
        { lesson: "c/m/l1", state: "done" },
        { lesson: "c/m/l1", state: "opened" },
      ]),
    );
  });

  it("sends progress kept in this browser up once, then forgets it", async () => {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify({ done: ["x/y/z"], last: { x: "x/y/z" } }));
    await act(() => loadProgress());
    expect(posts).toEqual([{ lesson: "x/y/z", state: "done" }]);
    expect(localStorage.getItem(PROGRESS_KEY)).toBeNull();
  });

  it("keeps changes in memory when the server cannot be reached", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("offline")));
    const { result } = renderHook(() => useCourseProgress());
    await act(() => loadProgress());
    act(() => result.current.markDone("a/b/c"));
    expect(result.current.done.has("a/b/c")).toBe(true);
  });

  it("picks the newest lesson per course", () => {
    expect(
      fromServer({
        lessons: {
          "c/1": { state: "done", updatedAt: "2026-01-02" },
          "c/2": { state: "opened", updatedAt: "2026-01-01" },
        },
      }),
    ).toEqual({ done: ["c/1"], last: { c: "c/1" } });
  });
});
