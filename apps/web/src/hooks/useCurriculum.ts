import { useEffect, useRef, useState } from "react";
import type { Curriculum } from "../types";

const POLL_MS = 5000;
const MAX_POLLS = 12;

/**
 * The curriculum facet for the filter panel: null until the first answer, and the panel
 * shows plain directory chips until then. `revision` changes with each graph payload, which
 * also covers reconnects (the socket sends one on connect). While the server reports a stale
 * snapshot it is rebuilding, so this polls for a little. An unchanged answer keeps the same
 * object, so a poll can't refit the view.
 */
export function useCurriculum(revision: unknown, enabled: boolean): Curriculum | null {
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const lastBody = useRef<string | null>(null);

  useEffect(() => {
    if (!enabled) return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let polls = 0;

    async function load() {
      try {
        const res = await fetch("/api/graph/curriculum");
        if (!res.ok) return;
        const text = await res.text();
        if (cancelled) return;
        const body = JSON.parse(text) as Curriculum;
        if (text !== lastBody.current) {
          lastBody.current = text;
          setCurriculum(body);
        }
        if (body.stale && polls++ < MAX_POLLS) timer = setTimeout(() => void load(), POLL_MS);
      } catch {
        // Keep what we have; the next graph payload retries.
      }
    }
    void load();

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [revision, enabled]);

  return curriculum;
}
