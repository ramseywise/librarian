import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch } from "../utils/api";
import { createSseParser, describeHttpError, NETWORK_ERROR } from "./useChatStream";

export type LabRunMode = "run" | "check";

export interface LabOutputChunk {
  stream: "stdout" | "stderr";
  text: string;
}

export interface LabImage {
  path: string;
  mime: string;
  data: string;
}

export interface LabRunState {
  mode: LabRunMode;
  running: boolean;
  command: string;
  output: LabOutputChunk[];
  images: LabImage[];
  /** Set by the `done` event. */
  exit: number | null;
  seconds: number | null;
  timedOut: boolean;
  truncated: boolean;
  /** The run could not start or the stream failed; the server's or the network's reason. */
  error: string | null;
}

/** The run's output as one text, stdout and stderr interleaved as they arrived. */
export function outputText(run: LabRunState | null): string {
  return run ? run.output.map((c) => c.text).join("") : "";
}

/** Merge a chunk into the list, extending the last one when it is the same stream. */
export function appendChunk(output: LabOutputChunk[], chunk: LabOutputChunk): LabOutputChunk[] {
  const last = output[output.length - 1];
  if (last && last.stream === chunk.stream) return [...output.slice(0, -1), { ...last, text: last.text + chunk.text }];
  return [...output, chunk];
}

/**
 * Runs one lab on the server (POST /api/courses/lab-runs, dev machines only) and streams its
 * output. `start` replaces any run in flight; `stop` closes the stream, which kills the process.
 */
export function useLabRun(labId: string) {
  const [run, setRun] = useState<LabRunState | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  useEffect(() => () => controllerRef.current?.abort(), []);
  useEffect(() => {
    controllerRef.current?.abort();
    setRun(null);
  }, [labId]);

  const start = useCallback(
    async (mode: LabRunMode, files: Record<string, string>) => {
      controllerRef.current?.abort();
      const controller = new AbortController();
      controllerRef.current = controller;
      const patch = (fn: (r: LabRunState) => LabRunState) =>
        !controller.signal.aborted && setRun((r) => (r ? fn(r) : r));
      setRun({
        mode, running: true, command: "", output: [], images: [],
        exit: null, seconds: null, timedOut: false, truncated: false, error: null,
      });
      try {
        const resp = await apiFetch("/api/courses/lab-runs", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ lab: labId, mode, files }),
          signal: controller.signal,
        });
        if (!resp.ok || !resp.body) {
          const body: unknown = await resp.json().catch(() => null);
          patch((r) => ({ ...r, running: false, error: describeHttpError(resp.status, body) }));
          return;
        }
        const parser = createSseParser((event) => {
          if (event.type === "start") patch((r) => ({ ...r, command: String(event.command ?? "") }));
          else if (event.type === "output") {
            const chunk = { stream: event.stream === "stderr" ? "stderr" : "stdout", text: String(event.text ?? "") } as const;
            patch((r) => ({ ...r, output: appendChunk(r.output, chunk) }));
          } else if (event.type === "image") {
            const image = { path: String(event.path), mime: String(event.mime), data: String(event.data) };
            patch((r) => ({ ...r, images: [...r.images, image] }));
          } else if (event.type === "done") {
            patch((r) => ({
              ...r,
              exit: typeof event.exit === "number" ? event.exit : null,
              seconds: typeof event.seconds === "number" ? event.seconds : null,
              timedOut: event.timedOut === true,
              truncated: event.truncated === true,
            }));
          } else if (event.type === "error") {
            patch((r) => ({ ...r, error: String(event.message ?? "The run failed") }));
          }
        });
        const reader = resp.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          parser.push(decoder.decode(value, { stream: true }));
        }
        parser.push(decoder.decode());
        parser.end();
        patch((r) => ({ ...r, running: false }));
      } catch {
        if (controller.signal.aborted) {
          setRun((r) => (r && controllerRef.current === controller ? { ...r, running: false, error: "Stopped" } : r));
        } else {
          patch((r) => ({ ...r, running: false, error: NETWORK_ERROR }));
        }
      }
    },
    [labId],
  );

  const stop = useCallback(() => controllerRef.current?.abort(), []);

  return { run, start, stop };
}
