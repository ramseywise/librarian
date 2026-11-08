import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// The graph has its own test; here it only has to mount.
vi.mock("../components/WikiGraph", () => ({ WikiGraph: () => <div data-testid="graph" /> }));

const ME = {
  id: "u1",
  email: "ada@example.com",
  name: "Ada",
  role: "admin",
  timezone: "UTC",
  scopes: ["read", "write"],
  chat: { spent_today_usd: 0.25, daily_budget_usd: null },
};

let signedIn: boolean;
let calls: { url: string; init?: RequestInit }[];

function route(url: string, init?: RequestInit): Response {
  calls.push({ url, init });
  const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
  if (url === "/api/auth/config") return json({ methods: ["google", "email"], open: false });
  if (url === "/api/me") return signedIn ? json(ME) : json({ detail: "Not signed in." }, 401);
  if (url === "/auth/logout") return new Response(null, { status: 204 });
  if (url === "/api/legal/third-party") return new Response("# Third-party material\n\nMIT things.", { status: 200 });
  if (url === "/api/admin/users") return json([{ ...ME, last_seen_at: null, chat_spent_today_usd: 0.25 }]);
  if (url === "/api/admin/invites") return json([{ email: "bob@example.com", created_at: null, used_at: null }]);
  if (url.startsWith("/api/admin/audit")) return json([{ ts: null, email: "ada@example.com", action: "login", target: "google" }]);
  return json({ detail: "not found" }, 404);
}

beforeEach(() => {
  signedIn = true;
  calls = [];
  window.location.hash = "";
  vi.stubGlobal("fetch", vi.fn(async (url: string, init?: RequestInit) => route(url, init)));
  vi.stubGlobal("matchMedia", (query: string) => ({ matches: false, media: query, addEventListener() {}, removeEventListener() {} }));
  // jsdom has no layout; the chat panel scrolls its last message into view.
  Element.prototype.scrollIntoView = vi.fn();
});
afterEach(() => vi.unstubAllGlobals());

async function renderApp() {
  const { default: App } = await import("../App");
  return render(<App />);
}

describe("App", () => {
  it("shows the graph and who is signed in, with the admin link for an admin", async () => {
    await renderApp();
    expect(screen.getByTestId("graph")).toBeInTheDocument();
    fireEvent.click(await screen.findByRole("button", { name: "Ada" }));
    expect(screen.getByText("Chat today: $0.25")).toBeInTheDocument();
    expect(screen.getByRole("menuitem", { name: "Admin" })).toHaveAttribute("href", "#/admin");
  });

  it("sends a signed-out visitor to the login page, keeping where they were", async () => {
    signedIn = false;
    window.location.hash = "#/courses";
    await renderApp();
    await waitFor(() => expect(window.location.hash).toBe(`#/login?next=${encodeURIComponent("/courses")}`));
    act(() => window.dispatchEvent(new HashChangeEvent("hashchange")));
    const google = await screen.findByRole("link", { name: "Continue with Google" });
    expect(google).toHaveAttribute("href", `/auth/login/google?next=${encodeURIComponent("/#/courses")}`);
    expect(screen.getByLabelText("Email me a sign-in link")).toBeInTheDocument();
  });

  it("explains a refused sign-in", async () => {
    signedIn = false;
    window.location.hash = "#/login?error=not_invited";
    await renderApp();
    expect(await screen.findByRole("alert")).toHaveTextContent("not invited");
  });

  it("signs out with the CSRF header and returns to the login page", async () => {
    document.cookie = "lb_csrf=c5rf";
    await renderApp();
    fireEvent.click(await screen.findByRole("button", { name: "Ada" }));
    fireEvent.click(screen.getByRole("menuitem", { name: "Sign out" }));
    await waitFor(() => expect(window.location.hash).toBe("#/login"));
    const logout = calls.find((c) => c.url === "/auth/logout")!;
    expect(new Headers(logout.init?.headers).get("X-CSRF-Token")).toBe("c5rf");
    document.cookie = "lb_csrf=; max-age=0";
  });

  it("shows the privacy page with the third-party notice", async () => {
    window.location.hash = "#/privacy";
    await renderApp();
    expect(await screen.findByRole("heading", { name: "Privacy and terms" })).toBeInTheDocument();
    expect(screen.getByText(/Chat transcripts/)).toBeInTheDocument();
    expect(await screen.findByText("MIT things.")).toBeInTheDocument();
  });

  it("shows users, invites and the audit log on the admin page", async () => {
    window.location.hash = "#/admin";
    await renderApp();
    expect(await screen.findByRole("heading", { name: "Users (1)" })).toBeInTheDocument();
    expect(screen.getByText("bob@example.com")).toBeInTheDocument();
    expect(screen.getByRole("cell", { name: "login" })).toBeInTheDocument();
  });
});
