import { useCallback, useEffect, useState } from "react";

/**
 * Practice timer (D6). Client-only: state lives in sessionStorage per lesson, so leaving
 * a drill and coming back keeps the clock (a running clock keeps running while away).
 * Nothing is sent to the server or written to the sisyphus drill log.
 */
export interface TimerState {
  /** Time banked from earlier runs. */
  elapsedMs: number;
  /** Wall-clock start of the current run, or null when paused. */
  startedAt: number | null;
}

export type TimerAction =
  | { type: "start"; now: number }
  | { type: "pause"; now: number }
  | { type: "reset" };

export const IDLE: TimerState = { elapsedMs: 0, startedAt: null };

export function timerReducer(s: TimerState, a: TimerAction): TimerState {
  switch (a.type) {
    case "start":
      return s.startedAt === null ? { ...s, startedAt: a.now } : s;
    case "pause":
      return s.startedAt === null ? s : { elapsedMs: elapsedAt(s, a.now), startedAt: null };
    case "reset":
      return IDLE;
  }
}

export function elapsedAt(s: TimerState, now: number): number {
  return s.elapsedMs + (s.startedAt === null ? 0 : Math.max(0, now - s.startedAt));
}

/** Countdown text: "12:34" while time remains, "+01:05" once over the timebox. */
export function formatCountdown(remainingMs: number): string {
  const over = remainingMs < 0;
  // Round toward the countdown's direction so it shows 00:00 exactly at the limit.
  const total = over ? Math.floor(-remainingMs / 1000) : Math.ceil(remainingMs / 1000);
  const m = Math.floor(total / 60);
  const sec = total % 60;
  return `${over && total > 0 ? "+" : ""}${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

const storageKey = (lessonId: string) => `librarian.timer.${lessonId}`;

export function loadTimer(lessonId: string): TimerState {
  try {
    const raw = sessionStorage.getItem(storageKey(lessonId));
    if (raw) {
      const p = JSON.parse(raw) as Partial<TimerState>;
      return {
        elapsedMs: typeof p.elapsedMs === "number" ? p.elapsedMs : 0,
        startedAt: typeof p.startedAt === "number" ? p.startedAt : null,
      };
    }
  } catch {
    /* storage absent or corrupt */
  }
  return IDLE;
}

function saveTimer(lessonId: string, s: TimerState) {
  try {
    if (s.elapsedMs === 0 && s.startedAt === null) sessionStorage.removeItem(storageKey(lessonId));
    else sessionStorage.setItem(storageKey(lessonId), JSON.stringify(s));
  } catch {
    /* ignore */
  }
}

export function useDrillTimer(lessonId: string, timeboxMin: number) {
  const [state, setState] = useState<{ id: string; timer: TimerState }>(() => ({ id: lessonId, timer: loadTimer(lessonId) }));
  // Re-read when the lesson changes without remounting.
  const timer = state.id === lessonId ? state.timer : loadTimer(lessonId);
  const [now, setNow] = useState(() => Date.now());
  const running = timer.startedAt !== null;

  useEffect(() => {
    if (!running) return;
    setNow(Date.now());
    const t = setInterval(() => setNow(Date.now()), 500);
    return () => clearInterval(t);
  }, [running]);

  const dispatch = useCallback((a: TimerAction) => {
    setState((prev) => {
      const cur = prev.id === lessonId ? prev.timer : loadTimer(lessonId);
      const next = timerReducer(cur, a);
      saveTimer(lessonId, next);
      return { id: lessonId, timer: next };
    });
    setNow(Date.now());
  }, [lessonId]);

  const elapsedMs = elapsedAt(timer, now);
  const remainingMs = timeboxMin * 60_000 - elapsedMs;
  return {
    elapsedMs,
    remainingMs,
    running,
    started: running || timer.elapsedMs > 0,
    start: useCallback(() => dispatch({ type: "start", now: Date.now() }), [dispatch]),
    pause: useCallback(() => dispatch({ type: "pause", now: Date.now() }), [dispatch]),
    reset: useCallback(() => dispatch({ type: "reset" }), [dispatch]),
  };
}
