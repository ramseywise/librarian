import { useEffect, useRef } from "react";

/**
 * Runs `load` when `revision` changes, without abandoning a request already in flight: a change
 * mid-request queues one more run for when it lands. During a burst of wiki writes the revision
 * changes every few seconds while a cold request can take tens of seconds, and cancelling on each
 * change meant the answer never arrived. `alive()` is false once the component has unmounted.
 */
export function useRevisionFetch(
  load: (alive: () => boolean) => Promise<void>,
  revision: unknown,
  enabled: boolean,
): void {
  const loadRef = useRef(load);
  const state = useRef({ running: false, queued: false, mounted: true });

  useEffect(() => {
    loadRef.current = load;
  });

  useEffect(() => {
    const s = state.current;
    s.mounted = true;
    return () => {
      s.mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!enabled) return;
    const s = state.current;
    if (s.running) {
      s.queued = true;
      return;
    }
    s.running = true;
    void (async () => {
      do {
        s.queued = false;
        await loadRef.current(() => s.mounted);
      } while (s.queued && s.mounted);
      s.running = false;
    })();
  }, [revision, enabled]);
}
