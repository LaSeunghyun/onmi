import React from 'react';
import { StyleSheet, View, ViewProps } from 'react-native';

import { border, radius, space, surface } from '@/theme/tokens';

type CardProps = ViewProps;

export function Card({ style, ...props }: CardProps) {
  return <View {...props} style={[styles.base, style]} />;
}

const styles = StyleSheet.create({
  base: {
    backgroundColor: surface.elevated,
    borderWidth: 1,
    borderColor: border.subtle,
    borderRadius: radius.lg,
    padding: space[4],
    gap: space[2],
  },
});
