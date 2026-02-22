import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { apiRequest } from '@/lib/api';
import { deleteStoredValue, getStoredValue, setStoredValue } from '@/lib/storage';

const TOKEN_KEY = 'touch.accessToken';

export type User = {
  id: string;
  email: string;
  auth_provider: string;
  created_at: string;
  updated_at: string;
};

type AuthContextValue = {
  loading: boolean;
  token: string | null;
  user: User | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  setPendingReportDateKst: (dateKst: string) => void;
  consumePendingReportDateKst: () => string | null;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [pendingReportDateKst, setPendingReportDateKst] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function boot() {
      try {
        const stored = await getStoredValue(TOKEN_KEY);
        if (cancelled) return;
        if (!stored) return;

        setToken(stored);
        const me = await apiRequest<User>('/me', { token: stored });
        if (cancelled) return;
        setUser(me);
      } catch {
        await deleteStoredValue(TOKEN_KEY);
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    boot();
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      loading,
      token,
      user,
      async signIn(email, password) {
        const resp = await apiRequest<{ access_token: string }>('/auth/login', {
          method: 'POST',
          body: { email, password },
        });
        await setStoredValue(TOKEN_KEY, resp.access_token);
        setToken(resp.access_token);
        const me = await apiRequest<User>('/me', { token: resp.access_token });
        setUser(me);
      },
      async signUp(email, password) {
        const resp = await apiRequest<{ access_token: string }>('/auth/signup', {
          method: 'POST',
          body: { email, password },
        });
        await setStoredValue(TOKEN_KEY, resp.access_token);
        setToken(resp.access_token);
        const me = await apiRequest<User>('/me', { token: resp.access_token });
        setUser(me);
      },
      async signOut() {
        await deleteStoredValue(TOKEN_KEY);
        setToken(null);
        setUser(null);
      },
      setPendingReportDateKst(dateKst: string) {
        setPendingReportDateKst(dateKst);
      },
      consumePendingReportDateKst() {
        const v = pendingReportDateKst;
        setPendingReportDateKst(null);
        return v;
      },
    }),
    [loading, token, user, pendingReportDateKst]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

