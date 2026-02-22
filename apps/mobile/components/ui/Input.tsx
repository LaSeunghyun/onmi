import React, { useState } from 'react';
import { StyleSheet, TextInput, TextInputProps } from 'react-native';

import { border, color, radius, space, surface, text } from '@/theme/tokens';

type InputProps = TextInputProps & {
  hasError?: boolean;
};

export function Input({ hasError = false, style, ...props }: InputProps) {
  const [focused, setFocused] = useState(false);

  return (
    <TextInput
      {...props}
      style={[styles.base, focused && styles.focused, hasError && styles.error, style]}
      placeholderTextColor={text.tertiary}
      onFocus={(e) => {
        setFocused(true);
        props.onFocus?.(e);
      }}
      onBlur={(e) => {
        setFocused(false);
        props.onBlur?.(e);
      }}
    />
  );
}

const styles = StyleSheet.create({
  base: {
    borderWidth: 1,
    borderColor: border.default,
    borderRadius: radius.sm,
    paddingHorizontal: space[3],
    height: 42,
    backgroundColor: surface.canvas,
    color: text.primary,
  },
  focused: {
    borderColor: color.secondary[500],
  },
  error: {
    borderColor: color.error[600],
  },
});
