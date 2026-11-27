import { useEffect, useReducer, useRef, useState } from "react";
import { PipecatClient, RTVIEvent, type BotOutputData, type TranscriptData } from "@pipecat-ai/client-js";
import { PipecatClientAudio, PipecatClientProvider, usePipecatClientTransportState, useRTVIClientEvent } from "@pipecat-ai/client-react";
import { SmallWebRTCTransport } from "@pipecat-ai/small-webrtc-transport";
import {
  coachSaid,
  EMPTY_VIEW,
  refusalText,
  serverSaid,
  ungradedText,
  userSaid,
  type TurnLatency,
  type VoiceSessionInfo,
  type VoiceTarget,
  type VoiceView,
} from "../../voice/voiceSession";

/** Agreed with `INTERRUPT_MESSAGE` in app/voice/pipeline.py. */
const INTERRUPT_MESSAGE = "interrupt";

type Action =
  | { type: "you"; text: string; final: boolean }
  | { type: "coach"; text: string }
  | { type: "server"; message: unknown };

function reduce(view: VoiceView, action: Action): VoiceView {
  if (action.type === "you") return userSaid(view, action.text, action.final);
  if (action.type === "coach") return coachSaid(view, action.text);
  return serverSaid(view, action.message);
}

const STATE_TEXT: Record<string, string> = {
  disconnected: "Disconnected",
  initializing: "Asking for the microphone…",
  initialized: "Microphone ready",
  authenticating: "Opening a session…",
  authenticated: "Connecting…",
  connecting: "Connecting…",
  connected: "Connected, waiting for the voice…",
  ready: "Listening",
  disconnecting: "Ending…",
  error: "Connection failed",
};

function Numbers({ view }: { view: VoiceView }) {
  const last: TurnLatency | undefined = view.latency[view.latency.length - 1];
  if (!last) return null;
  const show = (value: number | null) => (value === null ? "-" : Math.round(value));
  return (
    <p className="voice-status" data-testid="voice-latency">
      Turn {last.turn}: {show(last.gap_ms)} ms to first audio (speech end {show(last.vad_stop_ms)}, STT {show(last.stt_ms)}, model {show(last.llm_first_ms)}, TTS {show(last.tts_first_ms)})
    </p>
  );
}

function Lines({ view }: { view: VoiceView }) {
  return (
    <ul className="voice-transcript" aria-label="Live transcript" aria-live="polite">
      {view.lines.map((line, i) => {
        switch (line.kind) {
          case "you":
            return <li key={i} className={line.final ? "" : "voice-line--interim"}><strong>You:</strong> {line.text}</li>;
          case "coach":
            return <li key={i}><strong>Coach:</strong> {line.text}</li>;
          case "graded":
            return <li key={i} className="voice-line--mark">Graded {Math.round(line.score * 100)}%</li>;
          case "ungraded":
            return <li key={i} className="voice-line--mark voice-line--ungraded">{ungradedText(line.reason)}</li>;
        }
      })}
    </ul>
  );
}

function Session({ client, offer, onEnded }: { client: PipecatClient; offer: string; onEnded: () => void }) {
  const [view, dispatch] = useReducer(reduce, EMPTY_VIEW);
  const [failure, setFailure] = useState<string | null>(null);
  const state = usePipecatClientTransportState();
  const connecting = useRef(false);

  useRTVIClientEvent(RTVIEvent.UserTranscript, (data: TranscriptData) => dispatch({ type: "you", text: data.text, final: data.final }));
  useRTVIClientEvent(RTVIEvent.BotOutput, (data: BotOutputData) => {
    // A segment arrives whole as "new", then again word by word as it is spoken.
    if (data.will_be_spoken === false || (data.spoken_status && data.spoken_status !== "new")) return;
    dispatch({ type: "coach", text: data.text });
  });
  useRTVIClientEvent(RTVIEvent.ServerMessage, (message: unknown) => {
    dispatch({ type: "server", message });
    if ((message as { type?: unknown } | null)?.type === "ended") onEnded();
  });
  useRTVIClientEvent(RTVIEvent.DeviceError, (error: { message?: string }) => setFailure(error.message || "The microphone could not be used."));

  useEffect(() => {
    if (connecting.current) return;
    connecting.current = true;
    client.connect({ webrtcRequestParams: { endpoint: offer } }).catch((error: unknown) => {
      setFailure(error instanceof Error && error.message ? error.message : "The voice connection failed.");
    });
  }, [client, offer]);

  const live = state === "ready" && !view.ended;
  return (
    <>
      <PipecatClientAudio />
      <div className="voice-controls">
        <button type="button" disabled={!live} onClick={() => client.sendClientMessage(INTERRUPT_MESSAGE)} className="round-btn voice-btn">
          Interrupt
        </button>
        <span role="status" className="voice-status">{view.ended ? "Ended" : STATE_TEXT[state] ?? state}</span>
      </div>
      {failure && <p role="alert" className="voice-error">{failure}</p>}
      {view.ended && <p role="status" className="voice-status">{view.ended}</p>}
      <Lines view={view} />
      {import.meta.env.DEV && <Numbers view={view} />}
    </>
  );
}

/** Owns one session: opens it on mount, and on unmount or tab close ends it and frees the mic. */
export default function VoicePanel({ target }: { target: VoiceTarget }) {
  const [session, setSession] = useState<{ client: PipecatClient; info: VoiceSessionInfo } | null>(null);
  const [refusal, setRefusal] = useState<string | null>(null);
  const release = useRef<() => void>(() => undefined);

  useEffect(() => {
    let client: PipecatClient | null = null;
    let sessionId: string | null = null;
    let done = false;

    const end = () => {
      if (done) return;
      done = true;
      void client?.disconnect().catch(() => undefined);
      // Keepalive, so that it still goes out while the tab is closing.
      if (sessionId) void fetch(`/api/voice/session/${sessionId}`, { method: "DELETE", keepalive: true }).catch(() => undefined);
    };
    release.current = end;

    const start = async () => {
      try {
        const response = await fetch("/api/voice/session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(target),
        });
        if (!response.ok) {
          setRefusal(await refusalText(response));
          return;
        }
        const info = (await response.json()) as VoiceSessionInfo;
        sessionId = info.sessionId;
        if (done) {
          done = false;
          end();
          return;
        }
        client = new PipecatClient({ transport: new SmallWebRTCTransport(), enableMic: true, enableCam: false });
        setSession({ client, info });
      } catch {
        setRefusal("Could not reach the API.");
      }
    };

    // Deferred so that StrictMode's throwaway first mount never opens a session.
    const timer = setTimeout(() => void start(), 0);
    window.addEventListener("pagehide", end);
    return () => {
      clearTimeout(timer);
      window.removeEventListener("pagehide", end);
      end();
    };
    // Each drawer is keyed by what it talks about, so the target can't change under a session.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (refusal) return <p role="alert" className="voice-error">{refusal}</p>;
  if (!session) return <p role="status" className="voice-status">Opening a session…</p>;
  return (
    <PipecatClientProvider client={session.client}>
      <Session client={session.client} offer={session.info.offer} onEnded={() => release.current()} />
      {(session.info.stt !== "local" || session.info.tts !== "local") && (
        <p className="voice-notice">Hosted speech is on: speech {session.info.stt}, voice {session.info.tts}.</p>
      )}
    </PipecatClientProvider>
  );
}
