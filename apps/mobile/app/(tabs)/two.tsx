import FontAwesome from '@expo/vector-icons/FontAwesome';
import React, { useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  SectionList,
  StyleSheet,
  Switch,
  Text,
  View,
} from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { Input } from '@/components/ui';
import { createKeyword, deleteKeyword, Keyword, listKeywords, updateKeyword } from '@/lib/keywords';
import { border, color, fontSize, fontWeight, radius, space, surface, text } from '@/theme/tokens';

type Section = { title: string; data: Keyword[] };

export default function KeywordsScreen() {
  const { token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState('');
  const [newText, setNewText] = useState('');
  const [items, setItems] = useState<Keyword[]>([]);

  async function refresh() {
    if (!token) return;
    setLoading(true);
    try {
      const kws = await listKeywords(token, query.trim() || undefined);
      setItems(kws);
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '키워드를 불러오지 못했습니다.';
      Alert.alert('오류', msg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      refresh();
    }, 250);
    return () => clearTimeout(t);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  const sections = useMemo<Section[]>(() => {
    const pinned = items.filter((k) => k.is_pinned);
    const active = items.filter((k) => !k.is_pinned && k.is_active);
    const inactive = items.filter((k) => !k.is_pinned && !k.is_active);
    return [
      { title: '핀', data: pinned },
      { title: '활성', data: active },
      { title: '비활성', data: inactive },
    ].filter((s) => s.data.length > 0);
  }, [items]);

  async function onAdd() {
    if (!token) return;
    const text = newText.trim();
    if (!text) return;
    try {
      const created = await createKeyword(token, text);
      setItems((prev) => [created, ...prev]);
      setNewText('');
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '추가에 실패했습니다.';
      Alert.alert('오류', msg);
    }
  }

  async function togglePin(k: Keyword) {
    if (!token) return;
    const next = !k.is_pinned;
    setItems((prev) => prev.map((x) => (x.id === k.id ? { ...x, is_pinned: next } : x)));
    try {
      const updated = await updateKeyword(token, k.id, { is_pinned: next });
      setItems((prev) => prev.map((x) => (x.id === k.id ? updated : x)));
    } catch {
      setItems((prev) => prev.map((x) => (x.id === k.id ? k : x)));
    }
  }

  async function toggleActive(k: Keyword) {
    if (!token) return;
    const next = !k.is_active;
    setItems((prev) => prev.map((x) => (x.id === k.id ? { ...x, is_active: next } : x)));
    try {
      const updated = await updateKeyword(token, k.id, { is_active: next });
      setItems((prev) => prev.map((x) => (x.id === k.id ? updated : x)));
    } catch {
      setItems((prev) => prev.map((x) => (x.id === k.id ? k : x)));
    }
  }

  function onDelete(k: Keyword) {
    if (!token) return;
    Alert.alert('삭제', `“${k.text}” 키워드를 삭제할까요?`, [
      { text: '취소', style: 'cancel' },
      {
        text: '삭제',
        style: 'destructive',
        onPress: async () => {
          const snapshot = items;
          setItems((prev) => prev.filter((x) => x.id !== k.id));
          try {
            await deleteKeyword(token, k.id);
          } catch {
            setItems(snapshot);
          }
        },
      },
    ]);
  }

  return (
    <KeyboardAvoidingView
      style={styles.page}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      <View style={styles.topBar}>
        <Input
          style={styles.search}
          placeholder="키워드 검색"
          value={query}
          onChangeText={setQuery}
          autoCapitalize="none"
        />
      </View>


      {loading ? (
        <View style={styles.center}>
          <ActivityIndicator />
        </View>
      ) : items.length === 0 ? (
        <View style={styles.center}>
          <Text style={styles.emptyTitle}>키워드가 없어요</Text>
          <Text style={styles.emptyDesc}>아래에 키워드를 입력하면 일일 리포트가 만들어집니다.</Text>
        </View>
      ) : (
        <SectionList
          sections={sections}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          renderSectionHeader={({ section }) => (
            <Text style={styles.sectionTitle}>{section.title}</Text>
          )}
          renderItem={({ item }) => (
            <View style={styles.row}>
              <Pressable style={styles.pin} onPress={() => togglePin(item)}>
                <FontAwesome name={item.is_pinned ? 'star' : 'star-o'} size={18} color={color.primary[500]} />
              </Pressable>
              <Text style={styles.text} numberOfLines={1}>
                {item.text}
              </Text>
              <Switch value={item.is_active} onValueChange={() => toggleActive(item)} />
              <Pressable style={styles.trash} onPress={() => onDelete(item)}>
                <FontAwesome name="trash" size={18} color={text.tertiary} />
              </Pressable>
            </View>
          )}
          onRefresh={refresh}
          refreshing={loading}
        />
      )}

      <View style={styles.addBar}>
        <Input
          style={styles.addInput}
          placeholder="새 키워드 입력"
          value={newText}
          onChangeText={setNewText}
          onSubmitEditing={onAdd}
          returnKeyType="done"
        />
        <Pressable style={styles.addButton} onPress={onAdd}>
          <FontAwesome name="plus" size={18} color={text.inverse} />
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: surface.canvas },
  topBar: { padding: space[3], paddingBottom: space[2] },
  search: {
    height: 40,
    borderRadius: radius.md,
    backgroundColor: color.neutral[100],
    paddingHorizontal: space[3],
  },
  addBar: {
    flexDirection: 'row',
    gap: space[2],
    paddingHorizontal: space[3],
    paddingVertical: space[3],
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: border.subtle,
    backgroundColor: surface.canvas,
  },
  addInput: {
    flex: 1,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: color.neutral[100],
    paddingHorizontal: space[3],
  },
  addButton: {
    width: 44,
    height: 44,
    borderRadius: radius.md,
    backgroundColor: color.primary[500],
    alignItems: 'center',
    justifyContent: 'center',
  },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 24 },
  emptyTitle: { fontSize: fontSize.base, fontWeight: fontWeight.semibold, color: text.primary },
  emptyDesc: { marginTop: 6, color: text.tertiary, textAlign: 'center' },
  listContent: { paddingHorizontal: space[3], paddingBottom: space[6] },
  sectionTitle: { marginTop: 14, marginBottom: 8, color: text.tertiary, fontWeight: fontWeight.semibold },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: border.subtle,
  },
  pin: { width: 32, alignItems: 'center' },
  text: { flex: 1, color: text.primary, fontSize: fontSize.sm },
  trash: { paddingLeft: space[5], paddingRight: 2 },
});
