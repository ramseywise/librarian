import { lazy, Suspense, useState } from "react";
import { dictationAllowed } from "../../voice/policy";
import { refusalText, VOICE_ANSWERS_NOTICE, VOICE_LOCAL_DEFAULT_NOTICE, VOICE_LOCAL_ONLY_NOTICE, type VoiceTarget } from "../../voice/voiceSession";

/** Loads the Pipecat client, and only once a session is really starting. */
const VoicePanel = lazy(() => import("./VoicePanel"));

type Step =
  | { name: "closed" }
  | { name: "checking" }
  | { name: "unavailable"; message: string }
  | { name: "ready" }
  | { name: "live" };

interface ServerStatus {
  stt?: string;
  tts?: string;
  sessionActive?: boolean;
}

function notReadyText(status: ServerStatus): string | null {
  if (status.sessionActive) return "Another voice session is open. End it first.";
  if (status.stt === "loading" || status.tts === "loading") return "The local speech models are still loading. Try again in a moment.";
  return null;
}

/** A conversation about this lesson or deck. Needs `make voice`; the page works without it. */
export function VoiceDrawer({ target, subject }: { target: VoiceTarget; subject: string }) {
  const [step, setStep] = useState<Step>({ name: "closed" });
  const localOnly = !dictationAllowed(subject);

  const check = async () => {
    setStep({ name: "checking" });
    try {
      const response = await fetch("/api/voice/status");
      if (!response.ok) {
        setStep({ name: "unavailable", message: await refusalText(response) });
        return;
      }
      const message = notReadyText((await response.json()) as ServerStatus);
      setStep(message ? { name: "unavailable", message } : { name: "ready" });
    } catch {
      setStep({ name: "unavailable", message: "Could not reach the API." });
    }
  };

  if (step.name === "closed") {
    return (
      <div className="voice-controls">
        <button type="button" onClick={() => void check()} className="round-btn voice-btn" aria-expanded={false}>
          Voice
        </button>
      </div>
    );
  }

  return (
    <section className="voice-drawer" aria-label="Voice">
      <div className="voice-controls">
        <button type="button" onClick={() => setStep({ name: "closed" })} className="round-btn voice-btn voice-btn--active" aria-expanded={true}>
          {step.name === "live" ? "End voice session" : "Close voice"}
        </button>
        {step.name === "checking" && <span role="status" className="voice-status">Checking the voice server…</span>}
      </div>
      {localOnly ? (
        <>
          <p className="voice-notice">{VOICE_LOCAL_ONLY_NOTICE}</p>
          <p className="voice-notice">{VOICE_ANSWERS_NOTICE}</p>
        </>
      ) : (
        <p className="voice-notice">{VOICE_LOCAL_DEFAULT_NOTICE}</p>
      )}
      {step.name === "unavailable" && (
        <div className="voice-controls">
          <p role="alert" className="voice-error">{step.message}</p>
          <button type="button" onClick={() => void check()} className="round-btn voice-btn">Check again</button>
        </div>
      )}
      {step.name === "ready" && (
        <button type="button" onClick={() => setStep({ name: "live" })} className="round-btn voice-btn">
          Start talking
        </button>
      )}
      {step.name === "live" && (
        <Suspense fallback={<p role="status" className="voice-status">Loading voice…</p>}>
          <VoicePanel target={target} />
        </Suspense>
      )}
    </section>
  );
}
