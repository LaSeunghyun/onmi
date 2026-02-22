import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, Text, View } from 'react-native';

import { type AdminMember, adminCreateMember, adminListMembers, adminUpdateMemberStatus } from '@/lib/admin';
import { ApiError } from '@/lib/api';
import { Button, Card, Input } from '@/components/ui';
import { useAdminAuth } from '@/lib/adminAuth';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function AdminMembersScreen() {
  const { token } = useAdminAuth();
  const [members, setMembers] = useState<AdminMember[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [status, setStatus] = useState<'active' | 'suspended'>('active');
  const [initialPoints, setInitialPoints] = useState('0');

  async function load() {
    if (!token) {
      setLoading(false);
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const rows = await adminListMembers(token, q);
      setMembers(rows);
    } catch (e) {
      setError(typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '회원 조회 실패');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token]);

  async function onCreateMember() {
    if (!token) return;
    setError(null);
    setMessage(null);
    try {
      const points = Number(initialPoints);
      await adminCreateMember(token, {
        email: email.trim(),
        password,
        status,
        initial_points: Number.isFinite(points) ? points : 0,
      });
      setMessage('회원이 생성되었습니다. 앱 로그인 가능 계정입니다.');
      setEmail('');
      setPassword('');
      setInitialPoints('0');
      setStatus('active');
      await load();
    } catch (e) {
      setError(typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '회원 생성 실패');
    }
  }

  async function toggleStatus(member: AdminMember) {
    if (!token) return;
    const next = member.status === 'active' ? 'suspended' : 'active';
    try {
      await adminUpdateMemberStatus(token, member.id, next, '운영자 변경');
      await load();
    } catch (e) {
      setError(typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '상태 변경 실패');
    }
  }

  return (
    <ScrollView contentContainerStyle={styles.page}>
      <Text style={styles.pageTitle}>회원관리</Text>
      <Text style={styles.subtitle}>회원 상태를 관리하고 활동을 확인합니다</Text>

      <View style={styles.kpiGrid}>
        <Card style={styles.kpiCard}>
          <Text style={styles.kpiNumber}>{members.length}</Text>
          <Text style={styles.kpiLabel}>전체 회원</Text>
        </Card>
        <Card style={styles.kpiCard}>
          <Text style={styles.kpiNumber}>{members.filter((m) => m.status === 'active').length}</Text>
          <Text style={styles.kpiLabel}>활성 회원</Text>
        </Card>
        <Card style={styles.kpiCard}>
          <Text style={[styles.kpiNumber, { color: color.error[600] }]}>{members.filter((m) => m.status === 'suspended').length}</Text>
          <Text style={styles.kpiLabel}>정지 회원</Text>
        </Card>
      </View>

      <Card style={styles.sectionCard}>
        <Text style={styles.title}>회원 추가</Text>
        <Input placeholder="email@example.com" value={email} onChangeText={setEmail} />
        <Input placeholder="비밀번호(8자 이상)" secureTextEntry value={password} onChangeText={setPassword} />
        <Input placeholder="초기 포인트" value={initialPoints} onChangeText={setInitialPoints} keyboardType="numeric" />
        <View style={styles.row}>
          <Button label="active" variant="secondary" size="md" onPress={() => setStatus('active')} style={[styles.stateBtn, status === 'active' && styles.selected]} />
          <Button label="suspended" variant="secondary" size="md" onPress={() => setStatus('suspended')} style={[styles.stateBtn, status === 'suspended' && styles.selected]} />
        </View>
        <Button label="회원 생성" variant="primary" onPress={onCreateMember} size="md" />
        {message ? <Text style={styles.ok}>{message}</Text> : null}
      </Card>

      <Card style={styles.sectionCard}>
        <Text style={styles.title}>회원 목록</Text>
        <View style={styles.row}>
          <Input
            accessibilityLabel="회원 검색 이메일"
            style={styles.flexInput}
            placeholder="회원 검색 (이메일)"
            value={q}
            onChangeText={setQ}
          />
          <Button label="검색" variant="secondary" size="md" onPress={load} style={styles.searchBtn} />
        </View>
        {loading ? (
          <View style={styles.loadingWrap}>
            <ActivityIndicator size="small" color={color.secondary[600]} />
            <Text style={styles.loadingText}>회원 목록 불러오는 중...</Text>
          </View>
        ) : members.length === 0 ? (
          <Text style={styles.emptyText}>등록된 회원이 없습니다. 위 폼에서 회원을 추가해 보세요.</Text>
        ) : (
          members.map((m) => (
            <View key={m.id} style={styles.memberRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.email}>{m.email}</Text>
                <Text style={styles.meta}>
                  status: {m.status} / points: {m.points}
                </Text>
              </View>
              <Button label={m.status === 'active' ? '정지' : '활성'} variant="secondary" size="md" onPress={() => toggleStatus(m)} style={styles.searchBtn} />
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
  row: { flexDirection: 'row', gap: space[2], alignItems: 'center' },
  flexInput: { flex: 1, height: 40 },
  searchBtn: { height: 36, minWidth: 68 },
  stateBtn: { height: 36, minWidth: 90 },
  selected: { backgroundColor: color.secondary[200] },
  memberRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space[2],
    borderWidth: 1,
    borderColor: color.neutral[200],
    borderRadius: radius.sm,
    padding: 10,
    marginTop: 4,
  },
  email: { fontWeight: fontWeight.bold, color: text.primary },
  meta: { color: text.secondary, fontSize: fontSize.xs },
  ok: { color: color.success[700], marginTop: 4 },
  error: { color: color.error[700], marginTop: 4 },
  loadingWrap: { flexDirection: 'row', alignItems: 'center', gap: space[2], paddingVertical: space[4] },
  loadingText: { color: color.neutral[600], fontSize: fontSize.sm },
  emptyText: { color: text.secondary, fontSize: fontSize.sm, paddingVertical: space[4] },
});
