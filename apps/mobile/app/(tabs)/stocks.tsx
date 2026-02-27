import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useRouter } from 'expo-router';
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  FlatList,
  Pressable,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import {
  addWatchItem,
  getSignals,
  getWatchlist,
  removeWatchItem,
  reorderWatchlist,
  toggleWatchlistFavorite,
  type SignalItem,
  type WatchItem,
} from '@/lib/stocks';
import {
  color,
  disclosure,
  fontSize,
  fontWeight,
  radius,
  signal,
  space,
  surface,
  text,
} from '@/theme/tokens';

const MAX_ITEMS = 10;

function SignalBadge({ signal: s }: { signal: 'buy' | 'sell' | 'hold' }) {
  const labels = { buy: '매수 후보', sell: '매도 고려', hold: '홀딩' };
  const colors = { buy: signal.buy, sell: signal.sell, hold: signal.hold };
  const icons = { buy: 'arrow-up', sell: 'arrow-down', hold: 'minus' } as const;
  return (
    <View style={[styles.badge, { backgroundColor: colors[s] + '20' }]}>
      <FontAwesome name={icons[s]} size={12} color={colors[s]} />
      <Text style={[styles.badgeText, { color: colors[s] }]}>{labels[s]}</Text>
    </View>
  );
}

function DisclosureChip({
  sentiment,
}: {
  sentiment: 'positive' | 'neutral' | 'negative' | null;
}) {
  if (!sentiment) return null;
  const labels = { positive: '긍정', neutral: '중립', negative: '부정' };
  const colors = disclosure;
  const c = colors[sentiment];
  return (
    <View style={[styles.chip, { backgroundColor: c + '20' }]}>
      <Text style={[styles.chipText, { color: c }]}>{labels[sentiment]}</Text>
    </View>
  );
}

