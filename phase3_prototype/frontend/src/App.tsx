import { useState } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000";

interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  url: string;
  status: string;
}

interface Analysis {
  summary: string;
  key_insights: string[];
  methodology: string;
  relevance_tags: string[];
  research_gaps: string[];
  strength_score: number;
  _meta?: {
    bias_disclaimer: string;
    provider: string;
    model: string;
  };
}

function App() {
  const [query, setQuery] = useState("");
  const [papers, setPapers] = useState<Paper[]>([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState("");

  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [analyses, setAnalyses] = useState<Record<string, Analysis>>({});
  const [analyzeError, setAnalyzeError] = useState("");

  const [provider, setProvider] = useState("gemini");
  const [apiKey, setApiKey] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setSearchError("");
    setPapers([]);
    try {
      const res = await fetch(`${API_BASE}/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: query.trim(), limit: 10, source: "hysts" }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || res.statusText);
      }
      const data = await res.json();
      setPapers(data.results || []);
    } catch (e: unknown) {
      setSearchError(e instanceof Error ? e.message : "Search failed");
    } finally {
      setSearching(false);
    }
  };

  const handleAnalyze = async (paperId: string) => {
    setAnalyzingId(paperId);
    setAnalyzeError("");
    try {
      const body: Record<string, string> = { paper_id: paperId, provider };
      if (apiKey.trim()) body.api_key = apiKey.trim();

      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || res.statusText);
      }
      const data = await res.json();
      setAnalyses((prev) => ({ ...prev, [paperId]: data.analysis }));
    } catch (e: unknown) {
      setAnalyzeError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setAnalyzingId(null);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>MACP Research Assistant</h1>
        <p className="subtitle">Phase 3A WebMCP Prototype</p>
      </header>

      <section className="config-section">
        <label>
          Provider:
          <select value={provider} onChange={(e) => setProvider(e.target.value)}>
            <option value="gemini">Google Gemini (free tier)</option>
            <option value="anthropic">Anthropic Claude</option>
            <option value="openai">OpenAI</option>
          </select>
        </label>
        <label>
          API Key (BYOK):
          <input
            type="password"
            placeholder="Leave blank to use env var"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        </label>
      </section>

      <section className="search-section">
        <div className="search-bar">
          <input
            type="text"
            placeholder="Search papers (e.g., multi-agent systems, LLM reasoning)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch} disabled={searching || !query.trim()}>
            {searching ? "Searching..." : "Search"}
          </button>
        </div>
        {searchError && <p className="error">{searchError}</p>}
      </section>

      <section className="results-section">
        {papers.length > 0 && <h2>Results ({papers.length} papers)</h2>}
        {papers.map((paper) => (
          <div key={paper.id} className="paper-card">
            <div className="paper-header">
              <h3>{paper.title}</h3>
              <span className={`status-badge status-${paper.status}`}>
                {paper.status}
              </span>
            </div>
            <p className="paper-meta">
              <strong>ID:</strong> <code>{paper.id}</code>
              {paper.authors.length > 0 && (
                <>
                  {" | "}
                  <strong>Authors:</strong>{" "}
                  {paper.authors.slice(0, 3).join(", ")}
                  {paper.authors.length > 3 && "..."}
                </>
              )}
            </p>
            {paper.abstract && (
              <p className="paper-abstract">
                {paper.abstract.length > 300
                  ? paper.abstract.slice(0, 300) + "..."
                  : paper.abstract}
              </p>
            )}
            <div className="paper-actions">
              {paper.url && (
                <a href={paper.url} target="_blank" rel="noopener noreferrer">
                  View on arXiv
                </a>
              )}
              <button
                onClick={() => handleAnalyze(paper.id)}
                disabled={analyzingId === paper.id}
              >
                {analyzingId === paper.id ? "Analyzing..." : "Analyze"}
              </button>
            </div>

            {analyses[paper.id] && (
              <div className="analysis-card">
                <h4>AI Analysis</h4>
                <p>
                  <strong>Summary:</strong> {analyses[paper.id].summary}
                </p>
                {analyses[paper.id].key_insights.length > 0 && (
                  <div>
                    <strong>Key Insights:</strong>
                    <ul>
                      {analyses[paper.id].key_insights.map((insight, i) => (
                        <li key={i}>{insight}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {analyses[paper.id].methodology && (
                  <p>
                    <strong>Methodology:</strong>{" "}
                    {analyses[paper.id].methodology}
                  </p>
                )}
                {analyses[paper.id].research_gaps.length > 0 && (
                  <div>
                    <strong>Research Gaps:</strong>
                    <ul>
                      {analyses[paper.id].research_gaps.map((gap, i) => (
                        <li key={i}>{gap}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <p>
                  <strong>Strength Score:</strong>{" "}
                  <span className="score">
                    {analyses[paper.id].strength_score}/10
                  </span>
                </p>
                {analyses[paper.id].relevance_tags.length > 0 && (
                  <div className="tags">
                    {analyses[paper.id].relevance_tags.map((tag) => (
                      <span key={tag} className="tag">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                {analyses[paper.id]._meta && (
                  <p className="bias-disclaimer">
                    {analyses[paper.id]._meta!.bias_disclaimer}
                    <br />
                    <em>
                      Provider: {analyses[paper.id]._meta!.provider} (
                      {analyses[paper.id]._meta!.model})
                    </em>
                  </p>
                )}
              </div>
            )}
          </div>
        ))}
        {analyzeError && <p className="error">{analyzeError}</p>}
      </section>

      <footer className="footer">
        <p>
          MACP Research Assistant | YSenseAI Ecosystem | GODELAI C-S-P Framework
        </p>
      </footer>
    </div>
  );
}

export default App;
