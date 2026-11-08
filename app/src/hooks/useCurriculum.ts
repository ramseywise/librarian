import { useCallback, useRef, useState } from "react";
import type { Curriculum } from "../types";
import { apiFetch } from "../utils/api";
import { useRevisionFetch } from "./useRevisionFetch";

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
  const polls = useRef(0);

  const load = useCallback(async (alive: () => boolean): Promise<void> => {
    try {
      const res = await apiFetch("/api/graph/curriculum");
      if (!res.ok) return;
      const text = await res.text();
      if (!alive()) return;
      const body = JSON.parse(text) as Curriculum;
      if (text !== lastBody.current) {
        lastBody.current = text;
        setCurriculum(body);
      }
      if (!body.stale) polls.current = 0;
      else if (polls.current++ < MAX_POLLS) {
        setTimeout(() => {
          if (alive()) void load(alive);
        }, POLL_MS);
      }
    } catch {
      // Keep what we have; the next graph payload retries.
    }
  }, []);
  useRevisionFetch(load, revision, enabled);

  return curriculum;
}
