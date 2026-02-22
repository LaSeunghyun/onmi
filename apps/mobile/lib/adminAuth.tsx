import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { adminChangePassword, adminLogin, adminMe, type AdminMe } from '@/lib/admin';
import { deleteStoredValue, getStoredValue, setStoredValue } from '@/lib/storage';

const ADMIN_TOKEN_KEY = 'touch.admin.accessToken';

type AdminAuthContextValue = {
  loading: boolean;
  token: string | null;
  admin: AdminMe | null;
  signIn: (adminId: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
};

const AdminAuthContext = createContext<AdminAuthContextValue | null>(null);

export function AdminAuthProvider({ children }: { children: React.ReactNode }) {
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [admin, setAdmin] = useState<AdminMe | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function boot() {
      try {
        const stored = await getStoredValue(ADMIN_TOKEN_KEY);
        if (cancelled) return;
        if (!stored) return;
        setToken(stored);
        const me = await adminMe(stored);
        if (!cancelled) setAdmin(me);
      } catch {
        await deleteStoredValue(ADMIN_TOKEN_KEY);
        if (!cancelled) {
          setToken(null);
          setAdmin(null);
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

  const value = useMemo<AdminAuthContextValue>(
    () => ({
      loading,
      token,
      admin,
      async signIn(adminId: string, password: string) {
        const resp = await adminLogin(adminId, password);
        await setStoredValue(ADMIN_TOKEN_KEY, resp.access_token);
        setToken(resp.access_token);
        const me = await adminMe(resp.access_token);
        setAdmin(me);
      },
      async signOut() {
        await deleteStoredValue(ADMIN_TOKEN_KEY);
        setToken(null);
        setAdmin(null);
      },
      async refresh() {
        if (!token) return;
        const me = await adminMe(token);
        setAdmin(me);
      },
      async changePassword(currentPassword: string, newPassword: string) {
        if (!token) throw new Error('no admin token');
        await adminChangePassword(token, currentPassword, newPassword);
        const me = await adminMe(token);
        setAdmin(me);
      },
    }),
    [loading, token, admin]
  );

  return <AdminAuthContext.Provider value={value}>{children}</AdminAuthContext.Provider>;
}

export function useAdminAuth() {
  const ctx = useContext(AdminAuthContext);
  if (!ctx) throw new Error('useAdminAuth must be used within AdminAuthProvider');
  return ctx;
}
