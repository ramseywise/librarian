import { useCallback, useRef, useState } from "react";
import type { Glossary, GlossaryTerm } from "../types";
import { apiFetch } from "../utils/api";
import { useRevisionFetch } from "./useRevisionFetch";

/**
 * The glossary and where each term is mentioned; null until both answer. `revision` changes with
 * each graph payload, so mentions follow the wiki. An unchanged answer keeps the same object,
 * so a graph update can't reshuffle the term layer. The layer is optional: a failed request
 * leaves the map without terms and without an error.
 */
export function useGlossary(revision: unknown, enabled: boolean): Glossary | null {
  const [glossary, setGlossary] = useState<Glossary | null>(null);
  const lastBody = useRef<string | null>(null);

  const load = useCallback(async (alive: () => boolean): Promise<void> => {
    try {
      const [terms, mentions] = await Promise.all([apiFetch("/api/glossary"), apiFetch("/api/glossary/mentions")]);
      if (!terms.ok || !mentions.ok) return;
      const [termsText, mentionsText] = await Promise.all([terms.text(), mentions.text()]);
      if (!alive()) return;
      const body = termsText + mentionsText;
      if (body === lastBody.current) return;
      lastBody.current = body;
      setGlossary({
        terms: (JSON.parse(termsText) as { terms: GlossaryTerm[] }).terms,
        mentions: JSON.parse(mentionsText) as Record<string, string[]>,
      });
    } catch {
      // Keep what we have; the next graph payload retries.
    }
  }, []);
  useRevisionFetch(load, revision, enabled);

  return glossary;
}
