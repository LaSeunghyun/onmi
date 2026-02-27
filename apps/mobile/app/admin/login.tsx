import { useRouter } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, View } from 'react-native';

import { ApiError } from '@/lib/api';
import { Button, Card, Input } from '@/components/ui';
import { useAdminAuth } from '@/lib/adminAuth';
import { useResponsive } from '@/lib/useResponsive';
import { toAdminLoginMessage, validateAdminIdRequired, validatePasswordRequired } from '@/lib/validation';
import { ui } from '@/theme/primitives';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function AdminLoginScreen() {
  const { signIn } = useAdminAuth();
  const router = useRouter();
  const responsive = useResponsive();
  const [adminId, setAdminId] = useState('admin');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const dynamicStyles = useMemo(
    () => ({
      page: {
        ...ui.pageSubtle,
        justifyContent: 'center' as const,
        alignItems: 'center' as const,
        paddingHorizontal: responsive.pagePaddingHorizontal,
        paddingVertical: responsive.pagePaddingVertical,
      },
      card: {
        width: '100%' as const,
        maxWidth: responsive.cardMaxWidthWide,
        padding: responsive.isNarrow ? space[4] : space[5],
        borderRadius: radius.lg,
      },
    }),
    [responsive]
  );

  async function onSubmit() {
    setError(null);
    const idErr = validateAdminIdRequired(adminId);
    if (idErr) {
      setError(idErr);
      return;
    }
    const pwdErr = validatePasswordRequired(password);
    if (pwdErr) {
      setError(pwdErr);
      return;
    }
    setSubmitting(true);
    try {
      await signIn(adminId.trim(), password);
      router.replace('/admin/dashboard');
    } catch (e) {
      const err = e as ApiError;
      setError(toAdminLoginMessage({ status: err?.status, message: err?.message }));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <KeyboardAvoidingView
      style={[styles.page, dynamicStyles.page]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <Card style={[styles.card, dynamicStyles.card]}>
          <Text style={styles.title}>관리자 로그인</Text>
          <Text style={styles.label}>관리자 ID</Text>
          <Input
            accessibilityLabel="관리자 ID"
            value={adminId}
            onChangeText={(t) => { setAdminId(t); setError(null); }}
            autoCapitalize="none"
            style={styles.input}
          />
          <Text style={styles.label}>비밀번호</Text>
          <Input
            accessibilityLabel="비밀번호"
            value={password}
            onChangeText={(t) => { setPassword(t); setError(null); }}
            secureTextEntry
            style={styles.input}
          />
          {error ? (
            <Text accessibilityLiveRegion="polite" style={styles.error}>
              {error}
            </Text>
          ) : null}
          {submitting ? (
            <View style={styles.loadingWrap}>
              <ActivityIndicator color={text.inverse} />
            </View>
          ) : (
            <Button label="로그인" variant="primary" onPress={onSubmit} disabled={submitting} style={styles.submitBtn} />
          )}
        </Card>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  page: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: space[4],
  },
  card: {},
  title: { fontSize: 22, fontWeight: fontWeight.bold, marginBottom: space[2], color: text.primary },
  label: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold, color: text.secondary, marginTop: space[2] },
  input: { marginBottom: space[1] },
  loadingWrap: {
    marginTop: 8,
    backgroundColor: color.secondary[600],
    borderRadius: 8,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
  },
  submitBtn: { marginTop: 8 },
  error: { color: color.error[700], marginTop: 4, fontSize: fontSize.sm },
});
