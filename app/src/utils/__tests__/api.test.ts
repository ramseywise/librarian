import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  ApiError,
  RELEASE_EVENT,
  apiFetch,
  apiJson,
  getToken,
  loginRoute,
  postJson,
  resetReleaseForTests,
  setToken,
  wsProtocols,
} from "../api";

const realFetch = window.fetch;

describe("api", () => {
  let upstream: ReturnType<typeof vi.fn>;
  const sent = (i = 0) => upstream.mock.calls[i][1] as RequestInit;

  beforeEach(() => {
    window.localStorage.clear();
    document.cookie = "lb_csrf=; max-age=0";
    window.location.hash = "";
    upstream = vi.fn().mockResolvedValue(new Response("{}", { status: 200 }));
    window.fetch = upstream as unknown as typeof window.fetch;
  });

  afterEach(() => {
    window.fetch = realFetch;
    vi.restoreAllMocks();
  });

  it("fires the release event when a response names a different release, not on the first", async () => {
    resetReleaseForTests();
    const seen: string[] = [];
    const listener = (e: Event) => seen.push((e as CustomEvent<string>).detail);
    window.addEventListener(RELEASE_EVENT, listener);
    const named = (name: string) => new Response("{}", { headers: { "X-Librarian-Release": name } });
    upstream.mockResolvedValueOnce(named("content-a"));
    upstream.mockResolvedValueOnce(named("content-a"));
    upstream.mockResolvedValueOnce(named("content-b"));
    for (let i = 0; i < 4; i++) await apiFetch("/api/graph"); // the last has no header
    window.removeEventListener(RELEASE_EVENT, listener);
    expect(seen).toEqual(["content-b"]);
  });

  it("sends the session cookie and no Authorization header while no token is stored", async () => {
    await apiFetch("/api/graph");
    expect(sent().credentials).toBe("same-origin");
    expect(new Headers(sent().headers).has("Authorization")).toBe(false);
    expect(wsProtocols()).toBeUndefined();
  });

  it("adds a stored token as a bearer token and to the socket subprotocols", async () => {
    setToken("abc");
    await apiFetch("/api/graph");
    expect(new Headers(sent().headers).get("Authorization")).toBe("Bearer abc");
    expect(wsProtocols()).toEqual(["bearer", "abc"]);
    setToken(null);
    expect(getToken()).toBeNull();
  });

  it("echoes the CSRF cookie on writes only", async () => {
    document.cookie = "lb_csrf=tok123";
    await apiFetch("/api/x");
    await apiFetch("/api/x", { method: "post" });
    expect(new Headers(sent(0).headers).has("X-CSRF-Token")).toBe(false);
    expect(new Headers(sent(1).headers).get("X-CSRF-Token")).toBe("tok123");
  });

  it("sends a 401 on /api to the login page, keeping where it was", async () => {
    window.location.hash = "#/courses/c/m/l";
    upstream.mockResolvedValue(new Response("{}", { status: 401 }));
    const resp = await apiFetch("/api/graph");
    expect(resp.status).toBe(401);
    expect(window.location.hash).toBe(`#/login?next=${encodeURIComponent("/courses/c/m/l")}`);
    expect(loginRoute()).toBe(window.location.hash.slice(1)); // already there: unchanged
  });

  it("raises the server's detail and posts JSON", async () => {
    upstream.mockResolvedValueOnce(new Response(JSON.stringify({ detail: "nope" }), { status: 422 }));
    await expect(apiJson("/api/x")).rejects.toEqual(new ApiError(422, "nope"));
    upstream.mockResolvedValueOnce(new Response(JSON.stringify({ ok: 1 }), { status: 200 }));
    expect(await postJson("/api/y", { a: 1 })).toEqual({ ok: 1 });
    expect(sent(1).body).toBe('{"a":1}');
    expect(new Headers(sent(1).headers).get("Content-Type")).toBe("application/json");
  });
});
