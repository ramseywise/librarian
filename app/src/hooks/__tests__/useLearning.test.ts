import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  CATALOG_POLL_MS,
  invalidateLearning,
  postLearningEvent,
  resetLearningForTests,
  useConcept,
  useDueConcepts,
  useLearning,
} from "../useLearning";

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const STATE = { concepts: {}, modules: { "c/m": { strength: null, concepts: 2, withEvidence: 0 } }, lessonsDone: [], catalogReady: true };
const HUB = { id: "p", title: "P", summary: "s", domain: "rag", mastery: null, lessons: [], drills: [], decks: [], catalogReady: true };

beforeEach(() => resetLearningForTests());
afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe("useLearning", () => {
  it("reads mastery, with a null module strength meaning no data", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(STATE)));
    const { result } = renderHook(() => useLearning());
    await waitFor(() => expect(result.current.data?.modules["c/m"].strength).toBeNull());
  });

  it("refetches when learning is invalidated", async () => {
    const fetchMock = vi.fn(async () => json(STATE));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useLearning());
    await waitFor(() => expect(result.current.data).not.toBeNull());
    act(() => invalidateLearning());
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
  });

  it("polls while the catalog is building, then stops", async () => {
    vi.useFakeTimers({ shouldAdvanceTime: true });
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(json({ ...STATE, catalogReady: false }))
      .mockResolvedValue(json(STATE));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useLearning());
    await waitFor(() => expect(result.current.data?.catalogReady).toBe(false));
    await act(async () => { await vi.advanceTimersByTimeAsync(CATALOG_POLL_MS + 10); });
    await waitFor(() => expect(result.current.data?.catalogReady).toBe(true));
    await act(async () => { await vi.advanceTimersByTimeAsync(CATALOG_POLL_MS * 3); });
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("keeps a shown value when a refetch fails", async () => {
    const fetchMock = vi.fn().mockResolvedValueOnce(json(STATE)).mockResolvedValue(new Response("x", { status: 500 }));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useLearning());
    await waitFor(() => expect(result.current.data).not.toBeNull());
    act(() => invalidateLearning());
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(result.current.data).not.toBeNull();
    expect(result.current.error).toBeNull();
  });
});

describe("useDueConcepts", () => {
  it("asks for the limit it was given", async () => {
    const fetchMock = vi.fn(async () => json([]));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useDueConcepts(3));
    await waitFor(() => expect(result.current.data).toEqual([]));
    expect(fetchMock).toHaveBeenCalledWith("/api/learning/next?limit=3", expect.anything());
  });
});

describe("useConcept", () => {
  it("encodes the id and loads the hub", async () => {
    const fetchMock = vi.fn(async () => json(HUB));
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useConcept("a/b"));
    await waitFor(() => expect(result.current.data?.title).toBe("P"));
    expect(fetchMock).toHaveBeenCalledWith("/api/learning/concept/a%2Fb", expect.anything());
  });

  it("maps a 404 to notFound, not an error banner", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ detail: "no such page" }, 404)));
    const { result } = renderHook(() => useConcept("gone"));
    await waitFor(() => expect(result.current.notFound).toBe(true));
    expect(result.current.data).toBeNull();
  });

  it("does not show one page's data under another's id", async () => {
    vi.stubGlobal("fetch", vi.fn(async (u: string) => json({ ...HUB, title: u.endsWith("one") ? "One" : "Two" })));
    const { result, rerender } = renderHook(({ id }) => useConcept(id), { initialProps: { id: "one" } });
    await waitFor(() => expect(result.current.data?.title).toBe("One"));
    rerender({ id: "two" });
    expect(result.current.data).toBeNull();
    await waitFor(() => expect(result.current.data?.title).toBe("Two"));
  });
});

describe("postLearningEvent", () => {
  it("posts the event and invalidates on success", async () => {
    const fetchMock = vi.fn(async () => json({ logged: true, concepts: ["p"] }));
    vi.stubGlobal("fetch", fetchMock);
    await postLearningEvent({ kind: "voice_grade", concept: "p", score: 0.8, mode: "explain" });
    const [url, init] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toBe("/api/learning/events");
    expect(JSON.parse(init.body as string)).toMatchObject({ kind: "voice_grade", concept: "p", score: 0.8 });
  });

  it("swallows a failure", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("no", { status: 503 })));
    await expect(postLearningEvent({ kind: "lesson_done", lesson: "c/m/l" })).resolves.toBeUndefined();
  });
});
