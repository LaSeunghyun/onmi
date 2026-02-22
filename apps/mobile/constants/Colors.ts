import { color, surface, text } from '@/theme/tokens';

const tintColorLight = color.primary[500];
const tintColorDark = text.inverse;

export default {
  light: {
    text: text.primary,
    background: surface.canvas,
    tint: tintColorLight,
    tabIconDefault: color.neutral[300],
    tabIconSelected: tintColorLight,
  },
  dark: {
    text: text.inverse,
    background: color.neutral[900],
    tint: tintColorDark,
    tabIconDefault: color.neutral[400],
    tabIconSelected: tintColorDark,
  },
};
