import { useState } from "react";
import type { Analysis, DeepAnalysis, Consensus, Paper } from "../../api/types";
import { AnalysisView, DeepAnalysisView, ConsensusView } from "../analysis/AnalysisView";
import { PdfPreview } from "../analysis/PdfPreview";
import { EmptyState } from "../common/EmptyState";

interface DetailPanelProps {
  paper: Paper | null;
  analysis: Analysis | undefined;
  deepAnalysis?: { analysis: DeepAnalysis; pageCount: number; sectionsExtracted: number } | null;
  consensus?: Consensus | null;
  onAnalyzeDeep?: (paperId: string) => void;
  onGenerateConsensus?: (paperId: string) => void;
  analyzingDeep?: boolean;
  generatingConsensus?: boolean;
}

export function DetailPanel({
  paper, analysis, deepAnalysis, consensus,
  onAnalyzeDeep, onGenerateConsensus,
  analyzingDeep, generatingConsensus,
}: DetailPanelProps) {
  const [overviewCollapsed, setOverviewCollapsed] = useState(false);

  if (!paper) {
    return (
      <aside className="detail-panel empty">
        <EmptyState icon="&#128196;" title="Select a paper" description="Click a paper to see details, analysis, and PDF preview." />
      </aside>
    );
  }

  return (
    <aside className="detail-panel">
      {/* Paper Overview — collapsible */}
      <div className="detail-card detail-card--overview">
        <button
          className="detail-card-header"
          onClick={() => setOverviewCollapsed(!overviewCollapsed)}
          aria-expanded={!overviewCollapsed}
        >
          <h2 className="detail-card-title">{paper.title}</h2>
          <span className="detail-card-toggle">{overviewCollapsed ? "+" : "\u2212"}</span>
        </button>

        {!overviewCollapsed && (
          <div className="detail-card-body">
            <div className="detail-meta-row">
              <span className={`status-badge status-${paper.status}`}>{paper.status}</span>
              <code className="detail-paper-id">{paper.id}</code>
            </div>

            {paper.authors.length > 0 && (
              <div className="detail-authors">{paper.authors.join(", ")}</div>
            )}

            {paper.abstract && (
              <div className="detail-abstract">
                <h4>Abstract</h4>
                <p className="analysis-summary">{paper.abstract}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Action buttons */}
      {analysis && (
        <div className="detail-actions">
          {onAnalyzeDeep && !deepAnalysis && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => onAnalyzeDeep(paper.id)}
              disabled={analyzingDeep}
            >
              {analyzingDeep ? "Analyzing..." : "Deep Analysis"}
            </button>
          )}
          {onGenerateConsensus && (
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => onGenerateConsensus(paper.id)}
              disabled={generatingConsensus}
            >
              {generatingConsensus ? "Generating..." : "Consensus"}
            </button>
          )}
        </div>
      )}

      {/* Abstract analysis — boxed */}
      {analysis && (
        <div className="detail-card detail-card--analysis">
          <div className="detail-card-label">
            <span className="detail-card-dot" style={{ background: "var(--color-analyses)" }} />
            AI Analysis
          </div>
          <AnalysisView analysis={analysis} />
        </div>
      )}

      {/* Deep analysis — boxed */}
      {deepAnalysis && (
        <div className="detail-card detail-card--deep">
          <div className="detail-card-label">
            <span className="detail-card-dot" style={{ background: "var(--color-papers)" }} />
            Deep Analysis
          </div>
          <DeepAnalysisView
            analysis={deepAnalysis.analysis}
            pageCount={deepAnalysis.pageCount}
            sectionsExtracted={deepAnalysis.sectionsExtracted}
          />
        </div>
      )}

      {/* Consensus — boxed */}
      {consensus && (
        <div className="detail-card detail-card--consensus">
          <div className="detail-card-label">
            <span className="detail-card-dot" style={{ background: "var(--color-graph)" }} />
            Multi-Agent Consensus
          </div>
          <ConsensusView consensus={consensus} />
        </div>
      )}

      <div className="detail-card detail-card--pdf">
        <div className="detail-card-label">
          <span className="detail-card-dot" style={{ background: "var(--text-tertiary)" }} />
          PDF Preview
        </div>
        <PdfPreview arxivId={paper.id} />
      </div>
    </aside>
  );
}
