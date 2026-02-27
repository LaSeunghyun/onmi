import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { type AdminAuditLog, adminListAuditLogs } from '@/lib/admin';
import { ApiError } from '@/lib/api';
import { Card, ErrorBanner } from '@/components/ui';
import { useAdminAuth } from '@/lib/adminAuth';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function AdminAuditScreen() {
  const { token } = useAdminAuth();
  const [logs, setLogs] = useState<AdminAuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!token) {
      setLoading(false);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      setLogs(await adminListAuditLogs(token));
    } catch (e) {
      setError(typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '감사로그 조회 실패');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  return (
    <ScrollView contentContainerStyle={styles.page}>
      <Text style={styles.pageTitle}>로그관리</Text>
      <Text style={styles.subtitle}>시스템 활동 로그를 확인합니다</Text>

      <View style={styles.kpiGrid}>
        <Card style={styles.kpiCard}>
          <Text style={styles.kpiNumber}>{logs.length}</Text>
          <Text style={styles.kpiLabel}>전체 로그</Text>
        </Card>
        <Card style={styles.kpiCard}>
          <Text style={[styles.kpiNumber, { color: color.success[700] }]}>
            {logs.filter((l) => !l.action_type.includes('error') && !l.action_type.includes('fail')).length}
          </Text>
          <Text style={styles.kpiLabel}>정상</Text>
        </Card>
        <Card style={styles.kpiCard}>
          <Text style={[styles.kpiNumber, { color: color.error[600] }]}>
            {logs.filter((l) => l.action_type.includes('error') || l.action_type.includes('fail')).length}
          </Text>
          <Text style={styles.kpiLabel}>오류</Text>
        </Card>
      </View>

      <Card style={styles.sectionCard}>
        <Text style={styles.title}>활동 로그</Text>
        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="small" color={color.secondary[600]} />
            <Text style={styles.loadingText}>로그 불러오는 중...</Text>
          </View>
        ) : logs.length === 0 ? (
          <Text style={styles.emptyText}>활동 로그가 없습니다.</Text>
        ) : (
          logs.map((l) => (
            <View key={l.id} style={styles.row}>
              <Text style={styles.action}>
                {l.action_type} ({l.target_type})
              </Text>
              <Text style={styles.meta}>at: {l.created_at}</Text>
              {l.reason ? <Text style={styles.meta}>reason: {l.reason}</Text> : null}
            </View>
          ))
        )}
        <ErrorBanner message={error} />
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { paddingBottom: space[8], gap: space[3] },
  pageTitle: { fontSize: 36, fontWeight: fontWeight.bold, color: text.primary, lineHeight: 42 },
  subtitle: { color: text.secondary, fontSize: fontSize.base, marginTop: -8, marginBottom: 4 },
  kpiGrid: { flexDirection: 'row', gap: 14, flexWrap: 'wrap' },
  kpiCard: { width: 188, minHeight: 114, justifyContent: 'center' },
  kpiNumber: { fontSize: 36, fontWeight: fontWeight.bold, color: text.primary },
  kpiLabel: { color: text.secondary, fontSize: fontSize.sm },
  sectionCard: { maxWidth: 980 },
  title: { fontSize: 24, fontWeight: fontWeight.bold, color: text.primary },
  row: { borderWidth: 1, borderColor: color.neutral[200], borderRadius: radius.sm, padding: 10, gap: 2 },
  action: { fontWeight: fontWeight.bold, color: text.primary },
  meta: { color: text.secondary, fontSize: fontSize.xs },
  loadingWrap: { flexDirection: 'row', alignItems: 'center', gap: space[2], paddingVertical: space[4] },
  loadingText: { color: color.neutral[600], fontSize: fontSize.sm },
  emptyText: { color: text.secondary, fontSize: fontSize.sm, paddingVertical: space[4] },
});
