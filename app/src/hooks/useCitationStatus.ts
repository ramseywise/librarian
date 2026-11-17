import { useEffect, useMemo, useState } from "react";
import { RELEASE_EVENT, postJson } from "../utils/api";
import type { ChatMessage, CitedSource } from "./useChatStream";

/** A cited page compared with the wiki now (POST /api/chat/citations/check). */
export interface CitationState {
  status: "current" | "changed" | "missing";
  /** The page's id today, when it was renamed since the answer. */
  now?: string;
}

/** A citation whose page is no longer what the answer read. */
export interface StaleCitation {
  status: "changed" | "missing";
  now?: string;
}

/** Stale citations of one answer, by cited page id. */
export type StaleMap = Record<string, StaleCitation>;

// The server's cap on citations per request.
const CHECK_BATCH = 50;

const keyOf = (s: CitedSource) => `${s.id}@${s.hash}`;

/** The stale citations among one answer's `sources`, given the hook's result. */
export function staleFor(sources: CitedSource[] | undefined, states: Record<string, CitationState>): StaleMap {
  const stale: StaleMap = {};
  for (const s of sources ?? []) {
    const state = states[keyOf(s)];
    if (state && state.status !== "current") stale[s.id] = { status: state.status, now: state.now };
  }
  return stale;
}

/**
 * Checks every finished answer's cited pages against the wiki: when an answer arrives, when the
 * content release changes and when the window regains focus. Returns states keyed by id and hash;
 * read one answer's with `staleFor`. A failed check leaves the chips as they were.
 */
export function useCitationStatus(messages: ChatMessage[]): Record<string, CitationState> {
  const [states, setStates] = useState<Record<string, CitationState>>({});
  const [tick, setTick] = useState(0);

  const sources = useMemo(() => {
    const unique = new Map<string, CitedSource>();
    for (const m of messages) {
      if (m.streaming) continue;
      for (const s of m.grounding?.sources ?? []) unique.set(keyOf(s), s);
    }
    return [...unique.values()];
  }, [messages]);
  // One string per set of citations, so a token arriving (new `messages`) does not recheck.
  const key = sources.map(keyOf).join("|");

  useEffect(() => {
    const recheck = () => setTick((t) => t + 1);
    window.addEventListener(RELEASE_EVENT, recheck);
    window.addEventListener("focus", recheck);
    return () => {
      window.removeEventListener(RELEASE_EVENT, recheck);
      window.removeEventListener("focus", recheck);
    };
  }, []);

  useEffect(() => {
    if (!key) return;
    let alive = true;
    void (async () => {
      const next: Record<string, CitationState> = {};
      try {
        for (let i = 0; i < sources.length; i += CHECK_BATCH) {
          const batch = sources.slice(i, i + CHECK_BATCH);
          const body = await postJson<{ citations: ({ id: string } & CitationState)[] }>(
            "/api/chat/citations/check",
            { citations: batch },
          );
          // Answers come back in request order.
          body.citations.forEach((c, j) => {
            if (batch[j]) next[keyOf(batch[j])] = { status: c.status, now: c.now };
          });
        }
      } catch {
        return;
      }
      if (alive) setStates(next);
    })();
    return () => {
      alive = false;
    };
    // `sources` is derived from `key`.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, tick]);

  return states;
}
