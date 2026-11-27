import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { FakeRecognition, installFakeRecognition, installFakeSynth, voice } from "../../test/fakeSpeech";
import { pickVoices, useDictation, useSpeech, type DictationEnd, type SpeakOptions, type SpeechSegment } from "../useSpeech";

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

let api: ReturnType<typeof useSpeech>;
function Speaker() {
  api = useSpeech();
  return <div data-testid="state">{api.speaking ? `speaking ${api.groupLabel ?? ""}` : api.error ?? "idle"}</div>;
}
const speak = (input: string | SpeechSegment[], options?: SpeakOptions) => act(() => api.speak(input, options));
const state = () => screen.getByTestId("state").textContent;

describe("useSpeech", () => {
  it("reports unsupported and speaks nothing when the API is absent", () => {
    render(<Speaker />);
    expect(api.supported).toBe(false);
    speak("words");
    expect(state()).toBe("idle");
  });

  it("queues long text a piece at a time, under Chrome's cutoff, and ends", () => {
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("One sentence that is fairly long and goes on for a while now. ".repeat(20));
    expect(synth.utterances).toHaveLength(1); // not all at once
    expect(state()).toContain("speaking");
    synth.drain();
    expect(synth.utterances.length).toBeGreaterThan(5);
    expect(Math.max(...synth.utterances.map((u) => u.text.length))).toBeLessThanOrEqual(180);
    expect(state()).toBe("idle");
  });

  it("does not depend on the boundary event", () => {
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("One. Two.");
    synth.drain(); // only `end` ever fires here
    expect(synth.spoken).toBe("One. Two.");
  });

  it("stop cancels, and a late event from the old utterance changes nothing", () => {
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("First words.");
    const old = synth.current!;
    act(() => api.stop());
    expect(synth.cancels).toBe(1);
    expect(state()).toBe("idle");
    speak("Second words.");
    const count = synth.utterances.length;
    act(() => old.onend?.());
    act(() => old.onerror?.({ error: "interrupted" }));
    expect(synth.utterances).toHaveLength(count);
    expect(state()).toContain("speaking");
  });

  it("stops on unmount", () => {
    const synth = installFakeSynth();
    const { unmount } = render(<Speaker />);
    speak("Words here.");
    unmount();
    expect(synth.cancels).toBe(1);
    expect(synth.current).toBeNull();
  });

  it("stops on a hash change with the component still mounted", () => {
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("Words here. More words.");
    act(() => {
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
    expect(synth.current).toBeNull();
    expect(synth.cancels).toBe(1);
    expect(state()).toBe("idle");
  });

  it("stops when the page is hidden for good", () => {
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("Words here.");
    act(() => {
      window.dispatchEvent(new Event("pagehide"));
    });
    expect(synth.current).toBeNull();
  });

  it("another component starting takes over, and the first no longer reads as speaking", () => {
    const synth = installFakeSynth();
    let other!: ReturnType<typeof useSpeech>;
    const Other = () => {
      other = useSpeech();
      return null;
    };
    render(<><Speaker /><Other /></>);
    speak("Mine.");
    act(() => other.speak("Theirs."));
    expect(state()).toBe("idle");
    expect(other.speaking).toBe(true);
    expect(synth.current?.text).toBe("Theirs.");
    act(() => api.stop()); // not the owner: must not stop the other one
    expect(synth.current?.text).toBe("Theirs.");
  });

  it.each([
    ["not-allowed", /blocked/],
    ["audio-hardware", /audio output/],
    ["something-new", /stopped unexpectedly/],
  ])("shows a human message for %s and ends", (error, message) => {
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("One. Two.");
    synth.fail(error);
    expect(state()).toMatch(message);
    expect(api.speaking).toBe(false);
  });

  it("gives up on an engine that never finishes, rather than looking busy forever", () => {
    vi.useFakeTimers();
    const synth = installFakeSynth();
    render(<Speaker />);
    speak("Words here.");
    act(() => {
      vi.advanceTimersByTime(60_000);
    });
    expect(state()).toMatch(/stopped responding/);
    expect(synth.current).toBeNull();
  });

  describe("groups", () => {
    const groups: SpeechSegment[] = [
      { text: "Alpha one.", group: 0, groupLabel: "Alpha" },
      { text: "Alpha two.", group: 0, groupLabel: "Alpha" },
      { text: "Beta.", group: 1, groupLabel: "Beta" },
    ];

    it("skip drops the rest of the group and starts the next", () => {
      const synth = installFakeSynth();
      render(<Speaker />);
      speak(groups);
      expect(state()).toBe("speaking Alpha");
      act(() => api.skip());
      expect(synth.current?.text).toBe("Beta.");
      expect(state()).toBe("speaking Beta");
      synth.drain();
      expect(synth.spoken).not.toContain("Alpha two");
    });

    it("skip past the last group stops", () => {
      const synth = installFakeSynth();
      render(<Speaker />);
      speak(groups);
      act(() => api.skip());
      act(() => api.skip());
      expect(synth.current).toBeNull();
      expect(state()).toBe("idle");
    });
  });

  describe("two voices", () => {
    const dialogue: SpeechSegment[] = [
      { text: "Why?", role: "interviewer", label: "Question", group: 0, pauseAfterMs: 900 },
      { text: "Because.", role: "candidate", label: "Answer", group: 0 },
    ];

    it("gives each role its own voice, with a pause between", () => {
      vi.useFakeTimers();
      const synth = installFakeSynth();
      render(<Speaker />);
      speak(dialogue);
      synth.end();
      expect(synth.current).toBeNull(); // pausing
      expect(api.speaking).toBe(true);
      act(() => {
        vi.advanceTimersByTime(900);
      });
      const [q, a] = synth.utterances;
      expect([q.text, a.text]).toEqual(["Why?", "Because."]);
      expect(q.voice?.name).toBe("Alpha");
      expect(a.voice?.name).toBe("Beta");
      expect(a.rate).toBeLessThan(q.rate);
    });

    it("says who is speaking when one voice has to play both", () => {
      vi.useFakeTimers();
      const synth = installFakeSynth([voice("Only")]);
      render(<Speaker />);
      speak(dialogue);
      synth.end();
      act(() => {
        vi.advanceTimersByTime(900);
      });
      expect(synth.utterances.map((u) => u.text)).toEqual(["Question. Why?", "Answer. Because."]);
    });

    it("still speaks with no voices yet, and uses them once they load", () => {
      vi.useFakeTimers();
      const synth = installFakeSynth([]);
      render(<Speaker />);
      speak(dialogue);
      expect(synth.current?.text).toBe("Question. Why?");
      expect(synth.current?.voice).toBeNull();
      synth.voices = [voice("Alpha"), voice("Beta")];
      synth.end();
      act(() => {
        vi.advanceTimersByTime(900);
      });
      expect(synth.current?.voice?.name).toBe("Beta");
      expect(synth.current?.text).toBe("Because.");
    });

    it("a stop during the pause means the next segment never starts", () => {
      vi.useFakeTimers();
      const synth = installFakeSynth();
      render(<Speaker />);
      speak(dialogue);
      synth.end();
      act(() => api.stop());
      act(() => {
        vi.advanceTimersByTime(5000);
      });
      expect(synth.utterances).toHaveLength(1);
    });

    it("skips sound-effect voices, and treats one real voice among them as a single voice", () => {
      const pick = pickVoices([voice("Albert"), voice("Bad News"), voice("Real")] as never);
      expect(pick.interviewer?.name).toBe("Real");
      expect(pick.distinct).toBe(false);
    });

    it("starts from the default voice and pairs it with one of the same accent", () => {
      const pick = pickVoices([voice("Uk", "en-GB"), { ...voice("Us1", "en-US"), default: true }, voice("Us2", "en-US")] as never);
      expect([pick.interviewer?.name, pick.candidate?.name]).toEqual(["Us1", "Us2"]);
    });

    it("prefers English, on-device voices", () => {
      const pick = pickVoices([voice("Net", "en-GB", false), voice("Fr", "fr-FR"), voice("Local", "en-US")] as never);
      expect(pick.interviewer?.name).toBe("Local");
      expect(pick.candidate?.name).toBe("Net");
      expect(pick.distinct).toBe(true);
    });
  });

  describe("segments that arrive later", () => {
    it("speaks the intro at once and continues when they load", async () => {
      const synth = installFakeSynth();
      render(<Speaker />);
      let resolve!: (s: SpeechSegment[]) => void;
      speak([{ text: "Intro." }], { more: new Promise((r) => (resolve = r)) });
      expect(synth.current?.text).toBe("Intro.");
      synth.end();
      expect(synth.current).toBeNull();
      expect(state()).toContain("speaking");
      await act(async () => resolve([{ text: "Loaded." }]));
      expect(synth.current?.text).toBe("Loaded.");
    });

    it("ends with the message if loading fails", async () => {
      const synth = installFakeSynth();
      render(<Speaker />);
      speak([{ text: "Intro." }], { more: Promise.reject(new Error("Could not load.")) });
      await act(async () => {});
      expect(synth.current).toBeNull();
      expect(state()).toBe("Could not load.");
    });

    it("drops what loads after a stop", async () => {
      const synth = installFakeSynth();
      render(<Speaker />);
      let resolve!: (s: SpeechSegment[]) => void;
      speak([{ text: "Intro." }], { more: new Promise((r) => (resolve = r)) });
      act(() => api.stop());
      await act(async () => resolve([{ text: "Loaded." }]));
      expect(synth.spoken).toBe("Intro.");
    });
  });
});

let mic: ReturnType<typeof useDictation>;
const results: [string, DictationEnd][] = [];
function Mic() {
  mic = useDictation((text, how) => results.push([text, how]));
  return <div data-testid="mic">{mic.listening ? `live:${mic.transcript}` : mic.error ?? "idle"}</div>;
}
const micState = () => screen.getByTestId("mic").textContent;
const startMic = () => {
  results.length = 0;
  installFakeRecognition();
  render(<Mic />);
  act(() => mic.start());
  return FakeRecognition.last;
};

describe("useDictation", () => {
  it("is unsupported with no recognition API", () => {
    render(<Mic />);
    expect(mic.supported).toBe(false);
    act(() => mic.start());
    expect(mic.listening).toBe(false);
  });

  it.each([[true], [false]])("feature-detects both spellings (prefixed %s)", (prefixed) => {
    installFakeRecognition(prefixed);
    render(<Mic />);
    expect(mic.supported).toBe(true);
  });

  it("shows interim text, and delivers the final text once on release", () => {
    const rec = startMic();
    expect(rec.interimResults).toBe(true);
    rec.hear("hello ", "wor");
    expect(micState()).toBe("live:hello wor");
    rec.hear("hello ", "world");
    act(() => mic.finish("released"));
    expect(rec.stopped).toBe(true);
    expect(results).toEqual([]); // final results may still come
    rec.hear("hello ", "world again");
    rec.end();
    expect(results).toEqual([["hello world again", "released"]]);
    expect(micState()).toBe("idle");
  });

  it("delivers nothing when nothing was heard", () => {
    const rec = startMic();
    rec.hear("   ");
    act(() => mic.finish("released"));
    rec.end();
    expect(results).toEqual([]);
  });

  it("gives up waiting for a service that never ends, keeping what it heard", () => {
    vi.useFakeTimers();
    const rec = startMic();
    rec.hear("hello");
    act(() => mic.finish("released"));
    act(() => {
      vi.advanceTimersByTime(3000);
    });
    expect(rec.aborted).toBe(true);
    expect(results).toEqual([["hello", "released"]]);
    expect(micState()).toBe("idle");
  });

  it("marks a session the service ended as not released", () => {
    const rec = startMic();
    rec.hear("hello");
    rec.end();
    expect(results).toEqual([["hello", "ended"]]);
  });

  it.each([
    ["not-allowed", /Microphone access is blocked/],
    ["service-not-allowed", /does not allow/],
    ["no-speech", /No speech was heard/],
    ["audio-capture", /No microphone/],
    ["network", /could not be reached/],
    ["language-not-supported", /language/],
    ["something-new", /stopped unexpectedly/],
  ])("%s shows a human message and leaves the mic off, with no `end` event", (error, message) => {
    const rec = startMic();
    rec.fail(error);
    expect(micState()).toMatch(message);
    expect(mic.listening).toBe(false);
  });

  it("`aborted` is not reported", () => {
    const rec = startMic();
    rec.fail("aborted");
    expect(micState()).toBe("idle");
  });

  it("an error then an `end` does not deliver twice, and it can start again", () => {
    const rec = startMic();
    rec.hear("hello");
    rec.fail("network");
    rec.end();
    expect(results).toEqual([["hello", "ended"]]);
    act(() => mic.start());
    expect(FakeRecognition.last).not.toBe(rec);
    expect(mic.error).toBeNull();
    expect(mic.listening).toBe(true);
  });

  it("a start that throws shows a message and does not stick", () => {
    installFakeRecognition();
    FakeRecognition.throwOnStart = true;
    render(<Mic />);
    act(() => mic.start());
    expect(micState()).toMatch(/could not start/);
  });

  it("cancel discards what was heard", () => {
    const rec = startMic();
    rec.hear("hello");
    act(() => mic.cancel());
    expect(rec.aborted).toBe(true);
    expect(results).toEqual([]);
    expect(micState()).toBe("idle");
  });

  it("aborts on unmount and on hash change, discarding", () => {
    const rec = startMic();
    rec.hear("hello");
    act(() => {
      window.dispatchEvent(new HashChangeEvent("hashchange"));
    });
    expect(rec.aborted).toBe(true);
    expect(micState()).toBe("idle");
    act(() => mic.start());
    const again = FakeRecognition.last;
    cleanup();
    expect(again.aborted).toBe(true);
    expect(results).toEqual([]);
  });

  it("speech and the mic never overlap", () => {
    const synth = installFakeSynth();
    const rec = startMic();
    render(<Speaker />);
    speak("Words.");
    expect(rec.aborted).toBe(true);
    expect(synth.current?.text).toBe("Words.");
    act(() => mic.start());
    expect(synth.current).toBeNull();
    expect(state()).toBe("idle");
  });

  it("uses the browser's language", () => {
    const rec = startMic();
    expect(rec.lang).toBe(navigator.language);
    fireEvent.blur(screen.getByTestId("mic")); // no effect from unrelated events
    expect(mic.listening).toBe(true);
  });
});
