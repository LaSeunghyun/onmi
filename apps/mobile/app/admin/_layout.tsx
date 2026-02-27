import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Slot, useRouter, useSegments } from 'expo-router';
import React, { useEffect } from 'react';
import { Platform, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { useAdminAuth } from '@/lib/adminAuth';
import { admin, color, fontSize, fontWeight, radius, text } from '@/theme/tokens';

type MCIconName = React.ComponentProps<typeof MaterialCommunityIcons>['name'];

interface NavItemDef {
  href: string;
  label: string;
  icon: MCIconName;
  key: string;
}

const MAIN_ITEMS: NavItemDef[] = [
  { href: '/admin/dashboard', label: '대시보드', icon: 'view-dashboard-outline', key: 'dashboard' },
];

const ADMIN_ITEMS: NavItemDef[] = [
  { href: '/admin/members', label: '회원관리', icon: 'account-group-outline', key: 'members' },
  { href: '/admin/modules', label: '모듈관리', icon: 'puzzle-outline', key: 'modules' },
  { href: '/admin/audit', label: '로그관리', icon: 'clipboard-text-outline', key: 'audit' },
  { href: '/admin/settings', label: '설정', icon: 'cog-outline', key: 'settings' },
];

const ACTIVE_COLOR = admin.sidebar.navActiveBg;
const INACTIVE_ICON_COLOR = admin.sidebar.navText;
const INACTIVE_TEXT_COLOR = admin.sidebar.navText;

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

  function renderNavItem(item: NavItemDef) {
    const isActive = active === item.key;
    return (
      <Pressable
        key={item.key}
        accessibilityLabel={item.label}
        accessibilityRole="link"
        style={[styles.navItem, isActive && styles.navItemActive]}
        onPress={() => router.push(item.href as any)}
      >
        <MaterialCommunityIcons
          name={item.icon}
          size={16}
          color={isActive ? ACTIVE_COLOR : INACTIVE_ICON_COLOR}
        />
        <Text style={[styles.navText, isActive && styles.navTextActive]}>{item.label}</Text>
      </Pressable>
    );
  }

  return (
    <View style={styles.page}>
      {!inAdminLogin ? (
        <>
          <View style={styles.sidebar}>
            <View style={styles.brandWrap}>
              <View style={styles.brandIcon}>
                <MaterialCommunityIcons name="circle-outline" size={18} color="#FFFFFF" />
              </View>
              <View>
                <Text style={styles.brandTitle}>관리자</Text>
                <Text style={styles.brandSub}>Admin Console</Text>
              </View>
            </View>

            <Text style={styles.sectionLabel}>MAIN</Text>
            {MAIN_ITEMS.map(renderNavItem)}

            <Text style={[styles.sectionLabel, { marginTop: 22 }]}>ADMIN</Text>
            {ADMIN_ITEMS.map(renderNavItem)}

            <Pressable
              accessibilityLabel="로그아웃"
              accessibilityRole="button"
              style={styles.logoutBtn}
              onPress={signOut}
            >
              <MaterialCommunityIcons name="logout" size={14} color="#475569" />
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
                <MaterialCommunityIcons
                  name="bell-outline"
                  size={20}
                  color={color.neutral[500]}
                  accessibilityLabel="알림"
                />
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
    width: 210,
    backgroundColor: admin.sidebar.bg,
    paddingHorizontal: 12,
    paddingTop: 20,
    paddingBottom: 16,
    borderRightWidth: 1,
    borderRightColor: admin.sidebar.border,
  },
  brandWrap: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 28,
    paddingHorizontal: 6,
  },
  brandIcon: {
    width: 36,
    height: 36,
    borderRadius: radius.full,
    backgroundColor: admin.sidebar.brandAccent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandTitle: { color: text.inverse, fontWeight: fontWeight.bold, fontSize: fontSize.base },
  brandSub: { color: admin.sidebar.brandSub, fontSize: fontSize.xs },
  sectionLabel: {
    color: admin.sidebar.sectionLabel,
    fontSize: 10,
    fontWeight: fontWeight.semibold,
    letterSpacing: 1,
    marginBottom: 6,
    paddingHorizontal: 10,
  },
  navItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    height: 38,
    borderRadius: radius.md,
    paddingHorizontal: 10,
    marginBottom: 2,
    borderLeftWidth: 3,
    borderLeftColor: 'transparent',
  },
  navItemActive: {
    borderLeftColor: ACTIVE_COLOR,
    backgroundColor: 'rgba(34, 211, 238, 0.07)',
  },
  navText: {
    color: INACTIVE_TEXT_COLOR,
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
  },
  navTextActive: {
    color: ACTIVE_COLOR,
    fontWeight: fontWeight.semibold,
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
    width: 440,
    maxWidth: '60%',
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
  avatar: { width: 32, height: 32, borderRadius: radius.full, backgroundColor: admin.sidebar.brandAccent },
  content: { flex: 1, minHeight: 400, paddingHorizontal: 24, paddingVertical: 20 },
  logoutBtn: {
    marginTop: 'auto',
    height: 36,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: admin.sidebar.logoutBorder,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 12,
  },
  logoutText: { color: admin.sidebar.navText, fontWeight: fontWeight.medium, fontSize: fontSize.sm },
});
