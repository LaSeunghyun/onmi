import { API_BASE_URL } from '@/lib/config';

export type ApiError = {
  status: number;
  message: string;
};

async function readJsonSafe(res: Response) {
  const text = await res.text();
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export async function apiRequest<T>(
  path: string,
  opts: {
    method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    token?: string | null;
    body?: unknown;
  } = {}
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, {
    method: opts.method ?? 'GET',
    headers: {
      ...(opts.body ? { 'Content-Type': 'application/json' } : {}),
      ...(opts.token ? { Authorization: `Bearer ${opts.token}` } : {}),
    },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });

  if (!res.ok) {
    const data = await readJsonSafe(res);
    const msg =
      (data && typeof data === 'object' && 'detail' in data && (data as any).detail) ||
      (typeof data === 'string' ? data : '요청에 실패했습니다.');
    const err: ApiError = { status: res.status, message: String(msg) };
    throw err;
  }

  const data = (await readJsonSafe(res)) as T;
  return data;
}

