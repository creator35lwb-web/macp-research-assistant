import type { Paper, ViewMode } from "../../api/types";
import type { Analysis } from "../../api/types";
import { SearchBar } from "../search/SearchBar";
import { PaperCard } from "../search/PaperCard";
import { PaperSkeleton } from "../common/Skeleton";
import { EmptyState } from "../common/EmptyState";
import { NoteEditor } from "../notes/NoteEditor";

interface MainPanelProps {
  view: ViewMode;
  // Search
  papers: Paper[];
  searching: boolean;
  searchError: string;
  onSearch: (query: string, source: string) => void;
  // Paper selection
  selectedPaper: Paper | null;
  onSelectPaper: (paper: Paper) => void;
  // Analysis
  analyses: Record<string, Analysis>;
  analyzingId: string | null;
  analyzeError: string;
  onAnalyze: (paperId: string) => void;
  onSave?: (paperId: string) => void;
  // Notes
  onAddNote: (content: string, tags: string[], paperId?: string) => void;
  // Graph
  onLoadGraph: () => void;
  graphLoading: boolean;
  // Config
  provider: string;
  onProviderChange: (p: string) => void;
  apiKey: string;
  onApiKeyChange: (k: string) => void;
  // BYOK
  byokValidated?: boolean;
  byokValidating?: boolean;
  onValidateKey?: () => void;
  onClearKey?: () => void;
  // Pagination
  hasMore?: boolean;
  onLoadMore?: () => void;
  loadingMore?: boolean;
}

export function MainPanel({
  view, papers, searching, searchError, onSearch,
  selectedPaper, onSelectPaper,
  analyses: _analyses, analyzingId, analyzeError, onAnalyze, onSave,
  onAddNote, onLoadGraph, graphLoading,
  provider, onProviderChange, apiKey, onApiKeyChange,
  byokValidated, byokValidating, onValidateKey, onClearKey,
  hasMore, onLoadMore, loadingMore,
}: MainPanelProps) {
  if (view === "search") {
    return (
      <main className="main-panel">
        <SearchBar onSearch={(q, s) => onSearch(q, s)} searching={searching} />

        <div className="config-row">
          <label>
            Provider:
            <select value={provider} onChange={(e) => onProviderChange(e.target.value)} style={{ marginLeft: 4 }}>
              <option value="gemini">Gemini (free)</option>
              <option value="anthropic">Claude</option>
              <option value="openai">OpenAI</option>
              <option value="grok">xAI Grok</option>
            </select>
          </label>
          <div className="byok-row">
            <label>
              API Key:
              <input
                type="password"
                placeholder="BYOK (optional)"
                value={apiKey}
                onChange={(e) => onApiKeyChange(e.target.value)}
                style={{ marginLeft: 4, width: 140 }}
              />
            </label>
            {apiKey && onValidateKey && (
              <button
                className="btn-validate"
                onClick={onValidateKey}
                disabled={byokValidating}
              >
                {byokValidating ? "..." : "Validate & Apply"}
              </button>
            )}
            {apiKey && onClearKey && (
              <button className="btn-clear-key" onClick={onClearKey}>Clear</button>
            )}
            {byokValidated && <span className="byok-status validated">Validated</span>}
          </div>
        </div>

        {searchError && <div className="error-message">{searchError}</div>}
        {analyzeError && <div className="error-message">{analyzeError}</div>}

        {searching && [1, 2, 3].map((i) => <PaperSkeleton key={i} />)}

        {!searching && papers.length === 0 && (
          <EmptyState icon="&#128269;" title="Search for papers" description="Enter a topic to discover the latest research from arXiv and HuggingFace Daily Papers." />
        )}

        {papers.map((paper) => (
          <PaperCard
            key={paper.id}
            paper={paper}
            selected={selectedPaper?.id === paper.id}
            onSelect={onSelectPaper}
            analyzing={analyzingId === paper.id}
            onAnalyze={(id) => onAnalyze(id)}
            onSave={onSave}
          />
        ))}

        {hasMore && onLoadMore && (
          <button
            className="btn btn-secondary"
            onClick={onLoadMore}
            disabled={loadingMore}
            style={{ width: "100%", marginTop: 12 }}
          >
            {loadingMore ? "Loading..." : "Load More Papers"}
          </button>
        )}
      </main>
    );
  }

  if (view === "library") {
    return (
      <main className="main-panel">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>My Library</h2>
        {papers.length === 0 ? (
          <EmptyState icon="&#128218;" title="No saved papers" description="Save papers from search results to build your library." />
        ) : (
          papers.filter((p) => p.status === "saved" || p.status === "analyzed" || p.status === "cited").map((paper) => (
            <PaperCard
              key={paper.id}
              paper={paper}
              selected={selectedPaper?.id === paper.id}
              onSelect={onSelectPaper}
              analyzing={analyzingId === paper.id}
              onAnalyze={(id) => onAnalyze(id)}
            />
          ))
        )}
      </main>
    );
  }

  if (view === "graph") {
    return (
      <main className="main-panel">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h2 style={{ fontSize: 18, fontWeight: 600 }}>Knowledge Graph</h2>
          <button className="btn btn-secondary btn-sm" onClick={onLoadGraph} disabled={graphLoading}>
            {graphLoading ? "Loading..." : "Refresh"}
          </button>
        </div>
        <EmptyState icon="&#127760;" title="Knowledge graph loads here" description="Click Refresh to visualize connections between papers and analyses." />
      </main>
    );
  }

  if (view === "notes") {
    return (
      <main className="main-panel">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Research Notes</h2>
        <NoteEditor onSave={onAddNote} />
        <EmptyState icon="&#128221;" title="No notes yet" description="Write research notes and link them to papers." />
      </main>
    );
  }

  return <main className="main-panel" />;
}
