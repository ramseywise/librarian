import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch, apiJson, setToken } from "../utils/api";

export type LoginMethod = "google" | "github" | "email";

export interface AuthConfig {
  methods: LoginMethod[];
  open: boolean; // no token and no login configured: everyone is the owner (local use)
}

export interface Me {
  id: string;
  email: string;
  name: string | null;
  role: "admin" | "member";
  timezone: string;
  scopes: string[];
  /** Active experiment variant for this user; may be empty. */
  experiment?: string;
  chat: { spent_today_usd: number; daily_budget_usd: number | null };
}

export function useAuthConfig(): AuthConfig | null {
  const [config, setConfig] = useState<AuthConfig | null>(null);
  useEffect(() => {
    let cancelled = false;
    apiJson<AuthConfig>("/api/auth/config")
      .then((c) => !cancelled && setConfig(c))
      .catch(() => !cancelled && setConfig({ methods: [], open: false }));
    return () => {
      cancelled = true;
    };
  }, []);
  return config;
}

/** The signed-in user, or null while loading or signed out (a 401 has already gone to the login page). */
export function useMe(): Me | null {
  const [me, setMe] = useState<Me | null>(null);
  const known = useRef(false);
  useEffect(() => {
    let cancelled = false;
    const load = () =>
      apiJson<Me>("/api/me")
        .then((m) => {
          known.current = true;
          if (!cancelled) setMe(m);
        })
        .catch(() => {
          known.current = false;
          if (!cancelled) setMe(null);
        });
    void load();
    // Signing in with a token on the login page, or signing out, lands on another hash: ask again then,
    // but not on every navigation while signed in.
    const onHash = () => {
      const atLogin = window.location.hash.startsWith("#/login");
      if (known.current === atLogin) void load();
    };
    window.addEventListener("hashchange", onHash);
    return () => {
      cancelled = true;
      window.removeEventListener("hashchange", onHash);
    };
  }, []);
  return me;
}

/** End the cookie session (if any), forget a stored token, and go to the login page. */
export function useSignOut(): () => Promise<void> {
  return useCallback(async () => {
    try {
      await apiFetch("/auth/logout", { method: "POST" });
    } catch {
      /* offline: the cookie expires on its own */
    }
    setToken(null);
    window.location.hash = "/login";
  }, []);
}
