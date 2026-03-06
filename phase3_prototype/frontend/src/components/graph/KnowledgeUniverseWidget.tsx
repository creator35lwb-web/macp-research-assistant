/**
 * KnowledgeUniverseWidget — P4.2 retention hook
 *
 * Shows graph growth stats prominently in the workspace.
 * On repeat visits, shows delta since last session.
 */
import type { GraphStats, GraphDelta } from "../../hooks/useGraphStats";

interface Props {
  stats: GraphStats | null;
  delta: GraphDelta | null;
  loading: boolean;
  onViewGraph: () => void;
}

export function KnowledgeUniverseWidget({ stats, delta, loading, onViewGraph }: Props) {
  if (loading && !stats) {
    return null; // silent load — don't flash a skeleton
  }

  const hasData = stats && (stats.papers > 0 || stats.concepts > 0);
  const hasGrowth = delta && (delta.papers > 0 || delta.concepts > 0 || delta.connections > 0);

  return (
    <div className="knowledge-universe-widget">
      <div className="knowledge-universe-widget__header">
        <span className="knowledge-universe-widget__title">Your Knowledge Universe</span>
        <button
          className="knowledge-universe-widget__cta"
          onClick={onViewGraph}
          type="button"
        >
          View Graph →
        </button>
      </div>

      {hasData ? (
        <>
          <div className="knowledge-universe-widget__stats">
            <span className="ku-stat">
              <span className="ku-stat__value">{stats.papers}</span>
              <span className="ku-stat__label">Papers</span>
            </span>
            <span className="ku-stat__sep">·</span>
            <span className="ku-stat">
              <span className="ku-stat__value">{stats.concepts}</span>
              <span className="ku-stat__label">Concepts</span>
            </span>
            <span className="ku-stat__sep">·</span>
            <span className="ku-stat">
              <span className="ku-stat__value">{stats.methods}</span>
              <span className="ku-stat__label">Methods</span>
            </span>
            <span className="ku-stat__sep">·</span>
            <span className="ku-stat">
              <span className="ku-stat__value">{stats.connections}</span>
              <span className="ku-stat__label">Connections</span>
            </span>
          </div>
          {hasGrowth && (
            <p className="knowledge-universe-widget__delta">
              Welcome back — your graph grew since your last visit:
              {delta.papers > 0 && <span> +{delta.papers} papers</span>}
              {delta.concepts > 0 && <span> · +{delta.concepts} concepts</span>}
              {delta.connections > 0 && <span> · +{delta.connections} connections</span>}
            </p>
          )}
        </>
      ) : (
        <p className="knowledge-universe-widget__empty">
          Start analyzing papers to build your knowledge graph.
        </p>
      )}
    </div>
  );
}
