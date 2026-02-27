import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useFocusEffect, useRouter } from 'expo-router';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { addDays, formatKstLabel, toKstDateString } from '@/lib/date';
import { getReport, ReportItem, ReportResponse } from '@/lib/report';
import { color, border, fontSize, fontWeight, radius, space, surface, text } from '@/theme/tokens';

export default function ReportScreen() {
  const { token, consumePendingReportDateKst } = useAuth();
  const router = useRouter();
  const [today, setToday] = useState(() => toKstDateString(new Date()));
  const [dateKst, setDateKst] = useState(today);

  // 화면 포커스 시 날짜가 바뀌었으면 today를 갱신
  useFocusEffect(
    useCallback(() => {
      const now = toKstDateString(new Date());
      if (now !== today) {
        setToday(now);
        setDateKst(now);
      }
    }, [today])
  );
  const [selectedKeywordId, setSelectedKeywordId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ReportResponse | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const res = await getReport(token, dateKst, selectedKeywordId);
      setData(res);
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '리포트를 불러오지 못했습니다.';
      setError(msg);
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [token, dateKst, selectedKeywordId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!token) return;
    const pending = consumePendingReportDateKst();
    if (pending) {
      setSelectedKeywordId(null);
      setDateKst(pending);
    }
  }, [token, consumePendingReportDateKst]);

  const keywordCount = data?.keywords.length ?? 0;
  const issueCount = data?.total_articles ?? 0;

  return (
    <View style={styles.page}>
      <View style={styles.headerPad} />

      <View style={styles.dateRow}>
        <Pressable
          style={styles.iconButton}
          onPress={() => setDateKst((d) => addDays(d, -1))}
          accessibilityLabel="이전 날짜"
        >
          <FontAwesome name="chevron-left" size={16} color={text.primary} />
        </Pressable>

        <Pressable
          style={styles.dateButton}
          onPress={() => setSelectedKeywordId(null)}
          accessibilityLabel="날짜"
        >
          <FontAwesome name="calendar" size={16} color={text.primary} />
          <Text style={styles.dateText}>{formatKstLabel(dateKst)}</Text>
          {dateKst === today ? <Text style={styles.today}>오늘</Text> : null}
        </Pressable>

        <Pressable
          style={[styles.iconButton, dateKst === today && styles.disabled]}
          onPress={() => setDateKst((d) => addDays(d, 1))}
          disabled={dateKst === today}
          accessibilityLabel="다음 날짜"
        >
          <FontAwesome name="chevron-right" size={16} color={text.primary} />
        </Pressable>
      </View>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>오늘의 요약</Text>
        <Text style={styles.summaryDesc}>
          {keywordCount}개의 키워드에 대한 {issueCount}개의 이슈를 발견했습니다
        </Text>
        {error ? <Text style={styles.errorText}>{error}</Text> : null}
      </View>

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.chips}
      >
        <Pressable
          style={[styles.chip, selectedKeywordId === null && styles.chipActive]}
          onPress={() => setSelectedKeywordId(null)}
        >
          <Text style={[styles.chipText, selectedKeywordId === null && styles.chipTextActive]}>전체</Text>
          <View style={[styles.badge, selectedKeywordId === null ? styles.badgeActive : styles.badgeInactive]}>
            <Text style={[styles.badgeText, selectedKeywordId === null ? styles.badgeTextActive : styles.badgeTextInactive]}>
              {issueCount}
            </Text>
          </View>
        </Pressable>

        {(data?.keywords ?? []).map((k) => (
          <Pressable
            key={k.id}
            style={[styles.chip, selectedKeywordId === k.id && styles.chipActiveAlt]}
            onPress={() => setSelectedKeywordId(k.id)}
          >
            <Text style={styles.chipTextAlt}>{k.text}</Text>
            <View style={styles.badgeInactive}>
              <Text style={styles.badgeTextInactive}>{k.count}</Text>
            </View>
          </Pressable>
        ))}
      </ScrollView>

      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      ) : !data || data.items.length === 0 ? (
        <View style={styles.center}>
          <Text style={styles.emptyTitle}>오늘은 관련 뉴스가 없어요</Text>
          <Text style={styles.emptyDesc}>키워드나 날짜를 바꿔보세요.</Text>
          <Pressable style={styles.retry} onPress={load}>
            <Text style={styles.retryText}>새로고침</Text>
          </Pressable>
        </View>
      ) : (
        <FlatList
          data={data.items}
          keyExtractor={(it) => it.article_id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <ArticleCard
              item={item}
              onPress={() =>
                router.push({
                  pathname: '/article/[articleId]',
                  params: { articleId: item.article_id },
                })
              }
            />
          )}
          refreshing={loading}
          onRefresh={load}
        />
      )}
    </View>
  );
}

function sentimentLabel(s: string | null) {
  if (!s) return { text: '처리중', icon: 'clock-o' as const };
  if (s === 'positive') return { text: '긍정', icon: 'thumbs-up' as const };
  if (s === 'negative') return { text: '부정', icon: 'thumbs-down' as const };
  return { text: '중립', icon: 'minus' as const };
}

