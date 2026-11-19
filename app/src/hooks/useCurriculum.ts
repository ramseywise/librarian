import { useCallback, useRef, useState } from "react";
import { curriculumSchema } from "../schemas/graph";
import type { Curriculum } from "../types";
import { apiFetch, parseJson } from "../utils/api";
import { errorText, type Resource } from "./resource";
import { useRevisionFetch } from "./useRevisionFetch";

const POLL_MS = 5000;
const MAX_POLLS = 12;

/**
 * The curriculum facet for the filter panel: `data` is null until the first answer, and the panel
 * shows plain directory chips until then. `revision` changes with each graph payload, which
 * also covers reconnects (the socket sends one on connect). While the server reports a stale
 * snapshot it is rebuilding, so this polls for a little. An unchanged answer keeps the same
 * object, so a poll can't refit the view. A failed request sets `error` only while there is
 * nothing to show; `retry` asks again.
 */
export function useCurriculum(revision: unknown, enabled: boolean): Resource<Curriculum> {
  const [curriculum, setCurriculum] = useState<Curriculum | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const lastBody = useRef<string | null>(null);
  const polls = useRef(0);

  const load = useCallback(async (alive: () => boolean): Promise<void> => {
    try {
      const res = await apiFetch("/api/graph/curriculum");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const text = await res.clone().text();
      const body = await parseJson(res, curriculumSchema);
      if (!alive()) return;
      setError(null);
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
    } catch (e) {
      // Keep what we have; the next graph payload retries.
      if (alive()) setError(errorText(e));
    }
  }, []);
  useRevisionFetch(load, revision, enabled, attempt);

  const retry = useCallback(() => {
    setError(null);
    setAttempt((a) => a + 1);
  }, []);
  const shown = curriculum ? null : error;
  return { data: curriculum, error: shown, loading: enabled && !curriculum && !shown, retry };
}
