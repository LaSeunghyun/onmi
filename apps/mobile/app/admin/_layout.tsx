import { Link, Slot, useRouter, useSegments } from 'expo-router';
import React, { useEffect } from 'react';
import { Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { useAdminAuth } from '@/lib/adminAuth';
import { admin, color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

export default function AdminLayout() {
  const { loading, token, signOut } = useAdminAuth();
  const segments = useSegments();
  const router = useRouter();
  const inAdminLogin = segments[1] === 'login';

  useEffect(() => {
    if (Platform.OS !== 'web') {
      router.replace('/(auth)/login');
      return;
    }
    if (loading) return;
    if (!token && !inAdminLogin) {
      router.replace('/admin/login');
    } else if (token && inAdminLogin) {
      router.replace('/admin/dashboard');
    }
  }, [loading, token, inAdminLogin, router]);

  const active = segments[1] ?? 'dashboard';

  return (
    <View style={styles.page}>
      {!inAdminLogin ? (
        <>
          <View style={styles.sidebar}>
            <View style={styles.brandWrap}>
              <View style={styles.brandIcon}>
                <Text style={styles.brandIconText}>◌</Text>
              </View>
              <View>
                <Text style={styles.brandTitle}>관리자</Text>
                <Text style={styles.brandSub}>Admin</Text>
              </View>
            </View>

            <Text style={styles.sectionLabel}>MAIN</Text>
            <Link href="/admin/dashboard" style={[styles.navLink, active === 'dashboard' && styles.navLinkActive]}>
              대시보드
            </Link>

            <Text style={[styles.sectionLabel, { marginTop: 20 }]}>ADMIN</Text>
            <Link href="/admin/members" style={[styles.navLink, active === 'members' && styles.navLinkActive]}>
              회원관리
            </Link>
            <Link href="/admin/modules" style={[styles.navLink, active === 'modules' && styles.navLinkActive]}>
              모듈관리
            </Link>
            <Link href="/admin/audit" style={[styles.navLink, active === 'audit' && styles.navLinkActive]}>
              로그관리
            </Link>
            <Link href="/admin/settings" style={[styles.navLink, active === 'settings' && styles.navLinkActive]}>
              설정
            </Link>

            <Pressable
              accessibilityLabel="로그아웃"
              accessibilityRole="button"
              style={styles.logoutBtn}
              onPress={signOut}
            >
              <Text style={styles.logoutText}>로그아웃</Text>
            </Pressable>
          </View>
          <View style={styles.main}>
            <View style={styles.topbar}>
              <TextInput
                accessibilityLabel="검색"
                placeholder="검색..."
                placeholderTextColor={color.neutral[400]}
                style={styles.searchInput}
              />
              <View style={styles.topIcons}>
                <Text style={styles.bell} accessibilityLabel="알림">🔔</Text>
                <View style={styles.avatar} accessibilityLabel="프로필" />
              </View>
            </View>
            <View style={styles.content}>
              <Slot />
            </View>
          </View>
        </>
      ) : null}
      {inAdminLogin ? <Slot /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, flexDirection: 'row', backgroundColor: admin.pageBg },
  sidebar: {
    width: 198,
    backgroundColor: admin.sidebar.bg,
    paddingHorizontal: 10,
    paddingTop: 18,
    paddingBottom: 12,
    borderRightWidth: 1,
    borderRightColor: admin.sidebar.border,
  },
  brandWrap: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 22, paddingHorizontal: 8 },
  brandIcon: {
    width: 36,
    height: 36,
    borderRadius: radius.full,
    backgroundColor: admin.sidebar.brandAccent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandIconText: { color: text.inverse, fontWeight: fontWeight.bold },
  brandTitle: { color: text.inverse, fontWeight: fontWeight.bold, fontSize: fontSize.base },
  brandSub: { color: admin.sidebar.brandSub, fontSize: fontSize.xs },
  sectionLabel: { color: admin.sidebar.sectionLabel, fontSize: 11, fontWeight: fontWeight.semibold, marginBottom: 8, paddingHorizontal: 8 },
  navLink: {
    color: admin.sidebar.navText,
    height: 36,
    borderRadius: radius.md,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginBottom: 6,
    fontSize: fontSize.sm,
  },
  navLinkActive: {
    backgroundColor: admin.sidebar.navActiveBg,
    color: text.inverse,
    fontWeight: fontWeight.semibold,
    shadowColor: admin.sidebar.navActiveBg,
    shadowOpacity: 0.35,
    shadowRadius: 10,
  },
  main: { flex: 1 },
  topbar: {
    height: 56,
    paddingHorizontal: 24,
    backgroundColor: admin.topbar.bg,
    borderBottomWidth: 1,
    borderBottomColor: admin.topbar.border,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  searchInput: {
    width: 444,
    maxWidth: '72%',
    height: 34,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: color.neutral[200],
    backgroundColor: color.neutral[50],
    color: text.primary,
    paddingHorizontal: 12,
    fontSize: fontSize.sm,
  },
  topIcons: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  bell: { fontSize: 18 },
  avatar: { width: 32, height: 32, borderRadius: radius.full, backgroundColor: admin.sidebar.brandAccent },
  content: { flex: 1, minHeight: 400, paddingHorizontal: 22, paddingVertical: 18 },
  logoutBtn: {
    marginTop: 'auto',
    height: 36,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: admin.sidebar.logoutBorder,
    alignItems: 'flex-start',
    justifyContent: 'center',
    paddingHorizontal: 12,
  },
  logoutText: { color: admin.sidebar.navText, fontWeight: fontWeight.medium, fontSize: fontSize.sm },
});
