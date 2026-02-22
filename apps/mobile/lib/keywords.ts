import { apiRequest } from '@/lib/api';

export type Keyword = {
  id: string;
  text: string;
  is_active: boolean;
  is_pinned: boolean;
  last_used_at: string | null;
  created_at: string;
  updated_at: string;
};

export async function listKeywords(token: string, q?: string) {
  const qs = q ? `?q=${encodeURIComponent(q)}` : '';
  return await apiRequest<Keyword[]>(`/keywords${qs}`, { token });
}

export async function createKeyword(token: string, text: string) {
  return await apiRequest<Keyword>('/keywords', {
    token,
    method: 'POST',
    body: { text },
  });
}

export async function updateKeyword(
  token: string,
  id: string,
  patch: Partial<Pick<Keyword, 'is_active' | 'is_pinned'>>
) {
  return await apiRequest<Keyword>(`/keywords/${id}`, {
    token,
    method: 'PATCH',
    body: patch,
  });
}

export async function deleteKeyword(token: string, id: string) {
  await apiRequest<void>(`/keywords/${id}`, { token, method: 'DELETE' });
}

