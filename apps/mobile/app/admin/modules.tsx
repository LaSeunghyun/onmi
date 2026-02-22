import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { type AdminModule, adminCreateModule, adminListModules } from '@/lib/admin';
import { ApiError } from '@/lib/api';
import { Button, Card, Input } from '@/components/ui';
import { useAdminAuth } from '@/lib/adminAuth';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function AdminModulesScreen() {
  const { token } = useAdminAuth();
  const [modules, setModules] = useState<AdminModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [moduleKey, setModuleKey] = useState('');
  const [name, setName] = useState('');
  const [routePath, setRoutePath] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function load() {
    if (!token) {
      setLoading(false);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      setModules(await adminListModules(token));
    } catch (e) {
      setError(typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '모듈 조회 실패');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function onCreate() {
    if (!token) return;
    setError(null);
    try {
      await adminCreateModule(token, {
        module_key: moduleKey.trim(),
        name: name.trim(),
        route_path: routePath.trim(),
        description: description.trim() || undefined,
        is_active: true,
      });
      setModuleKey('');
      setName('');
      setRoutePath('');
      setDescription('');
      await load();
    } catch (e) {
      setError(typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '모듈 생성 실패');
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.page}>
      <Text style={styles.pageTitle}>모듈관리</Text>
      <Text style={styles.subtitle}>시스템 모듈을 관리하고 모니터링합니다</Text>

      <View style={styles.kpiGrid}>
        <Card style={styles.kpiCard}>
          <Text style={styles.kpiNumber}>{modules.length}</Text>
          <Text style={styles.kpiLabel}>전체 모듈</Text>
        </Card>
        <Card style={styles.kpiCard}>
          <Text style={[styles.kpiNumber, { color: color.success[700] }]}>{modules.filter((m) => m.is_active).length}</Text>
          <Text style={styles.kpiLabel}>활성 모듈</Text>
        </Card>
        <Card style={styles.kpiCard}>
          <Text style={[styles.kpiNumber, { color: color.warning[600] }]}>{modules.filter((m) => !m.is_active).length}</Text>
          <Text style={styles.kpiLabel}>비활성 모듈</Text>
        </Card>
      </View>

      <Card style={styles.sectionCard}>
        <Text style={styles.title}>모듈 추가</Text>
        <Input style={styles.input} placeholder="module_key (예: news-report)" value={moduleKey} onChangeText={setModuleKey} />
        <Input style={styles.input} placeholder="이름" value={name} onChangeText={setName} />
        <Input style={styles.input} placeholder="route_path (예: /admin/modules/news-report)" value={routePath} onChangeText={setRoutePath} />
        <Input style={styles.input} placeholder="설명(선택)" value={description} onChangeText={setDescription} />
        <Button label="모듈 생성" variant="primary" onPress={onCreate} size="md" />
      </Card>

      <Card style={styles.sectionCard}>
        <Text style={styles.title}>모듈 목록</Text>
        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="small" color={color.secondary[600]} />
            <Text style={styles.loadingText}>모듈 목록 불러오는 중...</Text>
          </View>
        ) : modules.length === 0 ? (
          <Text style={styles.emptyText}>등록된 모듈이 없습니다. 위 폼에서 모듈을 추가해 보세요.</Text>
        ) : (
          modules.map((m) => (
            <View key={m.id} style={styles.row}>
              <View style={{ flex: 1 }}>
                <Text style={styles.name}>{m.name}</Text>
                <Text style={styles.meta}>
                  key={m.module_key} / path={m.route_path} / active={String(m.is_active)}
                </Text>
              </View>
            </View>
          ))
        )}
        {error ? <Text style={styles.error}>{error}</Text> : null}
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { paddingBottom: space[8], gap: space[3] },
  pageTitle: { fontSize: 36, fontWeight: fontWeight.bold, color: '#1E293B', lineHeight: 42 },
  subtitle: { color: '#64748B', fontSize: fontSize.base, marginTop: -8, marginBottom: 4 },
  kpiGrid: { flexDirection: 'row', gap: 14, flexWrap: 'wrap' },
  kpiCard: { width: 188, minHeight: 114, justifyContent: 'center' },
  kpiNumber: { fontSize: 36, fontWeight: fontWeight.bold, color: '#1E293B' },
  kpiLabel: { color: '#64748B', fontSize: fontSize.sm },
  title: { fontSize: 24, fontWeight: fontWeight.bold, color: text.primary },
  sectionCard: { maxWidth: 980 },
  input: { height: 40 },
  row: { borderWidth: 1, borderColor: color.neutral[200], borderRadius: radius.sm, padding: 10, marginTop: 4 },
  name: { fontWeight: fontWeight.bold, color: text.primary },
  meta: { color: text.secondary, fontSize: fontSize.xs },
  error: { color: color.error[700], marginTop: 4 },
  loadingWrap: { flexDirection: 'row', alignItems: 'center', gap: space[2], paddingVertical: space[4] },
  loadingText: { color: color.neutral[600], fontSize: fontSize.sm },
  emptyText: { color: text.secondary, fontSize: fontSize.sm, paddingVertical: space[4] },
});
