import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

export interface BarDataItem {
  label: string;
  value: number;
}

interface MiniBarChartProps {
  data: BarDataItem[];
  chartHeight?: number;
  primaryColor?: string;
  highlightColor?: string;
}

export function MiniBarChart({
  data,
  chartHeight = 100,
  primaryColor = '#3B82F6',
  highlightColor = '#1D4ED8',
}: MiniBarChartProps) {
  const maxValue = Math.max(...data.map((d) => d.value), 1);
  const peakIndex = data.findIndex((d) => d.value === maxValue);

  return (
    <View style={styles.root}>
      <View style={[styles.barsArea, { height: chartHeight }]}>
        {data.map((item, i) => {
          const barH = Math.max(4, (item.value / maxValue) * chartHeight * 0.88);
          const isPeak = i === peakIndex;
          return (
            <View key={i} style={styles.barWrapper}>
              {isPeak && <Text style={[styles.peakValue, { color: highlightColor }]}>{item.value}</Text>}
              <View
                style={[
                  styles.bar,
                  {
                    height: barH,
                    backgroundColor: isPeak ? highlightColor : primaryColor,
                    opacity: isPeak ? 1 : 0.38,
                  },
                ]}
              />
            </View>
          );
        })}
      </View>
      <View style={styles.labelsRow}>
        {data.map((item, i) => (
          <Text key={i} style={styles.labelText}>
            {item.label}
          </Text>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { width: '100%' },
  barsArea: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 6,
    paddingTop: 18,
  },
  barWrapper: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'flex-end',
    gap: 2,
  },
  peakValue: {
    fontSize: 10,
    fontWeight: '700',
    marginBottom: 2,
  },
  bar: {
    width: '100%',
    borderRadius: 4,
  },
  labelsRow: {
    flexDirection: 'row',
    marginTop: 6,
  },
  labelText: {
    flex: 1,
    textAlign: 'center',
    fontSize: 11,
    color: '#9CA3AF',
  },
});
