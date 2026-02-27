import { Platform } from 'react-native';

export const color = {
  primary: {
    50: '#FFF7ED',
    100: '#FFEDD5',
    200: '#FED7AA',
    300: '#FDBA74',
    400: '#FB923C',
    500: '#F97316',
    600: '#EA580C',
    700: '#C2410C',
    800: '#9A3412',
    900: '#7C2D12',
  },
  secondary: {
    50: '#EEF2FF',
    100: '#E0E7FF',
    200: '#C7D2FE',
    300: '#A5B4FC',
    400: '#818CF8',
    500: '#6366F1',
    600: '#4F46E5',
    700: '#4338CA',
    800: '#3730A3',
    900: '#312E81',
  },
  neutral: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  success: {
    500: '#22C55E',
    600: '#16A34A',
    700: '#15803D',
  },
  warning: {
    500: '#F59E0B',
    600: '#D97706',
  },
  error: {
    500: '#EF4444',
    600: '#DC2626',
    700: '#B91C1C',
  },
  info: {
    500: '#3B82F6',
    600: '#2563EB',
  },
} as const;

export const surface = {
  canvas: '#FFFFFF',
  subtle: color.neutral[50],
  elevated: '#FFFFFF',
  overlay: 'rgba(17,24,39,0.4)',
} as const;

export const text = {
  primary: color.neutral[900],
  secondary: color.neutral[700],
  tertiary: color.neutral[500],
  inverse: '#FFFFFF',
  link: color.secondary[600],
} as const;

export const border = {
  subtle: color.neutral[200],
  default: color.neutral[300],
  strong: color.neutral[400],
  inverse: '#FFFFFF',
  hairline: 'rgba(0,0,0,0.1)',
} as const;

export const space = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
} as const;

export const radius = {
  sm: 8,
  md: 10,
  lg: 12,
  xl: 16,
  full: 999,
} as const;

export const fontSize = {
  xs: 12,
  sm: 14,
  base: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
} as const;

export const lineHeight = {
  sm: 18,
  base: 22,
  lg: 24,
  xl: 28,
} as const;

export const fontWeight = {
  regular: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
  extrabold: '800',
} as const;

export const motion = {
  fast: 120,
  normal: 180,
  slow: 260,
  reduceMotion: Platform.OS !== 'web',
} as const;

/** 주식 신호·공시 (design-system-stock-feature) */
export const signal = {
  buy: color.success[600],
  sell: color.error[600],
  hold: color.neutral[600],
} as const;

export const disclosure = {
  positive: color.success[600],
  neutral: color.neutral[500],
  negative: color.error[600],
} as const;

/** 어드민 사이드바/레이아웃 전용 팔레트 */
export const admin = {
  pageBg: '#DCE1E8',
  sidebar: {
    bg: '#1F2E46',
    border: '#2B3B57',
    brandAccent: '#0EA5E9',
    brandSub: '#8EA0BF',
    sectionLabel: '#7E91AF',
    navText: '#D4DEEE',
    navActiveBg: '#06B6D4',
    logoutBorder: '#32435F',
  },
  topbar: {
    bg: surface.canvas,
    border: color.neutral[200],
  },
} as const;

export const semantic = {
  light: {
    surface: surface.canvas,
    surfaceSubtle: surface.subtle,
    textPrimary: text.primary,
    textSecondary: text.secondary,
    borderDefault: border.default,
    actionPrimary: color.primary[500],
    actionSecondary: color.secondary[600],
    feedbackDanger: color.error[600],
  },
  dark: {
    surface: color.neutral[900],
    surfaceSubtle: color.neutral[800],
    textPrimary: '#FFFFFF',
    textSecondary: color.neutral[300],
    borderDefault: color.neutral[600],
    actionPrimary: color.primary[400],
    actionSecondary: color.secondary[400],
    feedbackDanger: color.error[500],
  },
} as const;
