import { StyleSheet } from 'react-native';

import { border, color, fontSize, fontWeight, radius, space, surface, text } from '@/theme/tokens';

export const ui = StyleSheet.create({
  page: {
    flex: 1,
    backgroundColor: surface.canvas,
  },
  pageSubtle: {
    flex: 1,
    backgroundColor: surface.subtle,
  },
  card: {
    backgroundColor: surface.elevated,
    borderWidth: 1,
    borderColor: border.subtle,
    borderRadius: radius.lg,
    padding: space[4],
    gap: space[2],
  },
  input: {
    borderWidth: 1,
    borderColor: border.default,
    borderRadius: radius.sm,
    paddingHorizontal: space[3],
    height: 42,
    backgroundColor: surface.canvas,
    color: text.primary,
  },
  btnPrimary: {
    height: 44,
    borderRadius: radius.sm,
    backgroundColor: color.primary[500],
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnPrimaryText: {
    color: text.inverse,
    fontWeight: fontWeight.bold,
    fontSize: fontSize.sm,
  },
  btnSecondary: {
    height: 40,
    borderRadius: radius.sm,
    backgroundColor: color.neutral[100],
    alignItems: 'center',
    justifyContent: 'center',
  },
  btnDanger: {
    height: 44,
    borderRadius: radius.sm,
    backgroundColor: color.error[600],
    alignItems: 'center',
    justifyContent: 'center',
  },
});
