import { useCallback, useEffect, useState } from "react";
import { getAgents, switchAgent } from "../api/agent";
import type { AgentInfo } from "../types";

export function useAgents(sessionId: string) {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [activeAgent, setActiveAgent] = useState("a2ui_mcp");

  useEffect(() => {
    getAgents()
      .then(setAgents)
      .catch((err) => console.error("Failed to load agents:", err));
  }, []);

  const handleSwitch = useCallback(
    async (agentName: string) => {
      await switchAgent(sessionId, agentName);
      setActiveAgent(agentName);
    },
    [sessionId]
  );

  return { agents, activeAgent, switchAgent: handleSwitch };
}
