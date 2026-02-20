import { useState } from "react";

interface SearchBarProps {
  onSearch: (query: string, source: string) => void;
  searching: boolean;
}

export function SearchBar({ onSearch, searching }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [source, setSource] = useState("hysts");

  const handleSubmit = () => {
    if (query.trim()) onSearch(query.trim(), source);
  };

  return (
    <div>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search papers (e.g., multi-agent systems, LLM reasoning)"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
        />
        <button className="btn btn-primary" onClick={handleSubmit} disabled={searching || !query.trim()}>
          {searching ? "Searching..." : "Search"}
        </button>
      </div>
      <div className="search-filters" style={{ marginTop: 8 }}>
        {["hysts", "hf", "arxiv"].map((s) => (
          <button
            key={s}
            className={`filter-chip ${source === s ? "active" : ""}`}
            onClick={() => setSource(s)}
          >
            {s === "hysts" ? "Daily Papers" : s === "hf" ? "HuggingFace" : "arXiv ID"}
          </button>
        ))}
      </div>
    </div>
  );
}
