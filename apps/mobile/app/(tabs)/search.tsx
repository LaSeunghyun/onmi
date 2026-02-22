import FontAwesome from '@expo/vector-icons/FontAwesome';
import { useRouter } from 'expo-router';
import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import { ApiError } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { searchStocks, type CorpSearchItem } from '@/lib/stocks';
import { color, fontSize, fontWeight, radius, space, text } from '@/theme/tokens';

const DEBOUNCE_MS = 400;

export default function StockSearchScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [debounced, setDebounced] = useState('');
  const [items, setItems] = useState<CorpSearchItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query.trim()), DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [query]);

  const search = useCallback(async () => {
    if (!token || !debounced) {
      setItems([]);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const list = await searchStocks(token, debounced, 50);
      setItems(list);
    } catch (e) {
      const msg =
        typeof e === 'object' && e && 'message' in e ? String((e as ApiError).message) : '검색 실패';
      setError(msg);
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [token, debounced]);

  useEffect(() => {
    search();
  }, [search]);

  const onSelect = useCallback(
    (item: CorpSearchItem) => {
      const params = new URLSearchParams({
        corp_code: item.corp_code,
        srtn_cd: item.stock_code,
        itms_nm: item.corp_name,
      });
      router.push((`/stock/add?${params.toString()}` as any) as never);
    },
    [router]
  );

  if (!token) return null;

  return (
    <View style={styles.page}>
      <View style={styles.searchRow}>
        <FontAwesome name="search" size={18} color={text.tertiary} style={styles.searchIcon} />
        <TextInput
          style={styles.input}
          value={query}
          onChangeText={setQuery}
          placeholder="종목명 입력 (예: 삼성전자)"
          placeholderTextColor={text.tertiary}
          autoCapitalize="none"
          autoCorrect={false}
          returnKeyType="search"
        />
        {loading ? (
          <ActivityIndicator size="small" color={color.primary[500]} style={styles.loader} />
        ) : null}
      </View>
      {error ? <Text style={styles.errorText}>{error}</Text> : null}
      <FlatList
        data={items}
        keyExtractor={(item) => `${item.corp_code}-${item.stock_code}`}
        contentContainerStyle={styles.listContent}
        ListEmptyComponent={
          debounced ? (
            <View style={styles.empty}>
              <Text style={styles.emptyText}>
                {loading ? '검색 중…' : '검색 결과가 없습니다.'}
              </Text>
              <Text style={styles.emptySub}>종목명을 정확히 입력해 보세요.</Text>
            </View>
          ) : (
            <View style={styles.empty}>
              <Text style={styles.emptyText}>종목명을 입력하면</Text>
              <Text style={styles.emptySub}>고유번호·종목코드가 자동으로 채워집니다.</Text>
            </View>
          )
        }
        renderItem={({ item }) => (
          <Pressable
            style={({ pressed }) => [styles.row, pressed && styles.rowPressed]}
            onPress={() => onSelect(item)}
          >
            <View style={styles.rowBody}>
              <Text style={styles.name} numberOfLines={1}>
                {item.corp_name}
              </Text>
              <Text style={styles.code}>
                고유번호 {item.corp_code} · 종목코드 {item.stock_code || '-'}
              </Text>
            </View>
            <FontAwesome name="chevron-right" size={14} color={text.tertiary} />
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: color.neutral[50] },
  searchRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: color.neutral[200],
    paddingHorizontal: space[4],
    paddingVertical: space[2],
  },
  searchIcon: { marginRight: space[2] },
  input: {
    flex: 1,
    fontSize: fontSize.base,
    color: text.primary,
    paddingVertical: space[2],
  },
  loader: { marginLeft: space[2] },
  errorText: { color: color.error[600], fontSize: fontSize.sm, padding: space[2] },
  listContent: { padding: space[4] },
  empty: { padding: space[8], alignItems: 'center' },
  emptyText: { fontSize: fontSize.base, color: text.secondary, marginBottom: space[1] },
  emptySub: { fontSize: fontSize.sm, color: text.tertiary },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: space[4],
    marginBottom: space[2],
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: color.neutral[200],
  },
  rowPressed: { opacity: 0.9 },
  rowBody: { flex: 1, minWidth: 0 },
  name: { fontSize: fontSize.lg, fontWeight: fontWeight.semibold, color: text.primary },
  code: { fontSize: fontSize.sm, color: text.tertiary, marginTop: space[1] },
});
