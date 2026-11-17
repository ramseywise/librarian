import { useEffect, useRef, useState } from "react";

/** A slide with nothing to say stays up this long before the player moves on. */
const SILENT_MS = 2500;

/** The text as the sentences the player speaks one at a time. Chrome cuts a long utterance off part-way,
 * and a sentence is also the unit a pause resumes from and the captions highlight. */
export function sentences(text: string): string[] {
  return (text.replace(/\s+/g, " ").match(/[^.!?]+(?:[.!?]+["')\]]*|$)/g) ?? []).map((s) => s.trim()).filter(Boolean);
}

/** True when this browser can read text aloud. */
export function canSpeak(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window && typeof SpeechSynthesisUtterance !== "undefined";
}

/** Reads `text` aloud with the browser's own voice while `playing`. Pausing keeps the sentence it was
 * on and resuming starts that sentence again; a new `text` starts from its first sentence. `onDone`
 * fires once the last sentence has been spoken. Returns the index of the sentence being spoken. */
export function useNarration({ text, playing, rate, onDone }: { text: string; playing: boolean; rate: number; onDone: () => void }): number {
  const [index, setIndex] = useState(0);
  const at = useRef(0);
  const done = useRef(onDone);
  done.current = onDone;

  useEffect(() => {
    at.current = 0;
    setIndex(0);
  }, [text]);

  useEffect(() => {
    if (!playing || !canSpeak()) return;
    const parts = sentences(text);
    let live = true;
    let timer: number | undefined;
    const finish = () => {
      at.current = 0;
      done.current();
    };
    const say = (i: number) => {
      if (!live) return;
      if (i >= parts.length) return finish();
      at.current = i;
      setIndex(i);
      const u = new SpeechSynthesisUtterance(parts[i]);
      u.rate = rate;
      u.onend = () => say(i + 1);
      // A cancelled utterance reports an error too; only a real failure skips to the next sentence.
      u.onerror = (e) => e.error !== "canceled" && e.error !== "interrupted" && say(i + 1);
      window.speechSynthesis.speak(u);
    };
    window.speechSynthesis.cancel();
    if (parts.length) say(Math.min(at.current, parts.length - 1));
    else timer = window.setTimeout(() => live && finish(), SILENT_MS);
    return () => {
      live = false;
      window.clearTimeout(timer);
      window.speechSynthesis?.cancel();
    };
  }, [playing, text, rate]);

  return index;
}
