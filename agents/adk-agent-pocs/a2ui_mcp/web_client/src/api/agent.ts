const BASE =
  (import.meta.env.VITE_AGENT_GATEWAY_URL as string | undefined) ?? "";

export async function postChat(
  sessionId: string,
  requestId: string,
  message: string,
  agentName = "a2ui_mcp"
): Promise<void> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      request_id: requestId,
      message,
      agent_name: agentName,
    }),
  });
  if (!res.ok) throw new Error(`POST /chat failed: ${res.status}`);
}

export async function getAgents() {
  const res = await fetch(`${BASE}/agents`);
  if (!res.ok) throw new Error(`GET /agents failed: ${res.status}`);
  return (await res.json()) as { name: string; description: string }[];
}

export async function switchAgent(
  sessionId: string,
  agentName: string
): Promise<void> {
  const res = await fetch(`${BASE}/agents/switch`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, agent_name: agentName }),
  });
  if (!res.ok) throw new Error(`POST /agents/switch failed: ${res.status}`);
}

export function createEventSource(sessionId: string, agentName = "a2ui_mcp") {
  return new EventSource(
    `${BASE}/chat/stream?session_id=${encodeURIComponent(sessionId)}&agent_name=${encodeURIComponent(agentName)}`
  );
}
