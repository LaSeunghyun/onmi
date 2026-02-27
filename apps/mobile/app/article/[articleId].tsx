import { useLocalSearchParams } from 'expo-router';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { ArticleDetail, getArticle } from '@/lib/report';
import { color, fontSize, fontWeight, lineHeight, radius, space, surface, text } from '@/theme/tokens';

export default function ArticleDetailScreen() {
  const { token } = useAuth();
  const { articleId } = useLocalSearchParams<{ articleId: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ArticleDetail | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      if (!token || !articleId) return;
      setLoading(true);
      setError(null);
      try {
        const res = await getArticle(token, articleId);
        if (!cancelled) setData(res);
      } catch (e) {
        const msg =
          typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '상세를 불러오지 못했습니다.';
        if (!cancelled) setError(msg);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    run();
    return () => {
      cancelled = true;
    };
  }, [token, articleId]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator />
      </View>
    );
  }

  if (error || !data) {
    return (
      <View style={styles.center}>
        <Text style={styles.error}>{error ?? '데이터가 없습니다.'}</Text>
      </View>
    );
  }

  return (
    <View style={styles.page}>
      <Text style={styles.title}>{data.title}</Text>
      <Text style={styles.meta}>
        {(data.source_name ?? '출처 미상') + (data.published_at ? ` · ${data.published_at}` : '')}
      </Text>
      {data.sentiment ? <Text style={styles.senti}>감성: {data.sentiment}</Text> : null}
      {data.translation_status && data.translation_status !== 'not_needed' ? (
        <Text style={styles.note}>원문 기반 요약/분류 후 번역된 내용입니다.</Text>
      ) : null}

      <Text style={styles.body}>{data.summary_ko ?? ''}</Text>

      <Pressable style={styles.button} onPress={() => Linking.openURL(data.original_url)}>
        <Text style={styles.buttonText}>원문 보기</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: surface.canvas, padding: space[4] },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  title: { fontSize: fontSize.lg, fontWeight: fontWeight.bold, color: text.primary },
  meta: { marginTop: 8, color: text.tertiary },
  senti: { marginTop: 8, color: text.secondary },
  note: { marginTop: 8, color: text.tertiary },
  body: { marginTop: 16, fontSize: fontSize.sm, lineHeight: lineHeight.lg, color: text.secondary },
  button: {
    marginTop: 18,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: color.primary[500],
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: { color: text.inverse, fontWeight: fontWeight.bold },
  error: { color: color.error[700] },
});

