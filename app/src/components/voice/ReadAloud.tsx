import type { SpeechControls, SpeechSegment } from "../../hooks/useSpeech";

interface Props {
  speech: SpeechControls;
  /** Accessible name and visible text of the start button. */
  label: string;
  segments: () => SpeechSegment[];
  /** Shows a skip button with this text while speaking. */
  skipLabel?: string;
}

/** Start, stop and optionally skip speech. Renders nothing where the browser cannot speak. */
export function ReadAloud({ speech, label, segments, skipLabel }: Props) {
  if (!speech.supported) return null;
  return (
    <div className="voice-controls">
      {speech.speaking ? (
        <button type="button" onClick={speech.stop} className="round-btn voice-btn voice-btn--active">
          ■ Stop reading
        </button>
      ) : (
        <button type="button" onClick={() => speech.speak(segments())} className="round-btn voice-btn">
          ▶ {label}
        </button>
      )}
      {speech.speaking && skipLabel && (
        <button type="button" onClick={speech.skip} className="round-btn voice-btn">
          {skipLabel}
        </button>
      )}
      <span role="status" className="voice-status">
        {speech.speaking && speech.groupLabel ? `Reading: ${speech.groupLabel}` : ""}
      </span>
      {speech.error && <span role="alert" className="voice-error">{speech.error}</span>}
    </div>
  );
}
