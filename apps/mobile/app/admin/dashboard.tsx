import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { adminListAuditLogs, adminListMembers, adminListModules } from '@/lib/admin';
import { Card } from '@/components/ui';
import { useAdminAuth } from '@/lib/adminAuth';
import { color, fontSize, fontWeight, space } from '@/theme/tokens';

export default function AdminDashboardScreen() {
  const { token } = useAdminAuth();
  const [loading, setLoading] = useState(true);
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
      try {
        const [members, modules, logs] = await Promise.all([adminListMembers(token), adminListModules(token), adminListAuditLogs(token)]);
        setMemberCount(members.length);
        setModuleCount(modules.length);
        setErrorCount(logs.filter((l) => l.action_type.includes('error') || l.action_type.includes('fail')).length);
      } catch {
        setMemberCount(0);
        setModuleCount(0);
        setErrorCount(0);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, [token]);

  return (
    <ScrollView contentContainerStyle={styles.page}>
      <Text style={styles.pageTitle}>대시보드</Text>
      <Text style={styles.subtitle}>시스템 현황을 실시간으로 모니터링합니다</Text>

      {loading ? (
        <View style={styles.loadingWrap}>
          <ActivityIndicator size="large" color={color.secondary[600]} />
          <Text style={styles.loadingText}>데이터 불러오는 중...</Text>
        </View>
      ) : (
        <View style={styles.kpiGrid}>
          <Card style={styles.kpiCard}>
            <Text style={styles.kpiLabel}>전체 회원</Text>
            <Text style={styles.kpiValue}>{memberCount}</Text>
            <Text style={styles.kpiDelta}>+실시간 반영</Text>
          </Card>
          <Card style={styles.kpiCard}>
            <Text style={styles.kpiLabel}>활성 모듈</Text>
            <Text style={styles.kpiValue}>{moduleCount}</Text>
            <Text style={styles.kpiDelta}>운영 중</Text>
          </Card>
          <Card style={styles.kpiCard}>
            <Text style={styles.kpiLabel}>오류 로그</Text>
            <Text style={styles.kpiValue}>{errorCount}</Text>
            <Text style={[styles.kpiDelta, styles.kpiWarn]}>확인 필요</Text>
          </Card>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { paddingBottom: space[8], gap: space[3] },
  pageTitle: { fontSize: 36, fontWeight: fontWeight.bold, color: '#1E293B', lineHeight: 42 },
  subtitle: { color: '#64748B', fontSize: fontSize.base, marginTop: -8, marginBottom: 4 },
  loadingWrap: { minHeight: 200, justifyContent: 'center', alignItems: 'center', gap: space[3] },
  loadingText: { color: color.neutral[600], fontSize: fontSize.sm },
  kpiGrid: { flexDirection: 'row', gap: 14, flexWrap: 'wrap' },
  kpiCard: { width: 188, minHeight: 114, justifyContent: 'center' },
  kpiLabel: { color: '#64748B', fontSize: fontSize.sm },
  kpiValue: { color: '#1E293B', fontSize: 36, fontWeight: fontWeight.bold, marginTop: 2 },
  kpiDelta: { color: color.success[600], fontSize: fontSize.xs, fontWeight: fontWeight.semibold },
  kpiWarn: { color: color.error[600] },
});
