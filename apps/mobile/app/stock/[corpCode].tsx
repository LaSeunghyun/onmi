import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { getSignals, type SignalItem } from '@/lib/stocks';
import {
  color,
  disclosure,
  fontSize,
  fontWeight,
  radius,
  signal,
  space,
  text,
} from '@/theme/tokens';

export default function StockDetailScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const { corpCode } = useLocalSearchParams<{ corpCode: string }>();
  const [item, setItem] = useState<SignalItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token || !corpCode) return;
    setError(null);
    try {
      const list = await getSignals(token);
      const found = list.find((s) => s.corp_code === corpCode);
      setItem(found ?? null);
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '불러오기 실패';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [token, corpCode]);

  useEffect(() => {
    load();
  }, [load]);

  if (!token || !corpCode) return null;
  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color={color.primary[500]} />
      </View>
    );
  }
  if (error || !item) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>{error || '종목 정보 없음'}</Text>
        <Text style={styles.backLink} onPress={() => router.back()}>
          목록으로
        </Text>
      </View>
    );
  }

  const signalLabels = { buy: '매수 후보', sell: '매도 고려', hold: '홀딩' };
  const signalColors = signal;
  const discLabels = { positive: '긍정', neutral: '중립', negative: '부정' };
  const discColors = disclosure;

  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.content}>
      <View style={styles.block}>
        <Text style={styles.title}>{item.itms_nm || item.srtn_cd}</Text>
        <View style={[styles.badge, { backgroundColor: signalColors[item.signal] + '20' }]}>
          <FontAwesome
            name={item.signal === 'buy' ? 'arrow-up' : item.signal === 'sell' ? 'arrow-down' : 'minus'}
            size={16}
            color={signalColors[item.signal]}
          />
          <Text style={[styles.badgeText, { color: signalColors[item.signal] }]}>
            {signalLabels[item.signal]}
          </Text>
        </View>
      </View>

      <View style={styles.block}>
        <Text style={styles.sectionTitle}>판단 근거</Text>
        {item.reasons.length ? (
          item.reasons.map((r, i) => (
            <Text key={i} style={styles.reason}>
              • {r}
            </Text>
          ))
        ) : (
          <Text style={styles.placeholder}>근거 없음</Text>
        )}
      </View>

      {item.last_close != null && (
        <View style={styles.block}>
          <Text style={styles.sectionTitle}>최근 시세</Text>
          <Text style={styles.body}>
            종가 {item.last_close.toLocaleString()}원
            {item.last_bas_dt ? ` (기준일 ${item.last_bas_dt})` : ''}
          </Text>
        </View>
      )}

      {item.disclosure_sentiment && (
        <View style={styles.block}>
          <Text style={styles.sectionTitle}>공시 감성</Text>
          <View style={[styles.discBadge, { backgroundColor: discColors[item.disclosure_sentiment] + '20' }]}>
            <Text style={[styles.discText, { color: discColors[item.disclosure_sentiment] }]}>
              {discLabels[item.disclosure_sentiment]}
            </Text>
          </View>
          {item.disclosure_summary ? (
            <Text style={styles.body}>{item.disclosure_summary}</Text>
          ) : null}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: color.neutral[50] },
  content: { padding: space[4], paddingBottom: space[8] },
  centered: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  errorText: { color: color.error[600], marginBottom: space[2] },
  backLink: { color: color.primary[600], fontSize: fontSize.sm },
  block: { marginBottom: space[6] },
  title: { fontSize: fontSize['2xl'], fontWeight: fontWeight.bold, color: text.primary },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space[2],
    paddingVertical: space[2],
    paddingHorizontal: space[3],
    borderRadius: radius.md,
    marginTop: space[2],
    alignSelf: 'flex-start',
  },
  badgeText: { fontSize: fontSize.base, fontWeight: fontWeight.semibold },
  sectionTitle: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, color: text.primary, marginBottom: space[2] },
  reason: { fontSize: fontSize.sm, color: text.secondary, marginBottom: space[1] },
  placeholder: { fontSize: fontSize.sm, color: text.tertiary },
  body: { fontSize: fontSize.sm, color: text.secondary },
  discBadge: { alignSelf: 'flex-start', paddingVertical: space[1], paddingHorizontal: space[3], borderRadius: radius.sm, marginBottom: space[2] },
  discText: { fontSize: fontSize.sm, fontWeight: fontWeight.medium },
});
