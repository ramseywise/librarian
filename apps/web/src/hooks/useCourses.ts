import { useCallback, useEffect, useState } from "react";
import type { Course, PracticeDrill } from "../courses/types";

interface Resource<T> {
  data: T | null;
  promise: Promise<T> | null;
}

/**
 * A GET endpoint fetched once per page load and shared by every component that asks.
 * A failed fetch is forgotten so `retry` (or the next mount) tries again.
 */
function createResource<T>(url: string) {
  const res: Resource<T> = { data: null, promise: null };

  function load(force = false): Promise<T> {
    if (res.promise && !force) return res.promise;
    const p = fetch(url)
      .then((r) => (r.ok ? (r.json() as Promise<T>) : Promise.reject(new Error(`HTTP ${r.status}`))))
      .then(
        (data) => {
          if (res.promise === p) res.data = data;
          return data;
        },
        (e: unknown) => {
          if (res.promise === p) res.promise = null;
          throw e;
        },
      );
    res.promise = p;
    return p;
  }

  function reset() {
    res.data = null;
    res.promise = null;
  }

  /**
   * `revalidate`: show the cached copy at once but refetch on mount — for payloads that
   * change outside the app between visits (the drill log behind /api/courses/practice).
   */
  function useResource({ revalidate = false } = {}) {
    const [state, setState] = useState<{ data: T | null; error: string | null }>(() => ({ data: res.data, error: null }));
    const [attempt, setAttempt] = useState(0);

    useEffect(() => {
      let live = true;
      load(revalidate || attempt > 0).then(
        (data) => live && setState({ data, error: null }),
        (e: unknown) => live && setState((s) => ({
          // Keep showing a cached copy if a background refetch fails.
          data: s.data,
          error: s.data ? null : e instanceof Error ? e.message : String(e),
        })),
      );
      return () => { live = false; };
    }, [attempt, revalidate]);

    const retry = useCallback(() => {
      setState((s) => ({ data: s.data, error: null }));
      setAttempt((a) => a + 1);
    }, []);

    return { data: state.data, error: state.error, loading: !state.data && !state.error, retry };
  }

  return { useResource, reset };
}

const courses = createResource<Course[]>("/api/courses");
const practice = createResource<PracticeDrill[]>("/api/courses/practice");

/** The course catalog (~290 KB), fetched once per page load. */
export const useCourses = () => courses.useResource();

/** All drills; cached for instant display, refreshed on mount for live attempt counts. */
export const usePracticeDrills = () => practice.useResource({ revalidate: true });

export function resetCourseCachesForTests() {
  courses.reset();
  practice.reset();
}
