import { act } from "@testing-library/react";
import { vi } from "vitest";

/** Fake Web Speech API for tests. Installs on window, as a browser would, until vi.unstubAllGlobals. */

export class FakeUtterance {
  voice: { name: string; lang: string } | null = null;
  lang = "";
  rate = 1;
  onend: (() => void) | null = null;
  onerror: ((e: { error: string }) => void) | null = null;
  constructor(public text: string) {}
}

export const voice = (name: string, lang = "en-US", localService = true) => ({ name, lang, localService, default: false });

export function installFakeSynth(voices: ReturnType<typeof voice>[] = [voice("Alpha"), voice("Beta")]) {
  const synth = {
    voices,
    /** Every utterance handed to speak(), in order. */
    utterances: [] as FakeUtterance[],
    current: null as FakeUtterance | null,
    cancels: 0,
    get spoken() {
      return synth.utterances.map((u) => u.text).join(" ");
    },
    getVoices: () => synth.voices,
    resume: vi.fn(),
    speak(u: FakeUtterance) {
      synth.utterances.push(u);
      synth.current = u;
    },
    cancel() {
      synth.cancels++;
      const u = synth.current;
      synth.current = null;
      u?.onerror?.({ error: "canceled" });
    },
    /** The current utterance finishes. */
    end() {
      const u = synth.current;
      synth.current = null;
      act(() => u?.onend?.());
    },
    fail(error: string) {
      const u = synth.current;
      synth.current = null;
      act(() => u?.onerror?.({ error }));
    },
    /** Finish utterances until nothing is queued. Pauses need timers advanced by the caller. */
    drain() {
      for (let i = 0; synth.current && i < 5000; i++) synth.end();
    },
  };
  vi.stubGlobal("speechSynthesis", synth);
  vi.stubGlobal("SpeechSynthesisUtterance", FakeUtterance);
  return synth;
}

export class FakeRecognition {
  static instances: FakeRecognition[] = [];
  static get last() {
    return FakeRecognition.instances[FakeRecognition.instances.length - 1];
  }
  static throwOnStart = false;
  lang = "";
  continuous = false;
  interimResults = false;
  started = false;
  stopped = false;
  aborted = false;
  onresult: ((e: unknown) => void) | null = null;
  onerror: ((e: { error: string }) => void) | null = null;
  onend: (() => void) | null = null;
  constructor() {
    FakeRecognition.instances.push(this);
  }
  start() {
    if (FakeRecognition.throwOnStart) throw new Error("already started");
    this.started = true;
  }
  stop() {
    this.stopped = true;
  }
  abort() {
    this.aborted = true;
  }
  /** Deliver results; pieces are transcripts, the last of them interim. */
  hear(...pieces: string[]) {
    const results = Object.assign(
      pieces.map((transcript, i) => Object.assign([{ transcript }], { isFinal: i < pieces.length - 1 })),
      {}
    );
    act(() => this.onresult?.({ results }));
  }
  fail(error: string) {
    act(() => this.onerror?.({ error }));
  }
  end() {
    act(() => this.onend?.());
  }
}

/** `prefixed` installs it the way Chrome and Safari spell it. */
export function installFakeRecognition(prefixed = true) {
  FakeRecognition.instances = [];
  FakeRecognition.throwOnStart = false;
  vi.stubGlobal(prefixed ? "webkitSpeechRecognition" : "SpeechRecognition", FakeRecognition);
}
