/** A lesson note split by what the reader does with each part: read it (lecture), answer it (review) or run it
 * (exercises and code). The notes are written as one file: prose with code after each idea, then `## Try it`
 * and `## Interview checklist`. Each part is markdown, empty when the note has none of it. */
export interface LessonParts {
  /** The prose. A code block that moved to `code` leaves a `[Code N in Labs →](#code-N)` link in its place. */
  lecture: string;
  /** The `## Interview checklist` table, under the heading "Review questions". */
  review: string;
  /** The `## Try it` exercises, as written. */
  exercises: string;
  /** The code blocks taken out of the prose, each with its output, under the heading it came from. */
  code: string;
  codeCount: number;
}

/** Fences that are part of the explanation, not code to run: diagrams, formulas, printed output. */
const PROSE_LANGS = new Set(["", "text", "txt", "output", "console", "mermaid", "math"]);
const OUTPUT_LANGS = new Set(["", "text", "txt", "output", "console"]);
/** A shorter snippet reads as part of the sentence around it, so it stays in the prose. */
const MIN_CODE_LINES = 4;

const FENCE_RE = /^ {0,3}(`{3,}|~{3,})\s*([\w+#.-]*)/;
const HEADING_RE = /^(#{2,3})\s+(.+?)\s*#*\s*$/;
const RULE_RE = /^ {0,3}(?:-{3,}|\*{3,}|_{3,})\s*$/;

type Bucket = "lecture" | "review" | "exercises";

function bucketOf(h2: string): Bucket {
  if (/^try it\b/i.test(h2)) return "exercises";
  if (/^interview checklist\b/i.test(h2)) return "review";
  return "lecture";
}

/** Blank lines and `---` rules left at the end once the section after them has moved out. */
function trimEnd(lines: string[]): string {
  const out = [...lines];
  while (out.length && (!out[out.length - 1].trim() || RULE_RE.test(out[out.length - 1]))) out.pop();
  return out.join("\n");
}

export function splitLesson(body: string): LessonParts {
  const lines = body.split("\n");
  const out: Record<Bucket, string[]> = { lecture: [], review: [], exercises: [] };
  const code: string[] = [];
  let bucket: Bucket = "lecture";
  let heading = "";
  let codeHeading: string | null = null;
  let codeCount = 0;
  let awaitingOutput = false; // the last block moved to `code`: a printed-output fence next goes with it

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const fence = line.match(FENCE_RE);
    if (!fence) {
      const h = line.match(HEADING_RE);
      if (h) {
        if (h[1] === "##") bucket = bucketOf(h[2]);
        heading = h[2];
        awaitingOutput = false;
        // A rule before a section that moved out belongs to nothing in the lecture.
        if (bucket !== "lecture" && h[1] === "##") out.lecture = trimEnd(out.lecture).split("\n");
        if (bucket === "review" && h[1] === "##") {
          out.review.push("## Review questions");
          continue;
        }
      } else if (line.trim()) {
        awaitingOutput = false;
      }
      out[bucket].push(line);
      continue;
    }

    // A fenced block: runs to the closing fence of the same character and at least the same length.
    const [, marker, lang] = fence;
    const close = new RegExp(`^ {0,3}${marker[0]}{${marker.length},}\\s*$`);
    let end = i + 1;
    while (end < lines.length && !close.test(lines[end])) end++;
    const block = lines.slice(i, Math.min(end + 1, lines.length));
    i = end;

    const isCode = !PROSE_LANGS.has(lang.toLowerCase()) && block.length - 2 >= MIN_CODE_LINES;
    const isOutput = awaitingOutput && OUTPUT_LANGS.has(lang.toLowerCase());
    if (bucket !== "lecture" || !(isCode || isOutput)) {
      out[bucket].push(...block);
      awaitingOutput = false;
      continue;
    }
    if (isCode) {
      codeCount++;
      if (heading !== codeHeading) {
        if (heading) code.push(`### ${heading}`, "");
        codeHeading = heading;
      }
      code.push(`<a id="code-${codeCount}"></a>`, "");
      out.lecture.push(`[Code ${codeCount} in Labs →](#code-${codeCount})`);
    }
    code.push(...block, "");
    awaitingOutput = true;
  }

  return {
    lecture: trimEnd(out.lecture),
    review: trimEnd(out.review),
    exercises: trimEnd(out.exercises),
    code: code.length ? `## Code from this lesson\n\n${trimEnd(code)}` : "",
    codeCount,
  };
}
