import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { PROGRESS_KEY, resetProgressStoreForTests, useCourseProgress } from "../useCourseProgress";

beforeEach(() => {
  localStorage.clear();
  resetProgressStoreForTests();
});
afterEach(() => vi.restoreAllMocks());

describe("useCourseProgress", () => {
  it("shares one store across hook instances (Courses and Practice)", () => {
    const a = renderHook(() => useCourseProgress());
    const b = renderHook(() => useCourseProgress());
    act(() => a.result.current.toggleDone("c/m/l1"));
    expect(b.result.current.done.has("c/m/l1")).toBe(true);
    act(() => b.result.current.markVisited("c", "c/m/l1"));
    expect(a.result.current.last).toEqual({ c: "c/m/l1" });
    expect(JSON.parse(localStorage.getItem(PROGRESS_KEY)!)).toEqual({ done: ["c/m/l1"], last: { c: "c/m/l1" } });
    act(() => a.result.current.toggleDone("c/m/l1"));
    expect(b.result.current.done.has("c/m/l1")).toBe(false);
  });

  it("reads the existing stored shape", () => {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify({ done: ["x/y/z"], last: { x: "x/y/z" } }));
    const { result } = renderHook(() => useCourseProgress());
    expect(result.current.done.has("x/y/z")).toBe(true);
    expect(result.current.last.x).toBe("x/y/z");
  });

  it("tolerates storage that throws, keeping progress in memory", () => {
    vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => { throw new Error("denied"); });
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => { throw new Error("denied"); });
    const { result } = renderHook(() => useCourseProgress());
    expect(result.current.done.size).toBe(0);
    act(() => result.current.toggleDone("a/b/c"));
    expect(result.current.done.has("a/b/c")).toBe(true);
  });

  it("picks up changes made in another tab", () => {
    const { result } = renderHook(() => useCourseProgress());
    localStorage.setItem(PROGRESS_KEY, JSON.stringify({ done: ["other/tab/lesson"], last: {} }));
    act(() => { window.dispatchEvent(new StorageEvent("storage", { key: PROGRESS_KEY })); });
    expect(result.current.done.has("other/tab/lesson")).toBe(true);
  });

  it("re-reads storage when the course views remount, so another tab's progress survives", () => {
    const first = renderHook(() => useCourseProgress());
    act(() => first.result.current.toggleDone("mine"));
    first.unmount(); // switched to the Graph tab: nobody listens for storage events
    localStorage.setItem(PROGRESS_KEY, JSON.stringify({ done: ["mine", "other-tab"], last: {} }));
    const again = renderHook(() => useCourseProgress());
    expect([...again.result.current.done]).toEqual(["mine", "other-tab"]);
    act(() => again.result.current.toggleDone("third"));
    expect(JSON.parse(localStorage.getItem(PROGRESS_KEY)!).done).toEqual(["mine", "other-tab", "third"]);
  });
});
