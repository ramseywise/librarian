// --- Tool call / result items ---

export interface ToolCallItem {
  id: string;
  name: string;
  args: unknown;
}

export interface ToolResultItem {
  id: string;
  name: string;
  result: unknown;
}

/** One row in the tool-step list: either a batch of calls or a batch of results. */
export interface ToolRow {
  step: number;
  kind: "calls" | "results";
  items: ToolCallItem[] | ToolResultItem[];
}

// --- Timing ---

export interface TimingStep {
  label: string;
  start_ms: number;
  duration_ms: number;
  type: "llm" | "tool";
}

export interface AgentTiming {
  total_ms: number;
  first_token_ms: number | null;
  steps: TimingStep[];
}

// --- Chat ---

export interface ChatMessage {
  id: string;
  role: "user" | "agent";
  text: string;
  toolRows?: ToolRow[];
  timing?: AgentTiming;
}

export interface AgentInfo {
  name: string;
  description: string;
}

// --- SSE events ---

export type SSEEvent =
  | { type: "connected" }
  | { type: "text_chunk"; request_id: string; text: string }
  | { type: "a2ui"; request_id: string; messages: unknown[] }
  | { type: "tool_calls"; request_id: string; step: number; calls: ToolCallItem[] }
  | { type: "tool_results"; request_id: string; step: number; results: ToolResultItem[] }
  | { type: "timing"; request_id: string; total_ms: number; first_token_ms: number | null; steps: TimingStep[] }
  | { type: "done"; request_id: string }
  | { type: "error"; request_id: string; message: string };
