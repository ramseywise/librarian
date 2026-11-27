/**
 * Interviewing question banks as a two-voice mock interview: one voice asks, the other answers.
 * Nothing is generated. The words are the bank's own, and an answer a bank keeps apart from its
 * question (a collapsed block, an answer key) is withheld so listening does not spoil it.
 */
import type { LessonOutline } from "../components/courses/types";
import type { SpeechSegment } from "../hooks/useSpeech";
import { ANSWER_KEY_RE, stripFrontmatter, toSpeech } from "./speechText";

export type Withheld = "collapsed" | "answer-key";

export interface Exchange {
  question: string;
  /** Spoken text of the answer. Null when the bank has none here or it is withheld. */
  answer: string | null;
  withheld: Withheld | null;
}

export interface ParsedBank {
  exchanges: Exchange[];
  /** Headings with content that matched no known question shape. They are not read. */
  unparsed: string[];
}

const ANSWER_LABELS = new Set([
  "60-second answer", "one level deeper", "model answer", "model answer structure",
  "strong response structure", "approach", "what strong looks like",
]);
const QUESTION_LABELS = new Set(["prompt", "the scenario", "scenario", "setup"]);
const SKIPPED_LABELS = new Set([
  "what they're testing", "what they’re testing", "testing", "study ref", "study refs", "red flags",
  "common pitfalls", "follow-up probes", "key signals", "sources", "signal", "prep",
]);

