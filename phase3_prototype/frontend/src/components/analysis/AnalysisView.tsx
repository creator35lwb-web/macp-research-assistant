import type { Analysis } from "../../api/types";

interface AnalysisViewProps {
  analysis: Analysis;
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
