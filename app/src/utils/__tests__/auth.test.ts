import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { getToken, installAuthFetch, setToken, wsProtocols } from "../auth";

const realFetch = window.fetch;

describe("auth", () => {
  let upstream: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    window.localStorage.clear();
    upstream = vi.fn();
    window.fetch = upstream as unknown as typeof window.fetch;
    installAuthFetch();
  });

  afterEach(() => {
    window.fetch = realFetch;
    vi.restoreAllMocks();
  });

  it("sends no Authorization header while no token is stored", async () => {
    upstream.mockResolvedValue(new Response("{}", { status: 200 }));
    await window.fetch("/api/graph");
    expect(upstream.mock.calls[0][1]).toBeUndefined();
    expect(wsProtocols()).toBeUndefined();
  });

  it("adds the stored token to /api requests only", async () => {
    setToken("abc");
    upstream.mockResolvedValue(new Response("{}", { status: 200 }));
    await window.fetch("/api/graph");
    await window.fetch("https://example.com/api/x");
    expect(new Headers(upstream.mock.calls[0][1].headers).get("Authorization")).toBe("Bearer abc");
    expect(upstream.mock.calls[1][1]).toBeUndefined();
    expect(wsProtocols()).toEqual(["bearer", "abc"]);
  });

  it("prompts once on 401, stores the token and retries", async () => {
    vi.spyOn(window, "prompt").mockReturnValue("  secret ");
    upstream
      .mockResolvedValueOnce(new Response("{}", { status: 401 }))
      .mockResolvedValueOnce(new Response("{}", { status: 200 }));
    const resp = await window.fetch("/api/graph");
    expect(resp.status).toBe(200);
    expect(getToken()).toBe("secret");
    expect(new Headers(upstream.mock.calls[1][1].headers).get("Authorization")).toBe("Bearer secret");
  });

  it("returns the 401 when the prompt is dismissed", async () => {
    vi.spyOn(window, "prompt").mockReturnValue(null);
    upstream.mockResolvedValue(new Response("{}", { status: 401 }));
    const resp = await window.fetch("/api/graph");
    expect(resp.status).toBe(401);
    expect(upstream).toHaveBeenCalledTimes(1);
  });
});
