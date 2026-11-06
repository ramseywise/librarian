import { renderHook, waitFor, act } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { resetCourseCachesForTests, useCourses } from "../useCourses";

beforeEach(() => resetCourseCachesForTests());
afterEach(() => vi.unstubAllGlobals());

describe("useCourses", () => {
  it("fetches the catalog once per page load", async () => {
    const fetchMock = vi.fn(async () => new Response(JSON.stringify([{ id: "c1" }]), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const first = renderHook(() => useCourses());
    await waitFor(() => expect(first.result.current.data).toEqual([{ id: "c1" }]));
    first.unmount();
    const second = renderHook(() => useCourses());
    // Cached data is available on the first render of a remount: no loading flash.
    expect(second.result.current.data).toEqual([{ id: "c1" }]);
    await waitFor(() => expect(second.result.current.loading).toBe(false));
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it("reports errors and retries", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response("nope", { status: 500 }))
      .mockResolvedValueOnce(new Response(JSON.stringify([]), { status: 200 }));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useCourses());
    await waitFor(() => expect(result.current.error).toBe("HTTP 500"));
    act(() => result.current.retry());
    await waitFor(() => expect(result.current.data).toEqual([]));
    expect(result.current.error).toBeNull();
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
