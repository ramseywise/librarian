import { useCallback, useEffect, useState, useSyncExternalStore } from "react";
import type { z } from "zod";
import {
  conceptHubSchema,
  dueConceptsSchema,
  learningEventResultSchema,
  learningStateSchema,
} from "../schemas/learning";
import { apiFetch, parseJson, postJson } from "../utils/api";
import { errorText, type Resource } from "./resource";

/** While the server is still building its catalog, ask again this often. */
export const CATALOG_POLL_MS = 5000;

/**
 * Mastery changes whenever the learner answers a card, finishes a lesson or logs a drill, so every
 * learning hook refetches when this counter moves. `invalidateLearning` is the one way to move it.
 */
let epoch = 0;
const listeners = new Set<() => void>();

export function invalidateLearning() {
  epoch += 1;
  listeners.forEach((l) => l());
}

function subscribe(l: () => void) {
  listeners.add(l);
  return () => listeners.delete(l);
}

const useEpoch = () => useSyncExternalStore(subscribe, () => epoch);

/** Test hook: forget the epoch so one test's invalidation does not leak into the next. */
export function resetLearningForTests() {
  epoch = 0;
}

/** Why a request failed: a 404 means "no such page", anything else is the reply's own words. */
class NotFound extends Error {}

/**
 * One GET, refetched when the epoch moves and every `CATALOG_POLL_MS` while `pending(data)` says the
 * server's answer is provisional. A failed refetch never replaces a value already shown.
 * A null `url` is "nothing to ask yet".
 */
function useLearningResource<S extends z.ZodType>(
  url: string | null,
  schema: S,
  pending: (data: z.output<S>) => boolean = () => false,
): Resource<z.output<S>> & { notFound: boolean } {
  type T = z.output<S>;
  const version = useEpoch();
  const [attempt, setAttempt] = useState(0);
  const [tick, setTick] = useState(0);
  const [state, setState] = useState<{ url: string | null; data: T | null; error: string | null; notFound: boolean }>({
    url, data: null, error: null, notFound: false,
  });

  useEffect(() => {
    if (url === null) return;
    let live = true;
    apiFetch(url)
      .then((r) => {
        if (r.status === 404) throw new NotFound("not found");
        return r.ok ? parseJson(r, schema) : Promise.reject(new Error(`HTTP ${r.status}`));
      })
      .then(
        (data: T) => live && setState({ url, data, error: null, notFound: false }),
        (e: unknown) => live && setState((s) => {
          const keep = s.url === url ? s.data : null;
          return { url, data: keep, error: keep ? null : errorText(e), notFound: e instanceof NotFound };
        }),
      );
    return () => { live = false; };
    // `schema` and `pending` are module constants at every call site.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url, version, attempt, tick]);

  // The data on screen belongs to another url (the route changed): show nothing rather than stale data.
  const current = state.url === url ? state : { url, data: null, error: null, notFound: false };

  const provisional = current.data !== null && pending(current.data);
  useEffect(() => {
    if (!provisional) return;
    const id = setTimeout(() => setTick((t) => t + 1), CATALOG_POLL_MS);
    return () => clearTimeout(id);
  }, [provisional, tick]);

  const retry = useCallback(() => setAttempt((a) => a + 1), []);
  return {
    data: current.data,
    error: current.error,
    notFound: current.notFound,
    loading: url !== null && !current.data && !current.error,
    retry,
  };
}

/** Mastery per concept and module, and the lessons done. Polls while the server builds its catalog. */
export const useLearning = () =>
  useLearningResource("/api/learning/state", learningStateSchema, (s) => !s.catalogReady);

/** The Due list, weakest first. */
export const useDueConcepts = (limit = 5) =>
  useLearningResource(`/api/learning/next?limit=${limit}`, dueConceptsSchema);

/** One public wiki page's hub. `notFound` is true for a private, retired or unknown page. */
export const useConcept = (id: string) =>
  useLearningResource(`/api/learning/concept/${encodeURIComponent(id)}`, conceptHubSchema, (c) => !c.catalogReady);

export type LearningEvent =
  | { kind: "lesson_done"; lesson: string; ts?: string }
  | { kind: "drill_attempt"; lesson: string; score: number; ts?: string }
  | { kind: "card_grade"; deck: string; card: string; score: number; ts?: string }
  | { kind: "voice_grade"; concept?: string; lesson?: string; score: number; mode?: string; ts?: string };

/**
 * Log one study event and refresh mastery. Failure is swallowed: an event that did not land costs a
 * little accuracy, never the page the learner is on. The hook point for any new source of events.
 */
export function postLearningEvent(event: LearningEvent): Promise<void> {
  return postJson(learningEventResultSchema, "/api/learning/events", event).then(
    () => invalidateLearning(),
    () => undefined,
  );
}
