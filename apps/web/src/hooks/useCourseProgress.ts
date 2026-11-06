import { useCallback, useMemo, useSyncExternalStore } from "react";

export const PROGRESS_KEY = "librarian.courses.v1";

interface Stored {
  done: string[];
  last: Record<string, string>; // course id → last opened lesson id
}

const EMPTY: Stored = { done: [], last: {} };

// Per-browser convenience only; storage can be absent (private window) or throw.
function load(): Stored {
  try {
    const raw = localStorage.getItem(PROGRESS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Partial<Stored>;
      return {
        done: Array.isArray(parsed.done) ? parsed.done : [],
        last: parsed.last && typeof parsed.last === "object" ? parsed.last : {},
      };
    }
  } catch {
    /* fall through */
  }
  return EMPTY;
}

function save(s: Stored) {
  try {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(s));
  } catch {
    /* ignore: progress still lives in memory for this page */
  }
}

// One store for the whole page, so every view sees the same progress.
let snapshot: Stored | null = null;
const listeners = new Set<() => void>();

const getSnapshot = (): Stored => (snapshot ??= load());
const emit = () => listeners.forEach((l) => l());

function onStorage(e: StorageEvent) {
  // e.key is null when another tab calls localStorage.clear().
  if (e.key !== null && e.key !== PROGRESS_KEY) return;
  snapshot = load();
  emit();
}

function subscribe(listener: () => void) {
  if (listeners.size === 0) {
    // Nobody was listening, so storage events from other tabs were missed while the
    // course views were unmounted. Re-read now, or the next write would clobber them.
    snapshot = load();
    window.addEventListener("storage", onStorage);
  }
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
    if (listeners.size === 0) window.removeEventListener("storage", onStorage);
  };
}

function update(fn: (s: Stored) => Stored) {
  const prev = getSnapshot();
  const next = fn(prev);
  if (next === prev) return;
  snapshot = next;
  save(next);
  emit();
}

export function toggleDone(lessonId: string) {
  update((s) => ({
    ...s,
    done: s.done.includes(lessonId) ? s.done.filter((d) => d !== lessonId) : [...s.done, lessonId],
  }));
}

export function markVisited(courseId: string, lessonId: string) {
  update((s) => (s.last[courseId] === lessonId ? s : { ...s, last: { ...s.last, [courseId]: lessonId } }));
}

/** Test hook: forget the in-memory snapshot so the next read goes back to storage. */
export function resetProgressStoreForTests() {
  snapshot = null;
}

export function useCourseProgress() {
  const state = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
  const done = useMemo(() => new Set(state.done), [state.done]);
  const toggle = useCallback((lessonId: string) => toggleDone(lessonId), []);
  const visit = useCallback((courseId: string, lessonId: string) => markVisited(courseId, lessonId), []);
  return { done, last: state.last, toggleDone: toggle, markVisited: visit };
}
