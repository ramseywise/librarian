import { useCallback, useState } from "react";

const KEY = "librarian.courses.v1";

interface Stored {
  done: string[];
  last: Record<string, string>; // course id → last opened lesson id
}

// Per-browser convenience only; storage can be absent (private window) or throw.
function load(): Stored {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<Stored>;
      return { done: parsed.done ?? [], last: parsed.last ?? {} };
    }
  } catch {
    /* fall through */
  }
  return { done: [], last: {} };
}

function save(s: Stored) {
  try {
    localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    /* ignore */
  }
}

export function useCourseProgress() {
  const [state, setState] = useState<Stored>(load);
  const done = new Set(state.done);

  const update = useCallback((fn: (s: Stored) => Stored) => {
    setState((prev) => {
      const next = fn(prev);
      save(next);
      return next;
    });
  }, []);

  const toggleDone = useCallback(
    (lessonId: string) =>
      update((s) => ({
        ...s,
        done: s.done.includes(lessonId) ? s.done.filter((d) => d !== lessonId) : [...s.done, lessonId],
      })),
    [update]
  );

  const markVisited = useCallback(
    (courseId: string, lessonId: string) =>
      update((s) => (s.last[courseId] === lessonId ? s : { ...s, last: { ...s.last, [courseId]: lessonId } })),
    [update]
  );

  return { done, last: state.last, toggleDone, markVisited };
}
