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
  if (!paper) {
    return (
      <aside className="detail-panel empty">
        <EmptyState icon="&#128196;" title="Select a paper" description="Click a paper to see details, analysis, and PDF preview." />
      </aside>
    );
  }

  return (
    <aside className="detail-panel">
      <h2 style={{ fontSize: 16, fontWeight: 600, lineHeight: 1.4, marginBottom: 8 }}>
        {paper.title}
      </h2>

      <span className={`status-badge status-${paper.status}`} style={{ marginBottom: 12, display: "inline-block" }}>
        {paper.status}
      </span>

      {paper.authors.length > 0 && (
        <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 16 }}>
          {paper.authors.join(", ")}
        </div>
      )}

      {paper.abstract && (
        <div className="analysis-section">
          <h4>Abstract</h4>
          <p className="analysis-summary">{paper.abstract}</p>
        </div>
      )}

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

      {/* Abstract analysis */}
      {analysis && (
        <div style={{ marginTop: 16 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: "var(--color-analyses)" }}>
            AI Analysis
          </h3>
          <AnalysisView analysis={analysis} />
        </div>
      )}

      {/* Deep analysis */}
      {deepAnalysis && (
        <div style={{ marginTop: 16 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: "var(--color-papers)" }}>
            Deep Analysis
          </h3>
          <DeepAnalysisView
            analysis={deepAnalysis.analysis}
            pageCount={deepAnalysis.pageCount}
            sectionsExtracted={deepAnalysis.sectionsExtracted}
          />
        </div>
      )}

      {/* Consensus */}
      {consensus && (
        <div style={{ marginTop: 16 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: "var(--color-graph)" }}>
            Multi-Agent Consensus
          </h3>
          <ConsensusView consensus={consensus} />
        </div>
      )}

      <div style={{ marginTop: 16 }}>
        <PdfPreview arxivId={paper.id} />
      </div>
    </aside>
  );
}
