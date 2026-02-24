import type { User } from "../../api/types";
import type { ViewMode } from "../../api/types";
import { LoginButton } from "../auth/LoginButton";
import { UserMenu } from "../auth/UserMenu";
import { RepoConnect } from "../auth/RepoConnect";
import type { GitHubRepo } from "../../api/types";

interface SidebarProps {
  user: User | null;
  loginUrl: string;
  onLogout: () => void;
  activeView: ViewMode;
  onViewChange: (view: ViewMode) => void;
  // GitHub
  repos: GitHubRepo[];
  connected: boolean;
  connectedRepo: string | null;
  githubLoading: boolean;
  onFetchRepos: () => void;
  onConnect: (repo: string) => void;
  onSync: () => void;
}

const NAV_ITEMS: { id: ViewMode; label: string; color: string }[] = [
  { id: "search", label: "Search Papers", color: "var(--color-papers)" },
  { id: "library", label: "My Library", color: "var(--color-papers)" },
  { id: "graph", label: "Knowledge Graph", color: "var(--color-graph)" },
  { id: "notes", label: "Research Notes", color: "var(--color-notes)" },
  { id: "agents", label: "Agent Registry", color: "var(--color-graph)" },
];

export function Sidebar({
  user, loginUrl, onLogout, activeView, onViewChange,
  repos, connected, connectedRepo, githubLoading,
  onFetchRepos, onConnect, onSync,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">MACP Research</span>
      </div>

      {user ? (
        <UserMenu user={user} onLogout={onLogout} />
      ) : (
        <LoginButton loginUrl={loginUrl} />
      )}

      <nav className="sidebar-nav" style={{ marginTop: 16 }}>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeView === item.id ? "active" : ""}`}
            onClick={() => onViewChange(item.id)}
          >
            <span className="nav-dot" style={{ background: item.color }} />
            {item.label}
          </button>
        ))}
      </nav>

      {user && (
        <RepoConnect
          repos={repos}
          connected={connected}
          connectedRepo={connectedRepo}
          loading={githubLoading}
          onFetchRepos={onFetchRepos}
          onConnect={onConnect}
          onSync={onSync}
        />
      )}
    </aside>
  );
}
