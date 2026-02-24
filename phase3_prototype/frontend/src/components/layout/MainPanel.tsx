import type { Paper, ViewMode, Note, Agent } from "../../api/types";
import type { Analysis } from "../../api/types";
import { SearchBar } from "../search/SearchBar";
import { PaperCard } from "../search/PaperCard";
import { PaperSkeleton } from "../common/Skeleton";
import { EmptyState } from "../common/EmptyState";
import { NoteEditor } from "../notes/NoteEditor";
import { AgentRegistry } from "../agents/AgentRegistry";

interface MainPanelProps {
  view: ViewMode;
  // Search
  papers: Paper[];
  libraryPapers?: Paper[];
  libraryLoading?: boolean;
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
  // Notes
  notes?: Note[];
  notesLoading?: boolean;
  // Agents
  agents?: Agent[];
  agentsLoading?: boolean;
  onFetchAgents?: () => void;
}

export function MainPanel({
  view, papers, libraryPapers, libraryLoading, searching, searchError, onSearch,
  selectedPaper, onSelectPaper,
  analyses: _analyses, analyzingId, analyzeError, onAnalyze, onSave,
  onAddNote, onLoadGraph, graphLoading,
  provider, onProviderChange, apiKey, onApiKeyChange,
  byokValidated, byokValidating, onValidateKey, onClearKey,
  hasMore, onLoadMore, loadingMore,
  notes, notesLoading,
  agents, agentsLoading, onFetchAgents,
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
    const libPapers = libraryPapers || [];
    return (
      <main className="main-panel">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>My Library</h2>
        {libraryLoading && <div style={{ color: "var(--text-secondary)", fontSize: 13 }}>Loading library...</div>}
        {!libraryLoading && libPapers.length === 0 ? (
          <EmptyState icon="&#128218;" title="No saved papers" description="Save papers from search results to build your library." />
        ) : (
          libPapers.map((paper) => (
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
    const noteList = notes || [];
    return (
      <main className="main-panel">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>Research Notes</h2>
        <NoteEditor onSave={onAddNote} />
        {notesLoading && <div style={{ color: "var(--text-secondary)", fontSize: 13, marginTop: 8 }}>Loading notes...</div>}
        {!notesLoading && noteList.length === 0 && (
          <EmptyState icon="&#128221;" title="No notes yet" description="Write research notes and link them to papers." />
        )}
        {noteList.map((note) => (
          <div key={note.id} className="note-card" style={{
            background: "var(--bg-tertiary, #18181b)",
            borderRadius: 8,
            padding: "12px 16px",
            marginTop: 8,
            border: "1px solid var(--border, #27272a)",
          }}>
            <p style={{ margin: 0, fontSize: 14, whiteSpace: "pre-wrap" }}>{note.content}</p>
            <div style={{ display: "flex", gap: 6, marginTop: 8, flexWrap: "wrap" }}>
              {(note.tags || []).map((tag) => (
                <span key={tag} style={{
                  fontSize: 11,
                  background: "var(--color-notes, #f59e0b)",
                  color: "#000",
                  borderRadius: 4,
                  padding: "2px 6px",
                }}>{tag}</span>
              ))}
            </div>
            <div style={{ fontSize: 11, color: "var(--text-secondary, #71717a)", marginTop: 6 }}>
              {note.created_at ? new Date(note.created_at).toLocaleString() : ""}
            </div>
          </div>
        ))}
      </main>
    );
  }

  if (view === "agents") {
    return (
      <main className="main-panel">
        <AgentRegistry
          agents={agents || []}
          loading={agentsLoading || false}
          onRefresh={onFetchAgents || (() => {})}
        />
      </main>
    );
  }

  return <main className="main-panel" />;
}
