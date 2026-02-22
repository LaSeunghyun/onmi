import { apiRequest } from '@/lib/api';

export type WatchItem = {
  id: string;
  corp_code: string;
  srtn_cd: string;
  itms_nm: string | null;
  sort_order: number;
  is_favorite: boolean;
  created_at: string;
};

export type SignalRule = {
  stop_loss_pct: number | null;
  take_profit_pct: number | null;
  ema_slope_threshold: number;
  volume_ratio_on: boolean;
  volume_ratio_multiplier: number;
  push_enabled: boolean;
};

export type SignalItem = {
  corp_code: string;
  srtn_cd: string;
  itms_nm: string | null;
  signal: 'buy' | 'sell' | 'hold';
  reasons: string[];
  last_close: number | null;
  last_bas_dt: string | null;
  disclosure_sentiment: 'positive' | 'neutral' | 'negative' | null;
  disclosure_summary: string | null;
};

export async function getWatchlist(token: string): Promise<WatchItem[]> {
  return apiRequest<WatchItem[]>('/stocks/watchlist', { token });
}

export async function addWatchItem(
  token: string,
  body: { corp_code: string; srtn_cd: string; itms_nm?: string }
): Promise<WatchItem> {
  return apiRequest<WatchItem>('/stocks/watchlist', {
    method: 'POST',
    token,
    body,
  });
}

export async function removeWatchItem(token: string, itemId: string): Promise<void> {
  await apiRequest(`/stocks/watchlist/${itemId}`, { method: 'DELETE', token });
}

export async function reorderWatchlist(
  token: string,
  orderedIds: string[]
): Promise<WatchItem[]> {
  return apiRequest<WatchItem[]>('/stocks/watchlist/reorder', {
    method: 'PATCH',
    token,
    body: { ordered_ids: orderedIds },
  });
}

export async function toggleWatchlistFavorite(
  token: string,
  itemId: string
): Promise<WatchItem> {
  return apiRequest<WatchItem>(`/stocks/watchlist/${itemId}/favorite`, {
    method: 'PATCH',
    token,
  });
}

export async function getSignalRules(token: string): Promise<SignalRule> {
  return apiRequest<SignalRule>('/stocks/rules', { token });
}

export async function updateSignalRules(
  token: string,
  body: Partial<SignalRule>
): Promise<SignalRule> {
  return apiRequest<SignalRule>('/stocks/rules', {
    method: 'PUT',
    token,
    body,
  });
}

export async function getSignals(token: string): Promise<SignalItem[]> {
  return apiRequest<SignalItem[]>('/stocks/signals', { token });
}

/** 종목명 검색 (고유번호·종목코드 반환) */
export type CorpSearchItem = {
  corp_code: string;
  corp_name: string;
  stock_code: string;
};

export async function searchStocks(
  token: string,
  q: string,
  limit?: number
): Promise<CorpSearchItem[]> {
  const params = new URLSearchParams({ q: q.trim() });
  if (limit != null) params.set('limit', String(limit));
  return apiRequest<CorpSearchItem[]>(`/stocks/search?${params.toString()}`, { token });
}
