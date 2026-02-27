import { MaterialCommunityIcons } from '@expo/vector-icons';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { MiniBarChart, type BarDataItem } from '@/components/admin/MiniBarChart';
import { OverviewList, type OverviewItem } from '@/components/admin/OverviewList';
import { adminListAuditLogs, adminListMembers, adminListModules } from '@/lib/admin';
import { useAdminAuth } from '@/lib/adminAuth';
import { color, fontSize, fontWeight, radius } from '@/theme/tokens';

type MCIconName = React.ComponentProps<typeof MaterialCommunityIcons>['name'];

const TRAFFIC_DATA: BarDataItem[] = [
  { label: '월', value: 45 },
  { label: '화', value: 72 },
  { label: '수', value: 58 },
  { label: '목', value: 91 },
  { label: '금', value: 83 },
  { label: '토', value: 34 },
  { label: '일', value: 28 },
];

const OVERVIEW_ITEMS: OverviewItem[] = [
  {
    icon: 'account-plus-outline',
    iconColor: '#3B82F6',
    iconBg: '#EFF6FF',
    label: '신규 가입 완료',
    sublabel: '2시간 전',
    progress: 92,
    progressColor: '#3B82F6',
  },
  {
    icon: 'shield-check-outline',
    iconColor: '#10B981',
    iconBg: '#ECFDF5',
    label: '보안 인증 갱신',
    sublabel: '5시간 전',
    progress: 68,
    progressColor: '#10B981',
  },
  {
    icon: 'alert-outline',
    iconColor: '#F59E0B',
    iconBg: '#FFFBEB',
    label: 'API 응답 지연 감지',
    sublabel: '어제',
    progress: 44,
    progressColor: '#F59E0B',
  },
  {
    icon: 'database-sync-outline',
    iconColor: '#8B5CF6',
    iconBg: '#F5F3FF',
    label: 'DB 백업 완료',
    sublabel: '2일 전',
    progress: 100,
    progressColor: '#8B5CF6',
  },
];

interface KpiCardDef {
  label: string;
  icon: MCIconName;
  bg: string;
  accent: string;
  textMain: string;
  textSub: string;
  delta: string;
  deltaColor: string;
  getValue: (data: { memberCount: number; moduleCount: number; errorCount: number }) => number;
}

const KPI_CARDS: KpiCardDef[] = [
  {
    label: '전체 회원',
    icon: 'account-group',
    bg: '#EFF6FF',
    accent: '#3B82F6',
    textMain: '#1E40AF',
    textSub: '#60A5FA',
    delta: '▲ 12.4%  Since last week',
    deltaColor: '#16A34A',
    getValue: (d) => d.memberCount,
  },
  {
    label: '활성 모듈',
    icon: 'puzzle',
    bg: '#ECFDF5',
    accent: '#10B981',
    textMain: '#065F46',
    textSub: '#34D399',
    delta: '▲ 2 modules added',
    deltaColor: '#16A34A',
    getValue: (d) => d.moduleCount,
  },
  {
    label: '오류 로그',
    icon: 'alert-circle',
    bg: '#FFFBEB',
    accent: '#F59E0B',
    textMain: '#92400E',
    textSub: '#FBBF24',
    delta: '▼ 3.1%  Resolved',
    deltaColor: '#DC2626',
    getValue: (d) => d.errorCount,
  },
  {
    label: '오늘 접속자',
    icon: 'chart-line',
    bg: '#ECFEFF',
    accent: '#06B6D4',
    textMain: '#155E75',
    textSub: '#22D3EE',
    delta: '▲ 8.7%  Since yesterday',
    deltaColor: '#16A34A',
    getValue: () => 247,
  },
];

