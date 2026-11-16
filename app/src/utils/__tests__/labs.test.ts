import { describe, expect, it } from "vitest";
import type { LabDetail } from "../../components/courses/types";
import { appendChunk, outputText, type LabRunState } from "../../hooks/useLabRun";
import { changedFiles, languageLabel, moduleLabel, runVerdict } from "../labs";

const lab = {
  files: [
    { path: "run.py", text: "print(1)\n" },
    { path: "config.yaml", text: "k: 1\n" },
  ],
} as LabDetail;

const run = (over: Partial<LabRunState>): LabRunState => ({
  mode: "run", running: false, command: "uv run run.py", output: [], images: [],
  exit: 0, seconds: 1.5, timedOut: false, truncated: false, error: null, ...over,
});

describe("lab helpers", () => {
  it("labels modules and languages", () => {
    expect(moduleLabel("01-classical-ml")).toBe("Classical ml");
    expect(moduleLabel("05b-rl")).toBe("Rl");
    expect(languageLabel("jupyter")).toBe("Notebook");
    expect(languageLabel("rust")).toBe("rust");
  });

  it("keeps only edits that differ from the lab's own files", () => {
    expect(changedFiles(lab, { "run.py": "print(2)\n", "config.yaml": "k: 1\n", "stray.py": "x" })).toEqual({
      "run.py": "print(2)\n",
    });
  });

  it("says how a run went", () => {
    expect(runVerdict(run({ running: true }))).toBeNull();
    expect(runVerdict(run({}))).toEqual({ text: "Ran in 1.5s", ok: true });
    expect(runVerdict(run({ exit: 2 }))).toEqual({ text: "Exited with status 2 in 1.5s", ok: false });
    expect(runVerdict(run({ mode: "check" }))).toEqual({ text: "Check passed in 1.5s", ok: true });
    expect(runVerdict(run({ mode: "check", exit: 1 }))?.ok).toBe(false);
    expect(runVerdict(run({ timedOut: true, exit: -9 }))?.text).toBe("Timed out after 1.5s");
    expect(runVerdict(run({ error: "Stopped" }))).toEqual({ text: "Stopped", ok: false });
    expect(runVerdict(run({ exit: null }))?.ok).toBe(false);
  });

  it("merges output chunks from the same stream and joins them as text", () => {
    let out = appendChunk([], { stream: "stdout", text: "a" });
    out = appendChunk(out, { stream: "stdout", text: "b" });
    out = appendChunk(out, { stream: "stderr", text: "!" });
    expect(out).toEqual([{ stream: "stdout", text: "ab" }, { stream: "stderr", text: "!" }]);
    expect(outputText(run({ output: out }))).toBe("ab!");
    expect(outputText(null)).toBe("");
  });
});
