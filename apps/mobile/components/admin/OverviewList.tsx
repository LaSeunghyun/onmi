import { MaterialCommunityIcons } from '@expo/vector-icons';
import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export interface OverviewItem {
  icon: React.ComponentProps<typeof MaterialCommunityIcons>['name'];
  iconColor: string;
  iconBg: string;
  label: string;
  sublabel: string;
  progress: number; // 0–100
  progressColor: string;
}

export function OverviewList({ items }: { items: OverviewItem[] }) {
  return (
    <View style={styles.root}>
      {items.map((item, i) => (
        <View key={i} style={styles.row}>
          <View style={[styles.iconBox, { backgroundColor: item.iconBg }]}>
            <MaterialCommunityIcons name={item.icon} size={16} color={item.iconColor} />
          </View>
          <View style={styles.details}>
            <View style={styles.topRow}>
              <Text style={styles.labelText} numberOfLines={1}>
                {item.label}
              </Text>
              <Text style={styles.sublabelText}>{item.sublabel}</Text>
            </View>
            <View style={styles.trackBg}>
              <View
                style={[
                  styles.trackFill,
                  { width: `${item.progress}%` as any, backgroundColor: item.progressColor },
                ]}
              />
            </View>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { gap: 16 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  iconBox: {
    width: 36,
    height: 36,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
  },
  details: { flex: 1, gap: 6 },
  topRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  labelText: { fontSize: 13, fontWeight: '500', color: '#1F2937', flex: 1, marginRight: 8 },
  sublabelText: { fontSize: 11, color: '#9CA3AF', flexShrink: 0 },
  trackBg: {
    height: 5,
    borderRadius: 999,
    backgroundColor: '#F1F5F9',
    overflow: 'hidden',
  },
  trackFill: { height: '100%', borderRadius: 999 },
});
