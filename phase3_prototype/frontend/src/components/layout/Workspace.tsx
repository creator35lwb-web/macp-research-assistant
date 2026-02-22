import { useState } from "react";
import type { ViewMode } from "../../api/types";
import { useAuth } from "../../hooks/useAuth";
import { usePapers } from "../../hooks/usePapers";
import { useGraph } from "../../hooks/useGraph";
import { useGitHub } from "../../hooks/useGitHub";
import { mcpAddNote, mcpSave, validateApiKey } from "../../api/client";
import { Sidebar } from "./Sidebar";
import { MainPanel } from "./MainPanel";
import { DetailPanel } from "./DetailPanel";
import { KnowledgeGraph } from "../graph/KnowledgeGraph";
import { ErrorBoundary } from "../common/ErrorBoundary";
import { showToast } from "../common/Toast";
import type { Paper } from "../../api/types";

export function Workspace() {
  const { user, loading: authLoading, logout, loginUrl } = useAuth();
  const {
    papers, searching, searchError, search,
    analyses, analyzingId, analyzeError, analyze,
    hasMore, loadMore, loadingMore,
  } = usePapers();
  const { graphData, loading: graphLoading, fetchGraph } = useGraph();
  const {
    repos, connected, connectedRepo, loading: githubLoading,
    fetchStatus, fetchRepos, connect, sync,
  } = useGitHub();

  const [activeView, setActiveView] = useState<ViewMode>("search");
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [provider, setProvider] = useState(() => localStorage.getItem("byok_provider") || "gemini");
  const [apiKey, setApiKey] = useState(() => localStorage.getItem("byok_key") || "");
  const [byokValidated, setByokValidated] = useState(false);
  const [byokValidating, setByokValidating] = useState(false);

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
      showToast("success", "Paper saved to library");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to save paper";
      showToast("error", msg);
    }
  };

  const handleAddNote = async (content: string, tags: string[], paperId?: string) => {
    try {
      await mcpAddNote(content, tags, paperId);
      showToast("success", "Note saved");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to save note";
      showToast("error", msg);
    }
  };

  const handleValidateKey = async () => {
    if (!apiKey.trim()) {
      showToast("error", "Enter an API key first");
      return;
    }
    setByokValidating(true);
    try {
      const result = await validateApiKey(provider, apiKey);
      if (result.valid) {
        localStorage.setItem("byok_key", apiKey);
        localStorage.setItem("byok_provider", provider);
        setByokValidated(true);
        showToast("success", `Key validated for ${result.provider} (${result.model})`);
      } else {
        setByokValidated(false);
        showToast("error", result.error || "Invalid API key");
      }
    } catch (err) {
      setByokValidated(false);
      const msg = err instanceof Error ? err.message : "Validation failed";
      showToast("error", msg);
    } finally {
      setByokValidating(false);
    }
  };

  const handleClearKey = () => {
    setApiKey("");
    setByokValidated(false);
    localStorage.removeItem("byok_key");
    localStorage.removeItem("byok_provider");
    showToast("info", "API key cleared — using server default");
  };

  const handleProviderChange = (p: string) => {
    setProvider(p);
    setByokValidated(false);
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
            onProviderChange={handleProviderChange}
            apiKey={apiKey}
            onApiKeyChange={(k) => { setApiKey(k); setByokValidated(false); }}
            byokValidated={byokValidated}
            byokValidating={byokValidating}
            onValidateKey={handleValidateKey}
            onClearKey={handleClearKey}
            hasMore={hasMore}
            onLoadMore={() => loadMore()}
            loadingMore={loadingMore}
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
