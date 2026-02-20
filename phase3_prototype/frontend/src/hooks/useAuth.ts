import { useCallback, useEffect, useState } from "react";
import { getMe, logout as apiLogout } from "../api/client";
import type { User } from "../api/types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const data = await getMe();
      setUser(data.user);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  const loginUrl = `${import.meta.env.VITE_API_BASE || "http://localhost:8000"}/api/auth/github`;

  return { user, loading, logout, loginUrl, refetch: fetchUser };
}
