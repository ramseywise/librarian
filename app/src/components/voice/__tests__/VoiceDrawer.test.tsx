import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { DICTATION_NOTICE } from "../../../voice/policy";
import { VOICE_ANSWERS_NOTICE, VOICE_LOCAL_DEFAULT_NOTICE, VOICE_LOCAL_ONLY_NOTICE } from "../../../voice/voiceSession";
import { VoiceDrawer } from "../VoiceDrawer";

/** Stands in for the Pipecat client, so nothing here needs WebRTC, and counts how it was used. */
const pipecat = vi.hoisted(() => {
  const handlers = new Map<string, (data: unknown) => void>();
  return {
    handlers,
    loaded: 0,
    state: "ready",
    client: {
      connect: vi.fn(() => Promise.resolve()),
      disconnect: vi.fn(() => Promise.resolve()),
      sendClientMessage: vi.fn(),
    },
  };
});

vi.mock("@pipecat-ai/client-js", () => {
  pipecat.loaded += 1;
  return {
    PipecatClient: vi.fn(function PipecatClient() {
      return pipecat.client;
    }),
    RTVIEvent: { UserTranscript: "user", BotOutput: "bot", ServerMessage: "server", DeviceError: "device" },
  };
});
vi.mock("@pipecat-ai/small-webrtc-transport", () => ({ SmallWebRTCTransport: vi.fn() }));
vi.mock("@pipecat-ai/client-react", () => ({
  PipecatClientAudio: () => null,
  PipecatClientProvider: ({ children }: { children: unknown }) => children,
  usePipecatClientTransportState: () => pipecat.state,
  useRTVIClientEvent: (event: string, handler: (data: unknown) => void) => {
    pipecat.handlers.set(event, handler);
  },
}));

const NOT_RUNNING = "voice server not running, start with make voice";
const drill = { mode: "approach", lesson: "programming/drills/two-sum" } as const;
const interview = { mode: "interview", lesson: "interviewing/behavioural/story" } as const;
const SESSION = { sessionId: "abc", offer: "/api/voice/session/abc/offer", localOnly: false, stt: "local", tts: "local" };

function reply(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } });
}

function serve(routes: Record<string, () => Response>) {
  const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
    const route = routes[`${init?.method ?? "GET"} ${url}`];
    return route ? route() : reply(404, { detail: "no route" });
  });
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

const open = () => fireEvent.click(screen.getByRole("button", { name: "Voice" }));
const statusOk = () => reply(200, { running: true, stt: "ready", tts: "ready", sessionActive: false });

async function startSession() {
  open();
  fireEvent.click(await screen.findByRole("button", { name: "Start talking" }));
  await screen.findByRole("button", { name: "Interrupt" }, { timeout: 3000 });
}

