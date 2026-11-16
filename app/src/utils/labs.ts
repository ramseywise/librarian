import type { LabRunState } from "../hooks/useLabRun";
import type { LabDetail } from "../components/courses/types";

/** `01-classical-ml` → `Classical ml`: the module folder as a label. */
export function moduleLabel(module: string): string {
  const words = module.replace(/^\d+[a-z]?-/, "").replace(/[-_]+/g, " ").trim();
  return words ? words[0].toUpperCase() + words.slice(1) : module;
}

export function languageLabel(language: string): string {
  return { python: "Python", typescript: "TypeScript", javascript: "JavaScript", jupyter: "Notebook" }[language] ?? language;
}

/** Files whose editor text differs from the lab's own. */
export function changedFiles(lab: LabDetail, edits: Record<string, string>): Record<string, string> {
  const out: Record<string, string> = {};
  for (const f of lab.files) {
    if (f.path in edits && edits[f.path] !== f.text) out[f.path] = edits[f.path];
  }
  return out;
}

/** One line on how a finished run went, or null while it runs. */
export function runVerdict(run: LabRunState): { text: string; ok: boolean } | null {
  if (run.running) return null;
  if (run.error) return { text: run.error, ok: false };
  if (run.timedOut) return { text: `Timed out after ${run.seconds ?? "?"}s`, ok: false };
  if (run.exit === null) return { text: "The run ended without a result", ok: false };
  const took = run.seconds !== null ? ` in ${run.seconds}s` : "";
  if (run.mode === "check") return run.exit === 0 ? { text: `Check passed${took}`, ok: true } : { text: `Check failed (exit ${run.exit})${took}`, ok: false };
  return run.exit === 0 ? { text: `Ran${took}`, ok: true } : { text: `Exited with status ${run.exit}${took}`, ok: false };
}