function ArticleCard({ item, onPress }: { item: ReportItem; onPress: () => void }) {
  const senti = sentimentLabel(item.sentiment);
  return (
    <Pressable style={styles.card} onPress={onPress}>
      <View style={styles.cardTopRow}>
        {item.keyword_text ? (
          <View style={styles.keywordPill}>
            <Text style={styles.keywordPillText}>{item.keyword_text}</Text>
          </View>
        ) : null}
        <View style={styles.sentiRow}>
          <FontAwesome name={senti.icon} size={14} color={text.tertiary} />
          <Text style={styles.sentiText}>{senti.text}</Text>
        </View>
      </View>

      <Text style={styles.cardTitle} numberOfLines={2}>
        {item.title}
      </Text>

      <Text style={styles.cardMeta} numberOfLines={1}>
        {item.source_name ?? '출처 미상'}
        {item.translation_status && item.translation_status !== 'not_needed' ? ' · 번역됨' : ''}
      </Text>

      {item.summary_ko ? (
        <Text style={styles.cardBody} numberOfLines={3}>
          {item.summary_ko}
        </Text>
      ) : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: surface.canvas },
  headerPad: { height: 6 },
  dateRow: { flexDirection: 'row', alignItems: 'center', gap: space[2], paddingHorizontal: space[3], paddingTop: 10 },
  iconButton: {
    width: 32,
    height: 32,
    borderRadius: radius.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: border.hairline,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: surface.canvas,
  },
  disabled: { opacity: 0.5 },
  dateButton: {
    flex: 1,
    height: 36,
    borderRadius: radius.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: border.hairline,
    backgroundColor: surface.canvas,
    flexDirection: 'row',
    alignItems: 'center',
    gap: space[2],
    paddingHorizontal: space[3],
  },
  dateText: { flex: 1, color: text.primary, fontWeight: fontWeight.semibold },
  today: { color: color.primary[500], fontWeight: fontWeight.semibold },
  summaryCard: {
    marginTop: space[3],
    marginHorizontal: space[3],
    borderRadius: radius.lg,
    backgroundColor: color.primary[500],
    padding: space[4],
  },
  summaryTitle: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, color: text.inverse },
  summaryDesc: { marginTop: 6, color: color.primary[100] },
  errorText: { marginTop: 8, color: text.inverse },
  chips: { paddingHorizontal: space[3], paddingVertical: space[3], gap: space[2] },
  chip: {
    height: 32,
    paddingHorizontal: space[3],
    borderRadius: radius.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: border.hairline,
    backgroundColor: surface.canvas,
    flexDirection: 'row',
    alignItems: 'center',
    gap: space[2],
  },
  chipActive: { backgroundColor: color.primary[500], borderColor: 'transparent' },
  chipActiveAlt: { borderColor: color.primary[500], backgroundColor: color.primary[50] },
  chipText: { color: text.inverse, fontWeight: fontWeight.semibold },
  chipTextActive: { color: text.inverse },
  chipTextAlt: { color: text.primary, fontWeight: fontWeight.semibold },
  badge: { height: 22, minWidth: 24, paddingHorizontal: space[2], borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center' },
  badgeActive: { backgroundColor: surface.canvas },
  badgeInactive: { height: 22, minWidth: 24, paddingHorizontal: space[2], borderRadius: radius.sm, backgroundColor: color.neutral[100], alignItems: 'center', justifyContent: 'center' },
  badgeText: { fontSize: fontSize.xs, fontWeight: fontWeight.extrabold },
  badgeTextActive: { color: text.secondary },
  badgeTextInactive: { color: text.tertiary },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: space[6] },
  emptyTitle: { fontSize: fontSize.base, fontWeight: fontWeight.bold, color: text.primary },
  emptyDesc: { marginTop: 6, color: text.tertiary },
  retry: { marginTop: 12, paddingHorizontal: 14, paddingVertical: 10, borderRadius: radius.md, backgroundColor: color.neutral[100] },
  retryText: { color: text.primary, fontWeight: fontWeight.semibold },
  list: { paddingHorizontal: space[3], paddingBottom: space[6], gap: space[3] },
  card: {
    borderRadius: radius.lg,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: border.hairline,
    backgroundColor: surface.canvas,
    padding: space[4],
  },
  cardTopRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  keywordPill: { backgroundColor: color.primary[500], paddingHorizontal: space[3], paddingVertical: space[1], borderRadius: radius.sm },
  keywordPillText: { color: text.inverse, fontSize: fontSize.xs, fontWeight: fontWeight.bold },
  sentiRow: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  sentiText: { color: text.tertiary, fontSize: fontSize.xs },
  cardTitle: { marginTop: 10, fontSize: fontSize.base, fontWeight: fontWeight.bold, color: text.primary },
  cardMeta: { marginTop: 6, fontSize: fontSize.xs, color: text.tertiary },
  cardBody: { marginTop: 10, fontSize: fontSize.sm, color: text.secondary, lineHeight: 20 },
});
