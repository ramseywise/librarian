import { useEffect } from "react";

/** Marks an input as its view's search; the `/` key goes to the first visible one. */
export const VIEW_SEARCH_ATTR = "data-view-search";

function isTyping(el: Element | null): boolean {
  return el instanceof HTMLElement && el.closest("input, textarea, select, [contenteditable]:not([contenteditable='false'])") !== null;
}

/** The graph stays mounted, hidden, under the course views, so being in the DOM isn't enough. */
function isVisible(el: HTMLElement): boolean {
  if (getComputedStyle(el).visibility === "hidden") return false;
  for (let n: HTMLElement | null = el; n; n = n.parentElement) {
    if (getComputedStyle(n).display === "none") return false;
  }
  return true;
}

/** `/` focuses the current view's search, unless focus is somewhere that takes typing. */
export function useSlashSearch(): void {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "/" || e.ctrlKey || e.metaKey || e.altKey || e.isComposing || e.defaultPrevented) return;
      if (isTyping(e.target instanceof Element ? e.target : null) || isTyping(document.activeElement)) return;
      const target = [...document.querySelectorAll<HTMLElement>(`[${VIEW_SEARCH_ATTR}]`)].find(isVisible);
      // A view with no search keeps the key: Firefox's quick find, for one.
      if (!target) return;
      e.preventDefault();
      target.focus();
      if (target instanceof HTMLInputElement) target.select();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);
}
