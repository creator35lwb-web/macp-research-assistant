import type { Agent } from "../../api/types";

interface AgentRegistryProps {
  agents: Agent[];
  loading: boolean;
  onRefresh: () => void;
}

const COST_COLORS: Record<string, string> = {
  free: "var(--color-success)",
  freemium: "var(--color-notes)",
  paid: "var(--color-papers)",
  enterprise: "var(--color-graph)",
};

const CAPABILITY_LABELS: Record<string, string> = {
  abstract_analysis: "Abstract Analysis",
  deep_analysis: "Deep Analysis",
  deep_research: "Deep Research",
  citation_extraction: "Citations",
  full_text_search: "Full-Text Search",
  consensus_synthesis: "Consensus",
  knowledge_graph: "Knowledge Graph",
  comparative_analysis: "Comparative",
};

export function AgentRegistry({ agents, loading, onRefresh }: AgentRegistryProps) {
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>Agent Registry</h2>
        <button className="btn btn-secondary btn-sm" onClick={onRefresh} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
        {agents.length} AI agents registered in the MACP ecosystem. Each agent can analyze papers with different strengths.
      </p>

      {agents.length === 0 && !loading && (
        <div style={{ color: "var(--text-tertiary)", textAlign: "center", padding: 32 }}>
          No agents loaded. Click Refresh.
        </div>
      )}

      <div className="agent-grid">
        {agents.map((agent) => (
          <div key={agent.agent_id} className="agent-card">
            <div className="agent-card-header">
              <span className="agent-name">{agent.name}</span>
              <span
                className="agent-cost-badge"
                style={{ color: COST_COLORS[agent.cost_tier] || "var(--text-secondary)" }}
              >
                {agent.cost_tier}
              </span>
            </div>

            <div className="agent-model">{agent.model}</div>

            <div className="agent-strengths">{agent.strengths}</div>

            <div className="agent-capabilities">
              {agent.capabilities.map((cap) => (
                <span key={cap} className="agent-capability-chip">
                  {CAPABILITY_LABELS[cap] || cap}
                </span>
              ))}
            </div>

            <div className="agent-footer">
              {agent.env_key && (
                <span className="agent-key-hint">BYOK: {agent.env_key}</span>
              )}
              {!agent.env_key && agent.cost_tier === "enterprise" && (
                <span className="agent-key-hint">Internal agent</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
