import type { Analysis, DeepAnalysis, Consensus } from "../../api/types";

interface AnalysisViewProps {
  analysis: Analysis;
}

interface DeepAnalysisViewProps {
  analysis: DeepAnalysis;
  pageCount?: number;
  sectionsExtracted?: number;
}

export function AnalysisView({ analysis }: AnalysisViewProps) {
  const scoreColor = analysis.strength_score >= 7 ? "var(--color-success)" :
    analysis.strength_score >= 4 ? "var(--color-notes)" : "var(--color-error)";

  return (
    <div>
      <div className="analysis-section">
        <h4>Summary</h4>
        <p className="analysis-summary">{analysis.summary}</p>
      </div>

      {analysis.key_insights.length > 0 && (
        <div className="analysis-section">
          <h4>Key Insights</h4>
          <ul className="insight-list">
            {analysis.key_insights.map((insight, i) => (
              <li key={i}>{insight}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.methodology && (
        <div className="analysis-section">
          <h4>Methodology</h4>
          <p className="analysis-summary">{analysis.methodology}</p>
        </div>
      )}

      {analysis.research_gaps.length > 0 && (
        <div className="analysis-section">
          <h4>Research Gaps</h4>
          <ul className="insight-list">
            {analysis.research_gaps.map((gap, i) => (
              <li key={i}>{gap}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="analysis-section">
        <h4>Strength Score</h4>
        <div className="score-display">
          <span style={{ color: scoreColor }}>{analysis.strength_score}/10</span>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{ width: `${analysis.strength_score * 10}%`, background: scoreColor }}
            />
          </div>
        </div>
      </div>

      {analysis.relevance_tags.length > 0 && (
        <div className="analysis-section">
          <h4>Tags</h4>
          <div>
            {analysis.relevance_tags.map((tag) => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        </div>
      )}

      {analysis._meta && (
        <div className="provenance">
          {analysis._meta.bias_disclaimer}
          <br />
          Provider: {analysis._meta.provider} ({analysis._meta.model})
        </div>
      )}
    </div>
  );
}

export function DeepAnalysisView({ analysis, pageCount, sectionsExtracted }: DeepAnalysisViewProps) {
  const scoreColor = analysis.strength_score >= 7 ? "var(--color-success)" :
    analysis.strength_score >= 4 ? "var(--color-notes)" : "var(--color-error)";

  return (
    <div>
      <div className="analysis-section" style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
        <span className="tag" style={{ background: "var(--color-primary)", color: "#fff" }}>
          Deep Analysis
        </span>
        {pageCount !== undefined && (
          <span className="tag">{pageCount} pages</span>
        )}
        {sectionsExtracted !== undefined && (
          <span className="tag">{sectionsExtracted} sections</span>
        )}
        {analysis._meta && (
          <span className="tag">{analysis._meta.passes} LLM passes</span>
        )}
      </div>

      <div className="analysis-section">
        <h4>Summary</h4>
        <p className="analysis-summary">{analysis.summary}</p>
      </div>

      {analysis.key_contributions.length > 0 && (
        <div className="analysis-section">
          <h4>Key Contributions</h4>
          <ul className="insight-list">
            {analysis.key_contributions.map((c, i) => (
              <li key={i}>{c}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.methodology_detail && (
        <div className="analysis-section">
          <h4>Methodology Detail</h4>
          <p className="analysis-summary">{analysis.methodology_detail}</p>
        </div>
      )}

      {analysis.limitations.length > 0 && (
        <div className="analysis-section">
          <h4>Limitations</h4>
          <ul className="insight-list">
            {analysis.limitations.map((l, i) => (
              <li key={i}>{l}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.future_work.length > 0 && (
        <div className="analysis-section">
          <h4>Future Work</h4>
          <ul className="insight-list">
            {analysis.future_work.map((fw, i) => (
              <li key={i}>{fw}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.research_gaps.length > 0 && (
        <div className="analysis-section">
          <h4>Research Gaps</h4>
          <ul className="insight-list">
            {analysis.research_gaps.map((gap, i) => (
              <li key={i}>{gap}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="analysis-section">
        <h4>Strength Score</h4>
        <div className="score-display">
          <span style={{ color: scoreColor }}>{analysis.strength_score}/10</span>
          <div className="score-bar">
            <div
              className="score-fill"
              style={{ width: `${analysis.strength_score * 10}%`, background: scoreColor }}
            />
          </div>
        </div>
      </div>

      {analysis.relevance_tags.length > 0 && (
        <div className="analysis-section">
          <h4>Tags</h4>
          <div>
            {analysis.relevance_tags.map((tag) => (
              <span key={tag} className="tag">{tag}</span>
            ))}
          </div>
        </div>
      )}

      {analysis.section_analyses.length > 0 && (
        <div className="analysis-section">
          <h4>Analysis Passes</h4>
          <details>
            <summary style={{ cursor: "pointer", marginBottom: "0.5rem" }}>
              View {analysis.section_analyses.length} individual passes
            </summary>
            {analysis.section_analyses.map((sa, i) => (
              <div key={i} style={{ marginBottom: "0.75rem", paddingLeft: "1rem", borderLeft: "2px solid var(--color-border)" }}>
                <strong>Pass: {sa.pass}</strong>
                <pre style={{ fontSize: "0.75rem", whiteSpace: "pre-wrap", marginTop: "0.25rem" }}>
                  {JSON.stringify(sa.data, null, 2)}
                </pre>
              </div>
            ))}
          </details>
        </div>
      )}

      {analysis._meta && (
        <div className="provenance">
          {analysis._meta.bias_disclaimer}
          <br />
          Provider: {analysis._meta.provider} ({analysis._meta.model}) — {analysis._meta.passes}-pass deep analysis
        </div>
      )}
    </div>
  );
}

interface ConsensusViewProps {
  consensus: Consensus;
}

export function ConsensusView({ consensus }: ConsensusViewProps) {
  const scoreColor = consensus.agreement_score >= 0.7 ? "var(--color-success)" :
    consensus.agreement_score >= 0.4 ? "var(--color-notes)" : "var(--color-error)";

  const scorePercent = Math.round(consensus.agreement_score * 100);

  return (
    <div>
      <div className="consensus-header">
        <span className="tag" style={{ background: "var(--color-graph)", color: "#fff" }}>
          Consensus
        </span>
        <span className="tag">{consensus.agents_compared.length} agents</span>
        <span className="tag">{consensus.generated_by}</span>
      </div>

      <div className="analysis-section">
        <h4>Agreement Score</h4>
        <div className="consensus-score">
          <span className="consensus-score-value" style={{ color: scoreColor }}>
            {scorePercent}%
          </span>
          <div className="consensus-score-bar">
            <div
              className="consensus-score-fill"
              style={{ width: `${scorePercent}%`, background: scoreColor }}
            />
          </div>
          <span className="consensus-score-label">
            {scorePercent >= 70 ? "Strong agreement" :
             scorePercent >= 40 ? "Moderate agreement" : "Low agreement"}
          </span>
        </div>
      </div>

      <div className="analysis-section">
        <h4>Agents Compared</h4>
        <div className="consensus-agents">
          {consensus.agents_compared.map((agent) => (
            <span key={agent} className="consensus-agent-chip">{agent}</span>
          ))}
        </div>
      </div>

      <div className="analysis-section">
        <h4>Synthesized Summary</h4>
        <p className="analysis-summary">{consensus.synthesized_summary}</p>
      </div>

      {consensus.convergence_points.length > 0 && (
        <div className="analysis-section">
          <h4>Convergence Points</h4>
          <ul className="insight-list consensus-convergence">
            {consensus.convergence_points.map((point, i) => (
              <li key={i}>{point}</li>
            ))}
          </ul>
        </div>
      )}

      {consensus.divergence_points.length > 0 && (
        <div className="analysis-section">
          <h4>Divergence Points</h4>
          {consensus.divergence_points.map((dp, i) => (
            <div key={i} className="divergence-card">
              <div className="divergence-topic">{dp.topic}</div>
              <div className="divergence-positions">
                {Object.entries(dp.positions).map(([agent, position]) => (
                  <div key={agent} className="divergence-position">
                    <span className="divergence-agent">{agent}</span>
                    <span className="divergence-text">{position}</span>
                  </div>
                ))}
              </div>
              {dp.resolution && (
                <div className="divergence-resolution">
                  Resolution: {dp.resolution}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {consensus.recommended_action && (
        <div className="analysis-section">
          <h4>Recommended Action</h4>
          <p className="analysis-summary">{consensus.recommended_action}</p>
        </div>
      )}

      {consensus.bias_cross_check && (
        <div className="analysis-section">
          <h4>Bias Cross-Check</h4>
          <p className="analysis-summary" style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            {consensus.bias_cross_check}
          </p>
        </div>
      )}

      <div className="provenance">
        Multi-agent consensus generated by {consensus.generated_by} at{" "}
        {new Date(consensus.generated_at).toLocaleString()}
      </div>
    </div>
  );
}
