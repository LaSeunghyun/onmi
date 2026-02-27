import React, { useMemo, useState } from 'react';
import { ScrollView, StyleSheet, Text } from 'react-native';

import { ApiError } from '@/lib/api';
import { Button, Card, Input } from '@/components/ui';
import { useAdminAuth } from '@/lib/adminAuth';
import { useResponsive } from '@/lib/useResponsive';
import {
  toAdminChangePasswordMessage,
  validatePasswordLength,
  validatePasswordRequired,
} from '@/lib/validation';
import { color, fontSize, fontWeight, space, text } from '@/theme/tokens';

export default function AdminSettingsScreen() {
  const { admin, changePassword } = useAdminAuth();
  const responsive = useResponsive();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const cardMaxWidth = useMemo(
    () => Math.min(responsive.width - responsive.pagePaddingHorizontal * 2, 880),
    [responsive.width, responsive.pagePaddingHorizontal]
  );

  async function onChangePassword() {
    setError(null);
    setMessage(null);
    const currentErr = validatePasswordRequired(currentPassword);
    if (currentErr) {
      setError('현재 비밀번호를 입력해 주세요.');
      return;
    }
    const newErr = validatePasswordRequired(newPassword);
    if (newErr) {
      setError('새 비밀번호를 입력해 주세요.');
      return;
    }
    const lenErr = validatePasswordLength(newPassword);
    if (lenErr) {
      setError(lenErr);
      return;
    }
    if (currentPassword === newPassword) {
      setError('새 비밀번호는 현재 비밀번호와 달라야 합니다.');
      return;
    }
    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword('');
      setNewPassword('');
      setMessage('비밀번호가 변경되었습니다.');
    } catch (e) {
      const err = e as ApiError;
      setError(toAdminChangePasswordMessage({ status: err?.status, message: err?.message }));
    }
  }

  return (
    <ScrollView contentContainerStyle={[styles.page, { paddingHorizontal: responsive.pagePaddingHorizontal }]}>
      <Text style={styles.pageTitle}>설정</Text>
      <Text style={styles.subtitle}>시스템 설정을 관리합니다</Text>

      <Card style={[styles.formCard, { maxWidth: cardMaxWidth }]}>
        <Text style={styles.sectionTitle}>프로필 설정</Text>
        <Input accessibilityLabel="관리자 ID" value={admin?.admin_id ?? ''} editable={false} style={styles.inputSpacing} />
        <Input accessibilityLabel="역할" value={admin?.role ?? ''} editable={false} style={styles.inputSpacing} />
        <Input
          accessibilityLabel="보안 상태"
          value={admin?.must_change_password ? '비밀번호 변경 필요' : '보안 상태 정상'}
          editable={false}
        />
      </Card>

      <Card style={[styles.formCard, { maxWidth: cardMaxWidth }]}>
        <Text style={styles.sectionTitle}>보안 설정</Text>
        <Input
          accessibilityLabel="현재 비밀번호"
          secureTextEntry
          placeholder="현재 비밀번호"
          value={currentPassword}
          onChangeText={(t) => { setCurrentPassword(t); setError(null); }}
          style={styles.inputSpacing}
        />
        <Input
          accessibilityLabel="새 비밀번호"
          secureTextEntry
          placeholder="새 비밀번호(8자 이상)"
          value={newPassword}
          onChangeText={(t) => { setNewPassword(t); setError(null); }}
          style={styles.inputSpacing}
        />
        <Button label="변경 사항 저장" onPress={onChangePassword} variant="primary" />
        {message ? <Text style={styles.ok}>{message}</Text> : null}
        {error ? <Text accessibilityLiveRegion="polite" style={styles.error}>{error}</Text> : null}
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  page: { paddingBottom: space[8], gap: space[3] },
  pageTitle: { fontSize: 36, fontWeight: fontWeight.bold, color: text.primary, lineHeight: 42 },
  subtitle: { color: text.secondary, fontSize: fontSize.base, marginTop: -8, marginBottom: 4 },
  formCard: { maxWidth: 880 },
  sectionTitle: { fontSize: 30, fontWeight: fontWeight.bold, color: text.primary, marginBottom: space[2] },
  inputSpacing: { marginBottom: space[2] },
  ok: { color: color.success[700], marginTop: 4 },
  error: { color: color.error[700], marginTop: 4 },
});
