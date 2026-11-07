/**
 * API token for a deployment that sets LIBRARIAN_API_TOKEN. One user, one token, kept in
 * localStorage: the first 401 asks for it once, and every later /api request carries it.
 * Without a token on the server nothing here fires, so local dev is unchanged.
 */
const KEY = "librarian.apiToken";

export function getToken(): string | null {
  try {
    return window.localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  try {
    window.localStorage.setItem(KEY, token);
  } catch {
    // storage blocked: the prompt will ask again next time
  }
}

/** Subprotocols for `new WebSocket(url, ...)`: browsers cannot set headers on a socket. */
export function wsProtocols(): string[] | undefined {
  const token = getToken();
  return token ? ["bearer", token] : undefined;
}

function isApiRequest(input: RequestInfo | URL): boolean {
  const raw = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
  const url = new URL(raw, window.location.href);
  return url.origin === window.location.origin && url.pathname.startsWith("/api/");
}

function withToken(init: RequestInit | undefined, token: string | null): RequestInit | undefined {
  if (!token) return init;
  const headers = new Headers(init?.headers);
  headers.set("Authorization", `Bearer ${token}`);
  return { ...init, headers };
}

let pendingPrompt: Promise<string | null> | null = null;

function askForToken(): Promise<string | null> {
  pendingPrompt ??= Promise.resolve().then(() => {
    const entered = window.prompt("This Librarian needs an API token:")?.trim() || null;
    if (entered) setToken(entered);
    pendingPrompt = null;
    return entered;
  });
  return pendingPrompt;
}

/** Wrap `window.fetch` so same-origin /api requests carry the token and retry once after a 401. */
export function installAuthFetch(): void {
  const original = window.fetch.bind(window);
  window.fetch = async (input, init) => {
    if (!isApiRequest(input)) return original(input, init);
    const resp = await original(input, withToken(init, getToken()));
    if (resp.status !== 401) return resp;
    const token = await askForToken();
    return token ? original(input, withToken(init, token)) : resp;
  };
}
