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
import { Button, Card } from '@/components/ui';
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
          <Button label="새로고침" variant="secondary" size="md" onPress={load} style={styles.retry} />
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

const SENTI_CONFIG: Record<string, { label: string; icon: React.ComponentProps<typeof FontAwesome>['name']; bg: string; fg: string }> = {
  positive: { label: '긍정', icon: 'thumbs-up', bg: color.success[600] + '20', fg: color.success[600] },
  negative: { label: '부정', icon: 'thumbs-down', bg: color.error[600] + '20', fg: color.error[600] },
  neutral: { label: '중립', icon: 'minus', bg: color.neutral[200], fg: color.neutral[600] },
};

function SentimentBadge({ sentiment }: { sentiment: string | null }) {
  const cfg = sentiment ? (SENTI_CONFIG[sentiment] ?? null) : null;
  if (!cfg) {
    return (
      <View style={[styles.sentiBadge, { backgroundColor: color.neutral[100] }]}>
        <FontAwesome name="clock-o" size={11} color={color.neutral[500]} />
        <Text style={[styles.sentiBadgeText, { color: color.neutral[500] }]}>처리중</Text>
      </View>
    );
  }
  return (
    <View style={[styles.sentiBadge, { backgroundColor: cfg.bg }]}>
      <FontAwesome name={cfg.icon} size={11} color={cfg.fg} />
      <Text style={[styles.sentiBadgeText, { color: cfg.fg }]}>{cfg.label}</Text>
    </View>
  );
}

function ArticleCard({ item, onPress }: { item: ReportItem; onPress: () => void }) {
  return (
    <Pressable onPress={onPress}>
      <Card style={styles.card}>
        <View style={styles.cardTopRow}>
          {item.keyword_text ? (
            <View style={styles.keywordPill}>
              <Text style={styles.keywordPillText}>{item.keyword_text}</Text>
            </View>
          ) : null}
          <SentimentBadge sentiment={item.sentiment} />
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
      </Card>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: surface.canvas },
  headerPad: { height: 6 },
  dateRow: { flexDirection: 'row', alignItems: 'center', gap: space[2], paddingHorizontal: space[3], paddingTop: 10 },
  iconButton: {
    width: 44,
    height: 44,
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
    backgroundColor: color.primary[50],
    borderWidth: 1,
    borderColor: color.primary[100],
    padding: space[4],
  },
  summaryTitle: { fontSize: fontSize.xl, fontWeight: fontWeight.bold, color: color.primary[700] },
  summaryDesc: { marginTop: 6, color: color.primary[600] },
  errorText: { marginTop: 8, color: color.error[600] },
  chips: { paddingHorizontal: space[3], paddingVertical: space[3], gap: space[2] },
  chip: {
    height: 32,
    paddingHorizontal: space[3],
    borderRadius: radius.sm,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: border.hairline,
    backgroundColor: color.neutral[100],
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
  retry: { marginTop: 12 },
  list: { paddingHorizontal: space[3], paddingBottom: space[6], gap: space[3] },
  card: {},
  cardTopRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  keywordPill: { backgroundColor: color.primary[500], paddingHorizontal: space[3], paddingVertical: space[1], borderRadius: radius.sm },
  keywordPillText: { color: text.inverse, fontSize: fontSize.xs, fontWeight: fontWeight.bold },
  sentiBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, paddingHorizontal: space[2], paddingVertical: 3, borderRadius: radius.sm },
  sentiBadgeText: { fontSize: fontSize.xs, fontWeight: fontWeight.medium },
  cardTitle: { marginTop: 10, fontSize: fontSize.base, fontWeight: fontWeight.bold, color: text.primary },
  cardMeta: { marginTop: 6, fontSize: fontSize.xs, color: text.tertiary },
  cardBody: { marginTop: 10, fontSize: fontSize.sm, color: text.secondary, lineHeight: 20 },
});
