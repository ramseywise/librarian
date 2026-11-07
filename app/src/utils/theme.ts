/**
 * The colour theme: an attribute on <html> that theme/tokens.css reads. The default follows the
 * OS and keeps following it until the user picks one, which is then kept in localStorage.
 * index.html repeats the first step inline so a light page never paints dark first.
 */
export type Theme = "dark" | "light";

export const THEME_STORAGE_KEY = "librarian.theme";
const LIGHT_QUERY = "(prefers-color-scheme: light)";

const listeners = new Set<() => void>();

function stored(): Theme | null {
  try {
    const value = window.localStorage.getItem(THEME_STORAGE_KEY);
    return value === "light" || value === "dark" ? value : null;
  } catch {
    return null; // Storage can be blocked; the theme then lasts for this page only.
  }
}

function fromSystem(): Theme {
  return typeof window.matchMedia === "function" && window.matchMedia(LIGHT_QUERY).matches ? "light" : "dark";
}

function apply(theme: Theme): void {
  if (document.documentElement.dataset.theme === theme) return;
  document.documentElement.dataset.theme = theme;
  listeners.forEach((notify) => notify());
}

export function currentTheme(): Theme {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function setTheme(theme: Theme): void {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch {
    // Applied below all the same.
  }
  apply(theme);
}

export function toggleTheme(): void {
  setTheme(currentTheme() === "light" ? "dark" : "light");
}

export function subscribeTheme(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Apply the saved or system theme, then follow the OS and other tabs. Returns the teardown. */
export function initTheme(): () => void {
  const sync = () => apply(stored() ?? fromSystem());
  sync();
  const scheme = typeof window.matchMedia === "function" ? window.matchMedia(LIGHT_QUERY) : null;
  scheme?.addEventListener?.("change", sync);
  window.addEventListener("storage", sync);
  return () => {
    scheme?.removeEventListener?.("change", sync);
    window.removeEventListener("storage", sync);
  };
}
