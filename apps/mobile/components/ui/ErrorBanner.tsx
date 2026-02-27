import React from 'react';
import { StyleSheet, Text, View } from 'react-native';

import { color, fontSize, fontWeight, radius, space } from '@/theme/tokens';

type ErrorBannerProps = {
  message: string | null;
};

export function ErrorBanner({ message }: ErrorBannerProps) {
  if (!message) return null;

  return (
    <View accessibilityLiveRegion="polite" style={styles.banner}>
      <Text style={styles.text}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  banner: {
    backgroundColor: '#FEF2F2',
    borderWidth: 1,
    borderColor: color.error[500],
    borderRadius: radius.sm,
    paddingHorizontal: space[3],
    paddingVertical: space[2],
  },
  text: {
    color: color.error[700],
    fontSize: fontSize.sm,
    fontWeight: fontWeight.medium,
  },
});
