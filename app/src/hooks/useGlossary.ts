import { useCallback, useRef, useState } from "react";
import { glossaryMentionsSchema, glossaryTermsSchema } from "../schemas/graph";
import type { Glossary } from "../types";
import { apiFetch, parseJson } from "../utils/api";
import { errorText, type Resource } from "./resource";
import { useRevisionFetch } from "./useRevisionFetch";

/**
 * The glossary and where each term is mentioned; `data` is null until both answer. `revision`
 * changes with each graph payload, so mentions follow the wiki. An unchanged answer keeps the
 * same object, so a graph update can't reshuffle the term filters. The glossary is optional: a
 * failed request leaves the map without term filters, and `error` says why (only while there is
 * nothing to show) so the consumer can offer `retry`.
 */
export function useGlossary(revision: unknown, enabled: boolean): Resource<Glossary> {
  const [glossary, setGlossary] = useState<Glossary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const lastBody = useRef<string | null>(null);

  const load = useCallback(async (alive: () => boolean): Promise<void> => {
    try {
      const [terms, mentions] = await Promise.all([apiFetch("/api/glossary"), apiFetch("/api/glossary/mentions")]);
      if (!terms.ok || !mentions.ok) throw new Error(`HTTP ${terms.ok ? mentions.status : terms.status}`);
      const [termsText, mentionsText] = await Promise.all([terms.clone().text(), mentions.clone().text()]);
      const [termsBody, mentionsBody] = await Promise.all([
        parseJson(terms, glossaryTermsSchema),
        parseJson(mentions, glossaryMentionsSchema),
      ]);
      if (!alive()) return;
      setError(null);
      const body = termsText + mentionsText;
      if (body === lastBody.current) return;
      lastBody.current = body;
      setGlossary({ terms: termsBody.terms, mentions: mentionsBody });
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
  const shown = glossary ? null : error;
  return { data: glossary, error: shown, loading: enabled && !glossary && !shown, retry };
}
