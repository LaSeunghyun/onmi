import { Link } from 'expo-router';
import React, { useMemo, useState } from 'react';
import { ActivityIndicator, KeyboardAvoidingView, Platform, ScrollView, StyleSheet, Text, View } from 'react-native';

import { ApiError } from '@/lib/api';
import { Button, Card, Input } from '@/components/ui';
import { useAuth } from '@/lib/auth';
import { useResponsive } from '@/lib/useResponsive';
import {
  toAuthSignupMessage,
  validateEmail,
  validatePasswordLength,
  validatePasswordRequired,
} from '@/lib/validation';
import { ui } from '@/theme/primitives';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function SignupScreen() {
  const { signUp } = useAuth();
  const responsive = useResponsive();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const dynamicStyles = useMemo(
    () => ({
      page: {
        ...ui.page,
        alignItems: 'center' as const,
        justifyContent: 'center' as const,
        backgroundColor: color.primary[500],
        paddingHorizontal: responsive.pagePaddingHorizontal,
        paddingVertical: responsive.pagePaddingVertical,
      },
      card: {
        width: '100%' as const,
        maxWidth: responsive.cardMaxWidth,
        borderRadius: radius.xl,
        padding: responsive.isNarrow ? space[4] : space[5],
        gap: space[2],
      },
    }),
    [responsive]
  );

  async function onSubmit() {
    setError(null);
    const emailErr = validateEmail(email);
    if (emailErr) {
      setError(emailErr);
      return;
    }
    const pwdErr = validatePasswordRequired(password);
    if (pwdErr) {
      setError(pwdErr);
      return;
    }
    const pwdLenErr = validatePasswordLength(password);
    if (pwdLenErr) {
      setError(pwdLenErr);
      return;
    }
    if (password !== password2) {
      setError('비밀번호가 일치하지 않습니다.');
      return;
    }
    setSubmitting(true);
    try {
      await signUp(email.trim(), password);
    } catch (e) {
      const err = e as ApiError;
      setError(toAuthSignupMessage({ status: err?.status, message: err?.message }));
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
          <Text style={styles.brand}>#onmi</Text>
          <Text style={styles.subtitle}>오로지 나를 위한 서비스</Text>

          <Text style={styles.label}>이메일</Text>
          <Input
            style={styles.input}
            autoCapitalize="none"
            keyboardType="email-address"
            placeholder="email@example.com"
            value={email}
            onChangeText={(t) => { setEmail(t); setError(null); }}
          />

          <Text style={styles.label}>비밀번호</Text>
          <Input
            style={styles.input}
            secureTextEntry
            placeholder="8자 이상"
            value={password}
            onChangeText={(t) => { setPassword(t); setError(null); }}
          />

          <Text style={styles.label}>비밀번호 확인</Text>
          <Input
            style={styles.input}
            secureTextEntry
            placeholder="비밀번호 다시 입력"
            value={password2}
            onChangeText={(t) => { setPassword2(t); setError(null); }}
          />

          {error ? <Text style={styles.error} accessibilityLiveRegion="polite">{error}</Text> : null}

          {submitting ? (
            <View style={styles.loadingWrap}>
              <ActivityIndicator color="#FFFFFF" />
            </View>
          ) : (
            <Button label="회원가입" onPress={onSubmit} variant="primary" size="lg" style={styles.primaryButton} />
          )}

          <Link href="/(auth)/login" style={styles.link}>
            이미 계정이 있으신가요? 로그인
          </Link>
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
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: space[4],
  },
  card: {},
  brand: {
    alignSelf: 'center',
    backgroundColor: color.primary[500],
    color: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: radius.full,
    overflow: 'hidden',
    fontSize: fontSize.xl,
  },
  subtitle: { textAlign: 'center', color: text.secondary, marginBottom: space[2] },
  label: { fontSize: fontSize.sm, fontWeight: fontWeight.semibold, color: text.primary },
  input: {
    backgroundColor: color.neutral[100],
    height: 40,
  },
  primaryButton: {
    marginTop: 4,
  },
  loadingWrap: {
    marginTop: 4,
    height: 48,
    backgroundColor: color.primary[500],
    borderRadius: radius.sm,
    alignItems: 'center',
    justifyContent: 'center',
  },
  link: { marginTop: space[2], textAlign: 'center', color: text.tertiary, textDecorationLine: 'underline' },
  error: { color: color.error[700], marginTop: 4, fontSize: fontSize.sm },
});

