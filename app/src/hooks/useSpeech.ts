import { useCallback, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { chunkForSpeech } from "../voice/speechText";

/*
 * Browser speech (Web Speech API): one synthesis queue and one recognition session per page.
 * There is one of each in the browser, so the state lives here rather than in a component, and
 * leaving a route stops both from here too: views stay mounted across some hash changes.
 */

export type VoiceRole = "interviewer" | "candidate";

/** One stretch of speech-ready text (see voice/speechText.ts). */
export interface SpeechSegment {
  text: string;
  /** Segments sharing a group are skipped together; `group` undefined is never a skip target. */
  group?: number;
  groupLabel?: string;
  role?: VoiceRole;
  /** Spoken before the text only when the roles cannot be told apart by voice. */
  label?: string;
  pauseAfterMs?: number;
}

export interface SpeakOptions {
  /** Segments that arrive later, e.g. from a fetch. Rejecting ends speech with its message. */
  more?: Promise<SpeechSegment[]>;
}

export interface SpeechSnapshot {
  owner: symbol | null;
  active: boolean;
  groupLabel: string | null;
  error: string | null;
  errorOwner: symbol | null;
}

const ROLE_RATE: Record<VoiceRole, number> = { interviewer: 1, candidate: 0.95 };
/** Past this an utterance has hung: some engines never fire `end`, or `error`. */
const watchdogMs = (chars: number) => 8000 + chars * 150;

const SYNTH_ERRORS: Record<string, string> = {
  "not-allowed": "The browser blocked speech. Click the button again to start it.",
  "voice-unavailable": "That voice is not available on this device.",
  "language-unavailable": "No voice on this device can read this language.",
  "audio-busy": "Another app is using the audio output.",
  "audio-hardware": "No audio output was found.",
  network: "The speech voice needs a network connection.",
};

export function speechSupported(): boolean {
  return typeof window !== "undefined" && !!window.speechSynthesis && typeof window.SpeechSynthesisUtterance === "function";
}

// --- Voices -----------------------------------------------------------------------------------

export interface VoicePick {
  interviewer: SpeechSynthesisVoice | null;
  candidate: SpeechSynthesisVoice | null;
  /** False when one voice (or none) has to play both roles. */
  distinct: boolean;
}

/** macOS ships these sound-effect voices as ordinary local English ones. */
const NOVELTY_VOICE_RE = /^(?:albert|bad news|bahh|bells|boing|bubbles|cellos|deranged|good news|hysterical|jester|organ|pipe organ|superstar|trinoids|whisper|wobble|zarvox)\b/i;

/** Two different English voices if possible, on-device ones first (network voices are the ones that cut out). */
export function pickVoices(voices: readonly SpeechSynthesisVoice[]): VoicePick {
  const usable = voices.filter((v) => !NOVELTY_VOICE_RE.test(v.name));
  const english = usable.filter((v) => v.lang?.toLowerCase().startsWith("en"));
  const pool = english.length ? english : usable.length ? usable : [...voices];
  const ordered = [...pool].sort(
    (a, b) => Number(b.default) - Number(a.default) || Number(b.localService) - Number(a.localService)
  );
  const interviewer = ordered[0] ?? null;
  const others = ordered.filter((v) => v.name !== interviewer?.name);
  // The same accent reads as one conversation, so a different one is only the fallback.
  const other = others.find((v) => v.lang === interviewer?.lang && v.localService) ?? others[0] ?? null;
  return { interviewer, candidate: other ?? interviewer, distinct: !!other };
}

// --- Synthesis --------------------------------------------------------------------------------

interface Run {
  owner: symbol;
  segments: SpeechSegment[];
  at: number;
  chunks: string[];
  more: Promise<SpeechSegment[]> | null;
  utterance: SpeechSynthesisUtterance | null; // held so it is not collected before `end` fires
  timer: ReturnType<typeof setTimeout> | null;
}

let run: Run | null = null;
let snapshot: SpeechSnapshot = { owner: null, active: false, groupLabel: null, error: null, errorOwner: null };
const listeners = new Set<() => void>();

function publish(next: Partial<SpeechSnapshot>) {
  snapshot = { ...snapshot, ...next };
  listeners.forEach((l) => l());
}

function clearTimer(r: Run) {
  if (r.timer) clearTimeout(r.timer);
  r.timer = null;
}

function finish(error: string | null = null) {
  const r = run;
  if (!r) return;
  run = null;
  clearTimer(r);
  r.utterance = null;
  window.speechSynthesis?.cancel();
  publish({ owner: null, active: false, groupLabel: null, error, errorOwner: error ? r.owner : null });
}

function speakChunk(r: Run, text: string, role: VoiceRole | undefined) {
  const synth = window.speechSynthesis;
  const utterance = new SpeechSynthesisUtterance(text);
  // Read per utterance: getVoices() can be empty until `voiceschanged`, and later pieces then
  // pick up the voices without anything having to wait for that event.
  if (role) {
    const voice = pickVoices(synth.getVoices())[role];
    if (voice) {
      utterance.voice = voice;
      utterance.lang = voice.lang;
    }
    utterance.rate = ROLE_RATE[role];
  }
  utterance.onend = () => {
    if (run === r && r.utterance === utterance) advance(r);
  };
  utterance.onerror = (e: SpeechSynthesisErrorEvent) => {
    if (run !== r || r.utterance !== utterance) return; // stopped or skipped: not news
    if (e.error === "canceled" || e.error === "interrupted") finish();
    else finish(SYNTH_ERRORS[e.error] ?? "Speech stopped unexpectedly.");
  };
  r.utterance = utterance;
  clearTimer(r);
  r.timer = setTimeout(() => {
    if (run === r) finish("Speech stopped responding, so it was stopped here.");
  }, watchdogMs(text.length));
  synth.resume(); // Chrome can leave the queue paused after a tab switch
  synth.speak(utterance);
}

function startSegment(r: Run) {
  const segment = r.segments[r.at];
  const spoken =
    segment.label && segment.role && !pickVoices(window.speechSynthesis.getVoices()).distinct
      ? `${segment.label}. ${segment.text}`
      : segment.text;
  r.chunks = chunkForSpeech(spoken);
  publish({ groupLabel: segment.groupLabel ?? snapshot.groupLabel });
  if (r.chunks.length) speakChunk(r, r.chunks.shift()!, segment.role);
  else advance(r);
}

function nextSegment(r: Run) {
  r.at++;
  if (r.at < r.segments.length) {
    startSegment(r);
  } else if (!r.more) {
    finish();
  }
  // Otherwise out of text with more on the way: awaitMore starts it on arrival.
}

function advance(r: Run) {
  r.utterance = null;
  clearTimer(r);
  if (r.chunks.length) {
    speakChunk(r, r.chunks.shift()!, r.segments[r.at].role);
    return;
  }
  const pause = r.segments[r.at]?.pauseAfterMs ?? 0;
  if (pause > 0) {
    r.timer = setTimeout(() => {
      r.timer = null;
      if (run === r) nextSegment(r);
    }, pause);
  } else {
    nextSegment(r);
  }
}

function awaitMore(r: Run, more: Promise<SpeechSegment[]>) {
  more.then(
    (segments) => {
      if (run !== r) return;
      const waiting = r.at >= r.segments.length;
      r.more = null;
      r.segments.push(...segments);
      if (waiting) {
        if (r.at < r.segments.length) startSegment(r);
        else finish();
      }
    },
    (e: unknown) => {
      if (run === r) finish(e instanceof Error ? e.message : "Could not load that.");
    }
  );
}

/** Stop speech, whoever started it. */
export function stopSpeech() {
  finish();
}

function speakAs(owner: symbol, input: string | SpeechSegment[], options: SpeakOptions = {}) {
  if (!speechSupported()) return;
  installPageListeners();
  abortDictation();
  finish();
  const segments = typeof input === "string" ? [{ text: input }] : [...input];
  const r: Run = { owner, segments, at: 0, chunks: [], more: options.more ?? null, utterance: null, timer: null };
  run = r;
  publish({ owner, active: true, groupLabel: null, error: null, errorOwner: null });
  if (options.more) awaitMore(r, options.more);
  if (segments.length) startSegment(r);
  else if (!options.more) finish();
}

/** Drop what is playing and go to the next group. Past the last one, stop. */
function skipGroup(owner: symbol) {
  const r = run;
  if (!r || r.owner !== owner) return;
  const group = r.segments[r.at]?.group;
  let to = r.at + 1;
  while (to < r.segments.length && (r.segments[to].group === group || r.segments[to].group === undefined)) to++;
  clearTimer(r);
  r.utterance = null;
  r.chunks = [];
  window.speechSynthesis.cancel();
  r.at = Math.min(to, r.segments.length); // at the end, segments still loading start from here
  if (to < r.segments.length) startSegment(r);
  else if (!r.more) finish();
}

const subscribe = (l: () => void) => {
  listeners.add(l);
  return () => {
    listeners.delete(l);
  };
};
const getSnapshot = () => snapshot;

export interface SpeechControls {
  supported: boolean;
  /** True for the component that started the speech, not for other speech on the page. */
  speaking: boolean;
  groupLabel: string | null;
  error: string | null;
  speak: (input: string | SpeechSegment[], options?: SpeakOptions) => void;
  stop: () => void;
  skip: () => void;
}

export function useSpeech(): SpeechControls {
  const [owner] = useState(() => Symbol("speech"));
  const state = useSyncExternalStore(subscribe, getSnapshot);
  const mine = state.owner === owner;
  const speak = useCallback((input: string | SpeechSegment[], options?: SpeakOptions) => speakAs(owner, input, options), [owner]);
  const stop = useCallback(() => {
    if (run?.owner === owner) finish();
    if (snapshot.errorOwner === owner) publish({ error: null, errorOwner: null });
  }, [owner]);
  const skip = useCallback(() => skipGroup(owner), [owner]);
  useEffect(() => stop, [stop]);
  return {
    supported: speechSupported(),
    speaking: mine && state.active,
    groupLabel: mine ? state.groupLabel : null,
    error: state.errorOwner === owner ? state.error : null,
    speak,
    stop,
    skip,
  };
}

// --- Recognition ------------------------------------------------------------------------------

/** The slice of SpeechRecognition used here; lib.dom does not declare it. */
interface RecognitionResultItem { readonly transcript: string }
interface RecognitionResult { readonly isFinal: boolean; readonly length: number; readonly [i: number]: RecognitionResultItem }
interface RecognitionEvent { readonly results: { readonly length: number; readonly [i: number]: RecognitionResult } }
interface Recognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((e: RecognitionEvent) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
}
type RecognitionCtor = new () => Recognition;

function recognitionCtor(): RecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

export const dictationSupported = () => recognitionCtor() !== null;

const RECOGNITION_ERRORS: Record<string, string> = {
  "not-allowed": "Microphone access is blocked. Allow it in this site's browser settings, then try again.",
  "service-not-allowed": "This browser does not allow speech recognition here. You can type instead.",
  "no-speech": "No speech was heard. Hold the button and try again.",
  "audio-capture": "No microphone was found.",
  network: "The browser's speech service could not be reached. You can type instead.",
  "language-not-supported": "This browser cannot recognise your language setting.",
};

/** How long to wait for final results after a release before giving up on them. */
const RELEASE_TIMEOUT_MS = 2500;

/** "released": the person let go, so a host may act on it. "ended": it stopped some other way. */
export type DictationEnd = "released" | "ended";

let abortActive: (() => void) | null = null;

/** Drop any live dictation and whatever it heard. */
export function abortDictation() {
  abortActive?.();
}

export interface DictationControls {
  supported: boolean;
  listening: boolean;
  /** Final and interim text so far. */
  transcript: string;
  error: string | null;
  start: () => void;
  /** Stop listening and deliver what was heard, once final results are in. */
  finish: (how?: DictationEnd) => void;
  /** Stop listening and discard what was heard. */
  cancel: () => void;
}

/**
 * Push-to-talk dictation. `onResult` gets non-empty text only, so a host can never send an empty
 * transcript. Listening always ends: on release, error, the service ending, route change or unmount.
 */
export function useDictation(onResult: (text: string, how: DictationEnd) => void): DictationControls {
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const session = useRef<{ rec: Recognition; heard: string; how: DictationEnd | null; timer: ReturnType<typeof setTimeout> | null } | null>(null);
  const deliver = useRef(onResult);
  useEffect(() => {
    deliver.current = onResult;
  }, [onResult]);

  const close = useCallback((discard: boolean, how: DictationEnd) => {
    const s = session.current;
    if (!s) return;
    session.current = null;
    if (s.timer) clearTimeout(s.timer);
    s.rec.onresult = s.rec.onerror = s.rec.onend = null;
    abortActive = null;
    setListening(false);
    setTranscript("");
    const text = s.heard.trim();
    if (!discard && text) deliver.current(text, how);
  }, []);

  const cancel = useCallback(() => {
    const s = session.current;
    if (!s) return;
    close(true, "ended");
    try {
      s.rec.abort();
    } catch {
      /* already stopped */
    }
  }, [close]);

  const finishListening = useCallback((how: DictationEnd = "released") => {
    const s = session.current;
    if (!s || s.how) return;
    s.how = how;
    s.timer = setTimeout(() => {
      close(false, how);
      try {
        s.rec.abort();
      } catch {
        /* already stopped */
      }
    }, RELEASE_TIMEOUT_MS);
    try {
      s.rec.stop(); // results still to come arrive before `end`
    } catch {
      close(false, how);
    }
  }, [close]);

  const start = useCallback(() => {
    const Ctor = recognitionCtor();
    if (!Ctor || session.current) return;
    installPageListeners();
    stopSpeech(); // the mic would hear the page reading
    abortDictation();
    setError(null);
    setTranscript("");
    const rec = new Ctor();
    rec.lang = navigator.language || "en-US";
    rec.continuous = true;
    rec.interimResults = true;
    const s = { rec, heard: "", how: null as DictationEnd | null, timer: null as ReturnType<typeof setTimeout> | null };
    rec.onresult = (e) => {
      let text = "";
      for (let i = 0; i < e.results.length; i++) text += e.results[i][0]?.transcript ?? "";
      s.heard = text;
      setTranscript(text.trim());
    };
    rec.onerror = (e) => {
      // Our own abort is not news; anything else must not leave the mic looking live.
      if (e.error !== "aborted") setError(RECOGNITION_ERRORS[e.error] ?? "Dictation stopped unexpectedly. You can type instead.");
      close(false, "ended");
    };
    rec.onend = () => close(false, s.how ?? "ended");
    session.current = s;
    abortActive = cancel;
    setListening(true);
    try {
      rec.start();
    } catch {
      setError("Dictation could not start. Try again in a moment.");
      close(true, "ended");
    }
  }, [cancel, close]);

  useEffect(() => cancel, [cancel]);

  return { supported: dictationSupported(), listening, transcript, error, start, finish: finishListening, cancel };
}

// --- Leaving the page or route ----------------------------------------------------------------

let pageListeners = false;

/** Stop everything on any hash navigation, and on unload (Chrome keeps speaking through a reload). */
function installPageListeners() {
  if (pageListeners) return;
  pageListeners = true;
  const stopAll = () => {
    stopSpeech();
    abortDictation();
  };
  window.addEventListener("hashchange", stopAll);
  window.addEventListener("pagehide", stopAll);
}