beforeEach(() => {
  pipecat.handlers.clear();
  pipecat.state = "ready";
  vi.clearAllMocks();
});

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("with the voice server not running", () => {
  it("says how to start it, loads no Pipecat code, and opens no session", async () => {
    const fetchMock = serve({ "GET /api/voice/status": () => reply(503, { detail: NOT_RUNNING }) });
    const loadedBefore = pipecat.loaded;
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    open();
    expect((await screen.findByRole("alert")).textContent).toBe(NOT_RUNNING);
    expect(screen.queryByRole("button", { name: "Start talking" })).toBeNull();
    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual(["/api/voice/status"]);
    expect(pipecat.loaded).toBe(loadedBefore);
    expect(pipecat.client.connect).not.toHaveBeenCalled();
  });

  it("asks the server only after the drawer is opened", () => {
    const fetchMock = serve({});
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it("can check again once it has been started", async () => {
    let running = false;
    serve({ "GET /api/voice/status": () => (running ? statusOk() : reply(503, { detail: NOT_RUNNING })) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    open();
    await screen.findByRole("alert");
    running = true;
    fireEvent.click(screen.getByRole("button", { name: "Check again" }));
    await screen.findByRole("button", { name: "Start talking" });
  });
});

describe("what the drawer promises about privacy", () => {
  it("shows local-only status on interviewing, the Anthropic line, and no cloud notice", async () => {
    serve({ "GET /api/voice/status": statusOk });
    render(<VoiceDrawer subject={interview.lesson} target={interview} />);
    open();
    await screen.findByRole("button", { name: "Start talking" });
    expect(screen.getByText(VOICE_LOCAL_ONLY_NOTICE)).toBeTruthy();
    expect(screen.getByText(VOICE_ANSWERS_NOTICE)).toBeTruthy();
    expect(screen.queryByText(DICTATION_NOTICE)).toBeNull();
    expect(screen.queryByText(VOICE_LOCAL_DEFAULT_NOTICE)).toBeNull();
  });

  it("shows the local default elsewhere, and says so when hosted speech is on", async () => {
    serve({
      "GET /api/voice/status": statusOk,
      "POST /api/voice/session": () => reply(200, { ...SESSION, stt: "hosted", tts: "local" }),
    });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    expect(screen.getByText(VOICE_LOCAL_DEFAULT_NOTICE)).toBeTruthy();
    expect(screen.getByText(/Hosted speech is on: speech hosted/)).toBeTruthy();
  });

  it("shows the server's fail-closed refusal and doesn't connect", async () => {
    const refusal = "local speech recognition is not available, so this session cannot start";
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(503, { detail: refusal }) });
    render(<VoiceDrawer subject={interview.lesson} target={interview} />);
    open();
    fireEvent.click(await screen.findByRole("button", { name: "Start talking" }));
    expect((await screen.findByRole("alert", {}, { timeout: 3000 })).textContent).toBe(refusal);
    expect(pipecat.client.connect).not.toHaveBeenCalled();
  });
});

describe("a session", () => {
  it("posts what it talks about, and connects to the URL the server gave", async () => {
    const fetchMock = serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    const post = fetchMock.mock.calls.find(([url]) => url === "/api/voice/session");
    expect(JSON.parse(String(post?.[1]?.body))).toEqual(drill);
    expect(pipecat.client.connect).toHaveBeenCalledWith({ webrtcRequestParams: { endpoint: SESSION.offer } });
  });

  it("shows the live transcript, connection state, grades and ungraded turns", async () => {
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    expect(screen.getByRole("status").textContent).toBe("Listening");
    act(() => {
      pipecat.handlers.get("user")?.({ text: "a hash map of lanterns", final: true });
      pipecat.handlers.get("bot")?.({ text: "Why a hash map?", spoken_status: "new" });
      pipecat.handlers.get("bot")?.({ text: "Why", spoken_status: "in-progress" });
      pipecat.handlers.get("server")?.({ type: "grade", score: 0.6 });
      pipecat.handlers.get("server")?.({ type: "ungraded", reason: "no_grade" });
    });
    const transcript = screen.getByRole("list", { name: "Live transcript" }).textContent ?? "";
    expect(transcript).toContain("a hash map of lanterns");
    expect(transcript.match(/Why/g)).toHaveLength(1);
    expect(transcript).toContain("Graded 60%");
    expect(transcript).toContain("Not graded");
  });

  it("sends the interrupt from the button", async () => {
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    fireEvent.click(screen.getByRole("button", { name: "Interrupt" }));
    expect(pipecat.client.sendClientMessage).toHaveBeenCalledWith("interrupt");
  });

  it.each([
    ["closing the drawer", () => fireEvent.click(screen.getByRole("button", { name: "End voice session" }))],
    ["closing the tab", () => { window.dispatchEvent(new Event("pagehide")); }],
  ])("frees the mic and ends the session on %s", async (_name, leave) => {
    const fetchMock = serve({
      "GET /api/voice/status": statusOk,
      "POST /api/voice/session": () => reply(200, SESSION),
      "DELETE /api/voice/session/abc": () => reply(200, {}),
    });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    leave();
    await waitFor(() => expect(pipecat.client.disconnect).toHaveBeenCalledTimes(1));
    const ended = fetchMock.mock.calls.filter(([, init]) => init?.method === "DELETE");
    expect(ended).toHaveLength(1);
    expect(ended[0][1]?.keepalive).toBe(true);
  });

  it("frees the mic when the page unmounts", async () => {
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    const { unmount } = render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    unmount();
    expect(pipecat.client.disconnect).toHaveBeenCalledTimes(1);
  });

  it("frees the mic when the server ends the session, and says why", async () => {
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    act(() => pipecat.handlers.get("server")?.({ type: "ended", reason: "max_duration" }));
    expect(screen.getByText(/time limit/)).toBeTruthy();
    expect(pipecat.client.disconnect).toHaveBeenCalledTimes(1);
    expect((screen.getByRole("button", { name: "Interrupt" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("shows turn latency as numbers while developing", async () => {
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    act(() => pipecat.handlers.get("server")?.({ type: "latency", turn: 3, gap_ms: 1200.4, stt_ms: 90, vad_stop_ms: 200, llm_first_ms: 400, tts_first_ms: 300 }));
    expect(screen.getByTestId("voice-latency").textContent).toContain("Turn 3: 1200 ms");
  });

  it("surfaces a microphone or connection failure", async () => {
    pipecat.client.connect.mockRejectedValueOnce(new Error("permission denied"));
    serve({ "GET /api/voice/status": statusOk, "POST /api/voice/session": () => reply(200, SESSION) });
    render(<VoiceDrawer subject={drill.lesson} target={drill} />);
    await startSession();
    expect((await screen.findByRole("alert")).textContent).toBe("permission denied");
  });
});
