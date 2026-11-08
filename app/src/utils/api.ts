/**
 * One client for the API. A browser signed in with the login flow sends its `lb_session` cookie
 * and echoes the `lb_csrf` cookie in `X-CSRF-Token` on writes; a deployment still on the
 * bootstrap token (or a personal `lk_` key) keeps it in localStorage, entered on the login page,
 * and sends it as a bearer token. A 401 on /api sends the page to `#/login?next=<where it was>`.
 * In open mode (local dev) the server never answers 401, so none of this fires.
 */
const TOKEN_KEY = "librarian.apiToken";
const CSRF_COOKIE = "lb_csrf";
const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

export function getToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) window.localStorage.setItem(TOKEN_KEY, token);
    else window.localStorage.removeItem(TOKEN_KEY);
  } catch {
    // storage blocked: the token lasts for this page only
  }
}

export function csrfToken(): string | null {
  const m = document.cookie.match(new RegExp(`(?:^|;\\s*)${CSRF_COOKIE}=([^;]*)`));
  return m ? decodeURIComponent(m[1]) : null;
}

/** Subprotocols for `new WebSocket(url, ...)`: browsers cannot set headers on a socket. A
 *  cookie session needs none; the server checks the socket's Origin instead. */
export function wsProtocols(): string[] | undefined {
  const token = getToken();
  return token ? ["bearer", token] : undefined;
}

/** `#/login?next=...` for the current page, unless already there. */
export function loginRoute(): string {
  const here = window.location.hash.replace(/^#/, "") || "/";
  if (here.startsWith("/login")) return here;
  return `/login?next=${encodeURIComponent(here)}`;
}

function sendToLogin(): void {
  const to = loginRoute();
  if (window.location.hash.replace(/^#/, "") !== to) window.location.hash = to;
}

/** Fired on `window` when a response names a different content release than the last one did.
 *  `detail` is the new release name. The first release seen is not a change. */
export const RELEASE_EVENT = "librarian:release";
const RELEASE_HEADER = "X-Librarian-Release";
let seenRelease: string | null = null;

function noteRelease(resp: Response): void {
  const name = resp.headers?.get(RELEASE_HEADER);
  if (!name || name === seenRelease) return;
  const changed = seenRelease !== null;
  seenRelease = name;
  if (changed) window.dispatchEvent(new CustomEvent(RELEASE_EVENT, { detail: name }));
}

/** For tests: forget the release seen so far. */
export function resetReleaseForTests(): void {
  seenRelease = null;
}

/** `fetch` with credentials, the CSRF header on writes and the stored token, if any. */
export async function apiFetch(input: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  const method = (init.method ?? "GET").toUpperCase();
  const token = getToken();
  if (token && !headers.has("Authorization")) headers.set("Authorization", `Bearer ${token}`);
  if (!SAFE_METHODS.has(method)) {
    const csrf = csrfToken();
    if (csrf) headers.set("X-CSRF-Token", csrf);
  }
  const resp = await window.fetch(input, { ...init, headers, credentials: "same-origin" });
  if (resp.status === 401 && input.startsWith("/api/")) sendToLogin();
  noteRelease(resp);
  return resp;
}

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
  }
}

/** JSON from the API, or an ApiError carrying the server's `detail` when it gives one. */
export async function apiJson<T>(input: string, init: RequestInit = {}): Promise<T> {
  const resp = await apiFetch(input, init);
  if (!resp.ok) {
    let detail = `HTTP ${resp.status}`;
    try {
      const body = (await resp.json()) as { detail?: unknown };
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* not JSON */
    }
    throw new ApiError(resp.status, detail);
  }
  return (await resp.json()) as T;
}

/** POST a JSON body. */
export function postJson<T>(input: string, body: unknown): Promise<T> {
  return apiJson<T>(input, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}
