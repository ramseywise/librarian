import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useCurriculum } from "../useCurriculum";

const body = (stale: boolean, title = "AI") =>
  JSON.stringify({ courses: [{ id: "ai", title, pageIds: [], modules: [] }], beyond: [], primaryCourse: {}, stale });

function stubFetch(...answers: (string | null)[]) {
  const fn = vi.fn(async () => {
    const a = answers.length > 1 ? answers.shift()! : answers[0];
    if (a === null) throw new Error("down");
    return new Response(a);
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("useCurriculum", () => {
  it("waits until enabled", () => {
    const fetchMock = stubFetch(body(false));
    const { result } = renderHook(() => useCurriculum(1, false));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(result.current).toBeNull();
  });

  it("refetches on a new revision, and keeps the object when nothing changed", async () => {
    const fetchMock = stubFetch(body(false));
    const { result, rerender } = renderHook(({ rev }) => useCurriculum(rev, true), { initialProps: { rev: 1 } });
    await waitFor(() => expect(result.current).not.toBeNull());
    const first = result.current;
    rerender({ rev: 2 });
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    await act(async () => {});
    expect(result.current).toBe(first);
  });

  it("keeps the last answer when a refetch fails", async () => {
    stubFetch(body(false), null);
    const { result, rerender } = renderHook(({ rev }) => useCurriculum(rev, true), { initialProps: { rev: 1 } });
    await waitFor(() => expect(result.current).not.toBeNull());
    const first = result.current;
    rerender({ rev: 2 });
    await act(async () => {});
    expect(result.current).toBe(first);
  });

  it("polls while stale, then stops", async () => {
    vi.useFakeTimers();
    const fetchMock = stubFetch(body(true), body(false, "Fresh"));
    const { result } = renderHook(() => useCurriculum(1, true));
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
    expect(result.current?.stale).toBe(true);
    await act(async () => { await vi.advanceTimersByTimeAsync(5000); });
    expect(result.current?.courses[0].title).toBe("Fresh");
    await act(async () => { await vi.advanceTimersByTimeAsync(20000); });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
