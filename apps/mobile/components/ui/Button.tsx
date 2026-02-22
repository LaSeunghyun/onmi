import React, { useState } from 'react';
import { Pressable, StyleProp, StyleSheet, Text, ViewStyle } from 'react-native';

import { color, fontSize, fontWeight, radius, text as textToken } from '@/theme/tokens';

type ButtonVariant = 'primary' | 'secondary' | 'danger';
type ButtonSize = 'md' | 'lg';

type ButtonProps = {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  variant?: ButtonVariant;
  size?: ButtonSize;
  style?: StyleProp<ViewStyle>;
};

export function Button({ label, onPress, disabled = false, variant = 'primary', size = 'md', style }: ButtonProps) {
  const [focused, setFocused] = useState(false);

  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={({ pressed }) => [
        styles.base,
        variantStyles[variant],
        sizeStyles[size],
        pressed && styles.pressed,
        disabled && styles.disabled,
        focused && styles.focused,
        style,
      ]}
    >
      <Text style={[styles.text, variant === 'secondary' && styles.secondaryText]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: radius.sm,
  },
  text: {
    color: textToken.inverse,
    fontWeight: fontWeight.bold,
    fontSize: fontSize.sm,
  },
  secondaryText: {
    color: textToken.primary,
  },
  pressed: {
    opacity: 0.85,
  },
  disabled: {
    opacity: 0.6,
  },
  focused: {
    borderWidth: 2,
    borderColor: color.secondary[300],
  },
});

const variantStyles = StyleSheet.create({
  primary: {
    backgroundColor: color.primary[500],
  },
  secondary: {
    backgroundColor: color.neutral[100],
  },
  danger: {
    backgroundColor: color.error[600],
  },
});

const sizeStyles = StyleSheet.create({
  md: {
    height: 44,
    paddingHorizontal: 14,
  },
  lg: {
    height: 48,
    paddingHorizontal: 16,
  },
});
