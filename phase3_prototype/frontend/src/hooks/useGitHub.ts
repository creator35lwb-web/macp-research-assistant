import { useCallback, useState } from "react";
import { githubRepos, githubConnect, githubSync, githubStatus } from "../api/client";
import type { GitHubRepo } from "../api/types";

export function useGitHub() {
  const [repos, setRepos] = useState<GitHubRepo[]>([]);
  const [connected, setConnected] = useState(false);
  const [connectedRepo, setConnectedRepo] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = useCallback(async () => {
    try {
      const data = await githubStatus();
      setConnected(data.connected);
      setConnectedRepo(data.repo);
    } catch {
      // Not logged in or error
    }
  }, []);

  const fetchRepos = useCallback(async () => {
    setLoading(true);
    try {
      const data = await githubRepos();
      setRepos(data.repos);
    } catch {
      setRepos([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const connect = useCallback(async (repo: string) => {
    setLoading(true);
    try {
      await githubConnect(repo);
      setConnected(true);
      setConnectedRepo(repo);
    } finally {
      setLoading(false);
    }
  }, []);

  const sync = useCallback(async () => {
    setLoading(true);
    try {
      return await githubSync();
    } finally {
      setLoading(false);
    }
  }, []);

  return { repos, connected, connectedRepo, loading, fetchStatus, fetchRepos, connect, sync };
}