export default function AdminDashboardScreen() {
  const { token } = useAdminAuth();
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [memberCount, setMemberCount] = useState(0);
  const [moduleCount, setModuleCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);

  useEffect(() => {
    async function loadStats() {
      if (!token) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setLoadError(null);
      try {
        const [members, modules, logs] = await Promise.all([
          adminListMembers(token),
          adminListModules(token),
          adminListAuditLogs(token),
        ]);
        setMemberCount(members.length);
        setModuleCount(modules.length);
        setErrorCount(logs.filter((l) => l.action_type.includes('error') || l.action_type.includes('fail')).length);
      } catch (e) {
        const msg =
          typeof e === 'object' && e && 'message' in e
            ? String((e as { message: unknown }).message)
            : '데이터 불러오기 실패';
        setLoadError(msg);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, [token]);

  if (loading) {
    return (
      <View style={styles.centerWrap}>
        <ActivityIndicator size="large" color="#3B82F6" />
        <Text style={styles.loadingText}>데이터 불러오는 중...</Text>
      </View>
    );
  }

  if (loadError) {
    return (
      <View style={styles.centerWrap}>
        <MaterialCommunityIcons name="alert-circle-outline" size={40} color={color.error[500]} />
        <Text style={styles.errorMsg}>{loadError}</Text>
      </View>
    );
  }

  const statsData = { memberCount, moduleCount, errorCount };

  return (
    <ScrollView contentContainerStyle={styles.page}>
      {/* ── Header ── */}
      <View style={styles.header}>
        <View>
          <Text style={styles.pageTitle}>대시보드</Text>
          <Text style={styles.subtitle}>시스템 현황을 실시간으로 모니터링합니다</Text>
        </View>
        <View style={styles.dateBadge}>
          <MaterialCommunityIcons name="calendar-today" size={13} color="#6B7280" />
          <Text style={styles.dateText}>
            {new Date().toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })}
          </Text>
        </View>
      </View>

      {/* ── KPI Cards ── */}
      <View style={styles.kpiGrid}>
        {KPI_CARDS.map((card) => (
          <View key={card.label} style={[styles.kpiCard, { backgroundColor: card.bg }]}>
            <MaterialCommunityIcons
              name={card.icon}
              size={76}
              color={card.accent}
              style={styles.kpiBgIcon}
            />
            <Text style={[styles.kpiLabel, { color: card.textSub }]}>{card.label}</Text>
            <Text style={[styles.kpiValue, { color: card.textMain }]}>
              {card.getValue(statsData).toLocaleString()}
            </Text>
            <View style={styles.deltaBadge}>
              <Text style={[styles.deltaText, { color: card.deltaColor }]}>{card.delta}</Text>
            </View>
          </View>
        ))}
      </View>

      {/* ── Bottom Row: Chart + Overview ── */}
      <View style={styles.bottomRow}>
        <View style={styles.chartCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>일별 접속자 수</Text>
            <Text style={styles.cardSub}>최근 7일</Text>
          </View>
          <MiniBarChart
            data={TRAFFIC_DATA}
            chartHeight={110}
            primaryColor="#3B82F6"
            highlightColor="#1D4ED8"
          />
        </View>

        <View style={styles.overviewCard}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>최근 활동</Text>
            <Text style={styles.cardSub}>Overview</Text>
          </View>
          <OverviewList items={OVERVIEW_ITEMS} />
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { paddingBottom: 40, gap: 24 },
  centerWrap: { flex: 1, minHeight: 300, justifyContent: 'center', alignItems: 'center', gap: 12 },
  loadingText: { color: '#6B7280', fontSize: fontSize.sm },
  errorMsg: { color: color.error[600], fontSize: fontSize.sm, marginTop: 8 },

  // Header
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    flexWrap: 'wrap',
    gap: 12,
  },
  pageTitle: { fontSize: 28, fontWeight: fontWeight.bold, color: '#111827', lineHeight: 36 },
  subtitle: { color: '#6B7280', fontSize: fontSize.sm, marginTop: 3 },
  dateBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: radius.full,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  dateText: { fontSize: 12, color: '#6B7280' },

  // KPI Grid
  kpiGrid: { flexDirection: 'row', gap: 14, flexWrap: 'wrap' },
  kpiCard: {
    flex: 1,
    minWidth: 190,
    minHeight: 136,
    borderRadius: radius.xl,
    padding: 20,
    overflow: 'hidden',
    justifyContent: 'flex-end',
    gap: 4,
  },
  kpiBgIcon: {
    position: 'absolute',
    right: -8,
    top: -8,
    opacity: 0.12,
  },
  kpiLabel: {
    fontSize: fontSize.xs,
    fontWeight: fontWeight.semibold,
    letterSpacing: 0.4,
    textTransform: 'uppercase',
  },
  kpiValue: {
    fontSize: 34,
    fontWeight: fontWeight.bold,
    lineHeight: 40,
  },
  deltaBadge: {
    backgroundColor: 'rgba(255,255,255,0.6)',
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: radius.full,
    marginTop: 4,
  },
  deltaText: { fontSize: 11, fontWeight: fontWeight.semibold },

  // Bottom Row
  bottomRow: { flexDirection: 'row', gap: 16, flexWrap: 'wrap' },
  chartCard: {
    flex: 3,
    minWidth: 280,
    backgroundColor: '#FFFFFF',
    borderRadius: radius.xl,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 16,
  },
  overviewCard: {
    flex: 2,
    minWidth: 240,
    backgroundColor: '#FFFFFF',
    borderRadius: radius.xl,
    padding: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 16,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, color: '#111827' },
  cardSub: { fontSize: fontSize.xs, color: '#9CA3AF' },
});
