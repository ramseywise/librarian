import { useCallback, useMemo, useSyncExternalStore } from "react";
import { errorText, type Resource } from "./resource";
import { z } from "zod";
import { serverProgressSchema } from "../schemas/courses";
import { apiJson, postJson } from "../utils/api";
import { invalidateLearning } from "./useLearning";

/** Where progress lived before it moved to the server; read once, sent up, then removed. */
export const PROGRESS_KEY = "librarian.courses.v1";

interface Stored {
  done: string[];
  last: Record<string, string>; // course id → last opened lesson id
}

type ServerProgress = z.output<typeof serverProgressSchema>;

/** POST /api/courses/progress: `logged` is false when the write failed. */
const markResultSchema = z.object({ logged: z.boolean() });

const EMPTY: Stored = { done: [], last: {} };

/** Lesson ids start with their course id: `<course>/<module>/...`. */
const courseOf = (lessonId: string) => lessonId.split("/")[0];

export function fromServer(p: ServerProgress): Stored {
  const done: string[] = [];
  const newest: Record<string, [string, string]> = {}; // course → [updatedAt, lesson id]
  for (const [id, { state, updatedAt }] of Object.entries(p.lessons)) {
    if (state === "done") done.push(id);
    const c = courseOf(id);
    if (!newest[c] || updatedAt > newest[c][0]) newest[c] = [updatedAt, id];
  }
  return { done, last: Object.fromEntries(Object.entries(newest).map(([c, [, id]]) => [c, id])) };
}

// One store for the whole page, so every view sees the same progress. The server holds it per
// user; the store is a copy, written through optimistically and re-read when the course views mount.
let snapshot: Stored = EMPTY;
const listeners = new Set<() => void>();
const emit = () => listeners.forEach((l) => l());
const getSnapshot = (): Stored => snapshot;

// Whether the last read of the server's copy failed. Kept apart from the progress itself, which
// stays as the page has it either way.
interface Status { loading: boolean; error: string | null }
let status: Status = { loading: true, error: null };
const getStatus = (): Status => status;
function setStatus(next: Status) {
  if (next.loading === status.loading && next.error === status.error) return;
  status = next;
  emit();
}

function set(next: Stored) {
  if (next === snapshot) return;
  snapshot = next;
  emit();
}

function mark(lesson: string, state: "opened" | "done"): Promise<unknown> {
  // A failed write keeps the change in memory for this page; the next load corrects it.
  // A finished lesson is mastery evidence, so what the learning hooks show is refetched once it is stored.
  return postJson(markResultSchema, "/api/courses/progress", { lesson, state })
    .catch(() => undefined)
    .finally(() => {
      if (state === "done") invalidateLearning();
    });
}

/** Done lessons recorded in this browser before progress moved to the server. */
function takeLocalDone(): string[] {
  try {
    const raw = localStorage.getItem(PROGRESS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as { done?: unknown };
    localStorage.removeItem(PROGRESS_KEY);
    return Array.isArray(parsed.done) ? parsed.done.filter((d): d is string => typeof d === "string") : [];
  } catch {
    return [];
  }
}

let loading: Promise<void> | null = null;

export function loadProgress(): Promise<void> {
  loading ??= (async () => {
    const local = takeLocalDone();
    await Promise.all(local.map((id) => mark(id, "done")));
    setStatus({ loading: true, error: null });
    try {
      const server = fromServer(await apiJson(serverProgressSchema, "/api/courses/progress"));
      // Keep what this page marked while the request was in flight.
      const done = [...new Set([...server.done, ...snapshot.done])];
      set({ done, last: { ...server.last, ...snapshot.last } });
      setStatus({ loading: false, error: null });
    } catch (e) {
      // Offline or the server failed: keep what the page has, and say so.
      setStatus({ loading: false, error: errorText(e) });
    }
  })().finally(() => {
    loading = null;
  });
  return loading;
}

function subscribe(listener: () => void) {
  if (listeners.size === 0) void loadProgress();
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

/** Done stays done: the server never moves a finished lesson back. */
export function markDone(lessonId: string) {
  if (snapshot.done.includes(lessonId)) return;
  set({ ...snapshot, done: [...snapshot.done, lessonId] });
  void mark(lessonId, "done");
}

export function markVisited(courseId: string, lessonId: string) {
  if (snapshot.last[courseId] === lessonId) return;
  set({ ...snapshot, last: { ...snapshot.last, [courseId]: lessonId } });
  void mark(lessonId, "opened");
}

/** Test hook: forget the in-memory copy. */
export function resetProgressStoreForTests() {
  snapshot = EMPTY;
  loading = null;
  status = { loading: true, error: null };
}

export function useCourseProgress(): Pick<Resource<Stored>, "error" | "loading" | "retry"> & {
  done: Set<string>;
  last: Record<string, string>;
  markDone: (lessonId: string) => void;
  markVisited: (courseId: string, lessonId: string) => void;
} {
  const state = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
  const { loading: pending, error } = useSyncExternalStore(subscribe, getStatus, getStatus);
  const retry = useCallback(() => void loadProgress(), []);
  const done = useMemo(() => new Set(state.done), [state.done]);
  const markDoneCb = useCallback((lessonId: string) => markDone(lessonId), []);
  const visit = useCallback((courseId: string, lessonId: string) => markVisited(courseId, lessonId), []);
  return { done, last: state.last, markDone: markDoneCb, markVisited: visit, error, loading: pending, retry };
}
