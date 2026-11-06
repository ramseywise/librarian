import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  createSseParser,
  describeHttpError,
  toHistory,
  useChatStream,
  EARLY_CLOSE,
  NETWORK_ERROR,
  STOPPED,
  type ChatMessage,
} from "../useChatStream";

const enc = new TextEncoder();
const frame = (e: object) => `data: ${JSON.stringify(e)}\n\n`;

/** A response whose body is a stream we push chunks into by hand. */
function controlledResponse(signal?: AbortSignal | null) {
  let ctrl!: ReadableStreamDefaultController<Uint8Array>;
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      ctrl = c;
    },
  });
  signal?.addEventListener("abort", () => ctrl.error(new DOMException("aborted", "AbortError")));
  return {
    response: new Response(body, { status: 200 }),
    push: (s: string) => ctrl.enqueue(enc.encode(s)),
    close: () => ctrl.close(),
  };
}

function streamResponse(chunks: string[]) {
  return new Response(
    new ReadableStream<Uint8Array>({
      start(c) {
        chunks.forEach((s) => c.enqueue(enc.encode(s)));
        c.close();
      },
    }),
    { status: 200 }
  );
}

const assistant = (r: { current: { messages: ChatMessage[] } }) =>
  r.current.messages[r.current.messages.length - 1];

