import { useState } from "react";
import type { ViewMode } from "../../api/types";
import { useAuth } from "../../hooks/useAuth";
import { usePapers } from "../../hooks/usePapers";
import { useGraph } from "../../hooks/useGraph";
import { useGitHub } from "../../hooks/useGitHub";
import { mcpAddNote, mcpSave } from "../../api/client";
import { Sidebar } from "./Sidebar";
import { MainPanel } from "./MainPanel";
import { DetailPanel } from "./DetailPanel";
import { KnowledgeGraph } from "../graph/KnowledgeGraph";
import { ErrorBoundary } from "../common/ErrorBoundary";
import type { Paper } from "../../api/types";

export function Workspace() {
  const { user, loading: authLoading, logout, loginUrl } = useAuth();
  const {
    papers, searching, searchError, search,
    analyses, analyzingId, analyzeError, analyze,
  } = usePapers();
  const { graphData, loading: graphLoading, fetchGraph } = useGraph();
  const {
    repos, connected, connectedRepo, loading: githubLoading,
    fetchStatus, fetchRepos, connect, sync,
  } = useGitHub();

  const [activeView, setActiveView] = useState<ViewMode>("search");
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [provider, setProvider] = useState("gemini");
  const [apiKey, setApiKey] = useState("");

  // Fetch GitHub status on mount if user is logged in
  useState(() => {
    if (user) fetchStatus();
  });

  const handleSearch = (query: string, source: string) => {
    search(query, 10, source);
  };

  const handleAnalyze = (paperId: string) => {
    analyze(paperId, provider, apiKey || undefined);
  };

  const handleSave = async (paperId: string) => {
    try {
      await mcpSave(paperId);
    } catch {
      // Silently fail — user may not be logged in
    }
  };

  const handleAddNote = async (content: string, tags: string[], paperId?: string) => {
    try {
      await mcpAddNote(content, tags, paperId);
    } catch {
      // Silently fail
    }
  };

  if (authLoading) {
    return <div className="workspace" style={{ placeItems: "center", display: "grid" }}>Loading...</div>;
  }

  return (
    <div className="workspace">
      <Sidebar
        user={user}
        loginUrl={loginUrl}
        onLogout={logout}
        activeView={activeView}
        onViewChange={setActiveView}
        repos={repos}
        connected={connected}
        connectedRepo={connectedRepo}
        githubLoading={githubLoading}
        onFetchRepos={fetchRepos}
        onConnect={connect}
        onSync={sync}
      />

      <ErrorBoundary>
        {activeView === "graph" && graphData ? (
          <main className="main-panel" style={{ padding: 0 }}>
            <KnowledgeGraph data={graphData} />
          </main>
        ) : (
          <MainPanel
            view={activeView}
            papers={papers}
            searching={searching}
            searchError={searchError}
            onSearch={handleSearch}
            selectedPaper={selectedPaper}
            onSelectPaper={setSelectedPaper}
            analyses={analyses}
            analyzingId={analyzingId}
            analyzeError={analyzeError}
            onAnalyze={handleAnalyze}
            onSave={user ? handleSave : undefined}
            onAddNote={handleAddNote}
            onLoadGraph={fetchGraph}
            graphLoading={graphLoading}
            provider={provider}
            onProviderChange={setProvider}
            apiKey={apiKey}
            onApiKeyChange={setApiKey}
          />
        )}
      </ErrorBoundary>

      <DetailPanel
        paper={selectedPaper}
        analysis={selectedPaper ? analyses[selectedPaper.id] : undefined}
      />
    </div>
  );
}
