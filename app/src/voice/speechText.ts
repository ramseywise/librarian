/**
 * Lesson markdown to text a speech engine can read.
 *
 * Nothing here decides what is safe to speak on its own terms except the parts that say so:
 * `<details>` bodies never reach speech, and a drill reads only its Prompt section or nothing.
 * Symbols are never read out: code, math and tables are announced, not spelled.
 */

const FRONTMATTER_RE = /^\uFEFF?---[ \t]*\r?\n[\s\S]*?\r?\n---[ \t]*(?:\r?\n|$)/;
const FENCE_OPEN_RE = /^ {0,3}(`{3,}|~{3,})[ \t]*([^\s`]*)/;
const HEADING_RE = /^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$/;
const TABLE_RULE_RE = /^ {0,3}\|?[ \t]*:?-{1,}:?[ \t]*(\|[ \t]*:?-{1,}:?[ \t]*)*\|?[ \t]*$/;

/** A heading or summary that names a solution, answer or hint, in any of the forms seen or likely. */
const SPOILER_LABEL_RE =
  /^(?:(?:reference|model|worked|sample|full|suggested)\s+)?(?:solutions?|answers?|answer\s+key|hints?)(?:\s*\d+)?(?:\s*[:.—–-].*)?$/i;
/** A line in a prompt that starts giving the solution away ("**Answer:** 3", "Solution: ..."). */
const SPOILER_LINE_RE = /^\s*(?:>\s*)?(?:\*\*|__)?(?:solutions?|answers?(?:\s+key)?|hints?)(?:\s*\d+)?\s*(?:\*\*|__)?\s*:/i;
/** MCQ answer keys and their rationale: everything after one of these is withheld. */
export const ANSWER_KEY_RE = /^\s*(?:\*\*|__)(?:answers?(?:\s+key)?(?:\s+\S+)?|rationale(?:\s+notes)?):?(?:\*\*|__)/i;

export const stripFrontmatter = (md: string) => md.replace(FRONTMATTER_RE, "");

/** The text of a `<summary>`, without its tags and with its markup cleaned. */
function summaryText(block: string): string {
  const m = /<summary(?:\s[^>]*)?>([\s\S]*?)<\/summary>/i.exec(block);
  return m ? cleanInline(stripTags(m[1])).trim() : "";
}

const stripTags = (html: string) => html.replace(/<[^>]+>/g, "");

const finishSentence = (line: string) => (/[.!?:;,]["')\]]*$/.test(line) ? line : `${line}.`);

/** A code span is spoken when it reads as words; `x[i]->y` is announced instead of spelled. */
function speakCode(code: string): string {
  const symbols = code.replace(/[\w\s.,()'"-]/g, "").length;
  if (symbols > 2 || symbols / Math.max(code.length, 1) > 0.2) return "a code snippet";
  return code.replace(/_/g, " ");
}

const ENTITIES: Record<string, string> = {
  amp: "&", lt: "less than", gt: "greater than", quot: '"', apos: "'", nbsp: " ", mdash: ", ", ndash: ", ", hellip: "...",
};

function decodeEntities(text: string): string {
  return text
    .replace(/&#(\d+);/g, (_, n: string) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n: string) => String.fromCodePoint(parseInt(n, 16)))
    .replace(/&([a-z]+);/gi, (whole, name: string) => ENTITIES[name.toLowerCase()] ?? whole);
}

const URL_RE = /\b(?:https?:\/\/|www\.)[^\s<>)\]]+/gi;

function cleanProse(text: string): string {
  return decodeEntities(
    text
      // Math first: `$` and `\(` must go before emphasis and escapes touch their bodies.
      .replace(/\\\((.+?)\\\)/g, "a formula")
      .replace(/(^|[^\\$\w])\$(?=[^\s$])([^$\n]*?[^\s\\$])\$(?![\d$])/g, "$1a formula")
      // Images before links, which they contain.
      .replace(/!\[([^\]]*)\]\([^)]*\)/g, (_, alt: string) => (alt.trim() ? `Image: ${alt.trim()}.` : ""))
      .replace(/!\[([^\]]*)\]\[[^\]]*\]/g, (_, alt: string) => (alt.trim() ? `Image: ${alt.trim()}.` : ""))
      .replace(/<img\b[^>]*>/gi, (tag) => {
        const alt = /\balt\s*=\s*"([^"]*)"/i.exec(tag)?.[1]?.trim();
        return alt ? `Image: ${alt}.` : "";
      })
      .replace(/\[\[([^\]|]+)\|([^\]]+)\]\]/g, "$2")
      .replace(/\[\[([^\]]+)\]\]/g, "$1")
      .replace(/\[\^[^\]]+\]/g, "")
      .replace(/\[([^\]]*)\]\([^)]*\)/g, (_, label: string) => (/^(?:https?:\/\/|www\.)/i.test(label) ? "a link" : label))
      .replace(/\[([^\]]+)\]\[[^\]]*\]/g, "$1")
      .replace(/<(?:https?:\/\/|mailto:)[^>]+>/gi, "a link")
      .replace(URL_RE, "a link")
      .replace(/<[^>\n]+>/g, "")
      .replace(/(\*\*|__)(?=\S)(.+?)\1/g, "$2")
      .replace(/(^|[^\w*])\*(?=[^\s*])([^*\n]+?)\*(?![\w*])/g, "$1$2")
      .replace(/(^|[^\w_])_(?=[^\s_])([^_\n]+?)_(?![\w_])/g, "$1$2")
      .replace(/~~(.+?)~~/g, "$1")
      .replace(/\\([\\`*_{}[\]()#+\-.!|~$])/g, "$1")
      // An em-dash reads better as a pause than as the word "dash".
      .replace(/\s*[—–]\s*/g, ", ")
      .replace(/\s*(?:→|->|=>)\s*/g, " to ")
      .replace(/[*#|~`]/g, " ")
  );
}

