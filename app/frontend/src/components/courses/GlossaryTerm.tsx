import { useCallback, useEffect, useId, useRef, useState, type CSSProperties, type ReactNode } from "react";

/** Long enough to cross the gap from the word to the definition, which stays hoverable (WCAG 1.4.13). */
const CLOSE_DELAY_MS = 150;
const GAP = 6;
const POP_WIDTH = 320;
/** Below the word unless this little room is left under it. */
const MIN_ROOM_BELOW = 180;

function place(el: HTMLElement): CSSProperties {
  // The first line box: a wrapped term's own rect spans both lines.
  const rect = el.getClientRects()[0] ?? el.getBoundingClientRect();
  const left = Math.max(8, Math.min(rect.left, window.innerWidth - POP_WIDTH - 8));
  return window.innerHeight - rect.bottom < MIN_ROOM_BELOW
    ? { left, bottom: window.innerHeight - rect.top + GAP }
    : { left, top: rect.bottom + GAP };
}

/**
 * A glossary term in reading text, its definition shown on hover or keyboard focus. Fixed
 * position, because a term can sit in a scrolling table or code-free block that would clip it.
 */
export function GlossaryTerm({ label, def, children }: { label: string; def: string; children?: ReactNode }) {
  const id = useId();
  const ref = useRef<HTMLSpanElement>(null);
  const closing = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const [style, setStyle] = useState<CSSProperties | null>(null);
  const open = style !== null;

  const show = useCallback(() => {
    clearTimeout(closing.current);
    if (ref.current) setStyle(place(ref.current));
  }, []);
  const hide = useCallback(() => {
    clearTimeout(closing.current);
    setStyle(null);
  }, []);
  const hideSoon = useCallback(() => {
    clearTimeout(closing.current);
    closing.current = setTimeout(() => setStyle(null), CLOSE_DELAY_MS);
  }, []);

  useEffect(() => () => clearTimeout(closing.current), []);

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      // Claimed here, so the same press doesn't also close the chat panel.
      e.preventDefault();
      hide();
    };
    document.addEventListener("keydown", onKey);
    // Fixed position would leave it behind; capture, because the lesson scrolls in its own element.
    window.addEventListener("scroll", hide, true);
    return () => {
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("scroll", hide, true);
    };
  }, [open, hide]);

  return (
    <span
      ref={ref}
      className="gloss-term"
      tabIndex={0}
      aria-describedby={id}
      onMouseEnter={show}
      onMouseLeave={hideSoon}
      onFocus={show}
      onBlur={hide}
    >
      {children}
      {/* Always in the DOM: aria-describedby reads it even while hidden. */}
      <span id={id} role="tooltip" className="gloss-pop" hidden={!open} style={style ?? undefined}>
        <span className="gloss-pop-label">{label}</span>
        {def}
      </span>
    </span>
  );
}
