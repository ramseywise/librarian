import { useEffect, useId, useRef, useState, type KeyboardEvent, type MouseEvent, type PointerEvent } from "react";
import type { DictationControls } from "../../hooks/useSpeech";
import { DICTATION_NOTICE } from "../../voice/policy";

/** A press shorter than this latches the mic on, so holding is never required. */
const TAP_MS = 300;

interface Props {
  dictation: DictationControls;
  disabled?: boolean;
  /** Full name for assistive technology. Starts with the visible "Hold to talk". */
  label: string;
  className?: string;
}

/**
 * Push-to-talk. Hold with pointer, Space or Enter and let go to finish; a quick tap, or a click from
 * assistive technology, latches it until the next press. Escape discards. Losing focus or the
 * pointer finishes without counting as a release, so a host will not send on it.
 */
export function MicButton({ dictation, disabled, label, className }: Props) {
  const { listening, start, finish, cancel } = dictation;
  const pressedAt = useRef<number | null>(null);
  const [latched, setLatched] = useState(false);
  const keyHandled = useRef(false);
  const noticeId = useId();

  const press = () => {
    if (disabled) return;
    if (listening) {
      if (latched) {
        setLatched(false);
        finish("released");
      }
      return;
    }
    pressedAt.current = performance.now();
    start();
  };
  const lift = () => {
    if (pressedAt.current === null) return;
    const held = performance.now() - pressedAt.current;
    pressedAt.current = null;
    if (!listening) return; // it failed to start or has already ended
    if (held < TAP_MS) setLatched(true);
    else finish("released");
  };

  useEffect(() => {
    if (!listening) {
      pressedAt.current = null;
      setLatched(false);
    }
  }, [listening]);

  useEffect(() => {
    if (disabled && listening) finish("ended");
  }, [disabled, listening, finish]);

  const onPointerDown = (e: PointerEvent<HTMLButtonElement>) => {
    if (e.button !== 0) return;
    e.currentTarget.setPointerCapture?.(e.pointerId);
    press();
  };
  const onKeyDown = (e: KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Escape" && listening) {
      e.preventDefault();
      e.stopPropagation();
      cancel();
      return;
    }
    if (e.key !== " " && e.key !== "Enter") return;
    e.preventDefault();
    if (!e.repeat) press();
  };
  const onKeyUp = (e: KeyboardEvent<HTMLButtonElement>) => {
    if (e.key !== " " && e.key !== "Enter") return;
    e.preventDefault();
    keyHandled.current = true;
    setTimeout(() => {
      keyHandled.current = false;
    }, 0);
    lift();
  };
  const abandon = () => {
    pressedAt.current = null;
    if (listening) finish("ended");
  };
  // Pointer and key gestures are handled above. A click with no gesture is assistive technology.
  const onClick = (e: MouseEvent<HTMLButtonElement>) => {
    if (e.detail > 0 || keyHandled.current || disabled) return;
    if (listening) {
      setLatched(false);
      finish("released");
    } else {
      setLatched(true);
      start();
    }
  };

  const name = listening ? (latched ? "Listening: press to finish" : "Listening: release to finish") : label;
  return (
    <>
      <button
        type="button"
        disabled={disabled}
        aria-label={name}
        aria-pressed={listening}
        aria-describedby={noticeId}
        title={`${name}. ${DICTATION_NOTICE}`}
        onPointerDown={onPointerDown}
        onPointerUp={lift}
        onPointerCancel={abandon}
        onKeyDown={onKeyDown}
        onKeyUp={onKeyUp}
        onBlur={abandon}
        onClick={onClick}
        onContextMenu={(e) => e.preventDefault()}
        className={`mic-btn${listening ? " mic-btn--listening" : ""}${className ? ` ${className}` : ""}`}
      >
        {listening ? "Listening" : "Hold to talk"}
      </button>
      <span id={noticeId} className="voice-notice">{DICTATION_NOTICE}</span>
    </>
  );
}
