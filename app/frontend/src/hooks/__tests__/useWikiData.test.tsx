import { StrictMode, type ReactNode } from "react";
import { act, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { deriveDomains, parseGraphMessage, useWikiData, wsUrl } from "../useWikiData";
import type { WikiNodeData } from "../../types";

const node = (id: string, dir: string, tags: string[], extra: Partial<WikiNodeData> = {}) => ({
  id,
  position: { x: 0, y: 0 },
  data: { title: id, tags, domain: [dir], typeTag: "concept", summary: "", updated: "", path: "", dimmed: false, highlighted: false, ...extra },
});

describe("wsUrl", () => {
  it("follows the page protocol and host", () => {
    expect(wsUrl({ protocol: "http:", host: "localhost:5173" })).toBe("ws://localhost:5173/ws");
    expect(wsUrl({ protocol: "https:", host: "wiki.example" })).toBe("wss://wiki.example/ws");
  });
});

describe("deriveDomains", () => {
  it("is the sorted set of primary directories without private", () => {
    expect(deriveDomains([node("a", "rag", []), node("b", "private", []), node("c", "eval", []), node("d", "rag", [])]))
      .toEqual(["eval", "rag"]);
  });
});

describe("parseGraphMessage", () => {
  const nodes = [node("a", "rag", ["rag"]), node("s", "private", ["rag"], { private: true })];
  const wikilink = { id: "w", source: "a", target: "s", data: { edgeType: "wikilink" } };
  const tagShared = { id: "t", source: "a", target: "s", data: { edgeType: "tag-shared" } };

  it("accepts the new payload shape", () => {
    const p = parseGraphMessage(JSON.stringify({ type: "graph_update", data: { nodes, edges: [wikilink], domains: ["rag"] } }));
    expect(p?.domains).toEqual(["rag"]);
    expect(p?.edges).toHaveLength(1);
  });

  it("accepts the old payload: drops server tag-shared edges and derives domains", () => {
    const p = parseGraphMessage(JSON.stringify({ type: "graph_update", data: { nodes, edges: [wikilink, tagShared] } }));
    expect(p?.edges.map((e) => e.id)).toEqual(["w"]);
    expect(p?.domains).toEqual(["rag"]);
  });

  it("keeps private pages as nodes (decision D1: visible locally) but never as a domain", () => {
    const p = parseGraphMessage(
      JSON.stringify({ type: "graph_update", data: { nodes, edges: [], domains: ["private", "rag"] } }),
    );
    expect(p?.nodes.map((n) => n.id)).toEqual(["a", "s"]);
    expect(p?.nodes[1].data.private).toBe(true);
    expect(p?.domains).toEqual(["rag"]);
  });

  it("returns null for bad JSON, other message types and malformed data", () => {
    expect(parseGraphMessage("{not json")).toBeNull();
    expect(parseGraphMessage(JSON.stringify({ type: "ping" }))).toBeNull();
    expect(parseGraphMessage(JSON.stringify({ type: "graph_update", data: { nodes: 1 } }))).toBeNull();
  });
});

class FakeWebSocket {
  static instances: FakeWebSocket[] = [];
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onmessage: ((e: { data: unknown }) => void) | null = null;
  closed = false;
  constructor(public url: string) {
    FakeWebSocket.instances.push(this);
  }
  close() {
    this.closed = true;
  }
  /** Simulate the server dropping the connection. */
  drop() {
    this.closed = true;
    this.onclose?.();
  }
}

describe("useWikiData socket lifecycle", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    FakeWebSocket.instances = [];
    vi.stubGlobal("WebSocket", FakeWebSocket);
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  const open = () => FakeWebSocket.instances.filter((s) => !s.closed);

  it("connects to /ws on the page origin and keeps one live socket under StrictMode", () => {
    const wrapper = ({ children }: { children: ReactNode }) => <StrictMode>{children}</StrictMode>;
    const { unmount } = renderHook(() => useWikiData(), { wrapper });
    act(() => vi.advanceTimersByTime(10_000));
    expect(open()).toHaveLength(1);
    expect(open()[0].url).toBe(`ws://${window.location.host}/ws`);
    unmount();
    act(() => vi.advanceTimersByTime(10_000));
    expect(open()).toHaveLength(0);
  });

  it("reconnects after a drop, but not after unmount", () => {
    const { unmount } = renderHook(() => useWikiData());
    act(() => FakeWebSocket.instances[0].drop());
    act(() => vi.advanceTimersByTime(2_000));
    expect(FakeWebSocket.instances).toHaveLength(2);

    act(() => FakeWebSocket.instances[1].drop());
    unmount(); // pending reconnect timer must be cancelled
    act(() => vi.advanceTimersByTime(10_000));
    expect(FakeWebSocket.instances).toHaveLength(2);
  });

  it("derives tag-shared edges from a graph_update", () => {
    const { result } = renderHook(() => useWikiData());
    const data = {
      nodes: [node("a", "rag", ["rag"]), node("b", "eval", ["rag"])],
      edges: [],
      domains: ["eval", "rag"],
    };
    act(() => FakeWebSocket.instances[0].onmessage?.({ data: JSON.stringify({ type: "graph_update", data }) }));
    expect(result.current.domains).toEqual(["eval", "rag"]);
    expect(result.current.tagSharedEdges.map((e) => e.id)).toEqual(["ts:a->b"]);
  });

  it("ignores malformed messages", () => {
    const { result } = renderHook(() => useWikiData());
    act(() => FakeWebSocket.instances[0].onmessage?.({ data: "garbage" }));
    expect(result.current.baseNodes).toEqual([]);
  });
});
