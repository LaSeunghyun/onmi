import { apiRequest } from '@/lib/api';

export type KeywordCount = {
  id: string;
  text: string;
  is_pinned: boolean;
  count: number;
};

export type ReportItem = {
  article_id: string;
  keyword_id: string | null;
  keyword_text: string | null;
  title: string;
  source_name: string | null;
  published_at: string | null;
  sentiment: string | null;
  summary_ko: string | null;
  translation_status: string | null;
  original_url: string;
};

export type ReportResponse = {
  date_kst: string;
  keywords: KeywordCount[];
  total_articles: number;
  items: ReportItem[];
};

export type ArticleDetail = {
  id: string;
  title: string;
  source_name: string | null;
  published_at: string | null;
  original_url: string;
  keyword_texts: string[];
  sentiment: string | null;
  summary_ko: string | null;
  translation_status: string | null;
};

export async function getReport(token: string, dateKst: string, keywordId?: string | null) {
  const params = new URLSearchParams({ date_kst: dateKst });
  if (keywordId) params.set('keyword_id', keywordId);
  return await apiRequest<ReportResponse>(`/report?${params.toString()}`, { token });
}

export async function getArticle(token: string, articleId: string) {
  return await apiRequest<ArticleDetail>(`/articles/${articleId}`, { token });
}

