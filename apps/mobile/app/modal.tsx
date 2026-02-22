import { StatusBar } from 'expo-status-bar';
import React, { useEffect, useState } from 'react';
import { Alert, Platform, StyleSheet, Switch, Text, View } from 'react-native';

import { Button, Input } from '@/components/ui';
import { API_BASE_URL } from '@/lib/config';
import { useAuth } from '@/lib/auth';
import { ensureNotificationPermission, scheduleDailyReportNotification, cancelDailyReportNotification } from '@/lib/notifications';
import { getNotificationSetting, updateNotificationSetting } from '@/lib/settings';
import { ui } from '@/theme/primitives';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function ModalScreen() {
  const { user, token, signOut } = useAuth();
  const [loaded, setLoaded] = useState(false);
  const [enabled, setEnabled] = useState(true);
  const [time, setTime] = useState('09:00');

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!token) return;
      try {
        const s = await getNotificationSetting(token);
        if (cancelled) return;
        setEnabled(s.is_enabled);
        setTime(s.daily_report_time_hhmm);
      } catch {
        // keep defaults
      } finally {
        if (!cancelled) setLoaded(true);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [token]);

  async function onSave() {
    if (!token) return;
    const m = /^(\d{2}):(\d{2})$/.exec(time.trim());
    if (!m) {
      Alert.alert('오류', '시간 형식은 HH:MM 입니다. 예) 09:00');
      return;
    }
    const hour = parseInt(m[1], 10);
    const minute = parseInt(m[2], 10);
    if (hour < 0 || hour > 23 || minute < 0 || minute > 59) {
      Alert.alert('오류', '유효한 시간을 입력해주세요.');
      return;
    }

    if (enabled) {
      const ok = await ensureNotificationPermission();
      if (!ok) {
        Alert.alert('권한 필요', '알림 권한이 필요합니다. OS 설정에서 허용해주세요.');
        return;
      }
      await scheduleDailyReportNotification({ hour, minute });
    } else {
      await cancelDailyReportNotification();
    }

    try {
      await updateNotificationSetting(token, { daily_report_time_hhmm: `${m[1]}:${m[2]}`, is_enabled: enabled });
      Alert.alert('저장됨', '알림 설정을 저장했어요.');
    } catch (e) {
      Alert.alert('오류', '설정 저장에 실패했습니다.');
    }
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>설정</Text>
      <Text style={styles.text}>로그인: {user?.email ?? '-'}</Text>
      <Text style={styles.text}>API: {API_BASE_URL}</Text>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>일일 리포트 알림</Text>
        <View style={styles.row}>
          <Text style={styles.label}>알림 사용</Text>
          <Switch value={enabled} onValueChange={setEnabled} />
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>시간(HH:MM)</Text>
          <Input style={styles.input} value={time} onChangeText={setTime} editable={loaded} />
        </View>
        <Button label="저장" variant="primary" onPress={onSave} disabled={!loaded} size="md" style={styles.saveButton} />
      </View>

      <Button label="로그아웃" variant="danger" onPress={() => signOut()} size="md" style={styles.button} />

      {/* Use a light status bar on iOS to account for the black space above the modal */}
      <StatusBar style={Platform.OS === 'ios' ? 'light' : 'auto'} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    ...ui.page,
    alignItems: 'stretch',
    justifyContent: 'center',
    gap: space[2],
    padding: space[6],
  },
  title: {
    fontSize: fontSize.xl,
    fontWeight: fontWeight.bold,
    textAlign: 'center',
  },
  text: { color: text.secondary, textAlign: 'center' },
  section: {
    marginTop: 10,
    padding: 14,
    borderRadius: radius.lg,
    backgroundColor: color.neutral[50],
    gap: space[2],
  },
  sectionTitle: { fontWeight: fontWeight.bold, color: text.primary },
  row: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 12 },
  label: { color: text.secondary },
  input: {
    width: 88,
    height: 36,
    textAlign: 'center',
  },
  saveButton: {
    marginTop: 4,
    height: 40,
  },
  button: { marginTop: 10, paddingHorizontal: 18 },
});