const LABEL_RE = /^\*\*([^*"“]{1,40}?):?\*\*:?\s*(.*)$/;
const NUMBERED_RE = /^(?:Q\d+[a-z]?\s*[:.]\s*|\d+\.\s+)/i;
const MCQ_ID_RE = /^[A-Z]\d+$/;

/** The lessons on a module page that are question banks. */
export function isQuestionBank(lesson: Pick<LessonOutline, "id" | "kind">): boolean {
  return lesson.kind === "reading" && /\/(?:questions|[\w-]+-bank)$/.test(lesson.id) && lesson.id.startsWith("interviewing/");
}

interface Section {
  level: number;
  heading: string;
  lines: string[];
}

function sectionsOf(body: string): Section[] {
  const sections: Section[] = [];
  let current: Section = { level: 0, heading: "", lines: [] };
  let fence = false;
  for (const line of stripFrontmatter(body).replace(/\r\n?/g, "\n").split("\n")) {
    if (/^ {0,3}(`{3,}|~{3,})/.test(line)) fence = !fence;
    const heading = fence ? null : /^(#{1,6})[ \t]+(.+?)[ \t]*$/.exec(line);
    if (heading) {
      sections.push(current);
      current = { level: heading[1].length, heading: heading[2], lines: [] };
    } else {
      current.lines.push(line);
    }
  }
  sections.push(current);
  return sections;
}

const hasContent = (lines: string[]) => lines.some((l) => l.trim() && !/^\s*(?:-{3,}|\*{3,})\s*$/.test(l));

/** The question heading as spoken: no "Q3:" or "3." prefix, no surrounding quotes, no aside. */
function questionFrom(heading: string): string {
  return heading
    .replace(NUMBERED_RE, "")
    .replace(/\s*\((?:[^()]*)\)\s*$/, "")
    .trim()
    .replace(/^["“](.*)["”]$/, "$1");
}

function labelled(lines: string[]): { question: string[]; answer: string[]; found: boolean } {
  const question: string[] = [];
  const answer: string[] = [];
  let into: string[] | null = null;
  let found = false;
  for (const line of lines) {
    if (/^\s*(?:-{3,}|\*{3,})\s*$/.test(line)) {
      into = null;
      continue;
    }
    const m = LABEL_RE.exec(line.trim());
    const label = m?.[1].trim().toLowerCase();
    if (m && label && (ANSWER_LABELS.has(label) || QUESTION_LABELS.has(label) || SKIPPED_LABELS.has(label))) {
      into = ANSWER_LABELS.has(label) ? answer : QUESTION_LABELS.has(label) ? question : null;
      if (ANSWER_LABELS.has(label)) found = true;
      if (into && m[2]) into.push(m[2]);
      if (into) into.push("");
      continue;
    }
    into?.push(line);
  }
  return { question, answer, found };
}

/** Every `<summary>` that asks a question, from a section whose answers are collapsed. */
function collapsedQuestions(lines: string[]): string[] {
  const text = lines.join("\n");
  return [...text.matchAll(/<details(?:\s[^>]*)?>\s*<summary(?:\s[^>]*)?>([\s\S]*?)<\/summary>/gi)]
    .map((m) => toSpeech(m[1].replace(/<[^>]+>/g, "")).replace(/^Q\s*:\s*/i, ""))
    .filter(Boolean);
}

function mcqQuestion(lines: string[]): string {
  const keyAt = lines.findIndex((l) => ANSWER_KEY_RE.test(l));
  return toSpeech((keyAt === -1 ? lines : lines.slice(0, keyAt)).join("\n"));
}

export function parseQuestionBank(body: string): ParsedBank {
  const exchanges: Exchange[] = [];
  const unparsed: string[] = [];
  const sections = sectionsOf(body);

  for (const [i, section] of sections.entries()) {
    const heading = section.heading.trim();
    if (!section.level) continue; // text before the first heading is not a question
    const hasChild = sections[i + 1] !== undefined && sections[i + 1].level > section.level;
    if (/<details(?:\s|>)/i.test(section.lines.join("\n"))) {
      for (const question of collapsedQuestions(section.lines)) {
        exchanges.push({ question, answer: null, withheld: "collapsed" });
      }
      continue;
    }
    if (MCQ_ID_RE.test(heading)) {
      const question = mcqQuestion(section.lines);
      if (question) exchanges.push({ question, answer: null, withheld: "answer-key" });
      else unparsed.push(heading);
      continue;
    }
    if (hasChild && !hasContent(section.lines)) continue; // only groups the questions under it
    const parts = labelled(section.lines);
    const shaped = NUMBERED_RE.test(heading) || /^["“]/.test(heading);
    if (!parts.found && !shaped) {
      if (hasContent(section.lines) && section.level > 1) unparsed.push(heading);
      continue;
    }
    const prompt = toSpeech(parts.question.join("\n"));
    const question = [toSpeech(questionFrom(heading)), prompt].filter(Boolean).join("\n\n");
    const answer = toSpeech(parts.answer.join("\n"));
    if (question) exchanges.push({ question, answer: answer || null, withheld: null });
  }
  return { exchanges, unparsed };
}

/** Why some answers are not read, if any are not. Spoken and shown. */
export function withheldNote(bank: ParsedBank): string | null {
  const collapsed = bank.exchanges.some((e) => e.withheld === "collapsed");
  const keyed = bank.exchanges.some((e) => e.withheld === "answer-key");
  if (collapsed) return "The answers in this bank are collapsed on the page, so only the questions are read.";
  if (keyed) return "The answer key is kept for the page, so only the questions and their options are read.";
  return null;
}

/** Questions in the interviewer's voice, answers in the candidate's, grouped so one can be skipped. */
export function bankToSegments(bank: ParsedBank): SpeechSegment[] {
  const total = bank.exchanges.length;
  const note = withheldNote(bank);
  const segments: SpeechSegment[] = [];
  if (note) segments.push({ text: note, role: "candidate", pauseAfterMs: 900 });
  bank.exchanges.forEach((exchange, i) => {
    const groupLabel = `Question ${i + 1} of ${total}`;
    segments.push({
      text: exchange.question,
      role: "interviewer",
      label: "Question",
      group: i,
      groupLabel,
      // No answer follows a withheld question: leave time to think of one.
      pauseAfterMs: exchange.answer ? 900 : 3000,
    });
    if (exchange.answer) {
      segments.push({ text: exchange.answer, role: "candidate", label: "Answer", group: i, groupLabel, pauseAfterMs: 1200 });
    }
  });
  return segments;
}
