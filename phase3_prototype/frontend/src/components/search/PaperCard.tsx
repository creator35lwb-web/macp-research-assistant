import type { Paper } from "../../api/types";

interface PaperCardProps {
  paper: Paper;
  selected: boolean;
  onSelect: (paper: Paper) => void;
  analyzing: boolean;
  onAnalyze: (paperId: string) => void;
  onSave?: (paperId: string) => void;
}

export function PaperCard({ paper, selected, onSelect, analyzing, onAnalyze, onSave }: PaperCardProps) {
  return (
    <div className={`paper-card ${selected ? "selected" : ""}`} onClick={() => onSelect(paper)}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div className="paper-card-title">{paper.title}</div>
        <span className={`status-badge status-${paper.status}`}>{paper.status}</span>
      </div>
      <div className="paper-card-meta">
        <code style={{ fontSize: 11 }}>{paper.id}</code>
        {paper.authors.length > 0 && (
          <> &middot; {paper.authors.slice(0, 3).join(", ")}{paper.authors.length > 3 && "..."}</>
        )}
      </div>
      {paper.abstract && (
        <div className="paper-card-abstract">{paper.abstract}</div>
      )}
      <div className="paper-card-actions" onClick={(e) => e.stopPropagation()}>
        {paper.url && (
          <a href={paper.url} target="_blank" rel="noopener noreferrer" className="btn btn-ghost btn-sm">
            arXiv
          </a>
        )}
        <button className="btn btn-secondary btn-sm" onClick={() => onAnalyze(paper.id)} disabled={analyzing}>
          {analyzing ? "Analyzing..." : "Analyze"}
        </button>
        {onSave && (
          <button className="btn btn-ghost btn-sm" onClick={() => onSave(paper.id)}>
            Save
          </button>
        )}
      </div>
    </div>
  );
}
