import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { currentTheme, initTheme, setTheme, subscribeTheme, THEME_STORAGE_KEY, toggleTheme } from "../theme";

function stubSystem(light: boolean) {
  const listeners = new Set<() => void>();
  const query = {
    matches: light,
    addEventListener: (_: string, l: () => void) => listeners.add(l),
    removeEventListener: (_: string, l: () => void) => listeners.delete(l),
  };
  vi.stubGlobal("matchMedia", () => query);
  return {
    change(next: boolean) {
      query.matches = next;
      listeners.forEach((l) => l());
    },
  };
}

let teardown: () => void = () => undefined;

beforeEach(() => {
  localStorage.clear();
  delete document.documentElement.dataset.theme;
});

afterEach(() => {
  teardown();
  teardown = () => undefined;
  vi.unstubAllGlobals();
});

describe("theme", () => {
  it("defaults from prefers-color-scheme", () => {
    stubSystem(true);
    teardown = initTheme();
    expect(document.documentElement.dataset.theme).toBe("light");
  });

  it("defaults to dark with no preference or no matchMedia", () => {
    teardown = initTheme();
    expect(document.documentElement.dataset.theme).toBe("dark");
  });

  it("a saved choice beats the system", () => {
    localStorage.setItem(THEME_STORAGE_KEY, "dark");
    stubSystem(true);
    teardown = initTheme();
    expect(currentTheme()).toBe("dark");
  });

  it("ignores a junk saved value", () => {
    localStorage.setItem(THEME_STORAGE_KEY, "sepia");
    stubSystem(true);
    teardown = initTheme();
    expect(currentTheme()).toBe("light");
  });

  it("the toggle flips and persists", () => {
    stubSystem(false);
    teardown = initTheme();
    toggleTheme();
    expect(currentTheme()).toBe("light");
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("light");
    toggleTheme();
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe("dark");
  });

  it("follows the OS only until the user chooses", () => {
    const system = stubSystem(false);
    teardown = initTheme();
    system.change(true);
    expect(currentTheme()).toBe("light");
    setTheme("dark");
    system.change(true);
    expect(currentTheme()).toBe("dark");
  });

  it("notifies subscribers once per actual change", () => {
    teardown = initTheme();
    const listener = vi.fn();
    const unsubscribe = subscribeTheme(listener);
    setTheme("light");
    setTheme("light");
    expect(listener).toHaveBeenCalledTimes(1);
    unsubscribe();
    setTheme("dark");
    expect(listener).toHaveBeenCalledTimes(1);
  });

  it("survives blocked storage", () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("blocked");
    });
    setTheme("light");
    expect(currentTheme()).toBe("light");
    vi.restoreAllMocks();
  });
});