export default function StocksScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [watchlist, setWatchlist] = useState<WatchItem[]>([]);
  const [signals, setSignals] = useState<SignalItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    setError(null);
    try {
      const [list, sig] = await Promise.all([getWatchlist(token), getSignals(token)]);
      setWatchlist(list);
      setSignals(sig);
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '불러오기 실패';
      setError(msg);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => {
    load();
  }, [load]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    load();
  }, [load]);

  const onRemove = useCallback(
    (item: WatchItem) => {
      if (!token) return;
      Alert.alert('종목 제거', `${item.itms_nm || item.srtn_cd}을(를) 목록에서 제거할까요?`, [
        { text: '취소', style: 'cancel' },
        {
          text: '제거',
          style: 'destructive',
          onPress: async () => {
            try {
              await removeWatchItem(token, item.id);
              setWatchlist((prev) => prev.filter((w) => w.id !== item.id));
              setSignals((prev) => prev.filter((s) => s.corp_code !== item.corp_code));
            } catch {
              setError('제거 실패');
            }
          },
        },
      ]);
    },
    [token]
  );

  const onToggleFavorite = useCallback(
    async (item: WatchItem) => {
      if (!token) return;
      try {
        const updated = await toggleWatchlistFavorite(token, item.id);
        setWatchlist((prev) =>
          prev.map((w) => (w.id === item.id ? { ...w, is_favorite: updated.is_favorite } : w))
        );
      } catch {
        setError('즐겨찾기 변경 실패');
      }
    },
    [token]
  );

  const sigByCorp = useMemo(
    () => Object.fromEntries(signals.map((s) => [s.corp_code, s])),
    [signals]
  );

  if (!token) return null;
  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={color.primary[500]} />
      </View>
    );
  }

  return (
    <View style={styles.page}>
      {error ? (
        <View style={styles.errorBar}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      ) : null}
      <FlatList
        data={watchlist}
        keyExtractor={(w) => w.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[color.primary[500]]} />
        }
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          <View style={styles.empty}>
            <FontAwesome name="line-chart" size={40} color={color.neutral[300]} style={styles.emptyIcon} />
            <Text style={styles.emptyText}>감시종목을 추가해 보세요.</Text>
            <Text style={styles.emptySub}>최대 10종목까지 등록할 수 있습니다.</Text>
            <Pressable
              style={({ pressed }) => [styles.emptyButton, pressed && styles.emptyButtonPressed]}
              onPress={() => router.push('/(tabs)/search' as any)}
            >
              <FontAwesome name="search" size={14} color={text.inverse} />
              <Text style={styles.emptyButtonText}>종목 검색하러 가기</Text>
            </Pressable>
          </View>
        }
        renderItem={({ item }) => {
          const sig = sigByCorp[item.corp_code];
          return (
            <Pressable
              style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
              onPress={() =>
                router.push({
                  pathname: '/stock/[corpCode]',
                  params: { corpCode: item.corp_code },
                })
              }
              accessibilityLabel={`${item.itms_nm || item.srtn_cd}, ${sig ? sig.signal : 'hold'} 신호`}
            >
              <View style={styles.cardRow}>
                <Pressable
                  onPress={() => onToggleFavorite(item)}
                  style={styles.star}
                  accessibilityLabel={item.is_favorite ? '즐겨찾기 해제' : '즐겨찾기'}
                >
                  <FontAwesome
                    name={item.is_favorite ? 'star' : 'star-o'}
                    size={20}
                    color={item.is_favorite ? color.warning[500] : text.tertiary}
                  />
                </Pressable>
                <View style={styles.cardBody}>
                  <Text style={styles.name} numberOfLines={1}>
                    {item.itms_nm || item.srtn_cd}
                  </Text>
                  <View style={styles.badges}>
                    {sig ? <SignalBadge signal={sig.signal} /> : null}
                    {sig?.disclosure_sentiment ? (
                      <DisclosureChip sentiment={sig.disclosure_sentiment} />
                    ) : null}
                  </View>
                  {sig?.last_close != null ? (
                    <Text style={styles.close}>
                      종가 {sig.last_close.toLocaleString()} {sig.last_bas_dt ? `(${sig.last_bas_dt})` : ''}
                    </Text>
                  ) : null}
                </View>
                <FontAwesome name="chevron-right" size={14} color={text.tertiary} />
              </View>
            </Pressable>
          );
        }}
      />
      <View style={styles.footer}>
        <Text style={styles.footerText}>
          {watchlist.length} / {MAX_ITEMS} 종목
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: color.neutral[50] },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorBar: { padding: space[2], backgroundColor: color.error[500] + '20' },
  errorText: { color: color.error[700], fontSize: fontSize.sm },
  listContent: { padding: space[4], paddingBottom: space[8] },
  empty: { padding: space[8], alignItems: 'center' },
  emptyIcon: { marginBottom: space[4] },
  emptyText: { fontSize: fontSize.lg, color: text.secondary, marginBottom: space[2], fontWeight: fontWeight.semibold },
  emptySub: { fontSize: fontSize.sm, color: text.tertiary, marginBottom: space[5] },
  emptyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space[2],
    paddingHorizontal: space[5],
    paddingVertical: 12,
    borderRadius: radius.md,
    backgroundColor: color.primary[500],
  },
  emptyButtonPressed: { opacity: 0.85 },
  emptyButtonText: { color: text.inverse, fontWeight: fontWeight.semibold, fontSize: fontSize.sm },
  card: {
    backgroundColor: surface.canvas,
    borderRadius: radius.md,
    padding: space[4],
    marginBottom: space[3],
    borderWidth: 1,
    borderColor: color.neutral[200],
  },
  cardPressed: { opacity: 0.9 },
  cardRow: { flexDirection: 'row', alignItems: 'center' },
  star: { padding: space[2], marginRight: space[2] },
  cardBody: { flex: 1, minWidth: 0 },
  name: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, color: text.primary },
  badges: { flexDirection: 'row', alignItems: 'center', gap: space[2], marginTop: space[2] },
  badge: { flexDirection: 'row', alignItems: 'center', gap: space[1], paddingHorizontal: space[2], paddingVertical: space[1], borderRadius: radius.sm },
  badgeText: { fontSize: fontSize.xs, fontWeight: fontWeight.medium },
  chip: { paddingHorizontal: space[2], paddingVertical: space[1], borderRadius: radius.sm },
  chipText: { fontSize: fontSize.xs },
  close: { fontSize: fontSize.xs, color: text.tertiary, marginTop: space[1] },
  footer: { padding: space[2], alignItems: 'center', borderTopWidth: 1, borderColor: color.neutral[200], backgroundColor: surface.canvas },
  footerText: { fontSize: fontSize.sm, color: text.tertiary },
});