afterEach(() => {
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe("createSseParser", () => {
  it("joins frames split across chunks and parses a final line without newline", () => {
    const events: Record<string, unknown>[] = [];
    const p = createSseParser((e) => events.push(e));
    p.push('data: {"type":"tok');
    p.push('en","content":"a"}\n\ndata:{"type":"token","content":"b"}\r\n');
    p.push(": comment\n");
    p.push("data: not json\n");
    p.push('data: {"type":"done"}');
    expect(events).toHaveLength(2);
    p.end();
    expect(events).toEqual([
      { type: "token", content: "a" },
      { type: "token", content: "b" },
      { type: "done" },
    ]);
  });
});

describe("toHistory", () => {
  const msg = (role: "user" | "assistant", content: string, extra: Partial<ChatMessage> = {}) =>
    ({ id: Math.random().toString(), role, content, streaming: false, ...extra }) as ChatMessage;

  it("keeps completed pairs and drops errored, stopped, streaming and empty replies", () => {
    const history = toHistory([
      msg("user", "q1"),
      msg("assistant", "a1"),
      msg("user", "q2"),
      msg("assistant", "partial", { error: true, stopped: true, note: STOPPED }),
      msg("user", "q3"),
      msg("assistant", "cut", { error: true, note: EARLY_CLOSE }),
      msg("user", "q4"),
      msg("assistant", "   "),
      msg("user", "q5"),
      msg("assistant", "a5"),
      msg("user", "q6"),
      msg("assistant", "still going", { streaming: true }),
    ]);
    expect(history).toEqual([
      { role: "user", content: "q1" },
      { role: "assistant", content: "a1" },
      { role: "user", content: "q5" },
      { role: "assistant", content: "a5" },
    ]);
  });
});

describe("describeHttpError", () => {
  it("maps statuses and FastAPI detail shapes", () => {
    expect(describeHttpError(400, { detail: "history must alternate" })).toBe("history must alternate");
    expect(
      describeHttpError(422, {
        detail: [{ loc: ["body", "query"], msg: "String should have at least 1 character", type: "x" }],
      })
    ).toBe("String should have at least 1 character (query)");
    expect(describeHttpError(404, null)).toBe("Request failed (HTTP 404)");
    expect(describeHttpError(500, { detail: "boom" })).toBe("Server error (HTTP 500)");
  });
});

describe("useChatStream", () => {
  it("streams tokens, grounding and highlight, then completes on done", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        streamResponse([
          frame({ type: "token", content: "Hello " }).slice(0, 10),
          frame({ type: "token", content: "Hello " }).slice(10),
          frame({ type: "token", content: "[page:rag]" }),
          frame({ type: "grounding", cited: ["rag"], pages_read: ["rag"], ungrounded: [] }),
          frame({ type: "highlight", pages: ["rag"] }),
          'data: {"type":"done"}',
        ])
      )
    );
    const onHighlight = vi.fn();
    const { result } = renderHook(() => useChatStream(onHighlight));
    await act(() => result.current.sendQuery("hi"));
    const a = assistant(result);
    expect(a.content).toBe("Hello [page:rag]");
    expect(a.streaming).toBe(false);
    expect(a.error).toBeUndefined();
    expect(a.grounding).toEqual({ cited: ["rag"], pagesRead: ["rag"], ungrounded: [] });
    expect(onHighlight).toHaveBeenCalledWith(["rag"]);
    expect(result.current.streaming).toBe(false);
  });

  it("keeps sendQuery/stop/clear stable across token updates", async () => {
    let stream!: ReturnType<typeof controlledResponse>;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_u: string, init?: RequestInit) => {
        stream = controlledResponse(init?.signal);
        return stream.response;
      })
    );
    const { result } = renderHook(() => useChatStream(() => {}));
    const first = { ...result.current };
    let pending!: Promise<void>;
    act(() => {
      pending = result.current.sendQuery("q");
    });
    await waitFor(() => expect(stream).toBeDefined());
    await act(async () => stream.push(frame({ type: "token", content: "a" })));
    await act(async () => stream.push(frame({ type: "token", content: "b" })));
    await waitFor(() => expect(assistant(result).content).toBe("ab"));
    expect(result.current.sendQuery).toBe(first.sendQuery);
    expect(result.current.stop).toBe(first.stop);
    expect(result.current.clear).toBe(first.clear);

    // The in-flight guard still holds with a stable callback.
    await act(() => result.current.sendQuery("ignored"));
    expect(fetch).toHaveBeenCalledTimes(1);

    await act(async () => {
      stream.push(frame({ type: "done" }));
      stream.close();
      await pending;
    });
    expect(result.current.streaming).toBe(false);
  });

  it("stop() keeps partial text, marks the reply stopped/error, and drops it from history", async () => {
    let stream!: ReturnType<typeof controlledResponse>;
    const fetchMock = vi.fn(async (_u: string, init?: RequestInit) => {
      stream = controlledResponse(init?.signal);
      return stream.response;
    });
    vi.stubGlobal("fetch", fetchMock);
    const { result } = renderHook(() => useChatStream(() => {}));
    let pending!: Promise<void>;
    act(() => {
      pending = result.current.sendQuery("q");
    });
    await waitFor(() => expect(stream).toBeDefined());
    await act(async () => stream.push(frame({ type: "token", content: "partial" })));
    await waitFor(() => expect(assistant(result).content).toBe("partial"));

    await act(async () => {
      result.current.stop();
      await pending;
    });
    const a = assistant(result);
    expect(a).toMatchObject({ content: "partial", streaming: false, error: true, stopped: true, note: STOPPED });
    expect(result.current.streaming).toBe(false);

    // Next query goes out with no history: the stopped pair is excluded.
    fetchMock.mockImplementationOnce(async () => streamResponse([frame({ type: "done" })]));
    await act(() => result.current.sendQuery("again"));
    const body = JSON.parse(fetchMock.mock.calls[1][1]!.body as string);
    expect(body).toEqual({ query: "again", history: [] });
  });

  it("clear() aborts and empties the conversation", async () => {
    let stream!: ReturnType<typeof controlledResponse>;
    vi.stubGlobal(
      "fetch",
      vi.fn(async (_u: string, init?: RequestInit) => {
        stream = controlledResponse(init?.signal);
        return stream.response;
      })
    );
    const { result } = renderHook(() => useChatStream(() => {}));
    let pending!: Promise<void>;
    act(() => {
      pending = result.current.sendQuery("q");
    });
    await waitFor(() => expect(stream).toBeDefined());
    await act(async () => {
      result.current.clear();
      await pending;
    });
    expect(result.current.messages).toEqual([]);
    expect(result.current.streaming).toBe(false);
  });

  it("network failure says the API could not be reached", async () => {
    vi.spyOn(console, "error").mockImplementation(() => {});
    vi.stubGlobal("fetch", vi.fn(async () => Promise.reject(new TypeError("Failed to fetch"))));
    const { result } = renderHook(() => useChatStream(() => {}));
    await act(() => result.current.sendQuery("q"));
    expect(assistant(result)).toMatchObject({ error: true, streaming: false, note: NETWORK_ERROR, content: "" });
  });

  it("422 shows the first pydantic message", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        Response.json(
          { detail: [{ loc: ["body", "history"], msg: "history must end on assistant" }] },
          { status: 422 }
        )
      )
    );
    const { result } = renderHook(() => useChatStream(() => {}));
    await act(() => result.current.sendQuery("q"));
    expect(assistant(result)).toMatchObject({ error: true, note: "history must end on assistant (history)" });
  });

  it("500 shows a server error with the status", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => new Response("Internal Server Error", { status: 500 })));
    const { result } = renderHook(() => useChatStream(() => {}));
    await act(() => result.current.sendQuery("q"));
    expect(assistant(result)).toMatchObject({ error: true, note: "Server error (HTTP 500)" });
  });

  it("stream closed without done keeps partial text and notes the early end", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => streamResponse([frame({ type: "token", content: "half" })])));
    const { result } = renderHook(() => useChatStream(() => {}));
    await act(() => result.current.sendQuery("q"));
    expect(assistant(result)).toMatchObject({
      content: "half",
      streaming: false,
      error: true,
      note: EARLY_CLOSE,
    });
  });
});