/** Inline markdown to speech, leaving code spans out of the emphasis and math passes. */
function cleanInline(line: string): string {
  return line
    .split(/(`[^`\n]+`)/)
    .map((part) => (part.length > 2 && part.startsWith("`") && part.endsWith("`") ? speakCode(part.slice(1, -1)) : cleanProse(part)))
    .join("")
    .replace(/[ \t]{2,}/g, " ")
    .trim();
}

/**
 * Remove every `<details>` block outside a code fence, leaving a marker line. An unclosed block
 * takes the rest of the text with it: what follows may well be its body.
 */
function dropDetails(lines: string[]): string[] {
  const out: string[] = [];
  let fence: string | null = null;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const open = FENCE_OPEN_RE.exec(line);
    if (fence) {
      if (open && open[1].startsWith(fence) && !open[2]) fence = null;
      out.push(line);
      continue;
    }
    if (open) {
      fence = open[1];
      out.push(line);
      continue;
    }
    const at = line.search(/<details(?:\s|>)/i);
    if (at === -1) {
      out.push(line);
      continue;
    }
    if (line.slice(0, at).trim()) out.push(line.slice(0, at));
    let depth = 0;
    const block: string[] = [];
    let j = i;
    let rest = line.slice(at);
    for (;;) {
      block.push(rest);
      depth += (rest.match(/<details(?:\s|>)/gi) ?? []).length - (rest.match(/<\/details>/gi) ?? []).length;
      if (depth <= 0 || ++j >= lines.length) break;
      rest = lines[j];
    }
    const label = summaryText(block.join("\n"));
    out.push(label ? `Collapsed section, not read: ${finishSentence(label)}` : "Collapsed section, not read.", "");
    i = depth > 0 ? lines.length : j;
    if (depth === 0) {
      const after = rest.slice(rest.toLowerCase().lastIndexOf("</details>") + "</details>".length);
      if (after.trim()) out.push(after);
    }
  }
  return out;
}

/** Markdown to text for speech: blocks announced or dropped, inline markup stripped, sentences closed. */
export function toSpeech(markdown: string): string {
  const source = stripFrontmatter(markdown)
    .replace(/\r\n?/g, "\n")
    .replace(/<!--[\s\S]*?(?:-->|$)/g, "")
    .replace(/<(script|style)\b[\s\S]*?(?:<\/\1>|$)/gi, "");
  const lines = dropDetails(source.split("\n"));
  const paragraphs: string[] = [];
  let current: string[] = [];
  const flush = () => {
    if (current.length) paragraphs.push(current.join(" "));
    current = [];
  };
  const block = (text: string) => {
    flush();
    paragraphs.push(text);
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) {
      flush();
      continue;
    }
    const fence = FENCE_OPEN_RE.exec(line);
    if (fence) {
      for (i++; i < lines.length; i++) {
        const close = FENCE_OPEN_RE.exec(lines[i]);
        if (close && close[1].startsWith(fence[1]) && !close[2]) break;
      }
      const language = fence[2].replace(/^\{|\}$/g, "");
      block(/^(math|latex)$/i.test(language) ? "Equation omitted." : `${language ? `${language} code` : "Code"} block omitted.`);
      continue;
    }
    if (/^ {0,3}(\$\$|\\\[)/.test(line)) {
      const closer = line.trim().startsWith("$$") ? "$$" : "\\]";
      const opener = line.trim().slice(0, 2);
      if (line.trim().slice(opener.length).indexOf(closer) === -1) {
        for (i++; i < lines.length && !lines[i].includes(closer); i++);
      }
      block("Equation omitted.");
      continue;
    }
    if (line.includes("|") && TABLE_RULE_RE.test(lines[i + 1] ?? "") && lines[i + 1].includes("-")) {
      let rows = 0;
      for (i += 2; i < lines.length && lines[i].includes("|"); i++) rows++;
      i--;
      block(`Table omitted, ${rows} ${rows === 1 ? "row" : "rows"}.`);
      continue;
    }
    if (/^(?: {4}|\t)/.test(line) && !current.length && !isListContext(lines, i)) {
      while (i + 1 < lines.length && (/^(?: {4}|\t)/.test(lines[i + 1]) || (!lines[i + 1].trim() && /^(?: {4}|\t)/.test(lines[i + 2] ?? "")))) i++;
      block("Code block omitted.");
      continue;
    }
    if (/^ {0,3}([-*_])[ \t]*(?:\1[ \t]*){2,}$/.test(line)) {
      flush();
      continue;
    }
    if (/^ {0,3}\[[^\]]+\]:\s+\S+/.test(line)) continue; // link reference definition
    const heading = HEADING_RE.exec(line);
    if (heading) {
      const text = cleanInline(heading[2]);
      if (text) block(finishSentence(text));
      continue;
    }
    const item = /^\s*(?:[-*+•]|(\d+)[.)])\s+(?:\[[ xX]\]\s+)?(.*)$/.exec(line);
    if (item) {
      flush();
      const text = cleanInline(item[2]);
      if (text) current.push(finishSentence(item[1] ? `${item[1]}. ${text}` : text));
      continue;
    }
    const prose = cleanInline(line.replace(/^\s*(?:>\s*)+/, ""));
    if (prose) current.push(prose);
  }
  flush();
  return paragraphs
    .map((p) => p.replace(/\s+([.,;:!?])/g, "$1").replace(/\s{2,}/g, " ").trim())
    .filter((p) => /[\p{L}\p{N}]/u.test(p))
    .join("\n\n");
}

/** An indented line that continues a list item is prose, not code. */
function isListContext(lines: string[], at: number): boolean {
  for (let i = at - 1; i >= 0; i--) {
    if (!lines[i].trim()) continue;
    return /^\s*(?:[-*+•]|\d+[.)])\s/.test(lines[i]) || /^(?: {2,}|\t)/.test(lines[i]);
  }
  return false;
}

/**
 * Split speech into pieces short enough to survive a long-utterance cutoff (Chrome ends some
 * voices at around 15 seconds): by paragraph and sentence, then at commas, then at spaces.
 */
export function chunkForSpeech(text: string, max = 180): string[] {
  const chunks: string[] = [];
  const push = (piece: string) => {
    const last = chunks[chunks.length - 1];
    if (last !== undefined && last.length + piece.length + 1 <= max) chunks[chunks.length - 1] = `${last} ${piece}`;
    else chunks.push(piece);
  };
  for (const paragraph of text.split(/\n{2,}/)) {
    const start = chunks.length;
    for (const sentence of splitKeeping(paragraph.trim(), /([.!?]+["')\]]*)\s+/)) {
      if (sentence.length <= max) {
        if (chunks.length > start) push(sentence);
        else if (sentence) chunks.push(sentence);
        continue;
      }
      for (const clause of splitKeeping(sentence, /([,;:])\s+/)) {
        if (clause.length <= max) {
          if (clause) push(clause);
          continue;
        }
        for (const word of clause.split(/\s+/)) push(word.slice(0, max));
      }
    }
  }
  return chunks;
}

/** Split on a separator with one capture group, keeping the capture on the piece before it. */
function splitKeeping(text: string, separator: RegExp): string[] {
  const parts = text.split(separator);
  const out: string[] = [];
  for (let i = 0; i < parts.length; i += 2) out.push(`${parts[i]}${parts[i + 1] ?? ""}`.trim());
  return out.filter(Boolean);
}

export interface SpeechSection {
  heading: string;
  text: string;
}

/**
 * A lesson as one spoken section per h1-h3. A heading that names a solution, answer or hint is
 * announced and skipped even when the page shows it, and so is an answer key after its marker.
 */
export function lessonSections(markdown: string, title: string): SpeechSection[] {
  const lines = stripFrontmatter(markdown).replace(/\r\n?/g, "\n").split("\n");
  const raw: { heading: string; lines: string[] }[] = [{ heading: title, lines: [] }];
  let fence: string | null = null;
  let details = 0;
  let inAnswerKey = false;
  for (const line of lines) {
    const open = FENCE_OPEN_RE.exec(line);
    if (fence) {
      if (open && open[1].startsWith(fence) && !open[2]) fence = null;
    } else if (open) {
      fence = open[1];
    } else {
      details += (line.match(/<details(?:\s|>)/gi) ?? []).length - (line.match(/<\/details>/gi) ?? []).length;
      const heading = details <= 0 ? HEADING_RE.exec(line) : null;
      if (heading && heading[1].length <= 3) {
        raw.push({ heading: cleanInline(heading[2]), lines: [] });
        inAnswerKey = false;
        continue;
      }
      if (details <= 0 && ANSWER_KEY_RE.test(line)) inAnswerKey = true;
    }
    if (!inAnswerKey) raw[raw.length - 1].lines.push(line);
  }
  const sections: SpeechSection[] = [];
  raw.forEach(({ heading, lines: body }, i) => {
    if (i > 0 && SPOILER_LABEL_RE.test(heading.trim())) {
      sections.push({ heading, text: `Section ${finishSentence(heading)} Not read.` });
      return;
    }
    const spoken = toSpeech(body.join("\n"));
    if (spoken) sections.push({ heading, text: i > 0 ? `${finishSentence(heading)}\n\n${spoken}` : spoken });
    else if (i > 0) sections.push({ heading, text: finishSentence(heading) });
  });
  return sections;
}

export type DrillPrompt = { ok: true; text: string } | { ok: false; reason: string };

/** A drill's lines with code fences blanked, so nothing inside an example can look like structure. */
function maskFences(lines: string[]): string[] {
  let fence: string | null = null;
  return lines.map((line) => {
    const open = FENCE_OPEN_RE.exec(line);
    if (fence) {
      if (open && open[1].startsWith(fence) && !open[2]) fence = null;
      return "";
    }
    if (open) {
      fence = open[1];
      return "";
    }
    return line;
  });
}

/**
 * The one thing a drill may say aloud: its `Prompt` section. Reads nothing unless the shape is
 * fully understood, because the Solution, the Hints and even the Tests give the drill away:
 * exactly one Prompt heading, closed by a later heading, with a Solution recognised after it and
 * no solution-like content inside it.
 */
export function drillPromptSpeech(body: string): DrillPrompt {
  const lines = stripFrontmatter(body).replace(/\r\n?/g, "\n").split("\n");
  const masked = maskFences(lines);
  const headings = masked.flatMap((line, at) => {
    const m = HEADING_RE.exec(line);
    return m ? [{ at, text: cleanInline(m[2]).replace(/:$/, "").trim() }] : [];
  });
  const prompts = headings.filter((h) => /^prompt$/i.test(h.text));
  if (prompts.length === 0) return { ok: false, reason: "it has no Prompt section" };
  if (prompts.length > 1) return { ok: false, reason: "it has more than one Prompt section" };

  const prompt = prompts[0];
  const end = headings.find((h) => h.at > prompt.at);
  if (!end) return { ok: false, reason: "nothing marks where its Prompt section ends" };
  const before = masked.slice(0, prompt.at).join("\n");
  if (/<details(?:\s|>)|<summary(?:\s|>)/i.test(before)) {
    return { ok: false, reason: "it has a collapsed block before the Prompt" };
  }
  const section = masked.slice(prompt.at + 1, end.at);
  const sectionText = section.join("\n");
  if (/<details(?:\s|>)|<summary(?:\s|>)|<[^>]*(?:solution|answer)[^>]*>/i.test(sectionText)) {
    return { ok: false, reason: "its Prompt section contains a collapsed or marked block" };
  }
  if (section.some((line) => SPOILER_LINE_RE.test(line))) {
    return { ok: false, reason: "its Prompt section appears to contain an answer" };
  }

  const rest = masked.slice(end.at).join("\n");
  const namedHeading = headings.some((h) => h.at > prompt.at && SPOILER_LABEL_RE.test(h.text) && !/^hints?\b/i.test(h.text));
  const summaries = [...rest.matchAll(/<summary(?:\s[^>]*)?>([\s\S]*?)<\/summary>/gi)].map((m) => stripTags(m[1]).trim());
  const namedSummary = summaries.some((s) => SPOILER_LABEL_RE.test(s) && !/^hints?\b/i.test(s));
  if (!namedHeading && !namedSummary) {
    return { ok: false, reason: "its Solution is not marked in a way this app recognises" };
  }

  const text = toSpeech(lines.slice(prompt.at + 1, end.at).join("\n"));
  return text ? { ok: true, text } : { ok: false, reason: "its Prompt section has nothing to read" };
}
