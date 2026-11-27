/**
 * What a voice session shows, kept apart from the Pipecat client so it needs no heavy imports.
 * Nothing here is stored: the transcript lives in component state and goes when the drawer closes.
 */

/** Shown in the Voice drawer on the interviewing course, in place of a cloud notice. */
export const VOICE_LOCAL_ONLY_NOTICE = "Local only: speech is heard and spoken on this machine, never by a hosted service.";
/** The one thing that leaves the machine in interview mode. */
export const VOICE_ANSWERS_NOTICE = "Your answers go to the Anthropic API as text.";
/** Everywhere else, unless a hosted speech service has been switched on by env key. */
export const VOICE_LOCAL_DEFAULT_NOTICE = "Speech runs on this machine. What you say goes to the Anthropic API as text.";

export type VoiceMode = "flashcard" | "approach" | "interview";

/** A session is on a lesson or a deck. The server decides what that lesson or deck allows. */
export type VoiceTarget = { mode: VoiceMode; lesson?: string; deck?: string };

export interface VoiceSessionInfo {
  sessionId: string;
  /** Where the browser sends its WebRTC offer. */
  offer: string;
  localOnly: boolean;
  stt: string;
  tts: string;
}

export interface TurnLatency {
  turn: number;
  vad_stop_ms: number | null;
  stt_ms: number | null;
  llm_first_ms: number | null;
  tts_first_ms: number | null;
  gap_ms: number | null;
}

export type VoiceLine =
  | { kind: "you"; text: string; final: boolean }
  | { kind: "coach"; text: string }
  | { kind: "graded"; score: number }
  | { kind: "ungraded"; reason: string };

export interface VoiceView {
  lines: VoiceLine[];
  latency: TurnLatency[];
  /** Why the server ended the session. */
  ended: string | null;
}

export const EMPTY_VIEW: VoiceView = { lines: [], latency: [], ended: null };

const UNGRADED_TEXT: Record<string, string> = {
  no_grade: "no grade was given",
  malformed: "the grade came back malformed",
  refusal: "the model declined to answer",
  cut_off: "the reply was cut off",
  llm_error: "the model call failed",
  write_failed: "the grade could not be saved",
  interrupted: "you interrupted it",
};

const END_TEXT: Record<string, string> = {
  idle: "Session ended: nothing was said for a while.",
  max_duration: "Session ended: it reached its time limit.",
  turn_cap: "Session ended: it reached its turn limit.",
  token_cap: "Session ended: it reached its token limit.",
  deck_end: "That was the last card.",
};

export function ungradedText(reason: string): string {
  return `Not graded: ${UNGRADED_TEXT[reason] ?? "no usable grade"}.`;
}

export function endText(reason: string, message?: unknown): string {
  return typeof message === "string" && message ? message : END_TEXT[reason] ?? "Session ended.";
}

export function userSaid(view: VoiceView, text: string, final: boolean): VoiceView {
  const last: VoiceLine | undefined = view.lines[view.lines.length - 1];
  const line: VoiceLine = { kind: "you", text, final };
  const lines = last?.kind === "you" && !last.final ? [...view.lines.slice(0, -1), line] : [...view.lines, line];
  return { ...view, lines };
}

export function coachSaid(view: VoiceView, text: string): VoiceView {
  const last: VoiceLine | undefined = view.lines[view.lines.length - 1];
  if (last?.kind === "coach") {
    return { ...view, lines: [...view.lines.slice(0, -1), { kind: "coach", text: `${last.text} ${text}` }] };
  }
  return { ...view, lines: [...view.lines, { kind: "coach", text }] };
}

function number(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/** Applies one message from the voice server. Anything unrecognised changes nothing. */
export function serverSaid(view: VoiceView, message: unknown): VoiceView {
  if (typeof message !== "object" || message === null) return view;
  const m = message as Record<string, unknown>;
  switch (m.type) {
    case "grade": {
      const score = number(m.score);
      if (score === null || score < 0 || score > 1) return view;
      return { ...view, lines: [...view.lines, { kind: "graded", score }] };
    }
    case "ungraded":
      return { ...view, lines: [...view.lines, { kind: "ungraded", reason: String(m.reason ?? "") }] };
    case "latency":
      return {
        ...view,
        latency: [
          ...view.latency,
          {
            turn: number(m.turn) ?? view.latency.length + 1,
            vad_stop_ms: number(m.vad_stop_ms),
            stt_ms: number(m.stt_ms),
            llm_first_ms: number(m.llm_first_ms),
            tts_first_ms: number(m.tts_first_ms),
            gap_ms: number(m.gap_ms),
          },
        ],
      };
    case "ended":
      return { ...view, ended: endText(String(m.reason ?? ""), m.message) };
    default:
      return view;
  }
}

/** The API's refusal text, which is written to be shown. */
export async function refusalText(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string" && body.detail) return body.detail;
  } catch {
    // Not JSON: fall through to the status.
  }
  return `Voice is unavailable (${response.status}).`;
}
