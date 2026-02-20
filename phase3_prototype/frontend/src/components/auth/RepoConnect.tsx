import { useEffect, useState } from "react";
import type { GitHubRepo } from "../../api/types";

interface RepoConnectProps {
  repos: GitHubRepo[];
  connected: boolean;
  connectedRepo: string | null;
  loading: boolean;
  onFetchRepos: () => void;
  onConnect: (repo: string) => void;
  onSync: () => void;
}

export function RepoConnect({
  repos, connected, connectedRepo, loading,
  onFetchRepos, onConnect, onSync,
}: RepoConnectProps) {
  const [showList, setShowList] = useState(false);

  useEffect(() => {
    if (showList && repos.length === 0) {
      onFetchRepos();
    }
  }, [showList, repos.length, onFetchRepos]);

  if (connected && connectedRepo) {
    return (
      <div className="github-section">
        <div className="github-connected">
          <span style={{ color: "var(--color-success)" }}>&#9679;</span>
          <span>Connected</span>
        </div>
        <div className="github-connected">
          <span className="repo-name">{connectedRepo}</span>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={onSync} disabled={loading} style={{ marginTop: 4 }}>
          {loading ? "Syncing..." : "Sync"}
        </button>
      </div>
    );
  }

  return (
    <div className="github-section">
      <button
        className="btn btn-secondary btn-sm"
        onClick={() => setShowList(!showList)}
        style={{ width: "100%" }}
      >
        Connect Repository
      </button>
      {showList && (
        <div style={{ marginTop: 8, maxHeight: 200, overflowY: "auto" }}>
          {loading && <div style={{ fontSize: 12, color: "var(--text-tertiary)" }}>Loading...</div>}
          {repos.map((r) => (
            <button
              key={r.full_name}
              className="btn btn-ghost btn-sm"
              style={{ width: "100%", justifyContent: "flex-start", fontSize: 12 }}
              onClick={() => onConnect(r.full_name)}
            >
              {r.name} {r.private && "(private)"}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
