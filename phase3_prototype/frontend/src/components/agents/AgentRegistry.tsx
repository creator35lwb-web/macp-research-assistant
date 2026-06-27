import type { Agent } from "../../api/types";

interface AgentRegistryProps {
  agents: Agent[];
  loading: boolean;
  onRefresh: () => void;
}

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
        <h2 style={{ fontSize: 18, fontWeight: 600 }}>Supported Models</h2>
        <button className="btn btn-secondary btn-sm" onClick={onRefresh} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
        Bring your own API key (BYOK) for any provider below to analyze papers. Models are the
        current defaults and can be overridden per deployment via env vars (e.g. <code>GEMINI_MODEL</code>).
      </p>

      {agents.length === 0 && !loading && (
        <div style={{ color: "var(--text-tertiary)", textAlign: "center", padding: 32 }}>
          No providers loaded. Click Refresh.
        </div>
      )}

      <div className="agent-grid">
        {agents.map((agent) => (
          <div key={agent.agent_id} className="agent-card">
            <div className="agent-card-header">
              <span className="agent-name">{agent.name}</span>
              {agent.server_key ? (
                <span className="agent-cost-badge" style={{ color: "var(--color-success)" }}>
                  ready
                </span>
              ) : (
                <span className="agent-cost-badge" style={{ color: "var(--text-tertiary)" }}>
                  BYOK
                </span>
              )}
            </div>

            <div className="agent-model">{agent.model}</div>

            <div className="agent-capabilities">
              {agent.capabilities.map((cap) => (
                <span key={cap} className="agent-capability-chip">
                  {CAPABILITY_LABELS[cap] || cap}
                </span>
              ))}
            </div>

            <div className="agent-footer">
              {agent.env_key && (
                <span className="agent-key-hint">
                  {agent.server_key ? "Server key set · " : ""}Key: {agent.env_key}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
