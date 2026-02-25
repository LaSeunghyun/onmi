import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useLocalSearchParams, useRouter } from 'expo-router';
import React, { useEffect, useState } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { addWatchItem } from '@/lib/stocks';
import { color, fontSize, fontWeight, radius, space, surface, text } from '@/theme/tokens';

const MAX_ITEMS = 10;

export default function StockAddScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const params = useLocalSearchParams<{ corp_code?: string; srtn_cd?: string; itms_nm?: string }>();
  const [corpCode, setCorpCode] = useState('');
  const [srtnCd, setSrtnCd] = useState('');
  const [itmsNm, setItmsNm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params.corp_code) setCorpCode(params.corp_code);
    if (params.srtn_cd) setSrtnCd(params.srtn_cd);
    if (params.itms_nm) setItmsNm(params.itms_nm);
  }, [params.corp_code, params.srtn_cd, params.itms_nm]);

  const corpClean = corpCode.replace(/\D/g, '').slice(0, 8);
  const srtnClean = srtnCd.replace(/\D/g, '').slice(0, 6);
  const canSubmit = corpClean.length === 8 && srtnClean.length === 6 && !!token;

  const onSubmit = async () => {
    if (!canSubmit || !token) return;
    setLoading(true);
    setError(null);
    try {
      await addWatchItem(token, {
        corp_code: corpClean,
        srtn_cd: srtnClean,
        itms_nm: itmsNm.trim() || undefined,
      });
      router.back();
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e
          ? String((e as ApiError).message)
          : '등록 실패';
      setError(msg);
      if (typeof e === 'object' && e && 'status' in e && (e as ApiError).status === 400) {
        Alert.alert('등록 불가', '감시종목은 최대 10개까지입니다.');
      }
    } finally {
      setLoading(false);
    }
  };

  if (!token) return null;

  return (
    <KeyboardAvoidingView
      style={styles.page}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <View style={styles.block}>
        <Text style={styles.label}>고유번호 (corp_code) 8자리</Text>
        <TextInput
          style={styles.input}
          value={corpCode}
          onChangeText={setCorpCode}
          placeholder="예: 00126380"
          placeholderTextColor={text.tertiary}
          keyboardType="number-pad"
          maxLength={8}
          editable={!loading}
        />
        <Text style={styles.hint}>DART 공시대상회사 고유번호</Text>
      </View>
      <View style={styles.block}>
        <Text style={styles.label}>종목코드 (srtn_cd) 6자리</Text>
        <TextInput
          style={styles.input}
          value={srtnCd}
          onChangeText={setSrtnCd}
          placeholder="예: 005930"
          placeholderTextColor={text.tertiary}
          keyboardType="number-pad"
          maxLength={6}
          editable={!loading}
        />
        <Text style={styles.hint}>시세 API 단축코드</Text>
      </View>
      <View style={styles.block}>
        <Text style={styles.label}>종목명 (선택)</Text>
        <TextInput
          style={styles.input}
          value={itmsNm}
          onChangeText={setItmsNm}
          placeholder="표시용 이름"
          placeholderTextColor={text.tertiary}
          editable={!loading}
        />
      </View>
      {error ? <Text style={styles.errorText}>{error}</Text> : null}
      <Pressable
        style={[styles.button, !canSubmit && styles.buttonDisabled]}
        onPress={onSubmit}
        disabled={!canSubmit || loading}
      >
        <Text style={styles.buttonText}>
          {loading ? '등록 중…' : `감시종목 추가 (최대 ${MAX_ITEMS}개)`}
        </Text>
      </Pressable>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, padding: space[4], backgroundColor: color.neutral[50] },
  block: { marginBottom: space[4] },
  label: { fontSize: fontSize.sm, fontWeight: fontWeight.medium, color: text.primary, marginBottom: space[1] },
  input: {
    borderWidth: 1,
    borderColor: color.neutral[300],
    borderRadius: radius.md,
    padding: space[3],
    fontSize: fontSize.base,
    color: text.primary,
    backgroundColor: surface.canvas,
  },
  hint: { fontSize: fontSize.xs, color: text.tertiary, marginTop: space[1] },
  errorText: { color: color.error[600], fontSize: fontSize.sm, marginBottom: space[2] },
  button: {
    backgroundColor: color.primary[500],
    padding: space[4],
    borderRadius: radius.md,
    alignItems: 'center',
    marginTop: space[4],
  },
  buttonDisabled: { opacity: 0.5 },
  buttonText: { color: text.inverse, fontSize: fontSize.base, fontWeight: fontWeight.semibold },
});
