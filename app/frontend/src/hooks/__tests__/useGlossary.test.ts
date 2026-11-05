import { renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useGlossary } from "../useGlossary";

const terms = { terms: [{ id: "rrf", label: "RRF", aliases: [], def: "d", page: null, mentions: 1 }] };
const mentions = { rrf: ["a"] };

function stubFetch(ok = true) {
  const fn = vi.fn(async (url: string) => {
    const body = url.endsWith("/mentions") ? mentions : terms;
    return { ok, text: async () => JSON.stringify(body) };
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

afterEach(() => vi.unstubAllGlobals());

describe("useGlossary", () => {
  it("joins the terms and their mentions", async () => {
    stubFetch();
    const { result } = renderHook(() => useGlossary(1, true));
    await waitFor(() => expect(result.current).not.toBeNull());
    expect(result.current).toEqual({ ...terms, mentions });
  });

  it("waits until enabled", () => {
    const fn = stubFetch();
    renderHook(() => useGlossary(1, false));
    expect(fn).not.toHaveBeenCalled();
  });

  it("keeps the same object when a new revision answers the same", async () => {
    const fn = stubFetch();
    const { result, rerender } = renderHook(({ rev }) => useGlossary(rev, true), { initialProps: { rev: 1 } });
    await waitFor(() => expect(result.current).not.toBeNull());
    const first = result.current;
    rerender({ rev: 2 });
    await waitFor(() => expect(fn).toHaveBeenCalledTimes(4));
    await new Promise((r) => setTimeout(r, 0));
    expect(result.current).toBe(first);
  });

  it("leaves the map without terms when the request fails", async () => {
    const fn = stubFetch(false);
    const { result } = renderHook(() => useGlossary(1, true));
    await waitFor(() => expect(fn).toHaveBeenCalled());
    await new Promise((r) => setTimeout(r, 0));
    expect(result.current).toBeNull();
  });
});
